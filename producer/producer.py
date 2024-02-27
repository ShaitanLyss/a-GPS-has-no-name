import json
import os
import random
import time
from typing import Optional
from pydantic import BaseModel

import requests
from confluent_kafka import Producer
from dotenv import load_dotenv
import socket
from models import KafkaProducerInfo

class Location(BaseModel):
    lat: float
    lng: float


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
            'coordinates': {'lat': lat, 'long': long}
        }
        return generated_data

def random_number(a: float, b: Optional[float] = None):
    if b is None:
        b = a
        a = -a
    return a + random.random() * (b - a)

def random_location():
    return Location(lat=random_number(90), lng=random_number(180))


kafka_producer = KafkaCoordinatesProducer()
def main():
    loc_0 = random_location()
    current_lat, current_long = loc_0.lat, loc_0.lng
    machine_ip = kafka_producer.get_machine_ip()
    assert machine_ip is not None
    i = int(machine_ip.split('.')[-1])
    try:
        dt = 1e-3
        while True:
            # Generate the data
            T_lng = 5 if i % 2 else 1
            w_lng = 360 / T_lng
            T_lat = 1
            w_lat = 180 / T_lat

            lat = current_lat
            lng = current_long

            lat += 90
            lng += 180

            lat = (lat + w_lat * dt) % 180
            lng = (lng + (-1) ** i * w_lng * dt) % 360

            lat -= 90
            lng -= 180

            current_lat = lat
            current_long = lng
            data = kafka_producer.generate_coordinates(current_lat, current_long)

            # Print or do something with the data
            #print(data)
            kafka_producer.producer.produce(kafka_producer.topic, key='some_key', value=(json.dumps(data).encode('ascii')),
                                            callback=kafka_producer.delivery_report)
            # Wait for any outstanding messages to be delivered
            kafka_producer.producer.flush()
            # Sleep for one second
            time.sleep(dt)

    except KeyboardInterrupt:
        # Handle Ctrl+C to exit the loop gracefully
        print("Exiting the loop.")

    # data_to_sent = KafkaProducerInfo(1, 'producer1', kafka_producer.get_machine_ip(), kafka_producer.get_public_ip(), data['coordinates'])


if __name__ == "__main__":
    main()