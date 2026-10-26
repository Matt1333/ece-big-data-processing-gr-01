# IMDb project - Report

> **How to use this file.** The structure, the questions and the result tables are here. Every
> block marked `<!-- TO WRITE -->` has to be written by a member of the group: the subject
> requires a *Methodological Explanation* for each major section, and the AI policy of the
> subject forbids using an AI tool to write the explanations and the reasoning of this report.
>
> Each `table.md` quoted below is produced by the corresponding job in `output/`. Paste its
> content under the heading, or keep the reference if you prefer.
>
> Delete this block before the submission.

Group: gr-01 - DAVIDSON Matt, TOUVRON Erwan, PINTO Kylian

---

## 1. Data preparation

Job: `jobs/02_preparation.py`

### 1.1 Percentage of missing values per column

Source: `output/01_missing_per_column/table.md`

<!-- paste the table here -->

### 1.2 The five columns with the highest percentage of nulls

Source: `output/02_top5_missing/table.md`

| table_name | column_name | n_rows | n_missing | pct_missing |
|---|---|---|---|---|
| title.akas | attributes | 59668790 | 59353075 | 99.47 |
| title.basics | endYear | 12846867 | 12684284 | 98.73 |
| name.basics | deathYear | 15716378 | 15452135 | 98.32 |
| name.basics | birthYear | 15716378 | 15033008 | 95.65 |
| title.principals | job | 102181300 | 82476931 | 80.72 |

For the first column, we've got the attributes. So it's empty, but we know that this column was
supposed to be empty, because a big part of the alternative titles doesn't need any qualificative
word. It's just the title in another language. So this part is only useful when there is some
particular case, and otherwise it's empty.

Then we have the end year. So we were also waiting for an empty case, it's a structural
emptiness. Why? Because a film doesn't have any year of end, so only the series and the
miniseries have one. And sometimes not even them, because it is not explicitly said that a series
is finished, so there is only the ones that are finished, for example Breaking Bad. The films are
dominating the 12.8 million titles, and this is why end year is 98.73% empty: the films are the
titles that are the most common in all the database.

Then the death year. So the emptiness was expected, and in the big part of the cases it is
because the person is still alive. But there is also a real gap, because for people that are dead
and whose dates are not mentioned, we can't distinguish the two. Between a person that is dead
whose date is not mentioned, and a person that is not dead, we cannot know. We can also say that
the quality control found people that have a death date before they were born, so it means that
we can't trust this date: even when it is filled, we can't say that it is 100% accurate and
reliable.

Then we've got the birth year. So this one is a real gap, and it's the most important one,
because 95.65% on 15.7 million people means that we have the birth date only for 683 000 people.
So IMDb only gives it for the well known persons, so not for the thousands and thousands of
technicians, or just people that appear like one frame in a film for example. The consequence on
the project is that we can't build anything based on the age. So that's why in the seventh
question, which is on the careers that peak early, it measures the length of the career with the
years of the films and not the age of the actor.

Finally, for the job, it was an emptiness that we were waiting for, because the column category
already says the work. So if someone is actor, director or writer, the job one is just a
precision, and it's only filled for a certain type of people. Like for example an actor will have
category equal to actor and the job will be empty, which is normal because we already said in the
category that it was an actor and we have nothing to add, so that's why.

So to conclude, four of the five columns are empty by construction, and none of the five are used
for a project question. So the filling rate blocked none of our analyses. The only thing that
cost us something is the birth year, because it closed the possibility for us to analyze people
by their age, but we succeeded to find another way to analyze the data, so that's fine.

### 1.3 Other data quality issues

Source: `output/03_quality_issues/table.md`

<!-- paste the table here -->

### 1.4 How these values are handled

Source: `output/04_rejected_rows/table.md`

<!-- paste the table here -->

### Methodological explanation - Data preparation

<!-- TO WRITE. The subject asks for: the methodology and why it was chosen, the alternatives
     considered and the trade-offs made. Points you can cover:
     - why two layers (`raw` as strings, then `clean` typed) instead of typing at ingest
     - why tsv.gz -> parquet before anything else
     - the policy: cast failure -> null, impossible value -> null but keep the row, orphan
       foreign key -> removed but saved in output/rejected, duplicated primary key -> dropped
     - the alternatives you rejected: dropping whole rows, guessing/imputing values, keeping
       the orphans
     - what this policy costs and what it protects -->

---

## 2. Data exploration

Job: `jobs/03_exploration.py`

### 2.1 Feature films whose length is notably different from their genre average

Sources: `output/q1_runtime_outliers_per_genre/table.md`, `output/q1_runtime_outliers_top/table.md`

<!-- paste the tables here -->

### 2.2 Top three genres per year, 1980-2025

Source: `output/q2_top3_genres_per_year/table.md`

<!-- paste the table here -->

### 2.3 The top three compared to the other genres of the same year

Source: `output/q3_top3_vs_rest/table.md`

<!-- paste the table here -->

### 2.4 Directors with one film >= 8.0 and several others averaging <= 6.0

Source: `output/q4_one_hit_directors/table.md`

<!-- paste the table here -->

### 2.5 Series whose worst episode is in the last season and best episode in the first two

Source: `output/q5_series_going_downhill/table.md`

<!-- paste the table here -->

### 2.6 Actors successful in several languages

Sources: `output/q6_actors_2plus_languages/table.md`, `output/q6_actors_3plus_languages/table.md`

<!-- paste the tables here -->

### 2.7 Actors with a 20+ year career whose popularity peaked early

Source: `output/q7_early_peak_actors/table.md`

<!-- paste the table here -->

### 2.8 Multi-talented film professionals

Sources: `output/q8_multi_talented/table.md`, `output/q8_multi_role_vs_single_role/table.md`

<!-- paste the tables here -->

### Methodological explanation - Data exploration

<!-- TO WRITE. Several questions of the subject are not directly measurable and had to be turned
     into a rule. For each one, say what rule was chosen and why, and what another rule would
     have changed:
     - "notably different" -> z-score > 3 inside each genre
     - "popular" genre -> total number of votes, and not the number of films
     - "successful" film -> rating >= 7.0 with at least 1000 votes
     - "peaked early" -> career cut in two halves, gap of at least 1 rating point
     - "feature film" -> titleType movie and runtime >= 60 minutes
     Also worth covering: the language of a film is taken from title.akas, which describes the
     versions of a title and not only the original one, and what this approximation costs. -->

---

## 3. Data enrichment

Jobs: `jobs/04a_select_targets.py`, `jobs/04b_fetch_wikipedia.py`, `jobs/04c_enrich_spark.py`

### 3.1 Scope

Source: `output/e1_enrichment_scope/table.md`

<!-- paste the table here -->

### 3.2 Coverage

Source: `output/e2_enrichment_coverage/table.md`

<!-- paste the table here -->

### 3.3 Why some records could not be enriched

Source: `output/e3_missing_reasons/table.md`

<!-- paste the table here -->

### 3.4 Sample of enriched records

Source: `output/e4_sample/table.md`

<!-- paste the table here -->

### Methodological explanation - Data enrichment

<!-- TO WRITE. Points to cover:
     - why Wikipedia (the subject names it; human-authored; open licence) and why no text is
       generated
     - how a film is matched to its article: through the Wikidata property P345 and not by
       searching the title, and what a title search would have broken
     - how the rate limits and the scraping policies are respected (User-Agent, serial requests,
       batch endpoints, backoff, resumable run, official APIs only)
     - the lineage kept on every record and why it matters
     - the note added programmatically when the information is missing
     - how the code would scale to the full dataset without a structural change -->

---

## 4. Streaming data processing

Jobs: `jobs/05a_wiki_producer.py`, `jobs/05b_streaming.py`

### 4.1 Filtering strategy

<!-- TO WRITE: what subset of the stream is kept and why it is broad enough to guarantee several
     matching events in a 15 to 30 minute window. -->

### 4.2 Metrics of the test window

<!-- paste here the console output of the windows, and the figures: events seen, events matched,
     average lag between event time and reception. -->

### 4.3 Handling of late arriving data

<!-- TO WRITE. The subject explicitly asks for this one. Cover: event time vs processing time on
     this stream, the watermark chosen and its duration, what spark does with an event that
     arrives after the watermark, and what would happen without a watermark. -->

### Methodological explanation - Streaming

<!-- TO WRITE: the methodology, why it was chosen, the alternatives considered and the
     trade-offs. In particular the stream-static join and the normalisation of both sides, and
     why an exact match on a normalised key was preferred to a fuzzy match. -->

---

## 5. Open question

Job: `jobs/06_open_question.py`

**Question: does a recurring director-actor duo make better films than the same two people
apart?**

### 5.1 What is investigated and why it is interesting

<!-- TO WRITE: the question, why it is worth asking, and what additional data was needed
     (none here, the imdb tables are enough). -->

### 5.2 Results

Sources: `output/o4_summary/table.md`, `output/o1_best_duos/table.md`,
`output/o2_worst_duos/table.md`, `output/o3_most_prolific_duos/table.md`,
`output/o5_lift_by_number_of_films/table.md`

<!-- paste the tables here -->

### 5.3 Key takeaways

<!-- TO WRITE -->

### Methodological explanation - Open question

<!-- TO WRITE. Points to cover:
     - the baseline excludes the shared films, and why comparing a duo to the full career of its
       members would have flattened the effect
     - how that baseline is computed by difference of sums instead of one join per pair
     - the thresholds: at least 3 films together, at least 1000 votes, lead billing only
     - the limit of the result: a correlation is not a causality, a director calling back the
       actor of a film that worked would produce the same numbers -->

---

## Appendix - execution environment

<!-- TO WRITE or complete: the machine, the container versions, the total runtime of each job. -->

| | |
|---|---|
| Spark | 4.2.0 (image `quay.io/jupyter/pyspark-notebook`) |
| Kafka | 4.1.1 (`apache/kafka-native`, KRaft) |
| Dataset | IMDb non-commercial, downloaded on 2026-10-08 |
| `title.principals` | 102 181 300 rows |
| `title.akas` | 59 668 790 rows |
| `name.basics` | 15 716 378 rows |
| `title.basics` | 12 846 867 rows |
| `title.crew` | 12 846 867 rows |
| `title.episode` | 9 934 901 rows |
| `title.ratings` | 1 718 390 rows |
