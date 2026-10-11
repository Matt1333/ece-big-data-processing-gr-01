#!/usr/bin/env bash
# Waits for 04a to produce the target lists, then downloads from wikipedia.
# Separate from run_all.sh on purpose: this one is network bound and runs on the host, so it
# can progress at the same time as the spark jobs without fighting for the same resource.
set -u
cd "$(dirname "$0")"

# The host dependencies live in a virtualenv kept outside the project folder, because the
# project folder is synchronised by OneDrive and a virtualenv is thousands of small files.
PY="${HOST_PYTHON:-/c/Users/mattd/.venvs/imdb-projet/Scripts/python.exe}"
[ -x "$PY" ] || { echo "host python not found: $PY (see PROJECT.md, setup step 2)"; exit 1; }

echo "waiting for the targets of 04a..."
while [ ! -d output/targets/films_csv ]; do sleep 20; done
sleep 10   # let the csv be fully written
echo "targets ready at $(date +%H:%M:%S)"
ls output/targets/
PROJECT_ROOT=. "$PY" jobs/04b_fetch_wikipedia.py
echo "FETCH DONE at $(date +%H:%M:%S)"
