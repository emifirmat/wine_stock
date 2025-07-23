import pytest
from models import Colour
from helpers import populate_db_model


def test_populate_creates_entries(session):
    populate_db_model(["Red", "White", "Rosé"], Colour, session)

    results = session.query(Colour).all()
    names = [colour.name for colour in results]

    assert set(names) == {"Red", "White", "Rosé"}
    assert len(names) == 3

def test_populate_does_not_duplicate(session):
    #  Initial values
    populate_db_model(["Red", "White"], Colour, session)

    # Attempt to repopulate with overlapping values
    populate_db_model(["Red", "White", "Rosé"], Colour, session)

    results = session.query(Colour).all()
    names = [colour.name for colour in results]

    assert set(names) == {"Red", "White", "Rosé"}
    assert len(names) == 3 
