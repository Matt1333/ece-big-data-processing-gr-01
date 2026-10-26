"""Step 1: ingest the 7 imdb tsv files into the `raw` parquet layer.

We keep every column as a string, and it is on purpose. The only thing we interpret is the
`\\N` that imdb writes for a missing value, and it becomes a real null. We touch nothing else,
like this the data preparation job can measure what is really missing before somebody casts or
cleans something.

Why we go to parquet: the tsv are gzip files, and gzip is not splittable, so spark reads each
file with one single task and has to parse the text again at every job. Parquet is columnar,
splittable and typed, so a query that needs 3 columns out of 9 reads only those 3.
"""
import os
import shutil
import sys

from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType

sys.path.insert(0, "/home/jovyan/work/jobs")
from common import get_spark, RAW, PARQUET, TABLES

# compose mounts here the host folder named by DATA_DIR, in read only
HOST_DATA = "/mnt/host-data"

# the columns of each table, in the same order as the tsv header
# (https://developer.imdb.com/non-commercial-datasets/)
COLUMNS = {
    "name.basics": ["nconst", "primaryName", "birthYear", "deathYear",
                    "primaryProfession", "knownForTitles"],
    "title.akas": ["titleId", "ordering", "title", "region", "language",
                   "types", "attributes", "isOriginalTitle"],
    "title.basics": ["tconst", "titleType", "primaryTitle", "originalTitle", "isAdult",
                     "startYear", "endYear", "runtimeMinutes", "genres"],
    "title.crew": ["tconst", "directors", "writers"],
    "title.episode": ["tconst", "parentTconst", "seasonNumber", "episodeNumber"],
    "title.principals": ["tconst", "ordering", "nconst", "category", "job", "characters"],
    "title.ratings": ["tconst", "averageRating", "numVotes"],
}


def stage_tsv():
    """Copies the tsv from the read only host mount into the docker volume.

    We download the dataset on the host, in the folder named by `DATA_DIR`, and compose mounts
    this folder in read only on `/mnt/host-data`. But the jobs read `data/raw`, which is inside
    the named volume, and we have two measured reasons for that: reading the dataset from the
    volume goes at 49 MB/s against 21 MB/s through the host mount, and the project folder is
    synchronised by OneDrive, which locks the files while spark is still writing them.

    We copy only the files which are not already in the volume, like this running this job again
    is cheap. This function is also what makes the pipeline runnable from zero: without it
    `data/raw` stays empty, because the named volume hides the `data/` folder of the host.
    """
    os.makedirs(RAW, exist_ok=True)
    for table in TABLES:
        name = f"{table}.tsv.gz"
        dst = os.path.join(RAW, name)
        if os.path.exists(dst):
            continue
        src = os.path.join(HOST_DATA, name)
        if not os.path.exists(src):
            raise SystemExit(
                f"{name} is neither in the volume nor on {HOST_DATA}.\n"
                f"Download the 7 files into the folder named by DATA_DIR (see .env.example), "
                f"then start the containers again. PROJECT.md, setup step 3.")
        print(f"staging {name} ...")
        shutil.copyfile(src, dst)


def main():
    stage_tsv()
    spark = get_spark("imdb-ingest")

    for table in TABLES:
        schema = StructType([StructField(c, StringType(), True) for c in COLUMNS[table]])

        df = (
            spark.read
            .option("sep", "\t")
            .option("header", True)
            # imdb writes a literal \N when a value is missing
            .option("nullValue", "\\N")
            # the files are not quoted at all: a title which contains a " has to stay a normal
            # character, if not spark thinks a quoted field starts and it swallows the next tabs
            .option("quote", "")
            .schema(schema)
            .csv(f"{RAW}/{table}.tsv.gz")
        )

        out = f"{PARQUET}/raw/{table}"
        df.write.mode("overwrite").parquet(out)
        print(f"{table:<20} -> {out}")

    # one pass to report the sizes, it is useful for the report and to verify we lost nothing
    print("\n--- rows per table ---")
    for table in TABLES:
        n = spark.read.parquet(f"{PARQUET}/raw/{table}").count()
        print(f"{table:<20} {n:>12,}")

    spark.stop()


if __name__ == "__main__":
    main()
