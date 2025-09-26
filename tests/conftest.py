import pytest
from decimal import Decimal
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, clear_mappers

from db.models import Base, Wine, Colour, Style, Varietal

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

@pytest.fixture
def sample_color_style_varietal(session):
    red = Colour(name="Red")
    dry = Style(name="Dry")
    malbec = Varietal(name="Malbec")

    session.add_all([red, dry, malbec])
    session.commit()
    return red, dry, malbec

@pytest.fixture
def sample_wine(session, sample_color_style_varietal):
    red, dry, malbec = sample_color_style_varietal
    wine = Wine(
        name="Test Wine",
        winery=malbec.id,
        colour_id=red.id,
        style_id=dry.id,
        vintage_year=2020,
        code="TW-001",
        purchase_price=Decimal("10.00"),
        selling_price=Decimal("15.00"),
    )

    session.add(wine)
    session.commit()
    return wine