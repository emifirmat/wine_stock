import pytest

from models import Shop, Wine, Colour, Style, Varietal
    
def test_shop_singleton(session):
    # Verify singleton creates a default shop
    shop = Shop.get_singleton(session)
    assert shop.name == "WINE STOCK"
    assert shop.logo_path == "assets/logos/app_logo.png"

    # Verify that in the second call, there is no second shop.
    shop2 = Shop.get_singleton(session)
    assert shop.id == shop2.id
    assert session.query(Shop).count() == 1


def test_create_colour_style_varietal(session):
    red = Colour(name="Red")
    dry = Style(name="Dry")
    malbec = Varietal(name="Malbec")

    session.add_all([red, dry, malbec])
    session.commit()

    assert red.id is not None
    assert dry.id is not None
    assert malbec.id is not None


def test_create_wine_with_references(session):
    # Primero se crean los objetos referenciados
    red = Colour(name="Red")
    dry = Style(name="Dry")
    malbec = Varietal(name="Malbec")
    session.add_all([red, dry, malbec])
    session.commit()

    wine = Wine(
        name="Test wine",
        winery="Test winery",
        colour_id=red.id,
        style_id=dry.id,
        varietal_id=malbec.id,
        vintage_year=2018,
        origin="Mendoza",
        code="R-001",
        wine_picture_path=None,
    )
    session.add(wine)
    session.commit()

    # Validations
    assert wine.id is not None
    assert wine.colour.name == "Red"
    assert wine.style.name == "Dry"
    assert wine.varietal.name == "Malbec"
    assert wine.vintage_year == 2018
    assert wine.code == "R-001"
    assert wine.wine_picture_path == None