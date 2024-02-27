import asyncio
from dataclasses import dataclass
from datetime import datetime
import json
import logging
from typing import Annotated, Any, AsyncGenerator, List, NewType
from app.models import GeoJSONType, Location, LocationDB, LocationWithGeoJson, TrackedObject
from app.service import get_db, random_location
from fastapi import Depends
from geoalchemy2 import WKBElement
from sqlalchemy import true
from sqlmodel import Session
import strawberry
from strawberry.fastapi import GraphQLRouter, BaseContext
from strawberry.types import Info as BaseInfo
from app import service
from app.models import Location
import shapely


def typeFromModel(obj: LocationWithGeoJson) -> TrackedObject:
    geom = json.loads(obj.geom_geojson)
    return TrackedObject(
        ip=f"{obj.pub_ip_address}->{obj.loc_ip_address}",
        location=Location(lat=geom["coordinates"][0], lng=geom["coordinates"][1]),
        at=obj.at,
        geom=GeoJSONType(coordinates=geom["coordinates"], type=geom["type"]),
    )

@dataclass
class GraphQLContext(BaseContext):
    db: Annotated[Session, Depends(get_db)]

Info = BaseInfo[GraphQLContext, Any]

@strawberry.type
class Query:        
    @strawberry.field
    def locations_after(self, info: Info, timestamp: datetime, unique: bool = False) -> List[TrackedObject]:
        res: List[TrackedObject] = []
        
        for obj in service.locations_after_timestamp(info.context.db, timestamp, unique):
            res.append(typeFromModel(obj))
        return res


@strawberry.type
class Subscription:
    @strawberry.subscription
    async def objectsUpdated(self, info: Info) -> AsyncGenerator[List[TrackedObject], None]:
        dt = 1e-3
        last_timestamp = datetime.utcnow()
        while True:            
            new_locs = service.locations_after_timestamp(db=info.context.db, timestamp=last_timestamp, unique=True)
            if new_locs:
                res: List[TrackedObject] = []
                logging.info("new locs %s", new_locs)
                for loc in new_locs:
                    last_timestamp = max(last_timestamp, loc.at)
                    res.append(typeFromModel(loc))
                yield res
            
            await asyncio.sleep(dt)
            # for i in range(len(tracked_objects)):
            #     T_lng = 5 if i % 2 else 1
            #     w_lng = 360 / T_lng
            #     T_lat = 1
            #     w_lat = 180 / T_lat

            #     lat = tracked_objects[i].location.lat
            #     lng = tracked_objects[i].location.lng

            #     lat += 90
            #     lng += 180

            #     lat = (lat + w_lat * dt) % 180
            #     lng = (lng + (-1) ** i * w_lng * dt) % 360

            #     lat -= 90
            #     lng -= 180

            #     tracked_objects[i].location.lat = lat
            #     tracked_objects[i].location.lng = lng


schema = strawberry.Schema(query=Query, subscription=Subscription)
graphql_app = GraphQLRouter(schema, context_getter=GraphQLContext)
