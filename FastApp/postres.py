from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Float, String, Integer, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

# Configuration de la base de données PostgreSQL
DATABASE_URL = "postgresql://username:password@localhost/dbname"
engine = create_engine(DATABASE_URL)
Base = declarative_base()

# Définition du modèle de données
class Coordinates(Base):
    __tablename__ = "coordinates"
    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float)
    longitude = Column(Float)

class Machine(Base):
    __tablename__ = "machines"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    local_ip_address = Column(String, unique=True, index=True)
    public_ip_address = Column(String, unique=True, index=True)
    
    # Relation avec la table Coordinates
    coordinates_id = Column(Integer, ForeignKey("coordinates.id"))
    coordinates = relationship("Coordinates", back_populates="machines")

# Ajout de la relation inverse dans la classe Coordinates
Coordinates.machines = relationship("Machine", back_populates="coordinates")

# Création de la table dans la base de données
Base.metadata.create_all(bind=engine)

# Configuration de FastAPI
app = FastAPI()

# Route pour récupérer les coordonnées GPS par adresse IP
@app.get("/machines/{ip_address}")
async def get_machine_coordinates(ip_address: str):
    # Création d'une session de base de données
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    # Récupération de la machine depuis la base de données
    machine = db.query(Machine).filter(
        (Machine.local_ip_address == ip_address) | (Machine.public_ip_address == ip_address)
    ).first()

    # Fermeture de la session de base de données
    db.close()

    # Vérification si l'adresse IP existe dans la base de données
    if machine is None:
        raise HTTPException(status_code=404, detail="Machine not found")

    # Récupération des coordonnées associées à la machine
    coordinates = {"latitude": machine.coordinates.latitude, "longitude": machine.coordinates.longitude}

    return {"id": machine.id, "name": machine.name, "local_ip_address": machine.local_ip_address, "public_ip_address": machine.public_ip_address, "coordinates": coordinates}
