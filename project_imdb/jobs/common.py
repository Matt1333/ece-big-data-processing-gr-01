"""Helpers shared by all the jobs of the project.

We put in one place the spark session, the paths and the way we save a result, like this each
job contains only the logic of its own question.
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
    """Local spark session that we tuned for a laptop.

    Two settings are really important here: the driver memory, because in local mode everything
    runs inside the driver, and the number of shuffle partitions. The spark default is 200,
    which gives 200 very small tasks for each shuffle. But doing the opposite is worse: we have
    102 million rows in `title.principals`, and if we shuffle them into 8 partitions the tasks
    become too big for the heap. With 32 we stay around 3 million rows per task, it fits in
    memory and we still use the cores we gave to spark (2 by default, 4 in `run_all.sh`).

    We put 2500m and not more: the container has 3.6 Go, and the jvm heap is not the only thing
    living inside. The python process, the off heap buffers and the os also need their place, so
    if we give the whole container to the heap the job is killed by the oom killer instead of
    going faster. We learned this one the hard way.
    """
    builder = SparkSession.builder.appName(app_name)

    # Maven coordinates that spark has to download before it starts, for the jobs that need a
    # connector which is not shipped with spark. Only the streaming job asks for one. We made it
    # a parameter and not a default because the download happens when the session starts, and
    # there is no reason that the batch jobs pay for it.
    if packages:
        builder = builder.config("spark.jars.packages", ",".join(packages))

    return (
        builder
        # local[2] and not local[*]: the machine has only 4 cores and they are shared with
        # everything else running on it. If we take all of them spark is a little bit faster
        # and the rest of the machine becomes unusable. SPARK_CORES lets us override it when
        # the machine is free.
        .master(f"local[{os.environ.get('SPARK_CORES', '2')}]")
        .config("spark.driver.memory", driver_memory)
        .config("spark.sql.shuffle.partitions", shuffle_partitions)
        .config("spark.sql.parquet.compression.codec", "snappy")
        # This is the maximum size of one input partition. The default is 128 Mo and it was
        # giving us only 4 to 7 tasks on our biggest tables, because the ingest writes one
        # single parquet file per table (the source tsv are gzip files, and a gzip file cannot
        # be split, so one file was read by one task and written by one task).
        #
        # Putting 32 Mo is what replaces rewriting all those files. A parquet file can be split
        # on its row groups, so spark is able to cut the *same* file into more tasks, we just
        # have to tell him to aim smaller: `title.principals` goes from around 7 tasks to around
        # 26. Rewriting the files would give us the same parallelism, but it costs a full read
        # and write pass on 2,5 Go, plus the same quantity of free disk. We measured first, and
        # the measure is what showed us that the rewrite was not necessary.
        .config("spark.sql.files.maxPartitionBytes", "32m")
        .getOrCreate()
    )


def read(spark, table, layer="clean"):
    """Reads one imdb table from parquet. Parquet describes itself, so we have no schema to give.

    We have two layers. `raw` keeps every column as a string, exactly like in the tsv (we only
    replaced `\\N` by null), so the data preparation can measure what is really missing. `clean`
    is the typed and corrected version, and this is the one used by all the other jobs.
    """
    return spark.read.parquet(f"{PARQUET}/{layer}/{table}")


def save_result(df, name, limit=None, show=True):
    """Saves a result as parquet (to reuse it later) and as a markdown table (for REPORT.md).

    We write the markdown by collecting the rows, so we call this function only on results which
    are already aggregated, never on a complete table.

    There are two actions on the same dataframe here: writing the parquet, and collecting the
    rows for the markdown table. Spark keeps nothing between two actions, so without the cache
    below the whole plan before is computed two times, and on these questions "the plan before"
    means scanning and joining the 102 million rows of `title.principals` a second time.

    We cache instead of reading again the parquet that we just wrote, because a parquet
    directory is a group of files with no order guaranteed between them, and our results are
    ordered (a top 20 is a top 20 only if the order stays).
    """
    os.makedirs(f"{OUTPUT}/{name}", exist_ok=True)

    # We only cache what we cached ourselves: when a caller needs the same result for several
    # calls it caches it around them, and if we unpersist it here we destroy exactly that.
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
