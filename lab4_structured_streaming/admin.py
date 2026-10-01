# %%
from confluent_kafka.admin import AdminClient, NewTopic

# %%
config =  {
  'bootstrap.servers': 'localhost:9092',
}

admin_client = AdminClient(config)

# %%
topic='wikistreams'
# create_topics is asynchronous : in a script the process finish before the request is even
# sent, so the topic is never created and we don't even get an error. We wait for the future
# so the creation really happens.
for t, fut in admin_client.create_topics(
    [NewTopic(topic, num_partitions=1, replication_factor=1)]
).items():
  try:
    fut.result()
    print(f'topic {t} created')
  except Exception as e:
    print(f'topic {t}: {e}')

# %%
x = admin_client.list_topics()
for  t in x.topics.keys():
  print(t)

# %%
#admin_client.delete_topics([topic])

# %%
