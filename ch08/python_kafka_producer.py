from kafka import KafkaProducer
producer = KafkaProducer()

producer.send(
  'flight_delay_classification_request',
  '{"Hello": "Producer!"}'.encode()
)
