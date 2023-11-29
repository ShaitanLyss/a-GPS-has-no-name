from kafka.producer import KafkaProducer
producer = KafkaProducer(bootstrap_servers='localhost:9092')
for _ in range(10):
  producer.send('foobar',b'dddd')
