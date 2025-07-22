from typing import Type, TypeVar

from sqlalchemy.orm import Session


def populate_db_model(fields: list[str], model: type, session: Session): 
    """
    Populate model with entries if the do not already exists.

    Parameters:
        - fields: List of entry names to be added
        - model: Model class from models.py
        - session: SQLAlchemy session to perform DB operations.
    """
    for field in fields:
        if not session.query(model).filter_by(name=field).first():
            session.add(model(name=field))
        session.commit()   
    
