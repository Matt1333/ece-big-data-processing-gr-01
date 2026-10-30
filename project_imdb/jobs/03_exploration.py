"""Section 2: Data exploration. The 8 questions of the subject.

Each question is one function, like this we can read and re run each one alone. They all work on
the `clean` layer.

Two definitions that we use everywhere, chosen one time so the whole section stays coherent:
  - a "feature film" is a title of type `movie` with a runtime of 60 minutes minimum. Imdb
    already separates `short` from `movie`, and the 60 minutes is the usual threshold on top.
  - a film is "successful" when its rating is >= 7.0 with at least 1000 votes. The threshold on
    the votes is important: without it a title rated 10.0 by 3 people would beat every real
    film.
"""
import sys
from pyspark.sql import functions as F
from pyspark.sql import Window

sys.path.insert(0, "/home/jovyan/work/jobs")
from common import get_spark, read, save_result

MIN_RUNTIME = 60
SUCCESS_RATING = 7.0
SUCCESS_VOTES = 1000


def movies_with_ratings(spark):
    """The base of almost all the questions: the feature films joined with their rating."""
    basics = read(spark, "title.basics")
    ratings = read(spark, "title.ratings")
    return (basics
            .where((F.col("titleType") == "movie")
                   & (F.col("runtimeMinutes") >= MIN_RUNTIME)
                   & F.col("startYear").isNotNull())
            .join(ratings, "tconst", "left"))


# ------------------------------------------------------------------- Q1 runtime outliers
def q1_runtime_outliers(spark):
    """Feature films with a length notably different from the average of their genre.

    We make "notably different" measurable with the z score: how many standard deviations the
    film is far from the mean of its genre. |z| > 3 is the usual threshold, it keeps the 0.3%
    most extreme values of a normal distribution. We use it per genre and not globally, because
    a documentary of 200 minutes and an animation of 200 minutes are not surprising the same
    way.

    A film has several genres, so we explode it: it is compared inside each of its genres.
    """
    films = movies_with_ratings(spark).select("tconst", "primaryTitle", "startYear",
                                              "runtimeMinutes", "genres_array")
    by_genre = films.withColumn("genre", F.explode("genres_array")).where(F.col("genre") != "")

    # the mean and the standard deviation of each genre, attached to every row with a window:
    # we need no self join, spark computes the aggregate one time per partition of the window
    w = Window.partitionBy("genre")
    scored = (by_genre
              .withColumn("genre_avg_runtime", F.avg("runtimeMinutes").over(w))
              .withColumn("genre_std_runtime", F.stddev("runtimeMinutes").over(w))
              .withColumn("z_score",
                          (F.col("runtimeMinutes") - F.col("genre_avg_runtime"))
                          / F.col("genre_std_runtime"))
              .where(F.abs(F.col("z_score")) > 3))

    outliers = (scored
                .select("genre", "primaryTitle", "startYear", "runtimeMinutes",
                        F.round("genre_avg_runtime", 1).alias("genre_avg_runtime"),
                        F.round("z_score", 2).alias("z_score"))
                .orderBy(F.col("z_score").desc()))

    per_genre = (scored.groupBy("genre")
                 .agg(F.count("*").alias("n_outliers"),
                      F.round(F.first("genre_avg_runtime"), 1).alias("genre_avg_runtime"))
                 .orderBy(F.col("n_outliers").desc()))
    return outliers, per_genre


# ------------------------------------------------------------------- Q2 top 3 genres per year
def q2_top3_genres_per_year(spark):
    """The three most popular genres of each year between 1980 and 2025.

    We have to define "popular". If we count the films we measure what the industry produced,
    not what the audience watched, and the number of films only grows with the time. So we
    measure the total number of votes instead: it is the closest thing to an audience that we
    have in this dataset.
    """
    films = (movies_with_ratings(spark)
             .where(F.col("startYear").between(1980, 2025) & F.col("numVotes").isNotNull()))
    by_genre = (films.withColumn("genre", F.explode("genres_array"))
                .where(F.col("genre") != ""))

    per_year_genre = by_genre.groupBy("startYear", "genre").agg(
        F.sum("numVotes").alias("total_votes"),
        F.count("*").alias("n_films"),
        F.round(F.avg("averageRating"), 2).alias("avg_rating"),
    )

    w = Window.partitionBy("startYear").orderBy(F.col("total_votes").desc())
    top3 = (per_year_genre
            .withColumn("rank", F.row_number().over(w))
            .where(F.col("rank") <= 3)
            .orderBy("startYear", "rank"))
    return top3, per_year_genre


# --------------------------------------------------- Q3 compare the top 3 to the other genres
def q3_top3_vs_rest(per_year_genre):
    """How the top three compares with all the other genres of the same year.

    Same window as Q2, but instead of keeping the first three we label every genre top3 or rest
    and we sum the two groups. The share of the votes tells us how concentrated a year is.
    """
    w = Window.partitionBy("startYear").orderBy(F.col("total_votes").desc())
    labelled = (per_year_genre
                .withColumn("rank", F.row_number().over(w))
                .withColumn("group", F.when(F.col("rank") <= 3, "top3").otherwise("rest")))

    grouped = labelled.groupBy("startYear", "group").agg(
        F.sum("total_votes").alias("votes"),
        F.sum("n_films").alias("films"),
        F.count("*").alias("n_genres"),
        F.round(F.avg("avg_rating"), 2).alias("avg_rating"),
    )

    # pivot to have one line per year with the two groups one next to the other
    pivoted = (grouped.groupBy("startYear").pivot("group", ["top3", "rest"])
               .agg(F.first("votes").alias("votes"),
                    F.first("films").alias("films"),
                    F.first("n_genres").alias("n_genres"),
                    F.first("avg_rating").alias("avg_rating")))

    return (pivoted
            .withColumn("top3_votes_share_pct",
                        F.round(100 * F.col("top3_votes")
                                / (F.col("top3_votes") + F.col("rest_votes")), 1))
            .orderBy("startYear"))


# ------------------------------------------------------------------- Q4 one hit, many misses
def q4_one_hit_directors(spark):
    """Directors with exactly one film rated >= 8.0, and several other ones averaging <= 6.0.

    `title.crew` stores the directors as a list separated by commas inside one cell, so we have
    to explode it to get one row per (film, director) before doing any group by.
    """
    films = movies_with_ratings(spark).where(F.col("averageRating").isNotNull())
    crew = read(spark, "title.crew")
    names = read(spark, "name.basics").select("nconst", "primaryName")

    directed = (crew.withColumn("nconst", F.explode("directors_array"))
                .where(F.col("nconst") != "")
                .join(films.select("tconst", "primaryTitle", "startYear", "averageRating"),
                      "tconst"))

    per_director = directed.groupBy("nconst").agg(
        F.count("*").alias("n_films"),
        F.sum(F.when(F.col("averageRating") >= 8.0, 1).otherwise(0)).alias("n_hits"),
        F.sum(F.when(F.col("averageRating") < 8.0, 1).otherwise(0)).alias("n_others"),
        F.round(F.avg(F.when(F.col("averageRating") < 8.0, F.col("averageRating"))),
                2).alias("avg_rating_others"),
        F.round(F.max(F.when(F.col("averageRating") >= 8.0, F.col("averageRating"))),
                1).alias("hit_rating"),
    )

    return (per_director
            .where((F.col("n_hits") == 1)
                   & (F.col("n_others") >= 2)          # "multiple other movies"
                   & (F.col("avg_rating_others") <= 6.0))
            .join(names, "nconst")
            .select("primaryName", "n_films", "hit_rating", "n_others", "avg_rating_others")
            .orderBy(F.col("n_others").desc(), F.col("avg_rating_others")))


# ----------------------------------------------------------------- Q5 series going downhill
def q5_series_going_downhill(spark):
    """Series with at least 3 seasons of >= 10 episodes, where the worst episode is in the last
    season and the best episode is in the first two seasons.

    One join to attach the rating to each episode, then everything is done with windows over the
    series: we find the position of the min and of the max with row_number on the rating.
    """
    episodes = read(spark, "title.episode")
    ratings = read(spark, "title.ratings")
    basics = read(spark, "title.basics")

    ep = (episodes
          .where(F.col("seasonNumber").isNotNull() & F.col("episodeNumber").isNotNull())
          .join(ratings.select("tconst", "averageRating", "numVotes"), "tconst")
          .where(F.col("averageRating").isNotNull()))

    # the seasons which really have 10 episodes or more
    big_seasons = (ep.groupBy("parentTconst", "seasonNumber")
                   .agg(F.count("*").alias("n_episodes"))
                   .where(F.col("n_episodes") >= 10))
    eligible = (big_seasons.groupBy("parentTconst")
                .agg(F.count("*").alias("n_big_seasons"))
                .where(F.col("n_big_seasons") >= 3))

    ep = ep.join(eligible, "parentTconst")

    w_series = Window.partitionBy("parentTconst")
    w_worst = Window.partitionBy("parentTconst").orderBy(F.col("averageRating").asc())
    w_best = Window.partitionBy("parentTconst").orderBy(F.col("averageRating").desc())

    marked = (ep
              .withColumn("last_season", F.max("seasonNumber").over(w_series))
              .withColumn("worst_rank", F.row_number().over(w_worst))
              .withColumn("best_rank", F.row_number().over(w_best)))

    worst = marked.where(F.col("worst_rank") == 1).select(
        "parentTconst", F.col("seasonNumber").alias("worst_season"),
        F.col("averageRating").alias("worst_rating"), "last_season")
    best = marked.where(F.col("best_rank") == 1).select(
        "parentTconst", F.col("seasonNumber").alias("best_season"),
        F.col("averageRating").alias("best_rating"))

    return (worst.join(best, "parentTconst")
            .where((F.col("worst_season") == F.col("last_season"))
                   & (F.col("best_season") <= 2))
            .join(basics.select(F.col("tconst").alias("parentTconst"),
                                "primaryTitle", "startYear"), "parentTconst")
            .withColumn("rating_drop", F.round(F.col("best_rating") - F.col("worst_rating"), 1))
            .select("primaryTitle", "startYear", "last_season", "best_season", "best_rating",
                    "worst_season", "worst_rating", "rating_drop")
            .orderBy(F.col("rating_drop").desc()))


# --------------------------------------------------------------- Q6 actors in many languages
def q6_multilingual_actors(spark):
    """Actors and actresses who succeeded in films of several different languages.

    The difficult part is not the join, it is to decide what "a film in french" means, because
    the non commercial imdb dataset does not carry the original language of a film anywhere. We
    measured it, we did not assume it:

        isOriginalTitle = 1 and a language          0 rows
        types = 'original' and a language           0 rows   (the same 12 842 443 rows)
        types = 'original' and a region             0 rows
        a language but no region                    0 rows

    The row which holds the original title carries the title string and nothing else, and every
    language in `title.akas` belongs to a localised release.

    We tried three rules.

    1. `isOriginalTitle = 1` *and* a language. This intersection is empty by construction, so
       the question was returning nothing at all.

    2. Every language declared in `title.akas`. A successful film declares 5.04 of them on
       average (median 4, up to 31) because every dub is counted, and 87 % declare two or more.
       With this rule almost every actor "succeeds in several languages" and the question does
       not mean anything anymore.

    3. Any market which shows the film under its own original title. On the paper it is better
       (1.82 languages per film, median 1) but in practice it is wrong: it was returning Tom
       Hanks in bengali, gujarati, kannada and telugu, because the indian markets display
       american films under their english title and they tag the row with the local language.

    So the rule below splits on what the dataset can really attest:

      - when `originalTitle` is different from `primaryTitle`, the original is really in another
        language than the display one, and the markets which show this untranslated original
        title are its home markets. We take those languages.
      - when the two are equal, the display title of imdb *is* the original, which means
        english. We credit the film with `en` only, and only if an english aka confirms it.

    What it costs us: a film whose original title is written exactly the same in english and in
    its own language is credited as english. Now the bias goes on the safe side, we prefer to
    miss a language than to invent one, and this is what a result table has to do.
    """
    films = movies_with_ratings(spark).where(
        (F.col("averageRating") >= SUCCESS_RATING) & (F.col("numVotes") >= SUCCESS_VOTES))

    akas = (read(spark, "title.akas").where(F.col("language").isNotNull())
            .select(F.col("titleId").alias("tconst"),
                    F.col("title").alias("aka_title"), "language"))

    titles = films.select("tconst", "primaryTitle", "originalTitle")

    # the films whose original title is not the display one: their home markets are the ones
    # which show the original title without translating it
    foreign = (titles.where(F.lower(F.col("originalTitle")) != F.lower(F.col("primaryTitle")))
               .join(akas, "tconst")
               .where(F.lower(F.col("aka_title")) == F.lower(F.col("originalTitle")))
               .select("tconst", "language"))

    # the films whose display title is the original one: english, if an english aka says so
    english = (titles.where(F.lower(F.col("originalTitle")) == F.lower(F.col("primaryTitle")))
               .join(akas.where(F.col("language") == "en"), "tconst")
               .select("tconst", "language"))

    film_language = foreign.unionByName(english).distinct()

    principals = read(spark, "title.principals").where(
        F.col("category").isin("actor", "actress"))
    names = read(spark, "name.basics").select("nconst", "primaryName")

    # we filter the films first and we join after: principals is the biggest table of the
    # dataset and joining it completely against the names would shuffle millions of rows for
    # nothing
    acted = (principals.join(films.select("tconst"), "tconst")
             .join(film_language, "tconst")
             .select("nconst", "language").distinct())

    per_actor = (acted.groupBy("nconst")
                 .agg(F.countDistinct("language").alias("n_languages"),
                      F.sort_array(F.collect_set("language")).alias("languages"))
                 .where(F.col("n_languages") >= 2)
                 .join(names, "nconst"))

    multi = per_actor.select("primaryName", "n_languages",
                             F.concat_ws(", ", "languages").alias("languages"))                      .orderBy(F.col("n_languages").desc(), "primaryName")
    three_plus = multi.where(F.col("n_languages") >= 3)
    return multi, three_plus


# ------------------------------------------------------------------ Q7 careers peaking early
def q7_early_peak_actors(spark):
    """Actors with a career of 20+ years and 15+ films, whose popularity peaked early.

    We make "peaked early" measurable: we cut the career in two halves on the year, and we keep
    the actors whose average rating in the first half is at least 1 point above the second half.
    One point on the imdb scale is a big gap, like this we do not catch the normal noise.
    """
    films = movies_with_ratings(spark).where(
        F.col("averageRating").isNotNull() & (F.col("numVotes") >= 100))
    principals = read(spark, "title.principals").where(
        F.col("category").isin("actor", "actress"))
    names = read(spark, "name.basics").select("nconst", "primaryName")

    acted = principals.join(
        films.select("tconst", "startYear", "averageRating"), "tconst")
    # we read `acted` two times below: one time to build the careers, one time to cut them in
    # halves. Without this cache spark replays the whole plan for each of them, which means
    # filtering and joining the 102 million rows of title.principals a second time.
    acted.cache()

    career = acted.groupBy("nconst").agg(
        F.min("startYear").alias("first_year"),
        F.max("startYear").alias("last_year"),
        F.count("*").alias("n_films"),
    ).where((F.col("last_year") - F.col("first_year") >= 20) & (F.col("n_films") >= 15))

    halves = (acted.join(career, "nconst")
              .withColumn("mid_year", (F.col("first_year") + F.col("last_year")) / 2)
              .withColumn("half", F.when(F.col("startYear") <= F.col("mid_year"), "first")
                          .otherwise("second")))

    pivot = (halves.groupBy("nconst", "first_year", "last_year", "n_films")
             .pivot("half", ["first", "second"])
             # count(lit(1)) and not count("*"): spark refuses the star inside a pivot
             # (INVALID_USAGE_OF_STAR_OR_REGEX), and the two count the same thing
             .agg(F.round(F.avg("averageRating"), 2).alias("avg_rating"),
                  F.count(F.lit(1)).alias("n_films")))

    result = (pivot
            .where(F.col("first_avg_rating") - F.col("second_avg_rating") >= 1.0)
            .withColumn("drop", F.round(F.col("first_avg_rating")
                                        - F.col("second_avg_rating"), 2))
            .join(names, "nconst")
            .select("primaryName", "first_year", "last_year", "n_films",
                    "first_avg_rating", "second_avg_rating", "drop")
            .orderBy(F.col("drop").desc()))
    # the caller runs the actions, so it is the caller who releases the cache, not here
    return result, acted


# ------------------------------------------------------------------- Q8 multi-talented people
def q8_multi_talented(spark):
    """People who combine writing, directing and acting, and how they perform when they cumulate
    several of these roles on the same film.

    `title.principals` already gives one row per (film, person, category), so the two questions
    are two group by on the same table: one by person to find the multi talented people, and one
    by (film, person) to compare a film where they had one role against a film where they had
    several.
    """
    films = movies_with_ratings(spark).where(F.col("averageRating").isNotNull())
    names = read(spark, "name.basics").select("nconst", "primaryName")
    creative = ["director", "writer", "actor", "actress"]

    principals = (read(spark, "title.principals")
                  .where(F.col("category").isin(creative))
                  .join(films.select("tconst", "primaryTitle", "averageRating"), "tconst")
                  # actor and actress is the same job, we merge them
                  .withColumn("role", F.when(F.col("category").isin("actor", "actress"), "actor")
                              .otherwise(F.col("category"))))

    # `principals` feeds the two aggregations below, and `per_person` is used for the final
    # table and also for the comparison per film. It makes four actions on the same two plans,
    # so caching them is what avoids scanning title.principals four times.
    principals.cache()

    # who is multi talented: at least 2 different roles during the whole career
    per_person = (principals.groupBy("nconst")
                  .agg(F.countDistinct("role").alias("n_roles"),
                       F.sort_array(F.collect_set("role")).alias("roles"),
                       F.countDistinct("tconst").alias("n_films"),
                       F.round(F.avg("averageRating"), 2).alias("avg_rating"))
                  .where((F.col("n_roles") >= 2) & (F.col("n_films") >= 5)))
    per_person.cache()

    multi = (per_person.join(names, "nconst")
             .select("primaryName", "n_roles", F.concat_ws("+", "roles").alias("roles"),
                     "n_films", "avg_rating")
             .orderBy(F.col("n_roles").desc(), F.col("n_films").desc()))

    # one role or several roles on the same film
    per_film = (principals.groupBy("nconst", "tconst", "averageRating")
                .agg(F.countDistinct("role").alias("roles_on_film"))
                .join(per_person.select("nconst"), "nconst")
                .withColumn("multi_role", F.col("roles_on_film") >= 2))

    comparison = (per_film.groupBy("multi_role")
                  .agg(F.count("*").alias("n_films"),
                       F.round(F.avg("averageRating"), 3).alias("avg_rating"))
                  .orderBy("multi_role"))
    # same as q7: the cached plans are released by the caller, after it ran the actions
    return multi, comparison, [principals, per_person]


QUESTIONS = ("q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8")


def main():
    """Answers the eight questions, or only the ones given on the command line.

    The questions are independent and each one writes its own result, so we can re run one
    alone. It is important here: one single question can take more than one hour on this
    dataset, and there is no reason to pay for the seven other ones just to retry it.

    `q3` is the only one which is not standalone: the subject asks it as a comparison against
    the result of `q2`, so if we ask for `q3` we compute `q2` too.
    """
    asked = [a for a in sys.argv[1:] if not a.startswith("-")] or list(QUESTIONS)
    unknown = [q for q in asked if q not in QUESTIONS]
    if unknown:
        raise SystemExit(f"unknown question(s) {unknown}, expected any of {QUESTIONS}")
    want = set(asked)

    spark = get_spark("imdb-exploration")

    if "q1" in want:
        outliers, per_genre = q1_runtime_outliers(spark)
        save_result(per_genre, "q1_runtime_outliers_per_genre")
        save_result(outliers, "q1_runtime_outliers_top", limit=20)

    if "q2" in want or "q3" in want:
        top3, per_year_genre = q2_top3_genres_per_year(spark)
        per_year_genre.cache()
        if "q2" in want:
            save_result(top3, "q2_top3_genres_per_year")
        if "q3" in want:
            save_result(q3_top3_vs_rest(per_year_genre), "q3_top3_vs_rest")
        per_year_genre.unpersist()

    if "q4" in want:
        save_result(q4_one_hit_directors(spark), "q4_one_hit_directors", limit=20)

    if "q5" in want:
        save_result(q5_series_going_downhill(spark), "q5_series_going_downhill", limit=20)

    if "q6" in want:
        # `three_plus` is only `multi_lang` filtered, so without this cache the whole plan
        # (title.principals joined with the films and with title.akas, then deduplicated and
        # grouped) runs one time for each result. Measured on this dataset: 55 minutes for the
        # first result, and then 64 more for the second one, which is a filter of the first.
        multi_lang, three_plus = q6_multilingual_actors(spark)
        multi_lang.cache()
        save_result(multi_lang, "q6_actors_2plus_languages", limit=20)
        save_result(three_plus, "q6_actors_3plus_languages", limit=20)
        multi_lang.unpersist()

    if "q7" in want:
        early_peak, q7_cached = q7_early_peak_actors(spark)
        save_result(early_peak, "q7_early_peak_actors", limit=20)
        q7_cached.unpersist()

    if "q8" in want:
        multi, comparison, q8_cached = q8_multi_talented(spark)
        save_result(multi, "q8_multi_talented", limit=20)
        save_result(comparison, "q8_multi_role_vs_single_role")
        for cached in q8_cached:
            cached.unpersist()

    spark.stop()


if __name__ == "__main__":
    main()
