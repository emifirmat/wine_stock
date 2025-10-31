"""
Pytest configuration and shared fixtures for database tests.

This module provides fixtures for in-memory database sessions and
sample data used across multiple test files.
"""
import pytest
from decimal import Decimal
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from db.models import Base, Wine, Colour, Style, Varietal

# Create a db in memory
@pytest.fixture
def session():
    """
    Create an in-memory SQLite database session for testing.
    
    Sets up a fresh database with all tables for each test, then
    tears it down after the test completes.
    
    Yields:
        SQLAlchemy session connected to in-memory database
    """
    engine = create_engine("sqlite:///:memory:", echo=False)

    # Activate foreign keys in SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    # Create all the tables in memory db
    Base.metadata.create_all(engine)

    # Create a session
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    # Cleanup
    session.close()
    Base.metadata.drop_all(engine)

@pytest.fixture
def sample_color_style_varietal(session):
    """
    Create sample Colour, Style, and Varietal records.
    
    Parameters:
        session: Database session fixture
        
    Returns:
        Tuple of (Colour, Style, Varietal) instances
    """
    red = Colour(name="Red")
    dry = Style(name="Dry")
    malbec = Varietal(name="Malbec")

    session.add_all([red, dry, malbec])
    session.commit()

    return red, dry, malbec

@pytest.fixture
def sample_wine(session, sample_color_style_varietal):
    """
    Create a sample Wine record for testing.
    
    Parameters:
        session: Database session fixture
        sample_color_style_varietal: Fixture providing colour, style, and varietal
        
    Returns:
        Wine instance with basic attributes
    """
    red, dry, malbec = sample_color_style_varietal
    wine = Wine(
        name="Test Wine",
        winery="Test Winery",
        colour_id=red.id,
        style_id=dry.id,
        varietal_id=malbec.id,
        vintage_year=2020,
        code="TW-001",
        quantity=10,
        purchase_price=Decimal("10.00"),
        selling_price=Decimal("15.00"),
    )

    session.add(wine)
    session.commit()
    return wine