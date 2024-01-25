import os
from typing import List
import asyncio
from math import sin
import math
import random
from typing import AsyncGenerator, List
import strawberry

from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from fastapi.params import Depends, Query
from shapely import wkb
from shapely.geometry import Point
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Float, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, attributes, Session
from geoalchemy2 import Geometry, WKBElement
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = "postgresql://" + os.getenv('PG_USER') + ":" + os.getenv('PG_PASSWORD') + "@" + os.getenv(
    'PG_HOST') + "/" + os.getenv('PG_DATABASE')

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base(metadata=MetaData())


class Location(Base):
    __tablename__ = "locations"
    id = Column(Integer, primary_key=True, index=True)
    libelle = Column(String, index=True)
    loc_ip_address = Column(String, index=True)
    pub_ip_address = Column(String, index=True)
    geom = Column(Geometry('POINT', srid=4326))


Base.metadata.create_all(bind=engine)


class LocationCreate(BaseModel):
    libelle: str
    loc_ip_address: str
    pub_ip_address: str
    lat: float
    long: float





@strawberry.type
class Location:
    lat: float
    lng: float


@strawberry.type
class TrackedObject:
    ip: str
    location: Location


def random_number(a: float, b = None):
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




origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost:5173",
    "http://localhost:8080",
    "http://localhost:3000",
    "http://localhost:4000",
    "http://fastapi:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#app.include_router(graphql_app, prefix="/graphql")


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/location/", response_model=LocationCreate)
async def create_location(location: LocationCreate):
    db_location = Location(**location.dict())
    db = SessionLocal()
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    db.close()
    return db_location

@app.get("/")
async def create_location():
    db = SessionLocal()
    location = db.query(Location).all()
    db.close()
    return location


@app.get("/c/{lib}", response_model=LocationCreate)
async def read_location(lib: str):
    db = SessionLocal()
    location = db.query(Location).filter(Location.libelle == lib).first()
    db.close()
    if location is None:
        raise HTTPException(status_code=404, detail="Location not found")
    location_dict = attributes.instance_dict(location)
    geometry = wkb.loads(bytes(location_dict['geom'].data))
    location_dict['lat'] = list(geometry.coords[0])[0]
    location_dict['long'] = list(geometry.coords[0])[1]
    return location_dict


@app.get("/location/tout/{lib}", response_model=List[LocationCreate])
async def read_locations(
    lib: str,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    locations = (
        db.query(Location)
        .filter(Location.libelle == lib)
        .offset(skip)
        .limit(limit)
        .all()
    )
    if locations is None:
        raise HTTPException(status_code=404, detail="Location not found")
    results = []
    for location in locations:
        location_dict = attributes.instance_dict(location)
        geometry = wkb.loads(bytes(location_dict['geom'].data))
        location_dict['lat'] = list(geometry.coords[0])[0]
        location_dict['long'] = list(geometry.coords[0])[1]
        results.append(location_dict)
    return results







