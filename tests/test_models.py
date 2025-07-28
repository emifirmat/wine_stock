import pytest
from decimal import Decimal
from datetime import datetime

from models import Shop, Wine, Colour, Style, Varietal, StockMovement
    
def test_shop_singleton(session):
    # Verify singleton creates a default shop
    shop = Shop.get_singleton(session)
    assert shop.name == "WINE STOCK"
    assert shop.logo_path == "assets/logos/app_logo.png"

    # Verify that in the second call, there is no second shop.
    shop2 = Shop.get_singleton(session)
    assert shop.id == shop2.id
    assert session.query(Shop).count() == 1


def test_create_colour_style_varietal(session, sample_color_style_varietal):
    red = Colour(name="Red")
    dry = Style(name="Dry")
    malbec = Varietal(name="Malbec")

    session.add_all([red, dry, malbec])
    session.commit()

    assert red.id is not None
    assert dry.id is not None
    assert malbec.id is not None


def test_create_wine(session, sample_color_style_varietal):
    red, dry, malbec = sample_color_style_varietal
    # New record of wine
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
        quantity=53,
        purchase_price=12.23,
        selling_price=99,
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
    assert wine.wine_picture_path is None
    assert wine.quantity == 53
    assert abs(wine.purchase_price - Decimal("12.23")) < Decimal("0.01")
    assert wine.selling_price == Decimal("99")

def test_create_stock_movement(session, sample_wine: Wine, sample_color_style_varietal):
    
    movement = StockMovement(
        wine_id=sample_wine.id,
        transaction_type="purchase",
        quantity=10,
        price=Decimal("12.23"),
    )
    session.add(movement)
    session.commit()

    result = session.query(StockMovement).filter_by(wine_id=sample_wine.id).first()

    # Validations
    assert result is not None
    assert result.transaction_type == "purchase"
    assert result.quantity == 10
    assert result.price == Decimal("12.23")
    assert isinstance(result.datetime, datetime)