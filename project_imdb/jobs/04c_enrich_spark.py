"""Section 3: Data enrichment, step C: everything which is not the download.

The subject is explicit: "Data gathering may be done outside of Spark but all other operations
such as cleaning, schema enforcement, etc., must be performed using Spark". So step B only wrote
raw jsonl, and this job does all the rest in spark: explicit schema, cleaning of the texts, join
back with the imdb tables, the note when an information is missing, and the coverage report.

The output is one row per film, with its synopsis, its lineage, and the 3 principals with their
biography and their own lineage.
"""
import sys
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType

sys.path.insert(0, "/home/jovyan/work/jobs")
from common import get_spark, read, save_result, ROOT, OUTPUT, PARQUET

ENRICHED = f"{ROOT}/enriched"

# the schema of the jsonl, we declare it instead of inferring it: inferring reads the whole file
# one more time, and a field missing from the first rows would silently disappear from the
# dataframe
WIKI_SCHEMA = StructType([
    StructField("imdb_id", StringType()),
    StructField("label", StringType()),
    StructField("text", StringType()),
    StructField("source_name", StringType()),
    StructField("source_url", StringType()),
    StructField("wikidata_uri", StringType()),
    StructField("retrieved_at", StringType()),
    StructField("note", StringType()),
])


def load_wiki(spark, path, kind):
    """Reads one jsonl, enforces the schema and cleans the text.

    The cleaning stays conservative on purpose: we must not rewrite what a human wrote, we only
    normalize the white spaces and we drop what is empty. Any transformation of the content
    would turn a text written by a human into something else.
    """
    df = spark.read.schema(WIKI_SCHEMA).json(path)

    return (df
            # the extracts keep the line breaks of the article, we put everything on one line
            .withColumn("text", F.regexp_replace(F.col("text"), r"\s+", " "))
            .withColumn("text", F.trim(F.col("text")))
            # a text of a few characters is not a synopsis, it is a leftover
            .withColumn("text", F.when(F.length(F.col("text")) >= 50, F.col("text")))
            .withColumn("text_length", F.length(F.col("text")))
            .withColumn("has_text", F.col("text").isNotNull())
            # we write the note here, when the text did not survive the cleaning, like this
            # the output always says why something is missing instead of being just null
            .withColumn("note",
                        F.when(F.col("text").isNotNull(), F.col("note"))
                        .when(F.col("note").isNotNull(), F.col("note"))
                        .otherwise(F.lit("extract too short to be a usable summary")))
            .withColumn("entity_type", F.lit(kind))
            .withColumn("retrieved_at", F.to_timestamp("retrieved_at"))
            .dropDuplicates(["imdb_id"]))


def main():
    spark = get_spark("imdb-enrichment")

    films_target = spark.read.parquet(f"{OUTPUT}/targets/films")
    film_people = spark.read.parquet(f"{OUTPUT}/targets/film_people")
    names = read(spark, "name.basics").select("nconst", "primaryName", "birthYear", "deathYear")

    wiki_films = load_wiki(spark, f"{ENRICHED}/films.jsonl", "film")
    wiki_people = load_wiki(spark, f"{ENRICHED}/people.jsonl", "person")

    # ---- the principals of each film, with their biography and their own lineage
    people_enriched = (film_people
                       .join(names, "nconst")
                       .join(wiki_people.select(
                           F.col("imdb_id").alias("nconst"),
                           F.col("text").alias("bio"),
                           F.col("source_url").alias("bio_source_url"),
                           F.col("source_name").alias("bio_source_name"),
                           F.col("wikidata_uri").alias("bio_wikidata_uri"),
                           F.col("retrieved_at").alias("bio_retrieved_at"),
                           F.col("note").alias("bio_note")), "nconst", "left")
                       .withColumn("bio_note",
                                   F.coalesce(F.col("bio_note"),
                                              F.lit("not downloaded in this run"))))

    principals_struct = (people_enriched
                         .groupBy("tconst")
                         .agg(F.sort_array(F.collect_list(F.struct(
                             F.col("ordering"), F.col("nconst"), F.col("primaryName"),
                             F.col("category"), F.col("birthYear"), F.col("deathYear"),
                             F.col("bio"), F.col("bio_source_name"), F.col("bio_source_url"),
                             F.col("bio_wikidata_uri"), F.col("bio_retrieved_at"),
                             F.col("bio_note")))).alias("principals"),
                              F.count("*").alias("n_principals"),
                              F.sum(F.when(F.col("bio").isNotNull(), 1).otherwise(0))
                              .alias("n_principals_with_bio")))

    # ---- one row per film: imdb facts + synopsis + lineage + the principals
    enriched = (films_target
                .join(wiki_films.select(
                    F.col("imdb_id").alias("tconst"),
                    F.col("text").alias("synopsis"),
                    F.col("source_url").alias("synopsis_source_url"),
                    F.col("source_name").alias("synopsis_source_name"),
                    F.col("wikidata_uri").alias("synopsis_wikidata_uri"),
                    F.col("retrieved_at").alias("synopsis_retrieved_at"),
                    F.col("note").alias("synopsis_note")), "tconst", "left")
                .withColumn("synopsis_note",
                            F.coalesce(F.col("synopsis_note"),
                                       F.lit("not downloaded in this run")))
                .join(principals_struct, "tconst", "left"))

    enriched.write.mode("overwrite").parquet(f"{PARQUET}/enriched/films")
    enriched.cache()

    # ---- the coverage report: how much of what we wanted did we really get
    coverage = enriched.agg(
        F.count("*").alias("n_films"),
        F.sum(F.when(F.col("synopsis").isNotNull(), 1).otherwise(0)).alias("n_with_synopsis"),
        F.round(100 * F.avg(F.when(F.col("synopsis").isNotNull(), 1.0).otherwise(0.0)),
                1).alias("pct_with_synopsis"),
        F.sum(F.coalesce(F.col("n_principals"), F.lit(0))).alias("n_principals"),
        F.sum(F.coalesce(F.col("n_principals_with_bio"), F.lit(0))).alias("n_principals_with_bio"),
        F.round(F.avg(F.length(F.col("synopsis"))), 0).alias("avg_synopsis_length"),
    )
    save_result(coverage, "e2_enrichment_coverage")

    # why the missing ones are missing, counted by reason
    reasons = (enriched.where(F.col("synopsis").isNull())
               .groupBy("synopsis_note").agg(F.count("*").alias("n_films"))
               .orderBy(F.col("n_films").desc()))
    save_result(reasons, "e3_missing_reasons")

    # a readable sample for the report, with its lineage
    sample = (enriched.where(F.col("synopsis").isNotNull())
              .orderBy(F.col("numVotes").desc())
              .select("primaryTitle", "startYear", "averageRating",
                      F.substring(F.col("synopsis"), 1, 240).alias("synopsis_start"),
                      "synopsis_source_url", "n_principals_with_bio"))
    save_result(sample, "e4_sample", limit=10)

    spark.stop()


if __name__ == "__main__":
    main()
