import json
import os
import random
import time

import requests
from confluent_kafka import Producer
from dotenv import load_dotenv
import socket
from models import KafkaProducerInfo


class KafkaCoordinatesProducer:

    def __init__(self):
        load_dotenv()

        self.producer_conf = {
            'bootstrap.servers': os.getenv('KAFKA_BROKER_ADDRESS'),
        }
        self.producer = Producer(self.producer_conf)
        self.topic = os.getenv('TOPIC')

    def delivery_report(self, err, msg):
        if err is not None:
            print(f'Message delivery failed: {err}')
        else:
            print(f'Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}')

    def get_machine_ip(self):
        try:
            # Get the local machine's hostname
            hostname = socket.gethostname()

            # Get the IP address associated with the local machine's hostname
            ip_address = socket.gethostbyname(hostname)

            return ip_address
        except socket.error as e:
            print(f"Error: {e}")
            return None

    def get_public_ip(self):
        try:
            response = requests.get('https://httpbin.org/ip')
            if response.status_code == 200:
                public_ip = response.json().get('origin', 'Unknown')
                return public_ip
            else:
                print(f"HTTP request failed with status code {response.status_code}")
                return None
        except requests.RequestException as e:
            print(f"Error: {e}")
            return None

    def generate_coordinates(self, lat: float, long: float) -> dict:
        hostname = os.environ.get("HOSTNAME")
        generated_data = {
            'id': 1,
            'name': hostname,
            'local_ip_address': kafka_producer.get_machine_ip(),  # Replace with actual method
            'public_ip_address': kafka_producer.get_public_ip(),  # Replace with actual method
            'coordinates': {'lat': random.uniform(-90, 90), 'long': random.uniform(-180, 180)}
        }
        return generated_data


if __name__ == "__main__":
    kafka_producer = KafkaCoordinatesProducer()
    current_lat, current_long = random.uniform(-90, 90), random.uniform(-180, 180)
    try:
        while True:
            # Generate the data
            current_lat += random.uniform(-0.001, 0.001)
            current_long += random.uniform(-0.001, 0.001)
            data = kafka_producer.generate_coordinates(current_lat, current_long)

            # Print or do something with the data
            print(data)
            kafka_producer.producer.produce(kafka_producer.topic, key='some_key', value=(json.dumps(data).encode('ascii')),
                                            callback=kafka_producer.delivery_report)
            # Wait for any outstanding messages to be delivered
            kafka_producer.producer.flush()
            # Sleep for one second
            time.sleep(1)

    except KeyboardInterrupt:
        # Handle Ctrl+C to exit the loop gracefully
        print("Exiting the loop.")

    # data_to_sent = KafkaProducerInfo(1, 'producer1', kafka_producer.get_machine_ip(), kafka_producer.get_public_ip(), data['coordinates'])

