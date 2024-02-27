import os
from typing import Annotated, List
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
user = os.getenv('PG_USER')
password = os.getenv('PG_PASSWORD')
host = os.getenv('PG_HOST')
db = os.getenv('PG_DATABASE')
assert user is not None
assert password is not None
assert host is not None
assert db is not None
DATABASE_URL = "postgresql://" + user + ":" + password + "@" + host + "/" + db

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


def random_number(a: float, b = None):
    if b is None:
        b = a
        a = -a
    return a + random.random() * (b - a)


def random_location():
    return Location(lat=random_number(90), lng=random_number(180))




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

@app.get("/location/", response_model=List[LocationCreate])
async def get_locations(db: Annotated[Session, Depends(get_db)]):
    location = db.query(Location).all()

    return location

@app.get("/")
async def helloWorld():
    return "Hello World!"


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
    db: Annotated[Session, Depends(get_db)],
    lib: str,
    skip: int = 0,
    limit: int = 10
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







