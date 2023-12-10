import os
from typing import List

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


app = FastAPI()


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


@app.get("/location/{lib}", response_model=LocationCreate)
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
