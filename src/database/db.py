from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.config.config import settings


user = settings.postgres_user
password = settings.postgres_password
db_name = settings.postgres_name
domain = settings.postgres_domain
port = settings.postgres_port


DB_URL = f'postgresql+psycopg2://{user}:{password}@{domain}:{port}/{db_name}'
engine = create_engine(DB_URL)


def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()
