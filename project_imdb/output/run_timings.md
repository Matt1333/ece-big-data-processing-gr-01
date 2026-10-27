# Measured runtimes

Durations of the runs that produced the results in `REPORT.md`. Measured on 10 October 2026, on
a laptop: 4 cores given to Spark (`SPARK_CORES=4`), a container limited to 3.65 Go of RAM, a
driver heap of 2500 Mo, 32 shuffle partitions, everything in Spark local mode.

| Job | Step | Duration |
|---|---|---|
| `02_preparation.py` | `missing` + `quality` (the measurements) | ~25 min |
| `02_preparation.py` | `clean` (the typed layer, 7 tables) | **80 min** |
| `04a_select_targets.py` | top 10 films per genre per year + 3 principals | 13 min |
| `03_exploration.py` | `q1` to `q5` | 27 min |
| `03_exploration.py` | `q6` (multilingual actors) | 22 min |
| `03_exploration.py` | `q7` + `q8` | **44 min** |
| `04b_fetch_wikipedia.py` | 6 256 films + 10 557 people, on the host | 15 min |
| `04c_enrich_spark.py` | join and coverage of the enrichment | 5 min |
| `06_open_question.py` | director/actor duos | 17 min |
| `05b_streaming.py` | streaming test window | 18 min (by design) |

Spark batch total: about **3 h 30**, plus 15 min of downloads and the 18 min streaming window.

`01_ingest.py` (tsv.gz to parquet) ran on an earlier day and was not timed.

The heaviest steps are the two that touch `title.principals` (102 181 300 rows): building its
clean layer, and questions 7 and 8. The figures above are *after* the optimisations described
in the job docstrings; before them, the clean layer got the driver killed by the oom killer, and
question 6 alone took 2 h for an empty result.
