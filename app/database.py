from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

# Connect to Database and create database session
engine = create_engine('sqlite:///cs_training.db')
Base.metadata.bind = engine

db_session = sessionmaker(bind=engine)
session = db_session()


def init_db():
    # import all modules here that might define model so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()

    import app.models.category_model
    import app.models.course_model
    Base.metadata.create_all(bind=engine)
