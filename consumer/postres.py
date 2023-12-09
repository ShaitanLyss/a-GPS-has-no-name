import os

import psycopg2
from shapely.geometry import Point
from dotenv import load_dotenv
from models import KafkaProducerInfo


class PG_Connexion:
    def __init__(self):
        load_dotenv()

        self.conn = psycopg2.connect(
            host=os.getenv('PG_HOST'),
            database=os.getenv('PG_DATABASE'),
            user=os.getenv('PG_USER'),
            password=os.getenv('PG_PASSWORD'),
        )

    def DB_initialize(self):
        # Create a cursor
        cursor = self.conn.cursor()

        # Enable PostGIS extension
        cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis;")

        # Create a table with a POINT column
        create_table_query = """
            CREATE TABLE IF NOT EXISTS locations (
                id SERIAL PRIMARY KEY,                
                libelle VARCHAR(255),
                loc_ip_address VARCHAR(255),
                pub_ip_address VARCHAR(255),
                geom GEOMETRY(Point, 4326)
            );
        """
        cursor.execute(create_table_query)
        self.conn.commit()

        # Close the cursor and connection
        cursor.close()

    def exec_request(self, data: KafkaProducerInfo):
        cursor = self.conn.cursor()
        # Insert a point into the table
        point = Point(data.coordinates['lat'], data.coordinates['long'])
        insert_point_query = "INSERT INTO locations (libelle, loc_ip_address, pub_ip_address, geom) VALUES (%s, %s, %s, " \
                             "ST_GeomFromText(%s, 4326));"
        cursor.execute(insert_point_query, (data.name, data.local_ip_address, data.public_ip_address, point.wkt))

        # Commit the transaction
        self.conn.commit()

        # Close the cursor and connection
        cursor.close()

    def close_db(self):
        self.conn.close()

    def get_all_locations(self):
        cursor = self.conn.cursor()

        # Select all locations from the table
        select_all_locations_query = "SELECT libelle, loc_ip_address, pub_ip_address, ST_X(geom) AS latitude, " \
                                     "ST_Y(geom) AS longitude FROM locations;"

        cursor.execute(select_all_locations_query)

        # Fetch all the rows
        locations = cursor.fetchall()

        # Close the cursor
        cursor.close()

        # Return the locations
        return locations

    def delete_locations_table(self):
        cursor = self.conn.cursor()

        # Drop the locations table if it exists
        drop_table_query = "DROP TABLE IF EXISTS locations;"

        cursor.execute(drop_table_query)

        # Commit the transaction
        self.conn.commit()

        # Close the cursor
        cursor.close()


