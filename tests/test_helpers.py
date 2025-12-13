"""
Unit tests for helper utility functions.

This module tests utility functions from helpers.py including database
utilities, image processing, and path handling functions.
"""
import pytest
from decimal import Decimal
from pathlib import Path
from unittest.mock import Mock
from PIL import Image

from db.models import Colour, Wine
from helpers import (
    populate_db_model, deep_getattr, get_coords_center, load_image_from_file
)


# == Database utilities ==

def test_populate_creates_entries(session):
    """
    Test that populate_db_model creates new entries.
    """
    populate_db_model(["Red", "White", "Rosé"], Colour, session)

    results = session.query(Colour).all()
    names = [colour.name for colour in results]

    assert set(names) == {"Red", "White", "Rosé"}
    assert len(names) == 3


def test_populate_does_not_duplicate(session):
    """
    Test that populate_db_model doesn't create duplicate entries.
    """
    #  Add initial values
    populate_db_model(["Red", "White"], Colour, session)

    # Attempt to repopulate with overlapping values
    populate_db_model(["Red", "White", "Rosé"], Colour, session)

    results = session.query(Colour).all()
    names = [colour.name for colour in results]

    assert set(names) == {"Red", "White", "Rosé"}
    assert len(names) == 3 


def test_populate_with_empty_list(session):
    """
    Test that populate_db_model handles empty list without errors.
    """
    populate_db_model([], Colour, session)
    
    results = session.query(Colour).all()
    assert len(results) == 0


# == Attribute utilities ==

def test_deep_getattr_single_level(sample_wine):
    """
    Test deep_getattr with single level attribute.
    """
    result = deep_getattr(sample_wine, "name")
    
    assert result == "Test Wine"


def test_deep_getattr_nested_attribute(session, sample_wine):
    """
    Test deep_getattr with nested attribute using dot notation.
    """
    result = deep_getattr(sample_wine, "colour.name")
    
    assert result == "Red"


def test_deep_getattr_multiple_levels(session, sample_color_style_varietal):
    """
    Test deep_getattr with deeply nested attributes.
    """
    red, _, _ = sample_color_style_varietal
    
    # Create a wine with the colour
    wine = Wine(
        name="Deep Test",
        winery="Test Winery",
        colour_id=red.id,
        style_id=1,
        vintage_year=2020,
        code="DT-001",
        purchase_price=Decimal("10.00"),
        selling_price=Decimal("15.00"),
    )
    session.add(wine)
    session.commit()
    
    # Access wine.colour.name through deep_getattr
    result = deep_getattr(wine, "colour.name")
    assert result == "Red"


def test_deep_getattr_returns_none_for_missing_attribute(sample_wine):
    """
    Test that deep_getattr returns None for non-existent attributes.
    """
    result = deep_getattr(sample_wine, "nonexistent.attribute")
    
    assert result is None


def test_deep_getattr_returns_none_for_none_intermediate(sample_wine):
    """
    Test that deep_getattr returns None if intermediate attribute is None.
    """
    # Sample wine has no varietal in the fixture
    sample_wine.varietal_id = None
    
    result = deep_getattr(sample_wine, "varietal.name")
    
    assert result is None


# == File operations ==

def test_load_image_from_file_preserves_extension(tmp_path):
    """
    Test that load_image_from_file preserves the original file extension.
    """
    # Create a JPG source image
    source_image = tmp_path / "source.jpg"
    img = Image.new('RGB', (100, 100), color='blue')
    img.save(source_image, format='JPEG')
    
    result = load_image_from_file(str(source_image))
    
    assert result.suffix == ".jpg"
    assert "logo_user" in result.name


# == UI utilities ==

def test_get_coords_center_returns_tuple():
    """
    Test that get_coords_center returns a tuple of coordinates.
    """
    mock_widget = Mock()
    mock_widget.winfo_screenwidth.return_value = 1920
    mock_widget.winfo_screenheight.return_value = 1080
    
    x, y = get_coords_center(mock_widget)
    
    assert x == 960
    assert y == 540
    assert isinstance(x, int)
    assert isinstance(y, int)


def test_get_coords_center_calculates_correctly():
    """
    Test that get_coords_center correctly calculates center coordinates.
    """
    mock_widget = Mock()
    mock_widget.winfo_screenwidth.return_value = 1280
    mock_widget.winfo_screenheight.return_value = 720
    
    x, y = get_coords_center(mock_widget)
    
    assert x == 640
    assert y == 360


def test_get_coords_center_handles_odd_dimensions():
    """
    Test that get_coords_center uses integer division for odd screen sizes.
    """
    mock_widget = Mock()
    mock_widget.winfo_screenwidth.return_value = 1921
    mock_widget.winfo_screenheight.return_value = 1081
    
    x, y = get_coords_center(mock_widget)
    
    # Integer division should round down
    assert x == 960
    assert y == 540