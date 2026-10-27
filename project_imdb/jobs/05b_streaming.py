"""Section 4: Streaming, the consumer.

A Structured Streaming pipeline which reads the live Wikipedia changes from kafka and keeps the
ones concerning our imdb dataset.

How we match an event with our data. The stream gives us a page title, our dataset gives film
titles and people names, so this is a stream static join: we join the stream with a static
dataframe built one time from the parquet. To be sure we do not miss a match because of a
detail, we normalize the two sides exactly the same way (lower case, accents and punctuation
removed), and the normalized title is the join key. It is an exact match on a normalized string,
never a fuzzy one: a fuzzy match would silently bring the wrong film, and we would have no way
to notice it.

About the late data. Wikipedia gives us two times: `meta.dt`, when the edit happened (event
time), and the moment when kafka received it (processing time). They are different, and an event
can arrive after the window where it belongs was already reported. We declare the event time
with a watermark of 10 minutes: spark then accepts a late event until 10 minutes after the
maximum event time it has seen, and it drops what arrives later. Without the watermark spark
would have to keep the state of every window for ever, because it could never know that a window
is finished. 10 minutes is a compromise: long enough for the normal lag of the stream (a few
seconds), short enough so the state stays small in a test window of 15 to 30 minutes.
"""
import sys
from pyspark.sql import functions as F
from pyspark.sql.types import (StructType, StructField, StringType, LongType,
                               BooleanType, IntegerType)

sys.path.insert(0, "/home/jovyan/work/jobs")
from common import get_spark, read, save_result, OUTPUT

KAFKA_BOOTSTRAP = "kafka:19092"      # the internal name, we are inside the docker network

# Spark does not ship the kafka source, it is downloaded when the session starts. The version
# has to match the spark version and the scala version of the image: spark 4.2.0 built against
# scala 2.13, the same pairing as in the structured streaming lab, which used 4.1.0 on the image
# of that time.
KAFKA_PACKAGE = "org.apache.spark:spark-sql-kafka-0-10_2.13:4.2.0"
TOPIC = "wiki-changes"
WATERMARK = "10 minutes"
WINDOW = "5 minutes"

# only the fields that we use: the schema is explicit because a stream has no place to infer
# one, and because an unexpected field must not change the shape of our dataframe
EVENT_SCHEMA = StructType([
    StructField("title", StringType()),
    StructField("type", StringType()),
    StructField("user", StringType()),
    StructField("bot", BooleanType()),
    StructField("timestamp", LongType()),
    StructField("server_name", StringType()),
    StructField("comment", StringType()),
    StructField("length", StructType([
        StructField("old", IntegerType()),
        StructField("new", IntegerType()),
    ])),
    StructField("meta", StructType([
        StructField("dt", StringType()),
        StructField("id", StringType()),
    ])),
])


def normalize(col):
    """The same normalization on the two sides of the join.

    Lower case, accents removed, and everything which is not a letter or a digit becomes one
    single space. Like this "WALL.E" and "Wall E" become the same key, and two different films
    stay different: we do not make the comparison loose, only insensitive to the writing.
    """
    no_accents = F.translate(F.lower(col),
                             "àâäáãçèéêëìíîïñòóôöõùúûüýÿ",
                             "aaaaaceeeeiiiinooooouuuuyy")
    return F.trim(F.regexp_replace(F.regexp_replace(no_accents, "[^a-z0-9]+", " "), " +", " "))


def build_reference(spark):
    """The static side of the join: what, in our dataset, a wikipedia page can talk about.

    How wide this is decides if the pipeline sees something or nothing at all. The subject asks
    for a filter "sufficiently broad to guarantee that multiple matching events are captured" in
    a window of 15 to 30 minutes, and our first version of this function failed on that: it was
    taking only the entities we had enriched, around 17 000 of them. Against the 3 to 5 edits
    per second that the english wikipedia receives over millions of articles, a target of
    17 000 pages is almost never hit, and a run of 16 minutes matched nothing.

    So the reference is now every title of the dataset which can plausibly have an article,
    measured on this dump:

        movie                               758 864
        movie + tvSeries + tvMiniSeries   1 138 819
        every person                     15 716 378

    We take the 1 138 819 titles, which is 66 times more than the first version, and we keep the
    enriched principals for the people. We leave out every person on purpose: 15.7 million rows
    on the static side of a join replayed at every micro batch costs much more than what the
    extra matches are worth, and the people who are really edited are mostly the ones who are
    known enough to be a principal of an enriched film.

    The primary title and the original title both become a key, because a wikipedia article can
    be named after one or after the other ("La Haine" and "Hate").

    The result is too big to broadcast (around 1.1 million rows), so the join is a normal stream
    static join: spark reads this side again at every micro batch, and this is the price of a
    reference wide enough to catch something.
    """
    titles = read(spark, "title.basics").where(
        F.col("titleType").isin("movie", "tvSeries", "tvMiniSeries"))

    primary = (titles.select(F.col("tconst").alias("imdb_id"),
                             F.col("primaryTitle").alias("label"),
                             F.col("startYear").alias("year"))
               .withColumn("entity_type", F.lit("title")))
    original = (titles.where(F.col("originalTitle") != F.col("primaryTitle"))
                .select(F.col("tconst").alias("imdb_id"),
                        F.col("originalTitle").alias("label"),
                        F.col("startYear").alias("year"))
                .withColumn("entity_type", F.lit("title")))

    people_ids = spark.read.parquet(f"{OUTPUT}/targets/film_people").select("nconst").distinct()
    people = (read(spark, "name.basics").join(people_ids, "nconst")
              .select(F.col("nconst").alias("imdb_id"),
                      F.col("primaryName").alias("label"),
                      F.col("birthYear").alias("year"))
              .withColumn("entity_type", F.lit("person")))

    return (primary.unionByName(original).unionByName(people)
            .withColumn("key", normalize(F.col("label")))
            .where(F.col("key") != "")
            # one row per key: if not, two films with the same title would duplicate every
            # matching edit, and we only need to know that the page concerns our dataset
            .dropDuplicates(["key"]))


def main():
    spark = get_spark("imdb-streaming", packages=[KAFKA_PACKAGE])
    spark.sparkContext.setLogLevel("WARN")

    # cached, because the static side of a stream static join is read again at every micro
    # batch, and without the cache each one would rebuild the whole plan from the parquet
    reference = build_reference(spark).cache()
    print(f"reference entities: {reference.count():,}")

    raw = (spark.readStream
           .format("kafka")
           .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP)
           .option("subscribe", TOPIC)
           .option("startingOffsets", "earliest")
           # without this, one slow batch makes the next one read everything which piled up
           .option("maxOffsetsPerTrigger", 5000)
           .load())

    events = (raw
              .select(F.from_json(F.col("value").cast("string"), EVENT_SCHEMA).alias("e"),
                      F.col("timestamp").alias("kafka_time"))
              .select("e.*", "kafka_time")
              # meta.dt is the event time given by wikipedia, kafka_time is when we received it
              .withColumn("event_time", F.to_timestamp("meta.dt"))
              .withColumn("lag_seconds",
                          F.unix_timestamp("kafka_time") - F.unix_timestamp("event_time"))
              .withColumn("key", normalize(F.col("title"))))

    # the watermark has to be declared before any stateful operation
    events = events.withWatermark("event_time", WATERMARK)

    # stream static join: the stream keeps its streaming nature, and the static side is read
    # again at each micro batch. An inner join keeps only the edits concerning our dataset.
    matched = (events.join(reference, "key")
               .select("event_time", "kafka_time", "lag_seconds", "title", "user", "bot",
                       "imdb_id", "entity_type", "label", "year",
                       F.col("length.new").alias("new_length"),
                       F.col("length.old").alias("old_length"),
                       "comment"))

    # 1. every matching edit, written to parquet. The checkpoint is what makes the job
    # restartable without losing a row and without duplicating one.
    q_rows = (matched.writeStream
              .format("parquet")
              .option("path", f"{OUTPUT}/streaming/matched_edits")
              .option("checkpointLocation", f"{OUTPUT}/streaming/_ckpt_rows")
              .outputMode("append")
              .trigger(processingTime="30 seconds")
              .queryName("matched_edits")
              .start())

    # 2. a windowed count on the event time, to see the activity over the time. The `update`
    # mode prints only the windows which changed in this batch, and this is what we want while
    # we watch it.
    q_windows = (matched
                 .groupBy(F.window(F.col("event_time"), WINDOW), F.col("entity_type"))
                 # approx_count_distinct and not countDistinct: an exact distinct count is not
                 # available on a stream, and there is a good reason. Counting exactly means
                 # remembering every id already seen in the window, so the state grows with the
                 # traffic and never goes down. The approximate version keeps a sketch of a
                 # fixed size instead. We compute the exact figure in `final_metrics`, on the
                 # parquet, in batch, where keeping everything in memory is not a problem.
                 .agg(F.count("*").alias("n_edits"),
                      F.approx_count_distinct("imdb_id").alias("n_entities_approx"),
                      F.round(F.avg("lag_seconds"), 1).alias("avg_lag_seconds"))
                 .writeStream
                 .format("console")
                 .outputMode("update")
                 .option("truncate", False)
                 .trigger(processingTime="30 seconds")
                 .queryName("edits_per_window")
                 .start())

    # 3. the volume we saw, matched or not: it is the denominator which shows the filter is wide
    q_total = (events
               .groupBy(F.window(F.col("event_time"), WINDOW))
               .agg(F.count("*").alias("n_events_total"))
               .writeStream
               .format("console")
               .outputMode("update")
               .option("truncate", False)
               .trigger(processingTime="60 seconds")
               .queryName("all_events_per_window")
               .start())

    run_minutes = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    queries = [q_rows, q_windows, q_total]

    if run_minutes:
        print(f"three queries started, stopping after {run_minutes} minutes")
        spark.streams.awaitAnyTermination(run_minutes * 60)
        for q in queries:
            if q.isActive:
                q.stop()
        for q in queries:
            q.awaitTermination()
        final_metrics(spark, run_minutes)
    else:
        print("three queries started, stop with ctrl+c")
        spark.streams.awaitAnyTermination()


def final_metrics(spark, run_minutes):
    """The figures asked by the report, measured once the window is closed.

    The three streaming queries print on the console, which is nice to watch but leaves nothing
    that we can quote. So we read back, in batch, what the run produced: the complete topic to
    know how many events went through, and the parquet of the matching edits to know how many
    were kept and how late they arrived.
    """
    total = (spark.read.format("kafka")
             .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP)
             .option("subscribe", TOPIC)
             .option("startingOffsets", "earliest")
             .option("endingOffsets", "latest")
             .load()
             .count())

    try:
        rows = spark.read.parquet(f"{OUTPUT}/streaming/matched_edits")
    except Exception:
        print("no matching edit was written, nothing to measure")
        return

    metrics = rows.agg(
        F.lit(run_minutes).alias("window_minutes"),
        F.lit(total).alias("events_seen"),
        F.count(F.lit(1)).alias("events_matched"),
        F.round(100.0 * F.count(F.lit(1)) / F.lit(total), 3).alias("pct_matched"),
        F.countDistinct("imdb_id").alias("distinct_entities_touched"),
        F.round(F.avg("lag_seconds"), 1).alias("avg_lag_seconds"),
        F.min("lag_seconds").alias("min_lag_seconds"),
        F.max("lag_seconds").alias("max_lag_seconds"),
    )
    save_result(metrics, "s1_streaming_metrics")

    save_result(rows.groupBy("entity_type").agg(
        F.count(F.lit(1)).alias("n_edits"),
        F.countDistinct("imdb_id").alias("n_entities"),
        F.round(F.avg("lag_seconds"), 1).alias("avg_lag_seconds"),
    ).orderBy(F.col("n_edits").desc()), "s2_matched_by_entity_type")

    save_result(rows.select("event_time", "title", "label", "entity_type", "imdb_id",
                            "user", "bot", "lag_seconds")
                .orderBy(F.col("event_time").desc()), "s3_matched_edits_sample", limit=25)


if __name__ == "__main__":
    main()
