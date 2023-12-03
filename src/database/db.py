from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.config.config import settings


user = settings.postgres_user
password = settings.postgres_password
db_name = settings.postgres_name
domain = settings.postgres_domain
port = settings.postgres_port


DB_URL = f'postgresql+psycopg2://{user}:{password}@{domain}:{port}/{db_name}'
# DB_URL = 'sqlite: ./test.db'
engine = create_engine(DB_URL)


def get_db():
    """
    The get_db function opens a new database connection if there is none yet for the current application context.
    It also binds the session to the current context so that you don't have to pass it around.

    :return: A database session
    :doc-author: Trelent
    """
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()
