from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from madr_book.settings import Settings

database = Settings().DATABASE_URL
engine = create_engine(database)


def get_session():  # pragma: no cover
    with Session(engine) as session:
        yield session
