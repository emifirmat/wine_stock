"""
Input validation utilities for form fields.

This module provides validators for different types of user inputs,
including strings, dropdowns, years, integers, and decimal numbers.
All validators raise ValueError with descriptive messages on validation failure.
"""
from datetime import datetime
from decimal import Decimal, InvalidOperation

def validate_string(input_name: str, input_content: str) -> str:
    """
    Strip whitespace and validate minimum string length.
    
    Parameters:
        input_name: Name of the input field, used in error messages
        input_content: String value to be validated
        
    Returns:
        Cleaned and validated string
        
    Raises:
        ValueError: If string has fewer than 2 characters after stripping
    """
    cleaned_input = input_content.strip()
    if len(cleaned_input) < 2:
        raise ValueError(
            f"The field '{input_name.capitalize()}' should have at least 2 characters."
        )
    return cleaned_input

def validate_dropdown(input_name: str, input_content: str) -> str:
    """
    Validate that a dropdown option has been selected.
    
    Parameters:
        input_name: Name of the dropdown field, used in error messages
        input_content: Selected dropdown option to be validated
        
    Returns:
        Cleaned and lowercased dropdown value
        
    Raises:
        ValueError: If no option is selected (empty string)
    """
    cleaned_input = input_content.strip().lower()
    if not cleaned_input:
        raise ValueError(
            f"You haven't selected an option for the field '{input_name.capitalize()}'."
        )
    return cleaned_input

def validate_year(input_name: str, input_content: str) -> int:
    """
    Validate that the input is a valid year between 0 and current year.
    
    Parameters:
        input_name: Name of the input field, used in error messages
        input_content: String representation of the year to be validated
        
    Returns:
        Validated year as an integer
        
    Raises:
        ValueError: If input is not numeric or outside valid year range
    """
    starting_year = 0
    end_year = datetime.now().year

    try:
        input_content_year = int(input_content)
    except (TypeError, ValueError):
        raise ValueError(
            f"The field '{input_name.title()}' should contain only numbers."
        )

    if not starting_year <= input_content_year <= end_year:
        raise ValueError(
            f"The field '{input_name.title()}' should be between "
            f"{starting_year} and {end_year}."
        )
    return input_content_year

def validate_int(
    input_name: str, input_content: str, allowed_signs: str = "all"
) -> int:
    """
    Validate integer input with optional sign constraints.
    
    Parameters:
        input_name: Name of the input field, used in error messages
        input_content: String representation of the integer to be validated
        allowed_signs: Sign constraint - "all", "positive", or "negative"
        
    Returns:
        Validated integer value
        
    Raises:
        ValueError: If input is not numeric or violates sign constraints
    """
    try:
        input_content_int = int(input_content)
    except (TypeError, ValueError):
        raise ValueError(
            f"The field '{input_name.title()}' should contain only numbers."
        )

    if allowed_signs == "positive" and input_content_int < 0:
        raise ValueError(
            f"The field '{input_name.title()}' should contain a number bigger "
            "than 0."
        )

    if allowed_signs == "negative" and input_content_int > 0:
        raise ValueError(
            f"The field '{input_name.title()}' should contain a number lower "
            "than 0."
        )
    
    return input_content_int

def validate_decimal(input_name: str, input_content: str) -> Decimal:
    """
    Validate decimal input and convert to Decimal type.
    
    Parameters:
        input_name: Name of the input field, used in error messages
        input_content: String representation of the decimal to be validated
        
    Returns:
        Validated Decimal value
        
    Raises:
        ValueError: If input cannot be converted to a valid decimal
        
    Note:
        Handles edge case where input is "." by converting it to 0
    """
    # Cover edge case where field is "."
    if input_content == ".":
        input_content = "0"

    # Convert content to decimal
    try:
        input_content_dec = Decimal(input_content)
    except (TypeError, ValueError, InvalidOperation):
        raise ValueError(
            f"The field '{input_name.title()}' should contain a price separated "
            "by dot."
        )

    return input_content_dec