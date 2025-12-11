"""
Unit tests for database models and ORM functionality.

This module tests all database models including Shop, Wine, Colour, Style,
Varietal, and StockMovement, as well as their relationships and triggers.
"""
import pytest
from decimal import Decimal
from datetime import datetime

from db.events import * # Activates event listeners
from db.models import Shop, Wine, Colour, Style, Varietal, StockMovement

    
def test_shop_singleton(session):
    """
    Test that Shop.get_singleton creates and returns a single instance.
    """
    # Verify singleton creates a default shop
    shop = Shop.get_singleton(session)
    assert shop.name == "WINE STOCK"
    assert shop.logo_path == "assets/logos/app_logo.png"

    # Verify that second call returns the same shop instance
    shop2 = Shop.get_singleton(session)
    assert shop.id == shop2.id
    assert session.query(Shop).count() == 1


def test_shop_singleton_with_existing_record(session):
    """
    Test that Shop.get_singleton returns existing record if already created.
    """
    # Create a custom shop
    custom_shop = Shop(name="Custom Wine Shop", logo_path="custom/logo.png")
    session.add(custom_shop)
    session.commit()
    
    # Verify singleton returns the existing shop
    shop = Shop.get_singleton(session)
    assert shop.id == custom_shop.id
    assert shop.name == "Custom Wine Shop"
    assert shop.logo_path == "custom/logo.png"
    assert session.query(Shop).count() == 1


def test_create_colour_style_varietal(session, sample_color_style_varietal):
    """
    Test creation of Colour, Style, and Varietal models.
    """
    red = Colour(name="Red")
    dry = Style(name="Dry")
    malbec = Varietal(name="Malbec")

    session.add_all([red, dry, malbec])
    session.commit()

    assert red.id is not None
    assert dry.id is not None
    assert malbec.id is not None


def test_named_model_mixin_all_ordered(session, sample_color_style_varietal):
    """
    Test that NamedModelMixin.all_ordered returns case-insensitive sorted results.
    """
    # Add more colours to test sorting
    session.add_all([
        Colour(name="White"),
        Colour(name="Orange"),
        Colour(name="amber"),  # Test case-insensitivity
    ])
    session.commit()
    
    colours = Colour.all_ordered(session)
    names = [c.name for c in colours]
    
    # Should be sorted case-insensitively
    assert names == ["amber", "Orange", "Red", "White"]


def test_named_model_mixin_get_name(session, sample_color_style_varietal):
    """
    Test NamedModelMixin.get_name retrieves instance by name.
    """
    red, _, _ = sample_color_style_varietal
    
    # Should find existing colour
    result = Colour.get_by_filter(session, name="Red")
    assert result is not None
    assert result.id == red.id
    
    # Should return None for non-existent name
    result = Colour.get_by_filter(session, name="Blue")
    assert result is None


def test_named_model_mixin_get_by_filter_raises_error(session):
    """
    Test that get_by_filter raises ValueError when the filter is not provided.
    """
    with pytest.raises(ValueError, match="At least one filter must be provided"):
        Colour.get_by_filter(session)

def test_create_wine(session, sample_color_style_varietal):
    """
    Test creation of Wine model with all attributes.
    """
    red, dry, malbec = sample_color_style_varietal
    
    wine = Wine(
        name="Test wine",
        winery="Test Winery",
        colour_id=red.id,
        style_id=dry.id,
        varietal_id=malbec.id,
        vintage_year=2018,
        origin="Mendoza",
        code="R-001",
        picture_path=None,
        quantity=53,
        min_stock=10,
        purchase_price=Decimal("12.23"),
        selling_price=Decimal("99.00"),
    )
    session.add(wine)
    session.commit()

    # Validations
    assert wine.id is not None
    assert wine.name == "Test wine"
    assert wine.winery == "Test Winery"
    assert wine.colour.name == "Red"
    assert wine.style.name == "Dry"
    assert wine.varietal.name == "Malbec"
    assert wine.vintage_year == 2018
    assert wine.origin == "Mendoza"
    assert wine.code == "R-001"
    assert wine.picture_path is None
    assert wine.quantity == 53
    assert wine.min_stock == 10
    assert wine.purchase_price == Decimal("12.23")
    assert wine.selling_price == Decimal("99.00")


def test_wine_all_ordered(session, sample_color_style_varietal):
    """
    Test Wine.all_ordered returns wines sorted by specified field.
    """
    red, dry, malbec = sample_color_style_varietal
    
    # Create wines with different names
    wines = [
        Wine(name="Zebra Wine", winery="Z Winery", colour_id=red.id, style_id=dry.id,
             vintage_year=2020, code="Z-001", purchase_price=10, selling_price=20),
        Wine(name="Alpha Wine", winery="A Winery", colour_id=red.id, style_id=dry.id,
             vintage_year=2020, code="A-001", purchase_price=10, selling_price=20),
        Wine(name="beta Wine", winery="B Winery", colour_id=red.id, style_id=dry.id,
             vintage_year=2020, code="B-001", purchase_price=10, selling_price=20),
    ]
    session.add_all(wines)
    session.commit()
    
    # Test sorting by name (default)
    result = Wine.all_ordered(session)
    names = [w.name for w in result]
    assert names == ["Alpha Wine", "beta Wine", "Zebra Wine"]
    
    # Test sorting by code
    result = Wine.all_ordered(session, order_by="code")
    codes = [w.code for w in result]
    assert codes == ["A-001", "B-001", "Z-001"]


def test_wine_all_ordered_invalid_field_raises_error(session):
    """
    Test that Wine.all_ordered raises ValueError for invalid field name.
    """
    with pytest.raises(ValueError, match="Field 'invalid_field' doesn't exist"):
        Wine.all_ordered(session, order_by="invalid_field")


    result = Wine.all_ordered(session, order_by="code")
    codes = [w.code for w in result]
    assert codes == ["A-001", "B-001", "Z-001"]


def test_wine_all_ordered_invalid_field_raises_error(session):
    """
    Test that Wine.all_ordered raises ValueError for invalid field name.
    """
    with pytest.raises(ValueError, match="Field 'invalid_field' doesn't exist"):
        Wine.all_ordered(session, order_by="invalid_field")


def test_wine_column_ordered(session, sample_color_style_varietal):
    """
    Test Wine.column_ordered returns specific column values sorted.
    """
    red, dry, _ = sample_color_style_varietal
    
    wines = [
        Wine(name="Wine C", winery="Winery C", colour_id=red.id, style_id=dry.id,
             vintage_year=2020, code="C-001", purchase_price=10, selling_price=20),
        Wine(name="Wine A", winery="Winery A", colour_id=red.id, style_id=dry.id,
             vintage_year=2020, code="A-001", purchase_price=10, selling_price=20),
        Wine(name="Wine B", winery="Winery B", colour_id=red.id, style_id=dry.id,
             vintage_year=2020, code="B-001", purchase_price=10, selling_price=20),
    ]
    session.add_all(wines)
    session.commit()
    
    # Get only names, sorted by name
    result = Wine.column_ordered(session, column="name")
    names = [row[0] for row in result]
    assert names == ["Wine A", "Wine B", "Wine C"]


def test_wine_validates_origin_title_case(session, sample_color_style_varietal):
    """
    Test that Wine.origin is converted to title case.
    """
    red, dry, malbec = sample_color_style_varietal
    
    wine = Wine(
        name="Test Wine",
        winery="Test Winery",
        colour_id=red.id,
        style_id=dry.id,
        varietal_id=malbec.id,
        vintage_year=2020,
        origin="buenos aires, argentina",
        code="T-001",
        purchase_price=10,
        selling_price=20,
    )
    session.add(wine)
    session.commit()
    
    assert wine.origin == "Buenos Aires, Argentina"


def test_wine_validates_min_stock_conversion(session, sample_color_style_varietal):
    """
    Test that Wine.min_stock handles various input types correctly.
    """
    red, dry, malbec = sample_color_style_varietal
    
    # Test with valid integer
    wine1 = Wine(
        name="Wine 1", winery="Winery", colour_id=red.id, style_id=dry.id,
        vintage_year=2020, code="W-001", purchase_price=10, selling_price=20,
        min_stock=5
    )
    session.add(wine1)
    session.commit()
    assert wine1.min_stock == 5
    
    # Test with string digit
    wine2 = Wine(
        name="Wine 2", winery="Winery", colour_id=red.id, style_id=dry.id,
        vintage_year=2020, code="W-002", purchase_price=10, selling_price=20,
        min_stock="10"
    )
    session.add(wine2)
    session.commit()
    assert wine2.min_stock == 10
    
    # Test with empty string
    wine3 = Wine(
        name="Wine 3", winery="Winery", colour_id=red.id, style_id=dry.id,
        vintage_year=2020, code="W-003", purchase_price=10, selling_price=20,
        min_stock=""
    )
    session.add(wine3)
    session.commit()
    assert wine3.min_stock is None


def test_wine_display_properties(session, sample_color_style_varietal):
    """
    Test Wine display properties return correct values or defaults.
    """
    red, dry, malbec = sample_color_style_varietal
    
    # Wine with all optional fields
    wine_full = Wine(
        name="Full Wine", winery="Winery", colour_id=red.id, style_id=dry.id,
        varietal_id=malbec.id, vintage_year=2020, code="F-001",
        origin="Mendoza", picture_path="path/to/image.png", min_stock=5,
        purchase_price=10, selling_price=20
    )
    session.add(wine_full)
    session.commit()
    
    assert wine_full.origin_display == "Mendoza"
    assert wine_full.varietal_display == "Malbec"
    assert wine_full.picture_path_display == "path/to/image.png"
    assert wine_full.min_stock_display == "5"
    assert wine_full.min_stock_sort == 5
    
    # Wine without optional fields
    wine_empty = Wine(
        name="Empty Wine", winery="Winery", colour_id=red.id, style_id=dry.id,
        vintage_year=2020, code="E-001", purchase_price=10, selling_price=20
    )
    session.add(wine_empty)
    session.commit()
    
    assert wine_empty.origin_display == "N/A"
    assert wine_empty.varietal_display == "N/A"
    assert wine_empty.picture_path_display == "default.png"
    assert wine_empty.min_stock_display == "N/A"
    assert wine_empty.min_stock_sort == -1


def test_wine_is_below_min_stock(session, sample_color_style_varietal):
    """
    Test Wine.is_below_min_stock property correctly identifies low stock.
    """
    red, dry, _ = sample_color_style_varietal
    
    # Wine with quantity below min_stock
    wine_low = Wine(
        name="Low Stock", winery="Winery", colour_id=red.id, style_id=dry.id,
        vintage_year=2020, code="L-001", quantity=3, min_stock=10,
        purchase_price=10, selling_price=20
    )
    session.add(wine_low)
    session.commit()
    assert wine_low.is_below_min_stock is True
    
    # Wine with quantity above min_stock
    wine_ok = Wine(
        name="OK Stock", winery="Winery", colour_id=red.id, style_id=dry.id,
        vintage_year=2020, code="O-001", quantity=15, min_stock=10,
        purchase_price=10, selling_price=20
    )
    session.add(wine_ok)
    session.commit()
    assert wine_ok.is_below_min_stock is False
    
    # Wine without min_stock
    wine_no_min = Wine(
        name="No Min", winery="Winery", colour_id=red.id, style_id=dry.id,
        vintage_year=2020, code="N-001", quantity=5,
        purchase_price=10, selling_price=20
    )
    session.add(wine_no_min)
    session.commit()
    assert wine_no_min.is_below_min_stock is False


def test_create_stock_movement(session, sample_wine: Wine):
    """
    Test creation of StockMovement model.
    """
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


def test_stock_movement_datetime_without_microseconds(session, sample_wine):
    """
    Test that StockMovement.datetime has no microseconds.
    """
    movement = StockMovement(
        wine_id=sample_wine.id,
        transaction_type="purchase",
        quantity=5,
        price=Decimal("10.00"),
    )
    session.add(movement)
    session.commit()
    
    assert movement.datetime.microsecond == 0


def test_stock_movement_validates_transaction_type_lowercase(session, sample_wine):
    """
    Test that StockMovement.transaction_type is converted to lowercase.
    """
    movement = StockMovement(
        wine_id=sample_wine.id,
        transaction_type="PURCHASE",
        quantity=5,
        price=Decimal("10.00"),
    )
    session.add(movement)
    session.commit()
    
    assert movement.transaction_type == "purchase"


def test_stock_movement_all_ordered_by_datetime(session, sample_wine):
    """
    Test StockMovement.all_ordered_by_datetime returns movements sorted by date.
    """
    # Create movements with different timestamps
    movements = [
        StockMovement(wine_id=sample_wine.id, transaction_type="purchase", 
                     quantity=5, price=Decimal("10.00")),
        StockMovement(wine_id=sample_wine.id, transaction_type="sale", 
                     quantity=2, price=Decimal("15.00")),
        StockMovement(wine_id=sample_wine.id, transaction_type="purchase", 
                     quantity=3, price=Decimal("10.00")),
    ]
    session.add_all(movements)
    session.commit()
    
    # Test all movements (newest first)
    all_movements = StockMovement.all_ordered_by_datetime(session)
    assert len(all_movements) == 3
    assert all_movements[0].datetime >= all_movements[1].datetime
    assert all_movements[1].datetime >= all_movements[2].datetime
    
    # Test filtered by sale
    sales = StockMovement.all_ordered_by_datetime(session, filter="sale")
    assert len(sales) == 1
    assert sales[0].transaction_type == "sale"
    
    # Test filtered by purchase
    purchases = StockMovement.all_ordered_by_datetime(session, filter="purchase")
    assert len(purchases) == 2
    assert all(m.transaction_type == "purchase" for m in purchases)


def test_stock_movement_insert_updates_wine_quantity(session, sample_wine):
    """
    Test that inserting a StockMovement automatically updates wine quantity.
    """
    initial_qty = sample_wine.quantity

    # Purchase should increase stock
    purchase = StockMovement(
        wine_id=sample_wine.id,
        transaction_type="purchase",
        quantity=5,
        price=Decimal("10.00"),
    )
    session.add(purchase)
    session.commit()
    session.refresh(sample_wine)
    assert sample_wine.quantity == initial_qty + 5

    # Sale should decrease stock
    sale = StockMovement(
        wine_id=sample_wine.id,
        transaction_type="sale",
        quantity=2,
        price=Decimal("15.00"),
    )
    session.add(sale)
    session.commit()
    session.refresh(sample_wine)
    assert sample_wine.quantity == initial_qty + 5 - 2


def test_stock_movement_update_adjusts_wine_quantity(session, sample_wine: Wine):
    """
    Test that updating a StockMovement correctly adjusts wine quantity.
    """
    initial_qty = sample_wine.quantity

    movement = StockMovement(
        wine_id=sample_wine.id,
        transaction_type="purchase",
        quantity=10,
        price=Decimal("12.00"),
    )
    session.add(movement)
    session.commit()
    session.refresh(sample_wine)
    assert sample_wine.quantity == initial_qty + 10

    # Change to "sale" with a different quantity
    movement.transaction_type = "sale"
    movement.quantity = 4
    session.commit()
    session.refresh(sample_wine)

    # Expected effect:
    # - Revert old value: -10 (previously purchase of 10)
    # - Apply new value: -4 (now sale of 4)
    assert sample_wine.quantity == initial_qty - 4


def test_stock_movement_update_quantity_only(session, sample_wine):
    """
    Test that updating only quantity adjusts wine quantity correctly.
    """
    initial_qty = sample_wine.quantity

    movement = StockMovement(
        wine_id=sample_wine.id,
        transaction_type="purchase",
        quantity=10,
        price=Decimal("12.00"),
    )
    session.add(movement)
    session.commit()
    session.refresh(sample_wine)
    assert sample_wine.quantity == initial_qty + 10

    # Change only the quantity
    movement.quantity = 15
    session.commit()
    session.refresh(sample_wine)

    # Expected: -10 (old) + 15 (new) = +5 net change
    assert sample_wine.quantity == initial_qty + 15


def test_stock_movement_update_no_change(session, sample_wine):
    """
    Test that updating with no actual changes doesn't affect wine quantity.
    """
    initial_qty = sample_wine.quantity

    movement = StockMovement(
        wine_id=sample_wine.id,
        transaction_type="purchase",
        quantity=10,
        price=Decimal("12.00"),
    )
    session.add(movement)
    session.commit()
    session.refresh(sample_wine)
    assert sample_wine.quantity == initial_qty + 10

    # "Update" with same values
    movement.price = Decimal("15.00")  # Change only price (not quantity or type)
    session.commit()
    session.refresh(sample_wine)

    # Quantity should remain unchanged
    assert sample_wine.quantity == initial_qty + 10


def test_stock_movement_delete_reverts_wine_quantity(session, sample_wine):
    """
    Test that deleting a StockMovement reverts the wine quantity change.
    """
    initial_qty = sample_wine.quantity

    movement = StockMovement(
        wine_id=sample_wine.id,
        transaction_type="purchase",
        quantity=7,
        price=Decimal("11.00"),
    )
    session.add(movement)
    session.commit()
    session.refresh(sample_wine)
    assert sample_wine.quantity == initial_qty + 7

    # Delete the movement
    session.delete(movement)
    session.commit()
    session.refresh(sample_wine)

    # Stock should return to the initial value
    assert sample_wine.quantity == initial_qty