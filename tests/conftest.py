import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, clear_mappers

from models import Base

# Create a db in memory
@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:", echo=False)

    # Activate FK in SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    # Crear all the tables in memory db
    Base.metadata.create_all(engine)

    # Crear a sesión
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    session.close()
    Base.metadata.drop_all(engine)  # Clear tables