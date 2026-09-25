# ECE Big Data Processing – Fall 2026

- Group: gr-01
- lab/project member 1: TOUVRON Erwan, `erwan-oss`
- lab/project member 2: PINTO Kylian, `Kycks912004`
- lab/project member 3: DAVIDSON Matt, `Matt1333`

## Contents

| Folder | Lab |
|---|---|
| `lab1_rdd_word_count/` | Lab 1 – Word count with RDDs (*Around the World in 80 Days*, EN vs FR) |
| `lab2_sparksql_dataframes/` | Lab 2 – Structured data analysis with DataFrames and SparkSQL (NYC TLC taxi data) |
| `lab3_kafka/` | Lab 3 – Kafka producer/topic/consumer with `confluent_kafka` (*Around the World in 80 Days* streamed line by line) |

## Note about lab 2

Our apologies: the lab 2 notebook was uploaded at some point as a file without its `.ipynb`
extension, so GitHub showed it as raw text instead of rendering it as a notebook. This was a
mistake on our side when re-uploading the file through the GitHub web interface, not an attempt
to submit a text file. The extension has been restored and the notebook renders correctly again.
The content itself was never changed. Sorry for the inconvenience.

Notebooks are written for Google Colab / the `quay.io/jupyter/pyspark-notebook` Docker image.
Lab 3 runs locally and needs a Kafka broker: `docker run -d --rm --name kafka_lab -p 9092:9092 apache/kafka-native:4.1.1`.
