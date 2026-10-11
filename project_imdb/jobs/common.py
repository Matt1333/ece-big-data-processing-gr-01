"""Shared helpers for every job of the project.

One place for the spark session, the paths and the way we save a result, so that each job
only contains the logic of its own question.
"""
import os
from pyspark.sql import SparkSession

# everything is relative to the project root, which is the working dir of the container
ROOT = os.environ.get("PROJECT_ROOT", "/home/jovyan/work")
RAW = f"{ROOT}/data/raw"
PARQUET = f"{ROOT}/data/parquet"
OUTPUT = f"{ROOT}/output"

# the 7 tables of the official imdb dataset (https://datasets.imdbws.com/)
TABLES = [
    "name.basics",
    "title.akas",
    "title.basics",
    "title.crew",
    "title.episode",
    "title.principals",
    "title.ratings",
]


def get_spark(app_name, shuffle_partitions=32, driver_memory="2500m", packages=None):
    """Local spark session tuned for a laptop.

    The two settings that matter here: the driver memory (everything runs in the driver in
    local mode) and the number of shuffle partitions. The spark default is 200, which creates
    200 tiny tasks per shuffle. But the opposite is worse here: `title.principals` has 102
    million rows, and shuffling it into 8 partitions makes tasks too big for the heap. 32 keeps
    around 3 million rows per task, which fits and still uses the 8 cores.

    2500m and not more: the container has 3.6 Go, and the jvm heap is not the only thing inside
    it. The python process, the off-heap buffers and the os also need their place, so asking the
    whole container for the heap gets the job killed by the oom killer instead of making it
    faster.
    """
    builder = SparkSession.builder.appName(app_name)

    # Maven coordinates to fetch before starting, for the jobs that need a connector spark
    # does not ship. Only the streaming job asks for one, and it is a parameter rather than a
    # default because the download happens at session start and the batch jobs have no reason
    # to pay for it.
    if packages:
        builder = builder.config("spark.jars.packages", ",".join(packages))

    return (
        builder
        # local[2] and not local[*]: the machine has 4 cores and they are shared with
        # whatever else runs on it. Taking them all makes spark marginally faster and
        # everything else unusable. SPARK_CORES overrides it when the machine is free.
        .master(f"local[{os.environ.get('SPARK_CORES', '2')}]")
        .config("spark.driver.memory", driver_memory)
        .config("spark.sql.shuffle.partitions", shuffle_partitions)
        .config("spark.sql.parquet.compression.codec", "snappy")
        # How big one input partition may get. The default is 128 Mo, which gave only 4 to 7
        # tasks on our biggest tables, because the ingest wrote one single parquet file per
        # table (the source tsv are gzip, and gzip cannot be split, so one file was read by one
        # task and written by one task).
        #
        # Lowering it to 32 Mo is what replaces rewriting those files. A parquet file is
        # splittable on its row groups, so spark can cut the *same* file into more tasks just
        # by being told to aim smaller: `title.principals` goes from about 7 tasks to about 26.
        # Rewriting the files would have given the same parallelism, but at the cost of a full
        # read and write pass over 2,5 Go and as much free disk again. Measuring first is what
        # showed the rewrite was not needed.
        .config("spark.sql.files.maxPartitionBytes", "32m")
        .getOrCreate()
    )


def read(spark, table, layer="clean"):
    """Reads one imdb table from parquet. Parquet is self describing, so no schema to give.

    Two layers: `raw` is every column as a string, exactly as in the tsv (only `\\N` turned into
    null), so the data preparation can measure what is really missing. `clean` is the typed and
    corrected version that every other job uses.
    """
    return spark.read.parquet(f"{PARQUET}/{layer}/{table}")


def save_result(df, name, limit=None, show=True):
    """Saves a result both as parquet (to reuse it) and as a markdown table (for REPORT.md).

    The markdown is written by collecting the rows, so we only call it on aggregated results,
    never on a full table.

    Two actions follow on the same dataframe: writing the parquet and collecting the rows of
    the markdown table. Spark keeps nothing between two actions, so without the cache below the
    whole plan upstream is computed twice, and on these questions "upstream" means scanning and
    joining the 102 million rows of `title.principals` a second time.

    Caching rather than re-reading the parquet we just wrote: a parquet directory is a set of
    files with no guaranteed order between them, and these results are ordered (a top 20 is
    only a top 20 if the order survives).
    """
    os.makedirs(f"{OUTPUT}/{name}", exist_ok=True)

    # Only cache what we cached ourselves: a caller that needs the same result for several
    # calls caches it around them, and unpersisting it here would defeat exactly that.
    ours = not df.is_cached
    if ours:
        df.cache()
    try:
        df.write.mode("overwrite").parquet(f"{OUTPUT}/{name}/data.parquet")

        rows = df.limit(limit).collect() if limit else df.collect()
        cols = df.columns

        lines = ["| " + " | ".join(cols) + " |",
                 "|" + "|".join(["---"] * len(cols)) + "|"]
        for r in rows:
            lines.append("| " + " | ".join(_fmt(r[c]) for c in cols) + " |")

        md = "\n".join(lines) + "\n"
        with open(f"{OUTPUT}/{name}/table.md", "w", encoding="utf-8") as f:
            f.write(md)
    finally:
        if ours:
            df.unpersist()

    if show:
        print(f"\n--- {name} ({len(rows)} rows) ---")
        print(md)
    return md


def _fmt(v):
    if v is None:
        return ""
    if isinstance(v, float):
        return f"{v:.2f}"
    return str(v).replace("|", "\\|").replace("\n", " ")
