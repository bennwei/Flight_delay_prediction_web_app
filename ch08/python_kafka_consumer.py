import sys, os, re
import json

from kafka import KafkaConsumer, TopicPartition
consumer = KafkaConsumer()
consumer.assign([TopicPartition('flight_delay_classification_request', 0)])
consumer.seek_to_beginning()

for message in consumer:
  message_bytes = message.value
  message_string = message_bytes.decode()
  message_object = json.loads(message_string)
  print(message_object)
