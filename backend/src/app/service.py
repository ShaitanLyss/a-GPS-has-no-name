from datetime import datetime
import os
import random
from typing import Any, Generator, List, Optional, Sequence
from app.models import LocationDB as Location, Location as LocationType, LocationWithGeoJson
from sqlalchemy import Engine, Select, create_engine
from geoalchemy2 import functions
from sqlmodel import Session, distinct, select


def get_db_engine() -> Engine:
    user = os.getenv("PG_USER")
    password = os.getenv("PG_PASSWORD")
    host = os.getenv("PG_HOST")
    db = os.getenv("PG_DATABASE")
    assert user is not None
    assert password is not None
    assert host is not None
    assert db is not None
    db_url = "postgresql://" + user + ":" + password + "@" + host + "/" + db

    connect_args = {}
    return create_engine(db_url, echo=True, connect_args=connect_args)


engine = get_db_engine()


def get_db() -> Generator[Session, Any, Any]:
    with Session(engine) as session:
        yield session


def random_number(a: float, b: float | None = None):
    if b is None:
        b = a
        a = -a
    return a + random.random() * (b - a)


def random_location():
    return LocationType(lat=random_number(90), lng=random_number(180))


def get_location(db: Session) -> Optional[Location]:
    return db.exec(select(Location)).first()

def locations_after_timestamp(db: Session, timestamp: datetime, unique: bool = False) -> Sequence[LocationWithGeoJson]:
    query: Select = select(Location, functions.ST_AsGeoJSON(Location.geom).label("geom")).order_by(Location.pub_ip_address, Location.loc_ip_address, Location.at.desc()).where(Location.at > timestamp).where(Location.pub_ip_address != None)
    if unique:
        query = query.distinct(Location.pub_ip_address, Location.loc_ip_address)
    return [LocationWithGeoJson(**loc.model_dump(), geom_geojson=geojson) for [loc, geojson] in db.exec(query).all()]
