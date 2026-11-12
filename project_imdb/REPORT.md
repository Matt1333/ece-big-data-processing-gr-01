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
| name.basics | birthYear before 1700 | 377 | rows |
| name.basics | deathYear before birthYear | 27 | rows |
| title.basics | startYear more than 5 years in the future | 5 | rows |
| title.basics | runtimeMinutes <= 0 | 4 | rows |
| title.episode | parentTconst with no parent row | 4 | distinct keys |
| name.basics | birthYear in the future | 0 | rows |
| name.basics | birthYear not a number | 0 | rows |
| name.basics | duplicated nconst | 0 | rows |
| title.basics | endYear before startYear | 0 | rows |
| title.basics | startYear before 1870 | 0 | rows |
| title.basics | runtimeMinutes not a number | 0 | rows |
| title.basics | startYear not a number | 0 | rows |
| title.basics | duplicated tconst | 0 | rows |
| title.ratings | tconst with no parent row | 0 | distinct keys |
| title.akas | titleId with no parent row | 0 | distinct keys |
| title.crew | tconst with no parent row | 0 | distinct keys |
| title.episode | tconst with no parent row | 0 | distinct keys |
| title.principals | tconst with no parent row | 0 | distinct keys |
| title.ratings | duplicated tconst | 0 | rows |
| title.crew | duplicated tconst | 0 | rows |
| title.episode | duplicated tconst | 0 | rows |

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

To conclude on this part, the numbers, we have 39 columns measured, 22 quality controls, and 7160
lines rejected. These rejected lines come from the orphan foreign keys: 3209 orphan nconst in
title.principals, which represent 7150 lines, and 4 orphan parentTconst in title.episode, which
represent 10 lines. The other problems are not rejected but set to null. We have 377 years of
birth before 1700, 27 deaths before birth, 5 impossible years, and 4 runtimes negative or null.

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

`output/q1_runtime_outliers_per_genre/table.md`:

| genre | n_outliers | genre_avg_runtime |
|---|---|---|
| Drama | 509 | 99.00 |
| Thriller | 342 | 97.60 |
| Romance | 324 | 100.60 |
| Adventure | 294 | 95.70 |
| Comedy | 292 | 95.20 |
| Crime | 279 | 97.30 |
| Action | 250 | 103.20 |
| Horror | 215 | 90.70 |
| Biography | 167 | 95.90 |
| Western | 85 | 87.30 |
| War | 83 | 98.50 |
| Animation | 82 | 87.70 |
| Adult | 70 | 83.30 |
| History | 65 | 101.30 |
| Family | 62 | 95.80 |
| Fantasy | 61 | 96.50 |
| Sci-Fi | 57 | 93.70 |
| Musical | 41 | 102.00 |
| Sport | 35 | 95.50 |
| Music | 33 | 94.70 |
| Mystery | 29 | 96.60 |
| Documentary | 23 | 88.80 |
| News | 17 | 85.70 |
| Film-Noir | 3 | 82.70 |
| Reality-TV | 1 | 100.00 |

`output/q1_runtime_outliers_top/table.md`:

| genre | primaryTitle | startYear | runtimeMinutes | genre_avg_runtime | z_score |
|---|---|---|---|---|---|
| Comedy | London EC1 | 2015 | 5460 | 95.20 | 192.41 |
| Documentary | Logistics | 2012 | 51420 | 88.80 | 191.17 |
| Drama | Hunger! | 2015 | 6000 | 99.00 | 161.74 |
| Documentary | Ambiancé | 2020 | 43200 | 88.80 | 160.56 |
| Drama | Matrjoschka | 2006 | 5700 | 99.00 | 153.51 |
| Drama | London EC1 | 2015 | 5460 | 99.00 | 146.94 |
| Documentary | Carnets Filmés (Liste Complète) | 2019 | 28643 | 88.80 | 106.34 |
| Mystery | London EC1 | 2015 | 5460 | 96.60 | 105.08 |
| Music | The Cure for Insomnia | 1987 | 5220 | 94.70 | 84.34 |
| Drama | A 2nd generation film | 2013 | 3077 | 99.00 | 81.62 |
| Drama | The Longest Most Meaningless Movie in the World | 1970 | 2880 | 99.00 | 76.22 |
| Family | World Peace & Prayer Day | 2011 | 2400 | 95.80 | 72.21 |
| Horror | 24 Hour Psycho | 1993 | 1440 | 90.70 | 64.67 |
| Action | h36: | 2017 | 2160 | 103.20 | 62.67 |
| Comedy | Azgrab: The Documentary | 2011 | 1669 | 95.20 | 56.44 |
| Documentary | Modern Times Forever | 2011 | 14400 | 88.80 | 53.30 |
| History | Saynatakuna: Masks | 2013 | 2905 | 101.30 | 51.49 |
| Drama | A Twist of Fate | 1970 | 1970 | 99.00 | 51.28 |
| History | The Longest Most Meaningless Movie in the World | 1970 | 2880 | 101.30 | 51.03 |
| Fantasy | Burning of the Red Lotus Temple | 1928 | 1620 | 96.50 | 49.14 |

### 2.2 Top three genres per year, 1980-2025

Source: `output/q2_top3_genres_per_year/table.md`

| startYear | genre | total_votes | n_films | avg_rating | rank |
|---|---|---|---|---|---|
| 1980 | Drama | 3149142 | 1062 | 6.14 | 1 |
| 1980 | Adventure | 2474259 | 135 | 5.89 | 2 |
| 1980 | Horror | 2057360 | 143 | 5.20 | 3 |
| 1981 | Adventure | 2239899 | 151 | 6.10 | 1 |
| 1981 | Drama | 1700038 | 1018 | 6.21 | 2 |
| 1981 | Horror | 1264285 | 158 | 5.44 | 3 |
| 1982 | Drama | 3061514 | 1107 | 6.16 | 1 |
| 1982 | Sci-Fi | 2446143 | 51 | 5.48 | 2 |
| 1982 | Action | 1866135 | 292 | 5.76 | 3 |
| 1983 | Drama | 2907014 | 1130 | 6.17 | 1 |
| 1983 | Action | 2018855 | 296 | 5.67 | 2 |
| 1983 | Adventure | 1979090 | 158 | 5.70 | 3 |
| 1984 | Action | 3655955 | 289 | 5.83 | 1 |
| 1984 | Drama | 3013188 | 1112 | 6.17 | 2 |
| 1984 | Adventure | 2921423 | 143 | 5.89 | 3 |
| 1985 | Comedy | 4544735 | 617 | 5.89 | 1 |
| 1985 | Adventure | 3397376 | 148 | 5.85 | 2 |
| 1985 | Drama | 3067083 | 1069 | 6.18 | 3 |
| 1986 | Drama | 3984021 | 1124 | 6.12 | 1 |
| 1986 | Adventure | 2953968 | 161 | 5.84 | 2 |
| 1986 | Comedy | 2775235 | 625 | 5.78 | 3 |
| 1987 | Drama | 4118569 | 1223 | 6.11 | 1 |
| 1987 | Comedy | 3671369 | 621 | 5.74 | 2 |
| 1987 | Action | 2347744 | 417 | 5.48 | 3 |
| 1988 | Drama | 4447852 | 1145 | 6.11 | 1 |
| 1988 | Comedy | 4411726 | 615 | 5.80 | 2 |
| 1988 | Action | 2698832 | 438 | 5.40 | 3 |
| 1989 | Comedy | 4992922 | 661 | 5.89 | 1 |
| 1989 | Drama | 3947171 | 1191 | 6.19 | 2 |
| 1989 | Adventure | 2934726 | 166 | 5.65 | 3 |
| 1990 | Drama | 6296515 | 1158 | 6.08 | 1 |
| 1990 | Comedy | 4002606 | 622 | 5.86 | 2 |
| 1990 | Crime | 3576348 | 354 | 5.74 | 3 |
| 1991 | Drama | 5539422 | 1172 | 6.16 | 1 |
| 1991 | Crime | 3657101 | 261 | 5.93 | 2 |
| 1991 | Comedy | 3182481 | 620 | 5.91 | 3 |
| 1992 | Drama | 4906417 | 1064 | 6.19 | 1 |
| 1992 | Comedy | 4056778 | 613 | 5.85 | 2 |
| 1992 | Crime | 3598468 | 283 | 5.88 | 3 |
| 1993 | Drama | 8964212 | 1068 | 6.15 | 1 |
| 1993 | Comedy | 4481088 | 553 | 5.83 | 2 |
| 1993 | Crime | 3034272 | 287 | 5.74 | 3 |
| 1994 | Drama | 15685341 | 1120 | 6.15 | 1 |
| 1994 | Crime | 6483981 | 271 | 5.79 | 2 |
| 1994 | Comedy | 5652685 | 628 | 5.82 | 3 |
| 1995 | Drama | 12478831 | 1161 | 6.14 | 1 |
| 1995 | Crime | 7735777 | 253 | 5.85 | 2 |
| 1995 | Comedy | 6054490 | 585 | 5.92 | 3 |
| 1996 | Drama | 7834640 | 1134 | 6.22 | 1 |
| 1996 | Comedy | 4695666 | 656 | 5.91 | 2 |
| 1996 | Crime | 4427858 | 244 | 5.93 | 3 |
| 1997 | Drama | 12585945 | 1221 | 6.21 | 1 |
| 1997 | Action | 6749406 | 336 | 5.51 | 2 |
| 1997 | Comedy | 5590405 | 720 | 5.89 | 3 |
| 1998 | Drama | 11746928 | 1252 | 6.18 | 1 |
| 1998 | Comedy | 9829215 | 752 | 5.86 | 2 |
| 1998 | Crime | 6203573 | 304 | 5.93 | 3 |
| 1999 | Drama | 15462227 | 1369 | 6.15 | 1 |
| 1999 | Comedy | 8199550 | 809 | 5.78 | 2 |
| 1999 | Crime | 7156938 | 295 | 5.87 | 3 |
| 2000 | Drama | 12985466 | 1461 | 6.13 | 1 |
| 2000 | Comedy | 8312637 | 805 | 5.82 | 2 |
| 2000 | Adventure | 6961266 | 141 | 5.58 | 3 |
| 2001 | Drama | 14691996 | 1592 | 6.17 | 1 |
| 2001 | Comedy | 9482449 | 885 | 5.91 | 2 |
| 2001 | Adventure | 9217788 | 150 | 5.64 | 3 |
| 2002 | Drama | 17011517 | 1636 | 6.21 | 1 |
| 2002 | Adventure | 8661553 | 147 | 5.71 | 2 |
| 2002 | Action | 8367253 | 391 | 5.64 | 3 |
| 2003 | Drama | 13212672 | 1674 | 6.16 | 1 |
| 2003 | Action | 11676594 | 367 | 5.60 | 2 |
| 2003 | Comedy | 10728536 | 1022 | 5.92 | 3 |
| 2004 | Drama | 16433938 | 1776 | 6.21 | 1 |
| 2004 | Action | 11475251 | 411 | 5.64 | 2 |
| 2004 | Comedy | 10915077 | 1030 | 5.86 | 3 |
| 2005 | Drama | 13651473 | 1923 | 6.21 | 1 |
| 2005 | Comedy | 10163033 | 1136 | 5.90 | 2 |
| 2005 | Action | 9309870 | 388 | 5.54 | 3 |
| 2006 | Drama | 20826699 | 2187 | 6.21 | 1 |
| 2006 | Comedy | 11740614 | 1248 | 5.80 | 2 |
| 2006 | Thriller | 8640222 | 421 | 5.38 | 3 |
| 2007 | Drama | 18486744 | 2215 | 6.21 | 1 |
| 2007 | Comedy | 11682777 | 1232 | 5.84 | 2 |
| 2007 | Action | 8969972 | 433 | 5.60 | 3 |
| 2008 | Drama | 17534308 | 2476 | 6.15 | 1 |
| 2008 | Action | 13370132 | 498 | 5.46 | 2 |
| 2008 | Comedy | 11299941 | 1402 | 5.75 | 3 |
| 2009 | Drama | 17539610 | 2768 | 6.18 | 1 |
| 2009 | Comedy | 13421962 | 1543 | 5.84 | 2 |
| 2009 | Action | 12089824 | 594 | 5.55 | 3 |
| 2010 | Drama | 17507340 | 2929 | 6.21 | 1 |
| 2010 | Action | 13293003 | 672 | 5.65 | 2 |
| 2010 | Adventure | 13132555 | 335 | 6.05 | 3 |
| 2011 | Drama | 20665332 | 3151 | 6.20 | 1 |
| 2011 | Action | 17112417 | 700 | 5.75 | 2 |
| 2011 | Comedy | 13944108 | 1718 | 5.85 | 3 |
| 2012 | Drama | 20025094 | 3262 | 6.27 | 1 |
| 2012 | Action | 14473452 | 685 | 5.76 | 2 |
| 2012 | Comedy | 11720782 | 1832 | 5.86 | 3 |
| 2013 | Drama | 21833132 | 3606 | 6.24 | 1 |
| 2013 | Action | 17088722 | 771 | 5.66 | 2 |
| 2013 | Comedy | 14762998 | 1933 | 5.90 | 3 |
| 2014 | Drama | 24445260 | 3777 | 6.25 | 1 |
| 2014 | Action | 20882981 | 812 | 5.72 | 2 |
| 2014 | Adventure | 17854073 | 516 | 6.11 | 3 |
| 2015 | Drama | 20416777 | 3903 | 6.20 | 1 |
| 2015 | Action | 15566469 | 847 | 5.60 | 2 |
| 2015 | Adventure | 14118324 | 512 | 6.04 | 3 |
| 2016 | Drama | 20805703 | 3933 | 6.20 | 1 |
| 2016 | Action | 17144654 | 887 | 5.63 | 2 |
| 2016 | Adventure | 12323963 | 528 | 5.97 | 3 |
| 2017 | Drama | 20666996 | 4060 | 6.18 | 1 |
| 2017 | Action | 16647977 | 909 | 5.66 | 2 |
| 2017 | Comedy | 11259839 | 2126 | 5.80 | 3 |
| 2018 | Drama | 17334745 | 4177 | 6.14 | 1 |
| 2018 | Action | 15056468 | 888 | 5.58 | 2 |
| 2018 | Adventure | 13290535 | 506 | 5.78 | 3 |
| 2019 | Drama | 21901447 | 4241 | 6.10 | 1 |
| 2019 | Action | 12299351 | 899 | 5.61 | 2 |
| 2019 | Comedy | 12187761 | 2126 | 5.74 | 3 |
| 2020 | Drama | 10419971 | 3147 | 6.00 | 1 |
| 2020 | Comedy | 6479734 | 1547 | 5.68 | 2 |
| 2020 | Action | 6103018 | 604 | 5.47 | 3 |
| 2021 | Drama | 14303445 | 3584 | 6.08 | 1 |
| 2021 | Action | 12763606 | 825 | 5.50 | 2 |
| 2021 | Adventure | 10139737 | 403 | 5.78 | 3 |
| 2022 | Drama | 15905374 | 4102 | 6.25 | 1 |
| 2022 | Action | 13285720 | 923 | 5.67 | 2 |
| 2022 | Comedy | 10153278 | 2200 | 5.85 | 3 |
| 2023 | Drama | 14763511 | 4291 | 6.22 | 1 |
| 2023 | Action | 10517397 | 1041 | 5.81 | 2 |
| 2023 | Comedy | 9427864 | 2240 | 5.96 | 3 |
| 2024 | Drama | 11543313 | 3962 | 6.27 | 1 |
| 2024 | Action | 8591715 | 987 | 5.83 | 2 |
| 2024 | Comedy | 7034226 | 2077 | 5.86 | 3 |
| 2025 | Drama | 8420383 | 3494 | 6.40 | 1 |
| 2025 | Action | 7556647 | 929 | 5.90 | 2 |
| 2025 | Comedy | 5766354 | 1882 | 6.04 | 3 |

### 2.3 The top three compared to the other genres of the same year

Source: `output/q3_top3_vs_rest/table.md`

| startYear | top3_votes | top3_films | top3_n_genres | top3_avg_rating | rest_votes | rest_films | rest_n_genres | rest_avg_rating | top3_votes_share_pct |
|---|---|---|---|---|---|---|---|---|---|
| 1980 | 7680761 | 1340 | 3 | 5.74 | 9619712 | 2243 | 21 | 6.16 | 44.40 |
| 1981 | 5204222 | 1327 | 3 | 5.92 | 5981925 | 2341 | 20 | 6.16 | 46.50 |
| 1982 | 7373792 | 1450 | 3 | 5.80 | 9479099 | 2259 | 19 | 6.03 | 43.80 |
| 1983 | 6904959 | 1584 | 3 | 5.85 | 8142783 | 2204 | 19 | 6.01 | 45.90 |
| 1984 | 9590566 | 1544 | 3 | 5.96 | 11832089 | 2289 | 19 | 6.07 | 44.80 |
| 1985 | 11009194 | 1834 | 3 | 5.97 | 10344930 | 2046 | 19 | 6.08 | 51.60 |
| 1986 | 9713224 | 1910 | 3 | 5.91 | 11280307 | 2086 | 19 | 6.10 | 46.30 |
| 1987 | 10137682 | 2261 | 3 | 5.78 | 13622236 | 1950 | 19 | 6.05 | 42.70 |
| 1988 | 11558410 | 2198 | 3 | 5.77 | 13097118 | 2036 | 19 | 6.07 | 46.90 |
| 1989 | 11874819 | 2018 | 3 | 5.91 | 12117652 | 2353 | 19 | 6.02 | 49.50 |
| 1990 | 13875469 | 2134 | 3 | 5.89 | 16540644 | 2046 | 19 | 6.03 | 45.60 |
| 1991 | 12379004 | 2053 | 3 | 6.00 | 15607385 | 1947 | 19 | 6.00 | 44.20 |
| 1992 | 12561663 | 1960 | 3 | 5.97 | 15868694 | 1854 | 19 | 6.16 | 44.20 |
| 1993 | 16479572 | 1908 | 3 | 5.91 | 20292861 | 1842 | 19 | 6.10 | 44.80 |
| 1994 | 27822007 | 2019 | 3 | 5.92 | 19901089 | 1885 | 19 | 6.03 | 58.30 |
| 1995 | 26269098 | 1999 | 3 | 5.97 | 27302245 | 2018 | 19 | 6.11 | 49.00 |
| 1996 | 16958164 | 2034 | 3 | 6.02 | 20981489 | 1968 | 20 | 6.16 | 44.70 |
| 1997 | 24925756 | 2277 | 3 | 5.87 | 31595885 | 1966 | 19 | 6.13 | 44.10 |
| 1998 | 27779716 | 2308 | 3 | 5.99 | 26164531 | 2098 | 19 | 6.01 | 51.50 |
| 1999 | 30818715 | 2473 | 3 | 5.93 | 39840797 | 2249 | 19 | 6.02 | 43.60 |
| 2000 | 28259369 | 2407 | 3 | 5.84 | 34464560 | 2673 | 19 | 6.03 | 45.10 |
| 2001 | 33392233 | 2627 | 3 | 5.91 | 45393061 | 2851 | 19 | 6.04 | 42.40 |
| 2002 | 34040323 | 2174 | 3 | 5.85 | 46212545 | 3408 | 22 | 6.41 | 42.40 |
| 2003 | 35617802 | 3063 | 3 | 5.89 | 42628002 | 2764 | 20 | 5.98 | 45.50 |
| 2004 | 38824266 | 3217 | 3 | 5.90 | 55100132 | 3127 | 21 | 6.24 | 41.30 |
| 2005 | 33124376 | 3447 | 3 | 5.88 | 48213466 | 3524 | 21 | 6.19 | 40.70 |
| 2006 | 41207535 | 3856 | 3 | 5.80 | 55290494 | 4078 | 20 | 6.18 | 42.70 |
| 2007 | 39139493 | 3880 | 3 | 5.88 | 62952316 | 4450 | 21 | 6.05 | 38.30 |
| 2008 | 42204381 | 4376 | 3 | 5.79 | 62233265 | 4979 | 20 | 6.05 | 40.40 |
| 2009 | 43051396 | 4905 | 3 | 5.86 | 61022079 | 5671 | 20 | 6.11 | 41.40 |
| 2010 | 43932898 | 3936 | 3 | 5.97 | 65965956 | 7671 | 21 | 6.03 | 40.00 |
| 2011 | 51721857 | 5569 | 3 | 5.93 | 60418776 | 7024 | 21 | 6.23 | 46.10 |
| 2012 | 46219328 | 5779 | 3 | 5.96 | 63420411 | 7571 | 21 | 6.14 | 42.20 |
| 2013 | 53684852 | 6310 | 3 | 5.93 | 75932454 | 8503 | 20 | 6.15 | 41.40 |
| 2014 | 63182314 | 5105 | 3 | 6.03 | 70621797 | 11006 | 23 | 6.62 | 47.20 |
| 2015 | 50101570 | 5262 | 3 | 5.95 | 57236893 | 10862 | 21 | 6.22 | 46.70 |
| 2016 | 50274320 | 5348 | 3 | 5.93 | 63712501 | 10923 | 21 | 6.25 | 44.10 |
| 2017 | 48574812 | 7095 | 3 | 5.88 | 59268061 | 9431 | 22 | 6.23 | 45.00 |
| 2018 | 45681748 | 5571 | 3 | 5.83 | 57367842 | 11161 | 22 | 6.09 | 44.30 |
| 2019 | 46388559 | 7266 | 3 | 5.82 | 58146095 | 9641 | 22 | 6.04 | 44.40 |
| 2020 | 23002723 | 5298 | 3 | 5.72 | 28157047 | 7767 | 21 | 6.00 | 45.00 |
| 2021 | 37206788 | 4812 | 3 | 5.79 | 42907240 | 9742 | 22 | 5.95 | 46.40 |
| 2022 | 39344372 | 7225 | 3 | 5.92 | 45699896 | 9741 | 22 | 6.34 | 46.30 |
| 2023 | 34708772 | 7572 | 3 | 6.00 | 42567821 | 9719 | 22 | 6.16 | 44.90 |
| 2024 | 27169254 | 7026 | 3 | 5.99 | 36052166 | 9661 | 23 | 6.33 | 43.00 |
| 2025 | 21743384 | 6305 | 3 | 6.11 | 33103263 | 8656 | 22 | 6.43 | 39.60 |

### 2.4 Directors with one film >= 8.0 and several others averaging <= 6.0

Source: `output/q4_one_hit_directors/table.md`

| primaryName | n_films | hit_rating | n_others | avg_rating_others |
|---|---|---|---|---|
| William Beaudine | 145 | 8.20 | 144 | 5.85 |
| Richard Thorpe | 114 | 8.10 | 113 | 5.86 |
| Alfredo B. Crevenna | 113 | 8.30 | 112 | 5.66 |
| Raoul Walsh | 108 | 8.10 | 107 | 5.93 |
| Franz Antel | 75 | 8.10 | 74 | 5.21 |
| Arthur Maria Rabenalt | 58 | 8.00 | 57 | 5.70 |
| Houssam El-Din Mustafa | 56 | 8.30 | 55 | 5.55 |
| Carmine Gallone | 55 | 8.10 | 54 | 5.86 |
| Tulio Demicheli | 51 | 8.00 | 50 | 5.94 |
| Rizal Mantovani | 50 | 9.00 | 49 | 5.42 |
| Sidney Salkow | 50 | 8.10 | 49 | 5.96 |
| Wai Keung Lau | 48 | 8.00 | 47 | 5.71 |
| Ramón Torrado | 47 | 8.00 | 46 | 5.66 |
| Hasan El-Emam | 46 | 8.10 | 45 | 5.69 |
| Alfred Vohrer | 45 | 8.60 | 44 | 5.95 |
| Yōjirō Takita | 44 | 8.00 | 43 | 5.59 |
| Hisayasu Satō | 44 | 8.00 | 43 | 5.79 |
| Viktor Tourjansky | 44 | 8.20 | 43 | 5.97 |
| A. Razak Mohaideen | 42 | 8.20 | 41 | 5.00 |
| Javier Aguirre | 40 | 8.10 | 39 | 5.06 |

### 2.5 Series whose worst episode is in the last season and best episode in the first two

Source: `output/q5_series_going_downhill/table.md`

| primaryTitle | startYear | last_season | best_season | best_rating | worst_season | worst_rating | rating_drop |
|---|---|---|---|---|---|---|---|
| The Queen of Flow | 2018 | 3 | 1 | 9.80 | 3 | 1.10 | 8.70 |
| One Punch Man | 2015 | 3 | 1 | 9.50 | 3 | 1.60 | 7.90 |
| The Gumby Show | 1956 | 3 | 1 | 8.10 | 3 | 1.00 | 7.10 |
| Rainbow High | 2020 | 6 | 2 | 9.40 | 6 | 2.30 | 7.10 |
| All Dogs Go to Heaven: The Series | 1996 | 3 | 2 | 9.20 | 3 | 2.60 | 6.60 |
| Family Law | 1999 | 3 | 2 | 9.40 | 3 | 2.80 | 6.60 |
| Margarita | 2024 | 3 | 1 | 9.40 | 3 | 3.10 | 6.30 |
| Soy Luna | 2016 | 4 | 2 | 9.10 | 4 | 3.00 | 6.10 |
| The Parrot Show | 2024 | 5 | 1 | 9.30 | 5 | 3.30 | 6.00 |
| Leaf Cast | 2006 | 5 | 1 | 8.30 | 5 | 2.40 | 5.90 |
| Love Is Blind: Sweden | 2024 | 3 | 2 | 7.70 | 3 | 1.90 | 5.80 |
| The Flash | 2014 | 9 | 1 | 9.60 | 9 | 3.80 | 5.80 |
| Rykter | 2022 | 4 | 2 | 9.20 | 4 | 3.40 | 5.80 |
| Bloodline | 2015 | 3 | 1 | 9.10 | 3 | 3.60 | 5.50 |
| 7vs.Wild | 2021 | 5 | 2 | 8.80 | 5 | 3.50 | 5.30 |
| Your Favorite Martian | 2010 | 3 | 2 | 9.20 | 3 | 4.00 | 5.20 |
| Kaverille ei jätetä | 1999 | 3 | 2 | 8.30 | 3 | 3.20 | 5.10 |
| Honey, I Shrunk the Kids: The TV Show | 1997 | 3 | 1 | 7.50 | 3 | 2.50 | 5.00 |
| Forræder | 2022 | 6 | 2 | 9.60 | 6 | 4.80 | 4.80 |
| Larva | 2011 | 4 | 2 | 9.60 | 4 | 4.80 | 4.80 |

### 2.6 Actors successful in several languages

Sources: `output/q6_actors_2plus_languages/table.md`, `output/q6_actors_3plus_languages/table.md`

`output/q6_actors_2plus_languages/table.md`:

| primaryName | n_languages | languages |
|---|---|---|
| Aishwarya Rai Bachchan | 7 | bn, en, fr, hi, ja, ta, tr |
| Anne Parillaud | 7 | ca, en, es, fr, hi, ja, tr |
| Monica Bellucci | 7 | bn, en, es, fr, hi, ml, tr |
| Nikolay Grinko | 7 | az, bg, en, ru, sk, uk, uz |
| Alain Lathière | 6 | ca, en, es, fr, hi, tr |
| Bruno Randon | 6 | ca, en, es, fr, hi, tr |
| Deepika Padukone | 6 | en, es, fr, hi, ja, tr |
| Helene Aligier | 6 | ca, en, es, fr, hi, tr |
| Jacques Boudet | 6 | ca, en, es, fr, hi, tr |
| Laura Chéron | 6 | ca, en, es, fr, hi, tr |
| Luis Zahera | 6 | en, es, fr, hi, ja, tr |
| Mammootty | 6 | en, fr, hi, ja, ml, ta |
| Manolo Solo | 6 | en, es, fr, hi, ja, tr |
| Marc Duret | 6 | ca, en, es, fr, hi, tr |
| Okan Yalabık | 6 | en, fr, hi, ja, th, tr |
| Patrick Fontana | 6 | ca, en, es, fr, hi, tr |
| Patrick Pérez | 6 | ca, en, es, fr, hi, tr |
| Pierre-Alain de Garrigues | 6 | ca, en, es, fr, hi, tr |
| Toni Servillo | 6 | ca, en, fr, he, sv, tr |
| Ulrich Tukur | 6 | de, en, fr, he, sv, tr |

`output/q6_actors_3plus_languages/table.md`:

| primaryName | n_languages | languages |
|---|---|---|
| Aishwarya Rai Bachchan | 7 | bn, en, fr, hi, ja, ta, tr |
| Anne Parillaud | 7 | ca, en, es, fr, hi, ja, tr |
| Monica Bellucci | 7 | bn, en, es, fr, hi, ml, tr |
| Nikolay Grinko | 7 | az, bg, en, ru, sk, uk, uz |
| Alain Lathière | 6 | ca, en, es, fr, hi, tr |
| Bruno Randon | 6 | ca, en, es, fr, hi, tr |
| Deepika Padukone | 6 | en, es, fr, hi, ja, tr |
| Helene Aligier | 6 | ca, en, es, fr, hi, tr |
| Jacques Boudet | 6 | ca, en, es, fr, hi, tr |
| Laura Chéron | 6 | ca, en, es, fr, hi, tr |
| Luis Zahera | 6 | en, es, fr, hi, ja, tr |
| Mammootty | 6 | en, fr, hi, ja, ml, ta |
| Manolo Solo | 6 | en, es, fr, hi, ja, tr |
| Marc Duret | 6 | ca, en, es, fr, hi, tr |
| Okan Yalabık | 6 | en, fr, hi, ja, th, tr |
| Patrick Fontana | 6 | ca, en, es, fr, hi, tr |
| Patrick Pérez | 6 | ca, en, es, fr, hi, tr |
| Pierre-Alain de Garrigues | 6 | ca, en, es, fr, hi, tr |
| Toni Servillo | 6 | ca, en, fr, he, sv, tr |
| Ulrich Tukur | 6 | de, en, fr, he, sv, tr |

### 2.7 Actors with a 20+ year career whose popularity peaked early

Source: `output/q7_early_peak_actors/table.md`

| primaryName | first_year | last_year | n_films | first_n_films | first_avg_rating | second_n_films | second_avg_rating | drop |
|---|---|---|---|---|---|---|---|---|
| Tom Savini | 1977 | 2015 | 20 | 7 | 6.13 | 13 | 3.16 | 2.97 |
| Dev Anand | 1951 | 2003 | 41 | 34 | 7.11 | 7 | 4.16 | 2.95 |
| Akbar Abdi | 1987 | 2023 | 40 | 14 | 6.46 | 26 | 3.68 | 2.78 |
| Reza Naji | 1997 | 2025 | 18 | 5 | 7.30 | 13 | 4.52 | 2.78 |
| Caroline Munro | 1972 | 2020 | 19 | 13 | 5.59 | 6 | 2.82 | 2.77 |
| Sumalatha | 1980 | 2023 | 25 | 19 | 7.24 | 6 | 4.65 | 2.59 |
| Ulli Lommel | 1964 | 2020 | 25 | 19 | 5.64 | 6 | 3.10 | 2.54 |
| Rekha | 1986 | 2026 | 28 | 14 | 7.34 | 14 | 4.89 | 2.45 |
| András Kern | 1973 | 2016 | 22 | 13 | 7.21 | 9 | 4.84 | 2.37 |
| Raju Shrestha | 1972 | 2012 | 16 | 11 | 7.00 | 5 | 4.64 | 2.36 |
| Martin Dejdar | 1987 | 2020 | 15 | 9 | 6.31 | 6 | 4.05 | 2.26 |
| Kaviyoor Ponnamma | 1973 | 2021 | 45 | 28 | 7.69 | 17 | 5.44 | 2.25 |
| Mikhail Boyarskiy | 1976 | 2025 | 20 | 7 | 6.63 | 13 | 4.38 | 2.25 |
| Johny | 1984 | 2022 | 17 | 10 | 7.10 | 7 | 4.86 | 2.24 |
| Seema | 1980 | 2019 | 23 | 15 | 7.26 | 8 | 5.05 | 2.21 |
| Shobha Khote | 1955 | 2022 | 27 | 18 | 6.73 | 9 | 4.56 | 2.17 |
| Virginia Mayo | 1943 | 1997 | 48 | 43 | 6.20 | 5 | 4.08 | 2.12 |
| Helen | 1957 | 2012 | 55 | 47 | 6.62 | 8 | 4.51 | 2.11 |
| Nandamuri Balakrishna | 1984 | 2025 | 46 | 20 | 6.41 | 26 | 4.32 | 2.09 |
| Mukhyamantri Chandru | 1987 | 2023 | 16 | 10 | 7.99 | 6 | 5.92 | 2.07 |

### 2.8 Multi-talented film professionals

Sources: `output/q8_multi_talented/table.md`, `output/q8_multi_role_vs_single_role/table.md`

`output/q8_multi_talented/table.md`:

| primaryName | n_roles | roles | n_films | avg_rating |
|---|---|---|---|---|
| Nassar | 3 | actor+director+writer | 352 | 6.17 |
| Tanikella Bharani | 3 | actor+director+writer | 333 | 6.16 |
| Anupam Kher | 3 | actor+director+writer | 314 | 5.58 |
| Prakash Raj | 3 | actor+director+writer | 308 | 6.14 |
| Ron Jeremy | 3 | actor+director+writer | 294 | 5.82 |
| Govardhan Asrani | 3 | actor+director+writer | 266 | 5.66 |
| Cüneyt Arkın | 3 | actor+director+writer | 261 | 5.32 |
| Nedumudi Venu | 3 | actor+director+writer | 241 | 6.34 |
| Jing Wong | 3 | actor+director+writer | 219 | 5.66 |
| Eric Tsang | 3 | actor+director+writer | 199 | 5.65 |
| Sadhu Kokila | 3 | actor+director+writer | 198 | 6.39 |
| Jesús Franco | 3 | actor+director+writer | 193 | 4.88 |
| Joey Silvera | 3 | actor+director+writer | 187 | 5.88 |
| Osman F. Seden | 3 | actor+director+writer | 183 | 5.73 |
| Paul Thomas | 3 | actor+director+writer | 180 | 6.01 |
| Gérard Depardieu | 3 | actor+director+writer | 177 | 6.01 |
| Salim Kumar | 3 | actor+director+writer | 176 | 5.37 |
| Anthony Chau-Sang Wong | 3 | actor+director+writer | 171 | 5.88 |
| René Cardona | 3 | actor+director+writer | 170 | 6.02 |
| Fernando Fernán Gómez | 3 | actor+director+writer | 165 | 5.93 |

`output/q8_multi_role_vs_single_role/table.md`:

| multi_role | n_films | avg_rating |
|---|---|---|
| False | 365064 | 5.92 |
| True | 107388 | 5.96 |

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

| year_min | year_max | top_n_per_genre_per_year | principals_per_film | min_votes | n_films | n_people |
|---|---|---|---|---|---|---|
| 1980 | 2025 | 10 | 3 | 1000 | 6256 | 10557 |

### 3.2 Coverage

Source: `output/e2_enrichment_coverage/table.md`

| n_films | n_with_synopsis | pct_with_synopsis | n_principals | n_principals_with_bio | avg_synopsis_length |
|---|---|---|---|---|---|
| 6256 | 5828 | 93.20 | 18140 | 15057 | 898.00 |

### 3.3 Why some records could not be enriched

Source: `output/e3_missing_reasons/table.md`

| synopsis_note | n_films |
|---|---|
| no english wikipedia article linked to this imdb id in wikidata | 427 |
| extract too short to be a usable summary | 1 |

### 3.4 Sample of enriched records

Source: `output/e4_sample/table.md`

| primaryTitle | startYear | averageRating | synopsis_start | synopsis_source_url | n_principals_with_bio |
|---|---|---|---|---|---|
| The Shawshank Redemption | 1994 | 9.30 | The Shawshank Redemption is a 1994 American drama film written and directed by Frank Darabont, based on the 1982 Stephen King novella Rita Hayworth and Shawshank Redemption. The film tells the story of banker Andy Dufresne (Tim Robbins), wh | https://en.wikipedia.org/wiki/The_Shawshank_Redemption | 3 |
| The Dark Knight | 2008 | 9.10 | The Dark Knight is a 2008 superhero film directed by Christopher Nolan, who co-wrote the screenplay with his brother Jonathan. Based on the DC Comics superhero Batman, it is the sequel to Batman Begins (2005), and the second installment in  | https://en.wikipedia.org/wiki/The_Dark_Knight | 3 |
| Inception | 2010 | 8.80 | Inception is a 2010 science fiction heist film written and directed by Christopher Nolan, who also produced it with his wife Emma Thomas. The film stars Leonardo DiCaprio as a professional thief who steals information by infiltrating his ta | https://en.wikipedia.org/wiki/Inception | 3 |
| Fight Club | 1999 | 8.80 | Fight Club is a 1999 American film directed by David Fincher starring Brad Pitt, Edward Norton, and Helena Bonham Carter. It is based on the 1996 novel Fight Club by Chuck Palahniuk. Norton plays the unnamed narrator, who is discontented wi | https://en.wikipedia.org/wiki/Fight_Club | 3 |
| Interstellar | 2014 | 8.70 | Interstellar is a 2014 epic science fiction drama film directed by Christopher Nolan, who co-wrote the screenplay with his brother, Jonathan Nolan. It features an ensemble cast led by Matthew McConaughey, Anne Hathaway, Jessica Chastain, Bi | https://en.wikipedia.org/wiki/Interstellar_(film) | 3 |
| Forrest Gump | 1994 | 8.80 | Forrest Gump is a 1994 American comedy-drama film directed by Robert Zemeckis. An adaptation of the 1986 novel of the same name by Winston Groom, the film's screenplay was written by Eric Roth. It stars Tom Hanks in the title role, alongsid | https://en.wikipedia.org/wiki/Forrest_Gump | 3 |
| Pulp Fiction | 1994 | 8.80 | Pulp Fiction is a 1994 American crime film written and directed by Quentin Tarantino from a story he conceived with Roger Avary. It tells four intertwining tales of crime and violence in Los Angeles. The film stars John Travolta, Samuel L.  | https://en.wikipedia.org/wiki/Pulp_Fiction | 3 |
| The Matrix | 1999 | 8.70 | The Matrix is a 1999 science fiction–action film written and directed by the Wachowskis. The first installment in the Matrix film series, it stars Keanu Reeves, Laurence Fishburne, Carrie-Anne Moss, Hugo Weaving, and Joe Pantoliano. The fil | https://en.wikipedia.org/wiki/The_Matrix | 3 |
| The Lord of the Rings: The Fellowship of the Ring | 2001 | 8.90 | The Lord of the Rings: The Fellowship of the Ring is a 2001 epic fantasy film directed by Peter Jackson from a screenplay by Fran Walsh, Philippa Boyens, and Jackson. It is based on J. R. R. Tolkien's 1954 The Fellowship of the Ring, the fi | https://en.wikipedia.org/wiki/The_Lord_of_the_Rings:_The_Fellowship_of_the_Ring | 3 |
| The Lord of the Rings: The Return of the King | 2003 | 9.00 | The Lord of the Rings: The Return of the King is a 2003 epic fantasy film directed by Peter Jackson from a screenplay he wrote with Fran Walsh and Philippa Boyens. It is based on 1955's The Return of the King, the third volume of the novel  | https://en.wikipedia.org/wiki/The_Lord_of_the_Rings:_The_Return_of_the_King | 3 |

### Methodological explanation - Data enrichment

IMDb has no summary and no bio so we decided to choose Wikipedia. The advantage is that it is an open model with content written by humans and under a free licence. Instead of using an AI to generate summaries which was completely forbidden in the subject,so we took directly the raw text of the introduction. And we did a minimal processing,in fact we just replaced the line breaks with spaces and we removed the texts of less than 50 characters.
We chose the English version of Wikipedia which lets us reach about 93.2% of global coverage.In the sample we looked at the missing ones are mostly Asian and Turkish cinema and Japanese animation.

To link a film to its Wikipedia article,doing a search just by the title would have been complicated with all the homonyms and the remakes. So we went through Wikidata by looking for the property P345 which is the unique IMDb identifier and this guarantees an exact match. 
And to avoid overloading the network we grouped the identifiers in batches of 300 in the SPARQL queries. This is how we saw that 427 films had no English article linked on Wikidata.

To respect the good practices of the APIs and to avoid HTML scraping we did everything in series and never in parallel with a pause of one second between each SPARQL query and of 0.3 second for Wikipedia. 
On the volume side we process by batches of 300 identifiers for SPARQL and of 20 articles per call. 
About the differents limits and the evolution of the code: 

- for the User-Agent:the contact was not there during the first download so we added it after the review to be in line with the instructions. 
- for the error handling:at the beginning the script retried in case of error even on 400 or 404 errors which were going to fail again anyway. 
  So we fixed it to target only the temporary errors, so 429 and 5xx, by following the Retry-After header.

About the resume of the download it restarts by type of data and not by batch since the final file is written only once when all the processing is finished.

To manage the traceability of the summaries and the bios each record contains 4 metadata:

- source_url,
- wikidata_uri
- source_name and retrieved_at. 

It is essential to check the source to date the extraction and to respect the authors with the CC BY-SA licence. It is in particular by reading the code again and by coming across the particular case of Face/Off that we spotted a bug with the "/" in the URLs. 
Frost/Nixon showed the same problem and by measuring then on the data we saw that it affected 18 URLs(17 films and one person:David France). 
Concretely, for 8 URLsthe system got the text of another article without showing any errors: Frost/Nixon for example ended up with the summary of Nixon. 
And for the 10 other URLs we got no text at all. This is actually where the missing introductions came from. 
Finally this traceability through source_url let us see exactly what was not working and so fix the code and run a clean extraction again.

When an information is missing the text field stays empty (null) and we always put a note to explain why.For example: "no english wikipedia article linked" (for 427 films),"extract too short" (for one film:Pardon) and "not downloaded in this run". 
About the concrete results for the synopses we got 5,828 out of the 6,256 targeted films which makes 93.2% of coverage.
And for the biographies we got 15,057 out of a total of 18,140 targeted slots which correspond to 10,557 distinct people.

The architecture of the project lets us adapt the volume of processing by simply changing the constants: the years, the top N or the number of principals, directly at the top of the Python script "04a_select_targets.py".
All the part of data selection and joins is entirely done by Spark. There is only the download phase that is done outside Spark and this component works by batches and handles the resume with only one constraint: the execution time logically grows with the number of requests so with the number of films to process.

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
many things. We can't separate it from the film without losing some real matches. 8 of the 25, so
one third of the sample, so the 2.81% is an upper bound and not a measure.

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
second and the maximum is 1 second. We have no negative value. The lag that we've measured is
between 0 and 1 second. The watermark is at 10 minutes, so none of the events can be this late to
be rejected.

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

`output/o4_summary/table.md`:

| n_duos | n_duos_better_together | n_duos_worse_together | n_duos_equal | avg_lift | median_lift | avg_rating_together | avg_rating_apart |
|---|---|---|---|---|---|---|---|
| 1429 | 979 | 430 | 20 | 0.22 | 0.23 | 6.70 | 6.48 |

`output/o1_best_duos/table.md`:

| director_name | actor_name | films_together | first_year | last_year | together_avg | director_apart_avg | actor_apart_avg | apart_avg | lift |
|---|---|---|---|---|---|---|---|---|---|
| Mehmet Ada Öztekin | Sarp Akkaya | 3 | 2021 | 2024 | 8.17 | 6.68 | 4.53 | 5.61 | 2.56 |
| Peter Jackson | Elijah Wood | 3 | 2001 | 2003 | 8.90 | 7.38 | 6.09 | 6.74 | 2.16 |
| Francis Ford Coppola | Al Pacino | 3 | 1972 | 1990 | 8.57 | 6.29 | 6.61 | 6.45 | 2.12 |
| Ertem Eğilmez | Halit Akçatepe | 6 | 1973 | 1977 | 8.50 | 7.59 | 5.43 | 6.51 | 1.99 |
| K. Selvaraghavan | Sonia Agarwal | 3 | 2003 | 2006 | 8.10 | 6.70 | 5.53 | 6.12 | 1.98 |
| Rajkumar Santoshi | Meenakshi Sheshadri | 3 | 1990 | 1996 | 7.70 | 6.41 | 5.10 | 5.75 | 1.95 |
| M. Rajesh | Santhanam | 3 | 2009 | 2012 | 6.93 | 4.23 | 5.73 | 4.98 | 1.95 |
| James Cameron | Michael Biehn | 3 | 1984 | 1989 | 8.00 | 7.09 | 5.23 | 6.16 | 1.84 |
| Robert Zemeckis | Christopher Lloyd | 3 | 1985 | 1990 | 7.90 | 6.85 | 5.51 | 6.18 | 1.72 |
| Anthony Russo | Robert Downey Jr. | 3 | 2016 | 2019 | 8.20 | 6.43 | 6.52 | 6.48 | 1.72 |
| Joe Russo | Robert Downey Jr. | 3 | 2016 | 2019 | 8.20 | 6.43 | 6.52 | 6.48 | 1.72 |
| Rajkumar Hirani | Sanjay Dutt | 3 | 2003 | 2014 | 8.10 | 7.50 | 5.33 | 6.41 | 1.69 |
| Karan Johar | Kajol | 3 | 1998 | 2010 | 7.63 | 5.89 | 6.05 | 5.97 | 1.66 |
| Francis Ford Coppola | Robert Duvall | 3 | 1969 | 1979 | 8.07 | 6.35 | 6.47 | 6.41 | 1.66 |
| Quentin Tarantino | Uma Thurman | 3 | 1994 | 2004 | 8.33 | 7.58 | 5.93 | 6.75 | 1.58 |
| Gareth Evans | Iko Uwais | 3 | 2009 | 2014 | 7.40 | 5.97 | 5.67 | 5.82 | 1.58 |
| Richard Linklater | Julie Delpy | 3 | 1995 | 2013 | 8.03 | 6.85 | 6.14 | 6.50 | 1.53 |
| Hansal Mehta | Rajkummar Rao | 5 | 2012 | 2020 | 7.38 | 5.45 | 6.34 | 5.90 | 1.49 |
| James Cameron | Arnold Schwarzenegger | 3 | 1984 | 1994 | 8.00 | 7.09 | 5.94 | 6.52 | 1.48 |
| Mohan Raja | Ravi Mohan | 4 | 2004 | 2015 | 7.57 | 6.13 | 6.06 | 6.10 | 1.47 |

`output/o2_worst_duos/table.md`:

| director_name | actor_name | films_together | first_year | last_year | together_avg | director_apart_avg | actor_apart_avg | apart_avg | lift |
|---|---|---|---|---|---|---|---|---|---|
| Kartal Tibet | Halit Akçatepe | 3 | 1985 | 2004 | 5.43 | 6.63 | 8.50 | 7.56 | -2.13 |
| George Gallo | Morgan Freeman | 3 | 2019 | 2021 | 4.53 | 5.99 | 6.55 | 6.27 | -1.74 |
| Prabhu Deva | Salman Khan | 3 | 2009 | 2021 | 3.80 | 5.58 | 5.50 | 5.54 | -1.74 |
| Giovanni Storti | Giacomo Poretti | 3 | 2002 | 2016 | 5.17 | 7.30 | 6.30 | 6.80 | -1.63 |
| Aldo Baglio | Giacomo Poretti | 3 | 2002 | 2016 | 5.17 | 7.30 | 6.30 | 6.80 | -1.63 |
| Matt Eskandari | Bruce Willis | 4 | 2019 | 2022 | 3.70 | 5.13 | 5.45 | 5.29 | -1.59 |
| David Dhawan | Varun Dhawan | 4 | 2014 | 2026 | 4.25 | 5.60 | 5.93 | 5.77 | -1.52 |
| Albert Pyun | Ice-T | 3 | 1997 | 2000 | 3.33 | 4.24 | 5.46 | 4.85 | -1.52 |
| Rohit Shetty | Ranveer Singh | 3 | 2018 | 2024 | 4.67 | 5.86 | 6.49 | 6.18 | -1.51 |
| Neri Parenti | Christian De Sica | 11 | 1998 | 2008 | 4.29 | 5.98 | 5.44 | 5.71 | -1.42 |
| Kôbun Shizuno | Takahiro Sakurai | 3 | 2017 | 2018 | 5.63 | 6.70 | 7.39 | 7.05 | -1.42 |
| Sidney J. Furie | Louis Gossett Jr. | 3 | 1986 | 1995 | 4.30 | 5.70 | 5.67 | 5.68 | -1.38 |
| James Huth | Jean Dujardin | 3 | 2005 | 2016 | 4.77 | 5.78 | 6.44 | 6.11 | -1.34 |
| Vikram Bhatt | Emraan Hashmi | 3 | 2012 | 2016 | 4.17 | 5.06 | 5.94 | 5.50 | -1.33 |
| Kôbun Shizuno | Kana Hanazawa | 3 | 2017 | 2018 | 5.63 | 6.70 | 7.21 | 6.95 | -1.32 |
| Patryk Vega | Agnieszka Dygant | 3 | 2017 | 2019 | 4.17 | 5.02 | 5.90 | 5.46 | -1.29 |
| Fumihiko Sori | Tsubasa Honda | 3 | 2017 | 2022 | 5.40 | 6.48 | 6.87 | 6.67 | -1.27 |
| Michael Almereyda | Ethan Hawke | 3 | 2000 | 2020 | 4.90 | 5.72 | 6.60 | 6.16 | -1.26 |
| William Beaudine | Bela Lugosi | 3 | 1943 | 1952 | 4.43 | 5.63 | 5.75 | 5.69 | -1.26 |
| Aldo Baglio | Giovanni Storti | 3 | 1998 | 2016 | 5.33 | 7.13 | 6.00 | 6.57 | -1.24 |

`output/o3_most_prolific_duos/table.md`:

| director_name | actor_name | films_together | first_year | last_year | together_avg | director_apart_avg | actor_apart_avg | apart_avg | lift |
|---|---|---|---|---|---|---|---|---|---|
| Kartal Tibet | Kemal Sunal | 26 | 1976 | 1990 | 6.91 | 5.40 | 7.33 | 6.37 | 0.54 |
| Gerald Thomas | Sidney James | 21 | 1960 | 1974 | 6.27 | 5.45 | 6.83 | 6.14 | 0.13 |
| David Dhawan | Govinda | 16 | 1990 | 2009 | 6.00 | 4.95 | 5.53 | 5.24 | 0.76 |
| Akira Kurosawa | Toshirō Mifune | 16 | 1948 | 1965 | 7.81 | 7.29 | 7.16 | 7.23 | 0.58 |
| Priyadarshan | Mohanlal | 15 | 1985 | 2021 | 7.51 | 6.61 | 6.88 | 6.75 | 0.76 |
| John Ford | John Wayne | 14 | 1939 | 1963 | 7.26 | 6.90 | 6.59 | 6.74 | 0.52 |
| Erik Balling | Ove Sprogøe | 13 | 1968 | 1981 | 6.94 | 6.87 | 5.97 | 6.42 | 0.52 |
| Neri Parenti | Paolo Villaggio | 13 | 1980 | 1996 | 5.98 | 4.29 | 6.63 | 5.46 | 0.52 |
| Terence Fisher | Peter Cushing | 13 | 1957 | 1974 | 6.48 | 6.28 | 5.91 | 6.09 | 0.39 |
| Rohit Shetty | Ajay Devgn | 12 | 2003 | 2024 | 5.76 | 5.28 | 5.92 | 5.60 | 0.16 |
| Woody Allen | Mia Farrow | 11 | 1982 | 1992 | 7.16 | 6.86 | 6.23 | 6.54 | 0.62 |
| Roy William Neill | Basil Rathbone | 11 | 1942 | 1946 | 6.83 | 6.70 | 6.52 | 6.61 | 0.22 |
| Roy William Neill | Nigel Bruce | 11 | 1942 | 1946 | 6.83 | 6.70 | 7.08 | 6.89 | -0.06 |
| Henry King | Tyrone Power | 11 | 1936 | 1957 | 6.61 | 6.81 | 6.93 | 6.87 | -0.26 |
| Neri Parenti | Christian De Sica | 11 | 1998 | 2008 | 4.29 | 5.98 | 5.44 | 5.71 | -1.42 |
| Natuk Baytan | Kemal Sunal | 10 | 1976 | 1986 | 7.48 | 6.10 | 7.14 | 6.62 | 0.86 |
| Martin Scorsese | Robert De Niro | 10 | 1973 | 2023 | 7.73 | 7.41 | 6.42 | 6.91 | 0.82 |
| Michael Curtiz | Errol Flynn | 10 | 1935 | 1941 | 7.01 | 6.81 | 6.78 | 6.79 | 0.22 |
| Claude Chabrol | Stéphane Audran | 10 | 1960 | 1992 | 7.00 | 6.71 | 6.90 | 6.81 | 0.19 |
| Ertem Eğilmez | Münir Özkul | 10 | 1972 | 1979 | 7.88 | 7.83 | 7.67 | 7.75 | 0.13 |

`output/o5_lift_by_number_of_films/table.md`:

| films_together_bucket | n_duos | avg_lift | avg_rating_together |
|---|---|---|---|
| 3 | 845 | 0.23 | 6.69 |
| 4-5 | 440 | 0.21 | 6.71 |
| 6-9 | 121 | 0.20 | 6.69 |
| 10+ | 23 | 0.24 | 6.74 |

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
preparation, 1 hour and 49 minutes. For the exploration, from the first question to the fifth, 27
minutes. For the exploration, 6th question, 22 minutes. For the exploration, 7th and 8th question,
44 minutes. For the select targets, 13 minutes. For the fetch Wikipedia, 15 minutes. The enrich
Spark, 5 minutes. The streaming, 18 minutes. And the open question, 17 minutes. So in total, the
Spark batch has been around 3 hours and 57 minutes. So why 3 hours and 57 minutes? It's because
the total excludes the Wikipedia fetch and also the streaming, because they are not Spark batch
jobs: one is waiting for the network to answer, and the other is waiting for the stream. The
cleaning of the preparation, 38 minutes. The reconstruction of the table from parquet, 42 seconds.

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
