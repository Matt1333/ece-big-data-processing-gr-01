"""Section 4: Streaming, the producer.

Same principle as the kafka lab: we read the live stream of the Wikipedia changes and we push
every event into a kafka topic. Two differences with the lab:

  - no `since` parameter, so the stream starts at the present moment. In the lab the course file
    was replaying the past, which was fine to see the windows filling up, but here we need real
    live events to measure a real latency.
  - we follow `en.wikipedia.org` and not the french one, because our enrichment uses the english
    Wikipedia, so the pages which can match our films are the english ones.

We keep the filter wide on purpose (every edit of the english Wikipedia, around 3 to 5 per
second). The subject asks that the criteria is "sufficiently broad to guarantee that multiple
matching events are captured and processed within a 15 to 30 minute test window": we do the
narrowing to our films in spark and not here, like this the stream stays representative and we
can show how many events we saw against how many matched.
"""
import json
import os
import socket
import sys
import time
from datetime import datetime, timedelta

from confluent_kafka import Producer
from pywikibot.comms.eventstreams import EventStreams

BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP", "localhost:9092")
TOPIC = "wiki-changes"
DURATION_MIN = int(sys.argv[1]) if len(sys.argv) > 1 else 30


def main():
    producer = Producer({
        "bootstrap.servers": BOOTSTRAP,
        "client.id": socket.gethostname(),
        "compression.type": "lz4",
        "linger.ms": 50,
    })

    stream = EventStreams(streams=["recentchange"])
    stream.register_filter(server_name="en.wikipedia.org", type="edit")

    stop_time = datetime.now() + timedelta(minutes=DURATION_MIN)
    sent = 0
    print(f"producing to {TOPIC} on {BOOTSTRAP} for {DURATION_MIN} minutes")

    while datetime.now() < stop_time:
        change = next(stream)
        producer.produce(
            topic=TOPIC,
            # the page title is the key: every edit of the same page goes to the same
            # partition, so the events of one page stay in order whatever the number of
            # partitions
            key=change["title"].encode("utf-8"),
            value=json.dumps(change).encode("utf-8"),
        )
        producer.poll(0)
        sent += 1
        if sent % 100 == 0:
            print(f"  {sent} events sent, last: {change['title']}")

    producer.flush()
    producer.close()
    print(f"done, {sent} events sent")


if __name__ == "__main__":
    main()
