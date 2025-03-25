# src/database.py
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from models.orm_models import Base
import pandas as pd
import os

# Chemin absolu pour la DB
DB_PATH = os.path.abspath("data/blood_donors.db")

def init_db(db_uri="sqlite:///data/blood_donors.db"):
    """Initialise la connexion et crée les tables si nécessaire"""
    engine = create_engine(db_uri)
    os.makedirs("data", exist_ok=True)
    return engine

def get_engine():
    """Retourne l'engine SQLAlchemy avec création du dossier si besoin"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return create_engine(f"sqlite:///{DB_PATH}")

class DatabaseHandler:
    def __init__(self, config):
        self.engine = create_engine(config['database']['uri'])
        os.makedirs("data", exist_ok=True)
        Base.metadata.create_all(self.engine)

    def save_to_database(self, df):
        """
        Sauvegarde le DataFrame dans la table 'donneurs'
        Args:
            df: DataFrame à sauvegarder
        """
        inspector = inspect(self.engine)
        if not inspector.has_table('donneurs'):
            Base.metadata.create_all(self.engine)
            
        df.to_sql(
            name='donneurs',
            con=self.engine,
            if_exists='replace',
            index=False
        )
        

def get_session(engine):
    """Retourne une nouvelle session SQLAlchemy"""
    Session = sessionmaker(bind=engine)
    return Session()