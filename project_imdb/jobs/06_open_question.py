"""Section 5: Open question.

**Does a recurring director and actor duo make better films than the same two people apart?**

Why the question is interesting. Cinema is full of famous pairs: Scorsese and De Niro, Burton and
Depp, Kurosawa and Mifune. The common idea is that these duos produce the best work of the two
careers. We can measure it on this dataset, and the interesting part is that the answer is not
obvious: it could also be that a director simply calls back the actor of a film which worked, and
in this case the duo would only follow the success instead of creating it.

Why it is not trivial. To answer we need four tables joined together (`title.crew` for the
directors, `title.principals` for the actors, `title.basics` to keep only the feature films,
`title.ratings` for the note), one list exploded into rows, a comparison of each person against
himself, and above all a baseline which has to *exclude* the shared films. If we compare a duo
against the complete career of its members we count the shared films on the two sides and we
flatten the effect mechanically.

How we compute the baseline without a second pass. For a director we know the sum and the count
of the ratings of all his films, and the sum and the count of the films made with this actor. The
average of the films made *without* this actor is the difference of the two sums divided by the
difference of the two counts. It is exact, and it costs one aggregation instead of one join per
pair.

We need no additional dataset, the imdb tables are enough.
"""
import sys
from pyspark.sql import functions as F

sys.path.insert(0, "/home/jovyan/work/jobs")
from common import get_spark, read, save_result

MIN_VOTES = 1000          # below that the rating is noise
MIN_TOGETHER = 3          # what we call a "recurring" duo
LEAD_ORDERING = 3         # imdb orders the principals by importance, we keep the top billing
MIN_APART = 3             # films each person needs outside the duo, for the baseline to be a career


def main():
    spark = get_spark("imdb-open-question")

    films = (read(spark, "title.basics")
             .where((F.col("titleType") == "movie")
                    & (F.col("runtimeMinutes") >= 60)
                    & F.col("startYear").isNotNull())
             .join(read(spark, "title.ratings"), "tconst")
             .where(F.col("numVotes") >= MIN_VOTES)
             .select("tconst", "primaryTitle", "startYear", "averageRating"))
    films.cache()

    # one row per (film, director)
    directors = (read(spark, "title.crew")
                 .withColumn("director", F.explode("directors_array"))
                 .where(F.col("director") != "")
                 .select("tconst", "director")
                 # a person can be listed twice on one film, and a film must count once
                 .dropDuplicates(["tconst", "director"])
                 .join(films, "tconst"))

    # one row per (film, lead actor)
    actors = (read(spark, "title.principals")
              .where(F.col("category").isin("actor", "actress")
                     & (F.col("ordering") <= LEAD_ORDERING))
              .select("tconst", F.col("nconst").alias("actor"))
              # title.principals can list the same person twice on a film (two orderings, or
              # once as actor and once as actress): without this the shared films are counted
              # twice on the duo side and once on the career side, and the baseline goes negative
              .dropDuplicates(["tconst", "actor"])
              .join(films.select("tconst"), "tconst"))

    # ---- the three aggregations, each one in a single pass
    # the complete career of each director, and of each actor
    dir_total = directors.groupBy("director").agg(
        F.sum("averageRating").alias("d_sum"), F.count("*").alias("d_n"))
    act_total = (actors.join(films, "tconst").groupBy("actor").agg(
        F.sum("averageRating").alias("a_sum"), F.count("*").alias("a_n")))

    # the films that the two of them made together
    pairs = (directors.join(actors, "tconst")
             # a director who is also the lead actor of his own film is not a duo: the two sides
             # of the comparison would be the same career, counted twice
             .where(F.col("director") != F.col("actor"))
             .groupBy("director", "actor")
             .agg(F.sum("averageRating").alias("t_sum"),
                  F.count("*").alias("t_n"),
                  F.round(F.avg("averageRating"), 2).alias("together_avg"),
                  F.min("startYear").alias("first_year"),
                  F.max("startYear").alias("last_year"))
             .where(F.col("t_n") >= MIN_TOGETHER))

    joined = (pairs.join(dir_total, "director").join(act_total, "actor")
              # the baseline: the same people, on everything *except* their shared films
              .where((F.col("d_n") - F.col("t_n") >= MIN_APART)
                     & (F.col("a_n") - F.col("t_n") >= MIN_APART))
              .withColumn("director_apart_avg",
                          (F.col("d_sum") - F.col("t_sum")) / (F.col("d_n") - F.col("t_n")))
              .withColumn("actor_apart_avg",
                          (F.col("a_sum") - F.col("t_sum")) / (F.col("a_n") - F.col("t_n")))
              .withColumn("apart_avg",
                          (F.col("director_apart_avg") + F.col("actor_apart_avg")) / 2)
              .withColumn("lift", F.round(F.col("together_avg") - F.col("apart_avg"), 2)))

    names = read(spark, "name.basics").select("nconst", "primaryName")
    result = (joined
              .join(names.withColumnRenamed("nconst", "director")
                    .withColumnRenamed("primaryName", "director_name"), "director")
              .join(names.withColumnRenamed("nconst", "actor")
                    .withColumnRenamed("primaryName", "actor_name"), "actor")
              .select("director_name", "actor_name",
                      F.col("t_n").alias("films_together"),
                      "first_year", "last_year", "together_avg",
                      F.round("director_apart_avg", 2).alias("director_apart_avg"),
                      F.round("actor_apart_avg", 2).alias("actor_apart_avg"),
                      # the baseline against which we measure the lift, we keep it in the
                      # output so a reader can verify the subtraction instead of trusting us
                      F.round("apart_avg", 2).alias("apart_avg"),
                      "lift"))
    result.cache()

    save_result(result.orderBy(F.col("lift").desc()), "o1_best_duos", limit=20)
    save_result(result.orderBy(F.col("lift").asc()), "o2_worst_duos", limit=20)
    save_result(result.orderBy(F.col("films_together").desc(), F.col("lift").desc()),
                "o3_most_prolific_duos", limit=20)

    # the answer to the question, in one line: does the duo help in general?
    summary = result.agg(
        F.count("*").alias("n_duos"),
        F.sum(F.when(F.col("lift") > 0, 1).otherwise(0)).alias("n_duos_better_together"),
        F.sum(F.when(F.col("lift") < 0, 1).otherwise(0)).alias("n_duos_worse_together"),
        # exact ties after rounding: without this column the three counts do not add up to n_duos
        F.sum(F.when(F.col("lift") == 0, 1).otherwise(0)).alias("n_duos_equal"),
        F.round(F.avg("lift"), 3).alias("avg_lift"),
        F.round(F.expr("percentile_approx(lift, 0.5)"), 3).alias("median_lift"),
        F.round(F.avg("together_avg"), 3).alias("avg_rating_together"),
        F.round(F.avg("apart_avg"), 3).alias("avg_rating_apart"),
    )
    save_result(summary, "o4_summary")

    # does the effect grow with the number of films made together?
    by_count = (result
                .withColumn("films_together_bucket",
                            F.when(F.col("films_together") >= 10, "10+")
                            .when(F.col("films_together") >= 6, "6-9")
                            .when(F.col("films_together") >= 4, "4-5")
                            .otherwise("3"))
                # the bucket is a label, so ordering on it would put "10+" before "3". We
                # carry the lower bound of the bucket and we sort on that instead
                .withColumn("bucket_from",
                            F.when(F.col("films_together") >= 10, 10)
                            .when(F.col("films_together") >= 6, 6)
                            .when(F.col("films_together") >= 4, 4)
                            .otherwise(3))
                .groupBy("bucket_from", "films_together_bucket")
                .agg(F.count("*").alias("n_duos"),
                     F.round(F.avg("lift"), 3).alias("avg_lift"),
                     F.round(F.avg("together_avg"), 2).alias("avg_rating_together"))
                .orderBy("bucket_from")
                .drop("bucket_from"))
    save_result(by_count, "o5_lift_by_number_of_films")

    spark.stop()


if __name__ == "__main__":
    main()
