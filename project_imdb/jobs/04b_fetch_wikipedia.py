"""Section 3: Data enrichment, step B: download the texts from Wikipedia.

This is the only part of the project which runs outside spark, and the subject allows it: "Data
gathering may be done outside of Spark but all other operations such as cleaning, schema
enforcement, etc., must be performed using Spark".

Why Wikipedia: the subject names it, "human-authored open sources such as Wikipedia or
open-license movie databases". Everything on Wikipedia is written by people and published under
CC BY-SA, so it answers the "human-authored" rule and the "open source" rule at the same time. We
generate no text, we only copy the first paragraphs of an article and we keep the link to it.

How we match a film with its article: not by searching its title, which would give us wrong films
for every remake and every common title. We pass by Wikidata, which stores the imdb id of a work
in the property P345, and gives back the exact english article of the same entity. One sparql
query matches a few hundred ids at the same time.

About the politeness, because the subject requires it ("must respect target domain API rate
limits and all other scraping policies"):
  - a real User-Agent which identifies the project, like the Wikimedia policy asks
  - the requests are serial, never in parallel, with a pause between them
  - we use the official apis, we never parse the html of the site
  - we use the batch endpoints (300 ids per sparql query, 20 articles per api call), which
    divides the number of requests by the same quantity
  - the run can be resumed: what is already downloaded is skipped, so a retry does not ask
    Wikimedia again for what we already have

Each record keeps its lineage: the url of the article, the id of the Wikidata entity, the name of
the source and the time of the download.
"""
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

ROOT = os.environ.get("PROJECT_ROOT", "/home/jovyan/work")
TARGETS = f"{ROOT}/output/targets"
# the downloaded texts go into the project folder and not under data/: data/ is a docker volume,
# the host writes here and the container reads the same files through its mount
ENRICHED = f"{ROOT}/enriched"

# Wikimedia asks every client to identify itself with a contact. We have to put a real contact
# of the group here before running it for the submission.
USER_AGENT = ("ECE-BigDataProcessing-Project/1.0 "
              "(https://github.com/Matt1333/ece-big-data-processing-gr-01; student project)")

SPARQL_URL = "https://query.wikidata.org/sparql"
API_URL = "https://en.wikipedia.org/w/api.php"
SPARQL_BATCH = 300          # ids per sparql query
EXTRACT_BATCH = 20          # the api limits `extracts` to 20 pages per call
SLEEP_SPARQL = 1.0          # seconds between two sparql queries
SLEEP_API = 0.3             # seconds between two api calls


def _ssl_context():
    """The certificate authorities that we trust.

    `urllib` validates against the certificate store of the operating system. On this machine
    this store makes wikidata.org and wikipedia.org fail with "certificate has expired", and
    exactly the same request succeeds against the `certifi` bundle, so the expired authority is
    on the system side and not on the wikimedia side. `certifi` ships the current mozilla list
    and it is refreshed at every release, so we validate against it when it is installed and we
    fall back on the system store if it is not.
    """
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


SSL_CONTEXT = _ssl_context()

# the errors which are worth to try again: a service under load, a timeout, a connection which
# dropped. A certificate or a dns error would fail again identically, so retrying them only
# wastes our time
RETRYABLE = (urllib.error.HTTPError, TimeoutError, ConnectionError)


def http_get(url, params):
    """One GET with the User-Agent of the project. Serial on purpose, no parallelism."""
    full = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(full, headers={"User-Agent": USER_AGENT,
                                                "Accept": "application/json"})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60, context=SSL_CONTEXT) as r:
                return json.loads(r.read().decode("utf-8"))
        except RETRYABLE as e:
            # exponential backoff: if the service is under load, asking again immediately is
            # exactly what the rate limit policies forbid
            wait = 2 ** attempt
            print(f"  retry in {wait}s ({e})")
            time.sleep(wait)
        except urllib.error.URLError as e:
            # a tls or a dns failure: five identical attempts would teach us nothing
            raise RuntimeError(f"{url} unreachable: {e.reason}") from e
    raise RuntimeError(f"5 failed attempts on {url}")


def read_csv_dir(path):
    """Reads the single csv part that spark wrote with coalesce(1)."""
    import csv
    name = [f for f in os.listdir(path) if f.endswith(".csv")][0]
    with open(f"{path}/{name}", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def map_imdb_to_wikipedia(imdb_ids):
    """imdb id -> title of the english wikipedia article, through Wikidata (property P345).

    VALUES puts the whole batch inside one query, so a few hundred ids cost one request.
    """
    mapping = {}
    for i in range(0, len(imdb_ids), SPARQL_BATCH):
        batch = imdb_ids[i:i + SPARQL_BATCH]
        values = " ".join(f'"{x}"' for x in batch)
        query = f"""
        SELECT ?imdb ?item ?article WHERE {{
          VALUES ?imdb {{ {values} }}
          ?item wdt:P345 ?imdb .
          ?article schema:about ?item ;
                   schema:isPartOf <https://en.wikipedia.org/> .
        }}"""
        data = http_get(SPARQL_URL, {"query": query, "format": "json"})
        for b in data["results"]["bindings"]:
            imdb = b["imdb"]["value"]
            url = b["article"]["value"]
            title = urllib.parse.unquote(url.rsplit("/", 1)[-1]).replace("_", " ")
            mapping[imdb] = {
                "wikipedia_title": title,
                "source_url": url,
                "wikidata_uri": b["item"]["value"],
            }
        print(f"  wikidata {i + len(batch):>6}/{len(imdb_ids)} -> {len(mapping)} matched")
        time.sleep(SLEEP_SPARQL)
    return mapping


def fetch_extracts(titles):
    """The first paragraphs of each article, as plain text, 20 articles per call.

    `exintro` gives only the lead section, which is the summary of the article written by the
    contributors. `explaintext` asks for text and not html, like this we have nothing to strip
    after. `redirects` follows the renamings instead of returning an empty page.
    """
    out = {}
    for i in range(0, len(titles), EXTRACT_BATCH):
        batch = titles[i:i + EXTRACT_BATCH]
        data = http_get(API_URL, {
            "action": "query", "format": "json", "formatversion": 2,
            "prop": "extracts", "exintro": 1, "explaintext": 1, "exlimit": EXTRACT_BATCH,
            "redirects": 1, "titles": "|".join(batch),
        })
        # a redirect changes the title, so we have to follow the mapping that the api returns
        redirects = {r["from"]: r["to"] for r in data.get("query", {}).get("redirects", [])}
        for page in data.get("query", {}).get("pages", []):
            if "extract" in page and page["extract"]:
                out[page["title"]] = page["extract"].strip()
        for src, dst in redirects.items():
            if dst in out:
                out[src] = out[dst]
        print(f"  extracts {i + len(batch):>6}/{len(titles)} -> {len(out)} texts")
        time.sleep(SLEEP_API)
    return out


def already_done(path):
    """The ids already downloaded, like this a second run does not ask Wikimedia again."""
    if not os.path.exists(path):
        return set()
    done = set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                done.add(json.loads(line)["imdb_id"])
            except Exception:
                pass
    return done


def enrich(kind, rows, id_field, label_field, out_file):
    """Downloads one kind of entity (films or people) and appends the records into a jsonl.

    We write a record even when we found nothing, with a `note` which says why. The subject asks
    exactly this: "notes should be programmatically added to the output when information is not
    currently available".
    """
    os.makedirs(ENRICHED, exist_ok=True)
    done = already_done(out_file)
    todo = [r for r in rows if r[id_field] not in done]
    print(f"{kind}: {len(rows)} targets, {len(done)} already downloaded, {len(todo)} to do")
    if not todo:
        return

    ids = [r[id_field] for r in todo]
    mapping = map_imdb_to_wikipedia(ids)

    titles = [m["wikipedia_title"] for m in mapping.values()]
    extracts = fetch_extracts(titles) if titles else {}

    now = datetime.now(timezone.utc).isoformat()
    with open(out_file, "a", encoding="utf-8") as f:
        for r in todo:
            imdb_id = r[id_field]
            m = mapping.get(imdb_id)
            if m is None:
                rec = {"imdb_id": imdb_id, "label": r[label_field], "text": None,
                       "source_name": None, "source_url": None, "wikidata_uri": None,
                       "retrieved_at": now,
                       "note": "no english wikipedia article linked to this imdb id in wikidata"}
            else:
                text = extracts.get(m["wikipedia_title"])
                rec = {"imdb_id": imdb_id, "label": r[label_field], "text": text,
                       "source_name": "Wikipedia (English)" if text else None,
                       "source_url": m["source_url"], "wikidata_uri": m["wikidata_uri"],
                       "retrieved_at": now,
                       "note": None if text else "article found but no lead section to extract"}
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"{kind}: written to {out_file}")


def main():
    films = read_csv_dir(f"{TARGETS}/films_csv")
    people = read_csv_dir(f"{TARGETS}/people_csv")

    # an optional cap, only to try the pipeline quickly. The full run is the default.
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    if limit:
        films, people = films[:limit], people[:limit]
        print(f"LIMITED RUN: {limit} films and {limit} people")

    enrich("films", films, "tconst", "primaryTitle", f"{ENRICHED}/films.jsonl")
    enrich("people", people, "nconst", "primaryName", f"{ENRICHED}/people.jsonl")


if __name__ == "__main__":
    main()
