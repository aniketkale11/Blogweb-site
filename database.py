from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


SQLALCHEMY_DATABASE_URL = "sqlite:///./Blog.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL , connect_args={"check_same_thread":False})

sessionlocal = sessionmaker(autoflush=False , autocommit= False , bind=engine)

Base= declarative_base()

def get_data():

    db = sessionlocal()
    try:
        yield db

    finally:
        db.close()