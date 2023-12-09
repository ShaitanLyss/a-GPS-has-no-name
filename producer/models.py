from pydantic import BaseModel


class Coordinates(BaseModel):
    lat: float
    long: float


class KafkaProducerInfo:
    def __init__(self, id: int, name: str, local_ip_address: str, public_ip_address: str, coordinates: Coordinates):
        self.id = id
        self.name = name
        self.local_ip_address = local_ip_address
        self.public_ip_address = public_ip_address
        self.coordinates = coordinates
