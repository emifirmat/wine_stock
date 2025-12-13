"""
Database session factory and initialization.

This module provides session creation with automatic initialization of
reference data and application defaults.
"""
import db.events  # Required for SQLAlchemy event listeners - do not remove
from sqlalchemy.orm import Session as SessionType

from db.models import Session, Shop, Colour, Style, Varietal
from helpers import populate_db_model

def build_session() -> SessionType:
    """
    Create and initialize a database session with default data.
    
    Performs the following initialization steps:
    1. Creates a new SQLAlchemy session
    2. Populates reference tables (Colour, Style, Varietal) if empty
    3. Ensures Shop singleton exists with default values
    
    Returns:
        Configured SQLAlchemy session ready for use
        
    Note:
        The session must be closed by the caller when finished.
        Reference data is only inserted if tables are empty.
    """
    session = Session()

    # Initialise reference data for wine attributes
    wine_colours = ["red", "rosé", "orange", "white", "other"]
    wine_styles = ["dessert", "fortified", "sparkling", "still", "other"]
    wine_varietals = [
        "baga", "cabernet sauvignon", "grenache", "hondarrabi zuri",
        "malbec", "moscato bianco", "tinta roriz", "torrontés",
        "touriga nacional", "other"
    ]

    populate_db_model(wine_colours, Colour, session)
    populate_db_model(wine_styles, Style, session)
    populate_db_model(wine_varietals, Varietal, session)

    # Ensure shop record exists (singleton pattern)
    Shop.get_singleton(session)

    return session
