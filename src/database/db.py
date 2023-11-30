from sqlalchemy import create_engine
from sqlalchemy.orm import Session


DB_URL = 'postgresql+psycopg2://postgres:567234@localhost:5432/rest_app'
engine = create_engine(DB_URL)


def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()
