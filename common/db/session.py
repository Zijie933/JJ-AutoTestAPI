from sqlmodel import Session, create_engine

from common.core.config import settings

engine = create_engine(
    settings.MYSQL_URL,
    pool_pre_ping=True,
    echo=True,
    future=True
)

def get_db():
    with Session(engine) as session:
        yield session