# ECE Big Data Processing - IMDb project

## Contributors

<!-- TO COMPLETE: real email of each member before the submission -->

| Name | GitHub | Email |
|---|---|---|
| DAVIDSON Matt | `Matt1333` | *to complete* |
| TOUVRON Erwan | `erwan-oss` | *to complete* |
| PINTO Kylian | `Kycks912004` | *to complete* |

Group: gr-01

## What this project does

It takes the public IMDb dataset, measures and repairs its quality problems, answers a series of
analytical questions on it, enriches the films and their principals with texts coming from
Wikipedia, and watches the live stream of Wikipedia edits to detect the ones that concern this
dataset.

Everything runs in two containers: one Spark, one Kafka. Nothing has to be installed on the host
except Docker and Python.

## Requirements

- Docker and Docker Compose
- Python 3.11 or later on the host, only for the two scripts that talk to the network
  (the Wikipedia download and the Kafka producer)
- **About 15 Go of free disk**, and more is safer. The files themselves are modest (1.9 Go of
  tsv, 2.5 Go for the `raw` parquet, 2.2 Go for the `clean` one), but the Spark shuffle writes
  far more than that in passing: the two questions that join `title.principals` moved more than
  40 Go of temporary files through the docker volume. A run started with 30 Go free filled the
  disk and got Docker Desktop itself stuck.
- An internet connection for the first run (dataset, Wikidata, Wikipedia, Wikipedia event stream)

## Setup

### 1. Choose where the dataset will live

The 7 IMDb files weigh 1.9 Go and the parquet derived from them a few gigabytes more. They are
kept **outside** this folder, for two reasons measured during the project: the project folder is
synchronised by OneDrive, which locks files while Spark is still writing them, and reading the
dataset through the host mount runs at 21 MB/s against 49 MB/s from a docker volume.

Copy the example configuration and point `DATA_DIR` at a folder outside any synchronised
directory:

```bash
cp .env.example .env
```

Compose reads `.env`, so this comes **before** starting the containers.

### 2. Download the IMDb dataset

Into the folder named by `DATA_DIR`, not into this one.

```bash
mkdir -p ~/imdb-data && cd ~/imdb-data && for f in name.basics title.akas title.basics title.crew title.episode title.principals title.ratings; do curl -O "https://datasets.imdbws.com/$f.tsv.gz"; done
```

On Windows PowerShell, with `$dir` set to the same folder as `DATA_DIR`:

```powershell
$dir = "$env:USERPROFILE\imdb-data"; mkdir -Force $dir; cd $dir; foreach ($f in "name.basics","title.akas","title.basics","title.crew","title.episode","title.principals","title.ratings") { curl.exe -O "https://datasets.imdbws.com/$f.tsv.gz" }
```

The link and the list of files come from the [IMDb non-commercial datasets](https://developer.imdb.com/non-commercial-datasets/) page.

### 3. Start the containers

```bash
docker compose up -d
```

This starts `imdb_spark` (the `quay.io/jupyter/pyspark-notebook` image, Spark 4.2.0) and
`imdb_kafka` (`apache/kafka-native:4.1.1` in KRaft mode). This folder is mounted in the Spark
container on `/home/jovyan/work`, the dataset volume on `/home/jovyan/work/data`, and the folder
from step 2 read only on `/mnt/host-data`. `01_ingest.py` copies the tsv from there into the
volume on its first run, which is what makes the pipeline runnable from scratch: the named
volume hides the `data/` folder of the host, so files downloaded into it would never be seen.

The compose project name is pinned to `projet-imdb` in `compose.yaml`. The named volume is
prefixed with it, so renaming this folder would otherwise make docker create a new empty volume
instead of finding the dataset.

### 4. Install the host dependencies

Only needed for the two scripts that go on the network: the Wikipedia download (`04b`) and the
Kafka producer (`05a`). They go in a virtualenv kept **outside** the project folder, because a
virtualenv is thousands of small files that OneDrive would try to upload one by one.

```bash
py -3.11 -m venv ~/.venvs/imdb-projet && ~/.venvs/imdb-projet/Scripts/python.exe -m pip install -r requirements-host.txt
```

`run_fetch.sh` picks that interpreter up on its own. To use another one, set `HOST_PYTHON`.

## Running the pipeline

Every job is run the same way, inside the Spark container, in this order. Each one depends on
the output of the previous ones.

```bash
docker exec imdb_spark python /home/jovyan/work/jobs/01_ingest.py
docker exec imdb_spark python /home/jovyan/work/jobs/02_preparation.py
docker exec imdb_spark python /home/jovyan/work/jobs/03_exploration.py
docker exec imdb_spark python /home/jovyan/work/jobs/04a_select_targets.py
```

`02_preparation.py` has three independent steps and accepts their names, so one can be re-run
without paying for the others (the measurements take about twenty five minutes):

```bash
docker exec imdb_spark python /home/jovyan/work/jobs/02_preparation.py clean
```

The steps are `missing` (percentage of missing values per column), `quality` (the other data
quality issues) and `clean` (the typed and corrected layer, plus the rejected rows). With no
argument the three run in that order.

`run_all.sh` chains everything with timestamps and stops at the first failure.

The Wikipedia download runs on the host, because the container has no reason to be given network
access to the outside:

```bash
PROJECT_ROOT=. ~/.venvs/imdb-projet/Scripts/python.exe jobs/04b_fetch_wikipedia.py
```

Or simply `./run_fetch.sh`, which waits for `04a` to publish its target lists and then starts.

It can be stopped and restarted, it skips what it already has. To only try the pipeline, give it
a number of entities: `python jobs/04b_fetch_wikipedia.py 50`.

Then back in Spark for the cleaning and the join:

```bash
docker exec imdb_spark python /home/jovyan/work/jobs/04c_enrich_spark.py
docker exec imdb_spark python /home/jovyan/work/jobs/06_open_question.py
```

### The streaming part

Two terminals. The producer runs on the host because it reads the Wikipedia event stream:

```bash
PROJECT_ROOT=. ~/.venvs/imdb-projet/Scripts/python.exe jobs/05a_wiki_producer.py 30
```

The consumer runs in Spark:

```bash
docker exec imdb_spark python /home/jovyan/work/jobs/05b_streaming.py
```

Start the producer first, let it run, then the consumer. The consumer prints its windows in the
console and writes the matching edits in `output/streaming/`.

## Where the results are

Every job writes in `output/<name>/`:

- `data.parquet`, the full result, to reuse it
- `table.md`, the same result as a markdown table, which is what `REPORT.md` quotes

`data/` and the parquet are not versioned: they are rebuilt by the jobs, and they are too big for
git.

## Project layout

```
compose.yaml              spark + kafka, compose project name pinned to projet-imdb
.env.example              DATA_DIR, where the dataset lives on the host (copy to .env)
requirements-host.txt     the 3 host dependencies, for 04b and 05a
run_all.sh                chains the spark batch jobs, with timestamps
run_fetch.sh              waits for 04a, then runs the wikipedia download on the host
PROJECT.md                this file
REPORT.md                 the results and the methodological write-up
jobs/
  common.py               the spark session, the paths, the saving of a result
  01_ingest.py            copies the tsv into the volume, then tsv -> parquet `raw` layer
  02_preparation.py       section 1: missing values, quality issues, `clean` layer
  03_exploration.py       section 2: the 8 questions
  04a_select_targets.py   section 3: what has to be enriched (spark)
  04b_fetch_wikipedia.py  section 3: the download (outside spark, on the host)
  04c_enrich_spark.py     section 3: cleaning, schema, join back (spark)
  05a_wiki_producer.py    section 4: wikipedia event stream -> kafka
  05b_streaming.py        section 4: structured streaming consumer
  06_open_question.py     section 5
enriched/                 the jsonl coming from wikipedia, written by the host (gitignored)
data/                     the docker volume: raw/ the tsv.gz, parquet/raw|clean/ the two layers
output/                   one folder per result, each with table.md and data.parquet
output/run_timings.md     the measured duration of every job
```

## Data sources

| Source | What for | Licence |
|---|---|---|
| [IMDb non-commercial datasets](https://developer.imdb.com/non-commercial-datasets/) | the 7 base tables | free for personal and non-commercial use |
| [Wikipedia (English)](https://en.wikipedia.org/) | the synopses and the biographies | CC BY-SA |
| [Wikidata](https://www.wikidata.org/) | the imdb id -> wikipedia article matching (property P345) | CC0 |
| [Wikimedia EventStreams](https://wikitech.wikimedia.org/wiki/Event_Platform/EventStreams_HTTP_Service) | the live stream of edits | CC0 |

Wikipedia was chosen because the subject names it: *"All information must come from
human-authored open sources such as Wikipedia or open-license movie databases"*. Everything there
is written by contributors and published under an open licence, so it answers both the
"human-authored" rule and the "open source" rule. No text is generated: we copy the lead section
of an article and we keep the link to it in a lineage field.

The scraping rules of the subject are respected: a `User-Agent` identifying the project as the
Wikimedia policy requires, serial requests with a pause and an exponential backoff, the official
batch APIs instead of parsing HTML, and a resumable run so a retry does not ask again for what we
already have.

## AI / LLM tools used

As required by the submission guidelines, here is the declaration.

| Tool | Used for | Not used for |
|---|---|---|
| Claude (Anthropic), through Claude Code | writing and debugging the PySpark and Python code of `jobs/`, the `compose.yaml`, and this file | the explanations and the reasoning of `REPORT.md` |

`REPORT.md` is written by the members of the group. The AI policy of the subject forbids the use
of AI tools for the explanations and the reasoning of the report, and this rule was followed.
