from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
#from config.base import Base
from models.orm_models import Base

class DatabaseHandler:
    def __init__(self, config):
        self.engine = create_engine(config['database']['uri'])
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
    def save_to_database(self, df):
        session = self.Session()
        try:
            df.to_sql(
                name='donneurs',
                con=self.engine,
                if_exists='append',
                index=False
            )
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

#Base.metadata.create_all(self.engine)