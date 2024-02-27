import asyncio
from math import sin
import math
import random
from typing import AsyncGenerator, List
import strawberry

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter



@strawberry.type
class Location:
    lat: float
    lng: float


@strawberry.type
class TrackedObject:
    ip: str
    location: Location


def random_number(a: float, b: float | None = None):
    if b is None:
        b = a
        a = -a
    return a + random.random() * (b - a)


def random_location():
    return Location(lat=random_number(90), lng=random_number(180))


tracked_objects = [
    TrackedObject(ip="ye", location=random_location()),
    TrackedObject(ip="ye2", location=random_location()),
]


@strawberry.type
class Query:
    @strawberry.field
    def trackedObjects(self) -> list[TrackedObject]:
        return tracked_objects


@strawberry.type
class Subscription:
    @strawberry.subscription
    async def count(self, target: int = 100) -> AsyncGenerator[int, None]:
        for i in range(target):
            yield i
            await asyncio.sleep(0.001)


    @strawberry.subscription
    async def objectsUpdated(self) -> AsyncGenerator[List[TrackedObject], None]:
        dt = 1e-3
        while True:
            yield tracked_objects
            await asyncio.sleep(dt)
            for i in range(len(tracked_objects)):
                T_lng = 5 if i % 2 else 1
                w_lng = 360 / T_lng
                T_lat = 1
                w_lat = 180 / T_lat

                lat = tracked_objects[i].location.lat
                lng = tracked_objects[i].location.lng

                lat += 90
                lng += 180

                lat = ( lat + w_lat * dt) % 180
                lng = (lng + (-1)**i * w_lng * dt) % 360

                lat -= 90
                lng -= 180

                tracked_objects[i].location.lat = lat
                tracked_objects[i].location.lng = lng





schema = strawberry.Schema(query=Query, subscription=Subscription)

graphql_app = GraphQLRouter(schema)

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}
app.include_router(graphql_app, prefix="/graphql")


origins = [
    "http://localhost:5173",
    "http://localhost:8080",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

