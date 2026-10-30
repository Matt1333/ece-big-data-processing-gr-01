"""Section 3: Data enrichment, step A: choose what has to be enriched.

The subject asks, for the feature films released between 1980 and 2025, a synopsis for the top 10
films of each genre of each year, and a biography for at least 3 principals of each of these
films.

This job only selects, it downloads nothing. It writes two small csv with imdb ids, and the
fetcher (step B, outside spark) reads them. Keeping the selection in spark and the download
outside is what the subject asks: "Data gathering may be done outside of Spark but all other
operations must be performed using Spark".

About the scalability: nothing here is hardcoded to a year or to a genre. YEARS and TOP_N are
parameters, and if we remove the filter the same code runs on the whole dataset without any
structural change.
"""
import sys
from pyspark.sql import functions as F
from pyspark.sql import Window

sys.path.insert(0, "/home/jovyan/work/jobs")
from common import get_spark, read, save_result, OUTPUT

YEAR_MIN, YEAR_MAX = 1980, 2025
TOP_N = 10               # films per genre per year
PRINCIPALS_PER_FILM = 3
MIN_VOTES = 1000         # a rating computed on 12 votes is not a ranking


def main():
    spark = get_spark("imdb-select-targets")

    basics = read(spark, "title.basics")
    ratings = read(spark, "title.ratings")

    films = (basics
             .where((F.col("titleType") == "movie")
                    & (F.col("runtimeMinutes") >= 60)
                    & F.col("startYear").between(YEAR_MIN, YEAR_MAX))
             .join(ratings, "tconst")
             .where(F.col("numVotes") >= MIN_VOTES))

    by_genre = (films.withColumn("genre", F.explode("genres_array"))
                .where((F.col("genre") != "") & F.col("genre").isNotNull()))

    # "top" = best rated, with the threshold on the votes above to keep the ranking
    # meaningful. numVotes breaks the ties: between two films at 7.8, the one seen by more
    # people wins.
    w = Window.partitionBy("startYear", "genre").orderBy(
        F.col("averageRating").desc(), F.col("numVotes").desc())

    top = (by_genre.withColumn("rank", F.row_number().over(w))
           .where(F.col("rank") <= TOP_N))

    # a film can be in the top of several genres, and we want to download it only one time
    target_films = (top.select("tconst", "primaryTitle", "originalTitle", "startYear",
                               "averageRating", "numVotes")
                    .dropDuplicates(["tconst"]))
    target_films.cache()
    n_films = target_films.count()

    # the principals of these films: imdb already gives them ordered by importance (`ordering`)
    principals = read(spark, "title.principals")
    names = read(spark, "name.basics").select("nconst", "primaryName", "birthYear")

    w_p = Window.partitionBy("tconst").orderBy(F.col("ordering").asc())
    target_people = (principals.join(target_films.select("tconst"), "tconst")
                     .where(F.col("category").isin("actor", "actress", "director", "writer"))
                     .withColumn("rank", F.row_number().over(w_p))
                     .where(F.col("rank") <= PRINCIPALS_PER_FILM)
                     .select("tconst", "nconst", "category", "ordering"))

    film_people = target_people  # the link film <-> person, we keep it for the join of step C
    people = (target_people.select("nconst").distinct().join(names, "nconst"))
    people.cache()
    n_people = people.count()

    print(f"films to enrich   : {n_films:,}")
    print(f"people to enrich  : {n_people:,}")

    # the lists for the fetcher: one small csv each, read by normal python
    (target_films.select("tconst", "primaryTitle", "originalTitle", "startYear")
     .coalesce(1).write.mode("overwrite")
     .option("header", True).csv(f"{OUTPUT}/targets/films_csv"))
    (people.select("nconst", "primaryName", "birthYear")
     .coalesce(1).write.mode("overwrite")
     .option("header", True).csv(f"{OUTPUT}/targets/people_csv"))

    # the mapping film <-> principal, we need it to rebuild the enriched record in step C
    film_people.write.mode("overwrite").parquet(f"{OUTPUT}/targets/film_people")
    target_films.write.mode("overwrite").parquet(f"{OUTPUT}/targets/films")

    save_result(
        spark.createDataFrame([(YEAR_MIN, YEAR_MAX, TOP_N, PRINCIPALS_PER_FILM,
                               MIN_VOTES, n_films, n_people)],
                              ["year_min", "year_max", "top_n_per_genre_per_year",
                               "principals_per_film", "min_votes", "n_films", "n_people"]),
        "e1_enrichment_scope")

    spark.stop()


if __name__ == "__main__":
    main()
