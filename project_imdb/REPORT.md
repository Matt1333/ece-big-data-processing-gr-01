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

| table_name | column_name | n_rows | n_missing | pct_missing |
|---|---|---|---|---|
| title.akas | attributes | 59668790 | 59353075 | 99.47 |
| title.basics | endYear | 12846867 | 12684284 | 98.73 |
| name.basics | deathYear | 15716378 | 15452135 | 98.32 |
| name.basics | birthYear | 15716378 | 15033008 | 95.65 |
| title.principals | job | 102181300 | 82476931 | 80.72 |
| title.akas | types | 59668790 | 39940930 | 66.94 |
| title.basics | runtimeMinutes | 12846867 | 8017609 | 62.41 |
| title.principals | characters | 102181300 | 52353528 | 51.24 |
| title.crew | writers | 12846867 | 6355076 | 49.47 |
| title.crew | directors | 12846867 | 5715026 | 44.49 |
| title.akas | language | 59668790 | 19468342 | 32.63 |
| title.akas | region | 59668790 | 12887488 | 21.60 |
| title.episode | seasonNumber | 9934901 | 2085819 | 20.99 |
| title.episode | episodeNumber | 9934901 | 2085819 | 20.99 |
| name.basics | primaryProfession | 15716378 | 3189614 | 20.29 |
| name.basics | knownForTitles | 15716378 | 1901087 | 12.10 |
| title.basics | startYear | 12846867 | 1484901 | 11.56 |
| title.basics | genres | 12846867 | 544458 | 4.24 |
| name.basics | primaryName | 15716378 | 88 | 0.00 |
| name.basics | nconst | 15716378 | 0 | 0.00 |
| title.akas | titleId | 59668790 | 0 | 0.00 |
| title.akas | ordering | 59668790 | 0 | 0.00 |
| title.akas | title | 59668790 | 0 | 0.00 |
| title.akas | isOriginalTitle | 59668790 | 0 | 0.00 |
| title.basics | tconst | 12846867 | 0 | 0.00 |
| title.basics | titleType | 12846867 | 0 | 0.00 |
| title.basics | primaryTitle | 12846867 | 0 | 0.00 |
| title.basics | originalTitle | 12846867 | 0 | 0.00 |
| title.basics | isAdult | 12846867 | 0 | 0.00 |
| title.crew | tconst | 12846867 | 0 | 0.00 |
| title.episode | tconst | 9934901 | 0 | 0.00 |
| title.episode | parentTconst | 9934901 | 0 | 0.00 |
| title.principals | tconst | 102181300 | 0 | 0.00 |
| title.principals | ordering | 102181300 | 0 | 0.00 |
| title.principals | nconst | 102181300 | 0 | 0.00 |
| title.principals | category | 102181300 | 0 | 0.00 |
| title.ratings | tconst | 1718390 | 0 | 0.00 |
| title.ratings | averageRating | 1718390 | 0 | 0.00 |
| title.ratings | numVotes | 1718390 | 0 | 0.00 |

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

| table_name | issue | n_affected | unit |
|---|---|---|---|
| title.principals | nconst with no parent row | 3209 | distinct keys |
| name.basics | deathYear before birthYear | 27 | rows |
| title.basics | startYear more than 5 years in the future | 5 | rows |
| title.basics | runtimeMinutes <= 0 | 4 | rows |
| title.episode | parentTconst with no parent row | 4 | distinct keys |
| name.basics | birthYear in the future | 0 | rows |
| name.basics | birthYear not a number | 0 | rows |
| name.basics | duplicated nconst | 0 | rows |
| title.basics | endYear before startYear | 0 | rows |
| title.basics | runtimeMinutes not a number | 0 | rows |
| title.basics | startYear not a number | 0 | rows |
| title.basics | duplicated tconst | 0 | rows |
| title.ratings | tconst with no parent row | 0 | distinct keys |
| title.akas | titleId with no parent row | 0 | distinct keys |
| title.crew | tconst with no parent row | 0 | distinct keys |
| title.episode | tconst with no parent row | 0 | distinct keys |
| title.principals | tconst with no parent row | 0 | distinct keys |
| title.ratings | duplicated tconst | 0 | rows |

### 1.4 How these values are handled

Source: `output/04_rejected_rows/table.md`

| table_name | n_rows_raw | n_rows_clean | n_rows_rejected |
|---|---|---|---|
| title.ratings | 1718390 | 1718390 | 0 |
| title.akas | 59668790 | 59668790 | 0 |
| title.crew | 12846867 | 12846867 | 0 |
| title.episode | 9934901 | 9934891 | 10 |
| title.principals | 102181300 | 102174150 | 7150 |

### Methodological explanation - Data preparation

So why this choice, and what choice we made. We know that we have two layers. The pipeline writes
first a raw layer, where every column is a character string. Then there is a clean layer, which is
typed and corrected. Why do we have two layers and not only one? Because if we typed right after
the ingestion, a value impossible to cast would be transformed into null silently, and we couldn't
measure what really missed in the process. So the raw layer is what makes the question 1.1
measurable.

Why we passed to the parquet format instead of CSV or any other structured data: because the TSV
sources are in gzip, and gzip is not splittable. So Spark will read every file with only one task
and needs to reparse the text at every job. Parquet is columnar, but it is also splittable and
typed. So every request that needs for example three columns on 9 will only read these three
columns.

How we clean the data now, it's everywhere the same case. If the cast is impossible, we fill with
the null value, because we will never try to guess a value. If the value is impossible, same
thing, we will put the null value in it, but we will keep the line. Because we will not delete an
entire person just because a date is wrong or anything else. So we prefer to have a missing date
but the entire line still there, instead of deleting everything. If a foreign key is orphan, we
will remove the line from the clean layer, because a join will lose it anyway, but its key will be
saved in output rejected, in order that nothing disappears in silence. Then if a primary key is
duplicated, we would have to handle it, but in our case none are duplicated, so we are fine in
this case.

To conclude on this part, the numbers. We have 39 columns measured, 18 quality controls, and 7160
lines rejected. These rejected lines come from the orphan foreign keys: 3209 orphan nconst in
title.principals, which represent 7150 lines, and 4 orphan parentTconst in title.episode, which
represent 10 lines. The other problems are not rejected but set to null: 27 deaths before birth, 5
impossible years, and 4 runtimes negative or null.

The alternatives we rejected. The first one is to delete the entire line when a field is bad: we
would lose millions of lines for a field that none of our questions were using, so it was useless.
The second one is the imputation, so filling with the mean or the median. It creates data which
does not exist, and on a quality report of data it is exactly what we are not supposed to do. And
finally, keeping the orphans: they would be lost in the first join that they cross, and we could
not count them.

About our solution, there was a drop duplicates which was created at the beginning, but we removed
it, because it was shuffling the whole table in order to delete nothing, and on title.basics this
one single call was killing the driver, so it was very difficult. The control stays in the quality
report, so a future IMDb dump that would introduce a duplicate would make it appear.

In the same way, the filtering of the foreign keys is conditional: we first count the orphans,
which shuffles only one narrow column, and we run the join only if there is really something to
remove. On this dump, it avoids the join for every key except two.

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

So for this part, the facts that we have. The producer, which is the job
`05a_wiki_producer.py`, reads the live stream of the modifications in Wikipedia, and it pushes
everything that has been read into Kafka. Every edit of the English Wikipedia is sent to Kafka, so
it means 3 to 5 things are sent every second. There is no filter at this level, and this is a
choice, it is voluntary. The subject needs a criteria "sufficiently broad to guarantee that
multiple matching events are captured and processed within a 15 to 30 minute test window". By
keeping this whole stream on the producer side, it stays representative, and we can show how many
events have been seen compared to how many have been matched.

Why Wikipedia in English and not in French? Because the enrichment of the section 3 uses Wikipedia
in English, so the pages that have the most chance to correspond are the film pages that are in
English.

The filtering is done by Spark with a join, and it is there that we reduce: we join the stream
with a static reference built from the Parquet.

There is a first fail, and it is the main point of our paragraph. In the first version, the
reference contained only the entities that had been enriched in the section 3, so approximately
17,000. Against 3 to 5 edits per second dispatched on millions of different articles, this aim of
17,000 pages was never touched, because a run of 16 minutes matched no event. It means that the
filter was too tight, and it was not aligned with the purpose of the subject.

The measure that served to build the new reference was: for the movie only we have 758,864 lines,
for the movie plus TV series plus TV miniseries we have 1,138,819 lines, and if we take all the
people we have more than 15 million lines. So we only took the second option, which is the movie
plus TV series plus TV miniseries, so around 66 times the first version. And we add to this the
principals that have been enriched.

Every people were voluntarily excluded, because 15 million lines are too expensive for our
pipeline, and the real people that are edited are mainly the guys who are well known enough to be
a principal actor of a film or a main character of the film.

The primary title and the original title both become keys, because a Wikipedia article can be
named on one or the other of the things that I mentioned just before, so it can be the primary
title or the original title.

And then the result that we measured on the test window. It has been running for 18 minutes, we
have seen 2,317 events, and we have matched 65 of these events. It means that this is around
2.81%, and we have 41 distinct entities. On this, we have 54 edits on titles and 11 on people. So
the requirement of the subject is maintained. We have many matches in a window of 18 minutes.

But we have a limitation to accept: the exact correspondence on the normalized title produces some
false positives when a page has the same name as a film. For example if a film is named Bruges, or
if it is a simple word that is the same for a film and for a town, a country, a dish, it can be
many things. We can't separate it from the film without losing some real matches.

### 4.2 Metrics of the test window

Console output of the windowed query, excerpt of four consecutive micro batches (the Spark
progress bars have been removed):

```
-------------------------------------------
Batch: 8
-------------------------------------------
+------------------------------------------+-----------+-------+-----------------+---------------+
|window                                    |entity_type|n_edits|n_entities_approx|avg_lag_seconds|
+------------------------------------------+-----------+-------+-----------------+---------------+
|{2026-10-29 10:50:00, 2026-10-29 10:55:00}|title      |10     |10               |0.8            |
+------------------------------------------+-----------+-------+-----------------+---------------+

-------------------------------------------
Batch: 9
-------------------------------------------
+------------------------------------------+-----------+-------+-----------------+---------------+
|window                                    |entity_type|n_edits|n_entities_approx|avg_lag_seconds|
+------------------------------------------+-----------+-------+-----------------+---------------+
|{2026-10-29 10:50:00, 2026-10-29 10:55:00}|person     |5      |1                |0.8            |
|{2026-10-29 10:50:00, 2026-10-29 10:55:00}|title      |11     |11               |0.8            |
+------------------------------------------+-----------+-------+-----------------+---------------+

-------------------------------------------
Batch: 10
-------------------------------------------
+------------------------------------------+-----------+-------+-----------------+---------------+
|window                                    |entity_type|n_edits|n_entities_approx|avg_lag_seconds|
+------------------------------------------+-----------+-------+-----------------+---------------+
|{2026-10-29 10:50:00, 2026-10-29 10:55:00}|person     |6      |1                |0.8            |
|{2026-10-29 10:50:00, 2026-10-29 10:55:00}|title      |12     |12               |0.8            |
+------------------------------------------+-----------+-------+-----------------+---------------+

-------------------------------------------
Batch: 11
-------------------------------------------
+------------------------------------------+-----------+-------+-----------------+---------------+
|window                                    |entity_type|n_edits|n_entities_approx|avg_lag_seconds|
+------------------------------------------+-----------+-------+-----------------+---------------+
|{2026-10-29 10:55:00, 2026-10-29 11:00:00}|title      |3      |3                |0.3            |
+------------------------------------------+-----------+-------+-----------------+---------------+

... and the query that counts everything the stream carried, matched or not:

-------------------------------------------
Batch: 5
-------------------------------------------
+------------------------------------------+--------------+
|window                                    |n_events_total|
+------------------------------------------+--------------+
|{2026-10-29 10:50:00, 2026-10-29 10:55:00}|488           |
+------------------------------------------+--------------+

-------------------------------------------
Batch: 6
-------------------------------------------
+------------------------------------------+--------------+
|window                                    |n_events_total|
+------------------------------------------+--------------+
|{2026-10-29 10:50:00, 2026-10-29 10:55:00}|603           |
+------------------------------------------+--------------+
```

Figures of the run, from `output/s1_streaming_metrics/table.md`:

| window_minutes | events_seen | events_matched | pct_matched | distinct_entities_touched | avg_lag_seconds | min_lag_seconds | max_lag_seconds |
|---|---|---|---|---|---|---|---|
| 18 | 2317 | 65 | 2.81 | 41 | 0.80 | 0 | 1 |

Matched edits by entity type, from `output/s2_matched_by_entity_type/table.md`:

| entity_type | n_edits | n_entities | avg_lag_seconds |
|---|---|---|---|
| title | 54 | 39 | 0.80 |
| person | 11 | 2 | 0.80 |

Sample of the matched edits, from `output/s3_matched_edits_sample/table.md`:

| event_time | title | label | entity_type | imdb_id | user | bot | lag_seconds |
|---|---|---|---|---|---|---|---|
| 2026-10-29 11:06:56.079000 | You're Next | You're Next | title | tt1853739 | Wikidude10000 | False | 0 |
| 2026-10-29 11:06:45.493000 | Panchavati | Panchavati | title | tt0156866 | ~2026-57234-52 | False | 1 |
| 2026-10-29 11:05:47.320000 | Panchavati | Panchavati | title | tt0156866 | Brboize | False | 1 |
| 2026-10-29 11:05:18.383000 | Mañón | Manon | title | tt6423434 | Cie tsy-yin | False | 1 |
| 2026-10-29 11:04:56.722000 | Pechino Express | Pechino Express | title | tt4944488 | Kazanl00k | False | 1 |
| 2026-10-29 11:04:24.778000 | Pinki Elli | Pinki Elli? | title | tt12670516 | Nirgathika | False | 1 |
| 2026-10-29 11:04:18.210000 | Pechino Express | Pechino Express | title | tt4944488 | Kazanl00k | False | 0 |
| 2026-10-29 11:03:51.207000 | Panchavati | Panchavati | title | tt0156866 | ~2026-57234-52 | False | 1 |
| 2026-10-29 11:03:46.623000 | TENA | Tena | title | tt10936918 | Entranced98 | False | 1 |
| 2026-10-29 11:03:13.440000 | Tetris | Tetris | title | tt1543151 | DuncanHill | False | 1 |
| 2026-10-29 11:03:09.261000 | When Heroes Fly | When Heroes Fly | title | tt8220344 | ProfSamBJones | False | 1 |
| 2026-10-29 11:02:37.578000 | JK Enum Nanbanin Vaazhkai | JK Enum Nanbanin Vaazhkai | title | tt3426294 | Kailash29792 | False | 1 |
| 2026-10-29 11:02:36.463000 | Digital transformation | Digital Transformation | title | tt6836116 | Kuru | False | 1 |
| 2026-10-29 11:01:33.989000 | Zorro, The Gay Blade | Zorro: The Gay Blade | title | tt0083366 | Carlotta2026 | False | 1 |
| 2026-10-29 11:01:32.730000 | Pierre Richard | Pierre Richard | person | nm0007069 | Psychloppos | False | 1 |
| 2026-10-29 11:01:31.953000 | Pechino Express | Pechino Express | title | tt4944488 | SuperFastSpellChecker | False | 1 |
| 2026-10-29 11:01:06.810000 | Royal family | Royal Family | title | tt0251380 | MusikBot II | True | 1 |
| 2026-10-29 11:00:58.037000 | The King in Yellow | The King in Yellow | title | tt25816248 | MusikBot II | True | 0 |
| 2026-10-29 11:00:55.160000 | Tayo the Little Bus | Tayo, the Little Bus | title | tt3270208 | MusikBot II | True | 0 |
| 2026-10-29 11:00:43.141000 | Lobotomy | Lobotomy | title | tt39314280 | MusikBot II | True | 0 |
| 2026-10-29 11:00:13.795000 | VisionQuest | VisionQuest | title | tt23112594 | MillenniumGeneration | False | 1 |
| 2026-10-29 11:00:07.253000 | The Wind in the Willows | The Wind in the Willows | title | tt7657564 | Strongshorts | False | 0 |
| 2026-10-29 10:59:59.813000 | 1916 | 1916 | title | tt3592380 | Rcb1 | False | 1 |
| 2026-10-29 10:59:55.417000 | Panchavati | Panchavati | title | tt0156866 | ~2026-57234-52 | False | 1 |
| 2026-10-29 10:59:35.658000 | The Wind in the Willows | The Wind in the Willows | title | tt7657564 | ~2026-56479-14 | False | 1 |

### 4.3 Handling of late arriving data

So in this block we will talk about the time. The facts: there are two times. Wikipedia gives
`meta.dt`, so the moment where the editing has been done, and this one is named the event time.
And then there is another one, which is the moment where Kafka receives it: it is the processing
time. These two are different, because an event can appear after the window that is attached to
him has been reported.

The watermark we chose is 10 minutes, declared on the event time. Spark accepts an event that is
late if this event is within the 10 minutes after the max event time that has been reached, and
then it throws away all the things that happen after these 10 minutes.

So why 10 and not another number? It is because it is long enough for the normal delay of the
stream, which is just a few seconds, but it is short enough so the state stays small in a test
window, which is from 15 to 30 minutes.

Without a watermark, Spark will keep the state of every window indefinitely, because it could
never know when a window is finished. The memory would grow and it would never get down. That is
also why the watermark has to be declared before every stateful operation.

Then we have a technical constraint which is linked to this. It is the same thinking that imposed
to us the `approx_count_distinct` instead of the `countDistinct` in the aggregation window: an
exact distinct count on a stream would force us to memorize every ID that we have already seen,
so the state would grow bigger and bigger with the traffic, without stopping or diminishing. It
would always be bigger and more costly. Spark forbids it. So the exact number is recomputed after,
in batch, on the parquet, where keeping everything in memory is not a matter.

What we measure is that the mean of the delay is approximately 0.80 seconds. The minimum is 0
second and the maximum is 1 second. We have no negative value.

So the first campaign gives us a negative lag, but we understood that it was a delay on the clock,
so we retry it on an empty topic, and the proper measure was between 0 and 1 second. So my
explanation was demonstrated and not supposed. So we confirmed that it was a mistake.

So the watermark is there in order to correct the computation, and not because the stream is
late.

### Methodological explanation - Streaming

So for this block, the first fail in the beginning was that the stream gives a title of a Wikipedia
page, but our dataset gives titles of films and the names of the persons, and we have to link the
two. So we have to link the title and the name of the people, and the two aren't written the same
way, so it was quite difficult to link them.

So how did we succeed to link them? We use the stream static join. We join the stream, that stays
a stream, with a static data frame built from our Parquet dataset. Spark re-reads this static side
at every micro batch, and that is why this side is put in cache: without the cache, every micro
batch would rebuild all the plan from the parquet.

And why didn't we use a broadcast for example? Because we have like 1.1 million lines, so it is
very very big for an executor to diffuse it. So we use a normal join, and that is the price for
this big reference. The `F.broadcast()` that we had in the beginning has been removed for this
reason in particular.

The normalization is identical on the both sides, so we put all the things in small letters, we
throw away all the accents, and all the things that are not a letter or a number become a space.
For example "WALL.E" becomes "wall e", and "Amélie" becomes "amelie", and it becomes the same key.
Whereas two films that are different stay different. So it is just in order to be insensitive to
the writing, and to be sure that a film is the right film and not another one.

The central choice is exact on a normalized key, and not an approximative correspondence, because
an approximative correspondence would bring the bad film silently, and we would have no way to
know that it is not the right film but the false one, because the stream is too fast for us to
read it, it is going at a very excessive pace. So with an exact correspondence it can also happen
that it fails, but we can verify it and we can also anticipate it, for example the homonyms.

We also have to deduplicate, so one line by key in the reference, because two films with the same
title would duplicate every edit that corresponds. And we only have to know one thing, which is
that the page concerns our dataset.

The three requests launched in parallel are: every edit that corresponds, written in Parquet with
a checkpoint, because it is what makes our job restartable without losing or duplicating any line.
Then we count every window on the event time with the update mode, because it only shows the
windows that are modified in the batch. And then finally the total volume seen, matched or not,
because it is the denominator that proves that the filter is big enough.

Finally we have a safeguard, `maxOffsetsPerTrigger`. It is a limit on what a micro batch swallows,
because without this, a batch that is slow makes the next one read everything that has piled up so
far, and the delay is going to be bigger and bigger.

Finally, the compromise that we assume on the people. The 15.7 million people are all excluded
from the reference, because including them would give more correspondences, but the cost of a join
replayed at every micro batch against 15.7 million lines didn't justify that, it would be too big
and too costly for us. And the people that are really edited are mainly the principals of films
that have already been enriched.

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

So for the machine and the container, it was a portable with four cores. The container limit was
3.652 Gio of RAM. Spark was on local mode without any cluster, all the things run in the driver
with a Java heap of 2500 megabytes. Two cores were given to Spark by default in order to let the
machine usable, because it was very long and very powerful queries. 32 partitions of shuffle
instead of 200 by default.

The versions that have been used: PySpark 4.2.0, compiled against Scala 2.13, and Kafka
apache/kafka-native 4.1.1 in KRaft mode, so without any zookeeper. The Kafka connector for Spark
is `org.apache.spark:spark-sql-kafka-0-10_2.13:4.2.0`, that has been downloaded from Maven in the
beginning of the session.

Then finally, here is all the time that has been needed for this project. The job for the
preparation, 80 minutes. For the exploration, from the first question to the fifth, 27 minutes.
For the exploration, 6th question, 22 minutes. For the exploration, 7th and 8th question, 44
minutes. For the select targets, 13 minutes. For the fetch Wikipedia, 15 minutes. The enrich
Spark, 5 minutes. The streaming, 18 minutes. And the open question, 17 minutes. So in total, the
Spark batch has been around 3 hours 30 minutes.

So the volume has been 7 tables. The biggest one was title.principals with 102 million lines. Then
title.akas with 59 million lines, then name.basics with 15 million, title.basics and title.crew
with 12 million, and title.episode with a little bit less than 10 million, and finally
title.ratings with 1.7 million. More than 40 gigabytes of shuffle traffic around the pipeline, and
next to 15 gigabytes of free disk has been necessary on our computer.

So of course all these lengths of time are for a local computer in two cores mode, because when we
selected four cores the computer was unusable, so we chose to use only two cores, and they are not
the ones of a cluster. The code contains nothing that makes it unusable on a real cluster, because
it is the same Spark session and the same transformations, only the `.master()` line would have to
be changed.

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
