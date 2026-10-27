#!/usr/bin/env bash
# Runs the whole spark side of the pipeline, one job after the other, with timestamps.
# Each job depends on the output of the previous one, so they cannot run in parallel.
# The wikipedia download is not here: it runs on the host and it is network bound, so it is
# started separately and both can progress at the same time.
set -u

step() {
  echo ""
  echo "=================================================================="
  echo "=== $1   started at $(date +%H:%M:%S)"
  echo "=================================================================="
  shift
  local t0=$(date +%s)
  MSYS_NO_PATHCONV=1 docker exec -e SPARK_CORES=4 imdb_spark python "$@" 2>&1 \
    | tr '\r' '\n' | grep -vE "^\[Stage|WARN |^\s*$|^Using |^Setting |^To adjust"
  local rc=${PIPESTATUS[0]}
  echo "=== finished in $(( $(date +%s) - t0 ))s (exit $rc)"
  return $rc
}

step "02_preparation"     /home/jovyan/work/jobs/02_preparation.py     || exit 1
step "04a_select_targets" /home/jovyan/work/jobs/04a_select_targets.py || exit 1
step "03_exploration"     /home/jovyan/work/jobs/03_exploration.py     || exit 1
step "06_open_question"   /home/jovyan/work/jobs/06_open_question.py   || exit 1

echo ""
echo "ALL SPARK JOBS DONE at $(date +%H:%M:%S)"
