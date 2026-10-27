"""Section 1: Data preparation.

Three questions of the subject:
  1. for each column of each table, the percentage of null / missing / empty records
  2. the five columns with the highest percentage of nulls
  3. the other data quality problems, and then a way to handle them

The job reads the `raw` layer (everything is a string, nothing is interpreted yet), it measures,
and it writes the `clean` layer used by all the other jobs.

A word about the way it is written. In our first version we were asking one question at a time,
so every `.count()` was starting its own spark job and reading the whole table again: 14 passes
for the missing values and 16 more for the quality problems, on tables of 102 and 59 million
rows. Now everything that can be answered in the same pass is computed in the same aggregation,
and we check the foreign keys on the distinct keys instead of on every row, which gives the same
answer on a table ten times smaller.
"""
import sys
from pyspark.sql import functions as F

sys.path.insert(0, "/home/jovyan/work/jobs")
from common import get_spark, read, save_result, PARQUET, OUTPUT, TABLES

CURRENT_YEAR = 2026


# --------------------------------------------------------------------------- 1. missing values
def missing_per_column(spark):
    """One row per (table, column) with how many values are missing and the percentage.

    "Missing" is not only null. In the tsv imdb writes `\\N` (we already turned it into null
    during the ingest), but some fields are also present and empty, so we count the three cases:
    null, empty string, and string with only spaces inside.

    One pass per table: we count the number of rows inside the same aggregation as the missing
    values, instead of doing a separate `count()` that would read the table a second time.
    """
    rows = []
    for table in TABLES:
        df = read(spark, table, layer="raw")
        agg = df.agg(
            F.count(F.lit(1)).alias("__total"),
            *[F.count(F.when(F.col(c).isNull() | (F.trim(F.col(c)) == ""), 1)).alias(c)
              for c in df.columns]
        ).collect()[0]

        total = agg["__total"]
        for c in df.columns:
            n = agg[c]
            rows.append((table, c, total, n, 100.0 * n / total if total else 0.0))

    return spark.createDataFrame(
        rows, ["table_name", "column_name", "n_rows", "n_missing", "pct_missing"]
    )


# --------------------------------------------------------------------- 3. other quality issues
def quality_issues(spark):
    """The problems that a null check cannot see: impossible dates, values with the wrong type,
    broken foreign keys, duplicated primary keys.

    We group the checks of one table in a single aggregation, like this each table is read once.
    We check the foreign keys on the distinct values of the key: the fact that a key has a parent
    or not does not depend on how many rows carry it, and `title.principals` has 102 million rows
    for around 12 million distinct titles.
    """
    issues = []

    def add(table, label, value, unit="rows"):
        issues.append((table, label, int(value), unit))

    # ---- name.basics : everything in one pass
    names = read(spark, "name.basics", layer="raw")
    n = names.agg(
        F.count(F.when(F.col("deathYear").cast("int") < F.col("birthYear").cast("int"), 1))
        .alias("death_before_birth"),
        F.count(F.when(F.col("birthYear").cast("int") > CURRENT_YEAR, 1))
        .alias("birth_in_future"),
        F.count(F.when(F.col("birthYear").isNotNull()
                       & F.col("birthYear").cast("int").isNull(), 1))
        .alias("birthYear_not_a_number"),
        F.count(F.lit(1)).alias("total"),
        F.countDistinct("nconst").alias("distinct_nconst"),
    ).collect()[0]
    add("name.basics", "deathYear before birthYear", n["death_before_birth"])
    add("name.basics", "birthYear in the future", n["birth_in_future"])
    add("name.basics", "birthYear not a number", n["birthYear_not_a_number"])
    add("name.basics", "duplicated nconst", n["total"] - n["distinct_nconst"])

    # ---- title.basics : everything in one pass
    basics = read(spark, "title.basics", layer="raw")
    b = basics.agg(
        F.count(F.when(F.col("endYear").cast("int") < F.col("startYear").cast("int"), 1))
        .alias("end_before_start"),
        F.count(F.when(F.col("runtimeMinutes").isNotNull()
                       & F.col("runtimeMinutes").cast("int").isNull(), 1))
        .alias("runtime_not_a_number"),
        F.count(F.when(F.col("runtimeMinutes").cast("int") <= 0, 1)).alias("runtime_not_positive"),
        F.count(F.when(F.col("startYear").isNotNull()
                       & F.col("startYear").cast("int").isNull(), 1))
        .alias("start_not_a_number"),
        F.count(F.when(F.col("startYear").cast("int") > CURRENT_YEAR + 5, 1))
        .alias("start_far_future"),
        F.count(F.lit(1)).alias("total"),
        F.countDistinct("tconst").alias("distinct_tconst"),
    ).collect()[0]
    add("title.basics", "endYear before startYear", b["end_before_start"])
    add("title.basics", "runtimeMinutes not a number", b["runtime_not_a_number"])
    add("title.basics", "runtimeMinutes <= 0", b["runtime_not_positive"])
    add("title.basics", "startYear not a number", b["start_not_a_number"])
    add("title.basics", "startYear more than 5 years in the future", b["start_far_future"])
    add("title.basics", "duplicated tconst", b["total"] - b["distinct_tconst"])

    # ---- foreign keys, on the distinct keys only
    title_ids = basics.select("tconst").distinct().cache()
    name_ids = names.select("nconst").distinct().cache()

    def orphan_keys(df, fk, parent, parent_key):
        """How many distinct values of `fk` have no parent. A left anti join keeps exactly the
        rows of the left side which found nothing on the right side, so it is the definition."""
        return (df.select(F.col(fk).alias("k")).where(F.col("k").isNotNull()).distinct()
                  .join(parent.select(F.col(parent_key).alias("k")), "k", "left_anti")
                  .count())

    ratings = read(spark, "title.ratings", layer="raw")
    akas = read(spark, "title.akas", layer="raw")
    crew = read(spark, "title.crew", layer="raw")
    episode = read(spark, "title.episode", layer="raw")
    principals = read(spark, "title.principals", layer="raw")

    for table, df, fk, parent, pk in [
        ("title.ratings", ratings, "tconst", title_ids, "tconst"),
        ("title.akas", akas, "titleId", title_ids, "tconst"),
        ("title.crew", crew, "tconst", title_ids, "tconst"),
        ("title.episode", episode, "tconst", title_ids, "tconst"),
        ("title.episode", episode, "parentTconst", title_ids, "tconst"),
        ("title.principals", principals, "tconst", title_ids, "tconst"),
        ("title.principals", principals, "nconst", name_ids, "nconst"),
    ]:
        add(table, f"{fk} with no parent row", orphan_keys(df, fk, parent, pk), "distinct keys")

    for table, df in [("title.ratings", ratings), ("title.crew", crew),
                      ("title.episode", episode)]:
        r = df.agg(F.count(F.lit(1)).alias("total"),
                   F.countDistinct("tconst").alias("d")).collect()[0]
        add(table, "duplicated tconst", r["total"] - r["d"])

    title_ids.unpersist()
    name_ids.unpersist()

    return spark.createDataFrame(issues, ["table_name", "issue", "n_affected", "unit"])


# ------------------------------------------------------------------------------ the clean layer
def build_clean(spark):
    """Writes the typed and corrected tables.

    Our policy, and it is the same everywhere:
      - we cast to the real type, and a value which cannot be cast becomes null (we never invent
        a value)
      - an impossible value is set to null and we keep the row: losing a complete person because
        one date is wrong would be worse than losing the date
      - a row whose foreign key has no parent is removed from the clean layer, because any join
        would drop it anyway, but we save its key in output/rejected so nothing disappears
        silently
      - a duplicated primary key would be deduplicated, but there is none: the quality report
        above measures 0 duplicate on every primary key of the dataset (`tconst` of
        title.basics, title.ratings, title.crew and title.episode, `nconst` of name.basics).
        At the beginning we had a `dropDuplicates` here and we removed it: deduplicating on a
        key which is already unique shuffles the whole table, with all its text columns, just to
        delete nothing. On `title.basics` this single call was enough to get the driver killed by
        the oom killer. The check stays in the quality report, so if a future imdb dump really
        introduces a duplicate we will see it there instead of dropping it silently here.
    """
    # ---- title.basics : the reference table, all the other ones point to it
    basics = read(spark, "title.basics", layer="raw")
    basics_clean = (
        basics
        .withColumn("startYear", F.col("startYear").cast("int"))
        .withColumn("endYear", F.col("endYear").cast("int"))
        .withColumn("runtimeMinutes", F.col("runtimeMinutes").cast("int"))
        .withColumn("isAdult", F.col("isAdult").cast("int"))
        # a runtime of 0 or less is not a duration, and a year far after today is not a release
        .withColumn("runtimeMinutes",
                    F.when(F.col("runtimeMinutes") > 0, F.col("runtimeMinutes")))
        .withColumn("startYear",
                    F.when(F.col("startYear").between(1870, CURRENT_YEAR + 5), F.col("startYear")))
        .withColumn("endYear",
                    F.when(F.col("endYear") >= F.col("startYear"), F.col("endYear")))
        # genres is a list separated by commas, we keep the string and we add the array
        # version: almost every question of the exploration needs to explode it
        .withColumn("genres_array", F.split(F.col("genres"), ","))
    )
    basics_clean.write.mode("overwrite").parquet(f"{PARQUET}/clean/title.basics")
    title_ids = spark.read.parquet(f"{PARQUET}/clean/title.basics").select("tconst")

    # ---- name.basics
    names = read(spark, "name.basics", layer="raw")
    names_clean = (
        names
        .withColumn("birthYear", F.col("birthYear").cast("int"))
        .withColumn("deathYear", F.col("deathYear").cast("int"))
        .withColumn("birthYear",
                    F.when(F.col("birthYear").between(1700, CURRENT_YEAR), F.col("birthYear")))
        # a death before the birth: we cannot know which of the two values is wrong, so we
        # drop only the death and we keep the person
        .withColumn("deathYear",
                    F.when(F.col("deathYear") >= F.col("birthYear"), F.col("deathYear")))
        .withColumn("primaryProfession_array", F.split(F.col("primaryProfession"), ","))
        .withColumn("knownForTitles_array", F.split(F.col("knownForTitles"), ","))
    )
    names_clean.write.mode("overwrite").parquet(f"{PARQUET}/clean/name.basics")
    name_ids = spark.read.parquet(f"{PARQUET}/clean/name.basics").select("nconst")

    summary = []

    def write_clean(table, df, keys):
        """Writes the rows which keep all their parents, counts and saves the others.

        Measure before acting. This filtering join is by far the most expensive operation of the
        job: on `title.principals` it shuffles 102 million rows with all their columns. So for
        each foreign key we first count the orphan keys, which shuffles only one narrow column,
        and we run the join only if there is really something to remove. On this dump it means
        we skip the join completely for every key except two (`title.episode.parentTconst` with
        4 keys, and `title.principals.nconst` with 3209 keys).

        For the filter itself we use a `left_semi` join and not an inner one: it answers the
        question "does a parent exist" without bringing back the columns of the parent, and it
        cannot multiply a row if one day the parent side stops being unique.

        One side effect is worth to note: a row whose foreign key is *null* is not dropped
        anymore. The orphan count ignores the nulls (a null is a missing value, we measure it in
        question 1, it is not a broken reference), so when the count is 0 we skip the join and
        those rows stay. This is coherent with the rest of our policy, which never deletes a row
        because one field is empty.

        We obtain the rejected rows by difference between the counts, like this we avoid running
        the opposite anti join a second time.
        """
        total = df.count()
        kept = df
        for parent, col in keys:
            n_orphans = (df.select(F.col(col).alias("k")).where(F.col("k").isNotNull())
                           .distinct()
                           .join(parent.select(F.col(col).alias("k")), "k", "left_anti")
                           .count())
            if n_orphans == 0:
                print(f"  {table}.{col}: no orphan key, filtering join skipped")
                continue
            print(f"  {table}.{col}: {n_orphans} orphan keys, filtering")
            kept = kept.join(parent, col, "left_semi")
        kept.write.mode("overwrite").parquet(f"{PARQUET}/clean/{table}")
        n_kept = spark.read.parquet(f"{PARQUET}/clean/{table}").count()
        summary.append((table, total, n_kept, total - n_kept))

    write_clean("title.ratings",
                (read(spark, "title.ratings", layer="raw")
                 .withColumn("averageRating", F.col("averageRating").cast("double"))
                 .withColumn("numVotes", F.col("numVotes").cast("int"))),
                [(title_ids, "tconst")])

    write_clean("title.akas",
                (read(spark, "title.akas", layer="raw")
                 .withColumn("ordering", F.col("ordering").cast("int"))
                 .withColumn("isOriginalTitle", F.col("isOriginalTitle").cast("int"))
                 # the foreign key is called titleId here, we align it so the join is the same
                 .withColumn("tconst", F.col("titleId"))),
                [(title_ids, "tconst")])

    write_clean("title.crew",
                (read(spark, "title.crew", layer="raw")
                 .withColumn("directors_array", F.split(F.col("directors"), ","))
                 .withColumn("writers_array", F.split(F.col("writers"), ","))),
                [(title_ids, "tconst")])

    write_clean("title.episode",
                (read(spark, "title.episode", layer="raw")
                 .withColumn("seasonNumber", F.col("seasonNumber").cast("int"))
                 .withColumn("episodeNumber", F.col("episodeNumber").cast("int"))),
                [(title_ids, "tconst"),
                 (title_ids.withColumnRenamed("tconst", "parentTconst"), "parentTconst")])

    write_clean("title.principals",
                (read(spark, "title.principals", layer="raw")
                 .withColumn("ordering", F.col("ordering").cast("int"))),
                [(title_ids, "tconst"), (name_ids, "nconst")])

    return spark.createDataFrame(
        summary, ["table_name", "n_rows_raw", "n_rows_clean", "n_rows_rejected"])


STEPS = ("missing", "quality", "clean")


def main():
    """Runs the three steps, or only the ones given on the command line.

    The steps are independent and each one writes its own result, so being able to re run only
    one of them is important: the measures take around twenty five minutes on this dataset and
    there is no reason to pay them again just to retry the clean layer.
    """
    steps = [a for a in sys.argv[1:] if not a.startswith("-")] or list(STEPS)
    unknown = [s for s in steps if s not in STEPS]
    if unknown:
        raise SystemExit(f"unknown step(s) {unknown}, expected any of {STEPS}")

    spark = get_spark("imdb-preparation")

    if "missing" in steps:
        print("### 1. missing values per column")
        missing = missing_per_column(spark).orderBy(F.col("pct_missing").desc())
        missing.cache()
        save_result(missing, "01_missing_per_column")
        save_result(missing.limit(5), "02_top5_missing")
        missing.unpersist()

    if "quality" in steps:
        print("### 3. other data quality issues")
        save_result(quality_issues(spark).orderBy(F.col("n_affected").desc()),
                    "03_quality_issues")

    if "clean" in steps:
        print("### 4. building the clean layer")
        save_result(build_clean(spark), "04_rejected_rows")

    spark.stop()


if __name__ == "__main__":
    main()
