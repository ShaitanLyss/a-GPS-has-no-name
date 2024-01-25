import json

from confluent_kafka import Consumer, KafkaError
from dotenv import load_dotenv
import os
from postres import PG_Connexion
from models import KafkaProducerInfo
import asyncio
import websockets


class KafkaCoordinatesConsumer:
    def __init__(self):
        load_dotenv()  # Load environment variables from .env file
        self.connection_db = PG_Connexion()

        self.consumer_conf = {
            'bootstrap.servers': os.getenv('KAFKA_BROKER_ADDRESS'),
            'group.id': os.getenv('KAFKA_CONSUMER_GROUP'),
            'auto.offset.reset': 'earliest',
        }
        self.consumer = Consumer(self.consumer_conf)
        self.topic = os.getenv('TOPIC')
        self.received_data = {}

    def subscribe(self):
        self.consumer.subscribe([self.topic])

    def consume_messages(self):
        try:
            while True:
                msg = self.consumer.poll(1.0)  # Poll for 1 second

                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError.PARTITION_EOF:
                        # End of partition event
                        print(f"Reached end of partition {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")
                    else:
                        print(f"Error: {msg.error()}")
                else:
                    # Print the received message value
                    data = json.loads(msg.value().decode('ascii'))
                    # print("Received message: \n", type(data))

                    # data = data[0]
                    data_to_sent = KafkaProducerInfo(1, data['name'], data['local_ip_address'],
                                                     data['public_ip_address'], data['coordinates'])

                    self.received_data = data_to_sent

                    self.connection_db.exec_request(self.received_data)

                    mes_points = self.connection_db.get_all_locations()

                    #print(f"les points : \n {mes_points}")

        except KeyboardInterrupt:
            pass
        finally:
            # Close down consumer to commit final offsets.
            self.consumer.close()

    def Create_Schema_DB(self):
        self.connection_db.DB_initialize()


if __name__ == "__main__":
    kafka_consumer = KafkaCoordinatesConsumer()
    kafka_consumer.connection_db.delete_locations_table()
    kafka_consumer.Create_Schema_DB()
    kafka_consumer.subscribe()

    kafka_consumer.consume_messages()
