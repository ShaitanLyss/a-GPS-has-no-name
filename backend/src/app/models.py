from datetime import datetime
from typing import Annotated
from sqlmodel import Field, SQLModel
import strawberry
from geoalchemy2 import Geometry, WKBElement

@strawberry.type
class GeoJSONType:
    type: str
    coordinates: list[float]


class LocationDB(SQLModel, table=True):
    """The location of a tracked object stored in the postgis database."""

    __tablename__: str = "locations"

    id: int = Field(primary_key=True)
    loc_ip_address: str
    pub_ip_address: str
    libelle: str
    at: datetime
    geom: Annotated[str, WKBElement] = Field(Geometry(geometry_type="POINT", srid=4326))
    
class LocationWithGeoJson(LocationDB):
    """The location of a tracked object stored in the postgis database."""
    geom_geojson: str


@strawberry.type
class Location:
    lat: float
    lng: float


@strawberry.type
class TrackedObject:
    ip: str
    location: Location
    at: datetime | None = None
    geom: GeoJSONType
