"""
Validators for inputs.
"""
from datetime import datetime
from decimal import Decimal, InvalidOperation

def validate_string(input_name: str, input_content: str) -> str:
    """
    Strips the string and validates if it has less than 2 chars.
    Parameters:
        - input_name: Name of the input, referenced if an error is raised.
        - input_content: String that needs to be validated.
    Returns:
        - Cleaned version of the input_content
    """
    cleaned_input = input_content.strip()
    if len(cleaned_input) < 2:
        raise ValueError(
            f"The field '{input_name.capitalize()}' should have at least 2 characters."
        )
    return cleaned_input

def validate_dropdown(input_name: str, input_content: str) -> str | None:
    """
    Checks that the selected option of the dropdown is not "".
    Parameters:
        - input_name: Name of the input, referenced if an error is raised.
        - input_content: Selected option in the dropdown that needs to be validated.
    Returns:
        - Cleaned version of the input_content
    """
    cleaned_input = input_content.strip().lower()
    if not cleaned_input:
        raise ValueError(
            f"You haven't selected an option for the field '{input_name.capitalize()}'."
        )
    return cleaned_input

def validate_year(input_name: str, input_content: str) -> int:
    """
    Checks that the user picked a non blank option of the dropdown.
    Parameters:
        - input_name: Name of the input, referenced if an error is raised.
        - input_content: Selected option in the dropdown that needs to be validated.
    Returns:
        - An int versin of the input_content (year).
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

def validate_int(input_name: str, input_content: str, allowed_signs: str = "all") -> int:
    """
    Validates the input_content which should be > 0 if allowed_signs is positive,
    or < 0 if allowed_sings is negative.
    Parameters:
        - input_name: Name of the input, referenced if an error is raised.
        - input_content: Int value of the input.
        - allowed_signs: Available signs are all, positive, or negative.
    Returns:
        - The input_content (number).
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
            f"than 0."
        )

    if allowed_signs == "negative" and input_content_int > 0:
        raise ValueError(
            f"The field '{input_name.title()}' should contain a number lower "
            f"than 0."
        )
    
    return input_content_int

def validate_decimal(input_name: str, input_content: str) -> Decimal:
    """
    Validates the input_content which should be a a decimal value.
    Parameters:
        - input_name: Name of the input, referenced if an error is raised.
        - input_content: Int value of the input.
    Returns:
        - The input_content (decimal number).
    """
    # Cover edge case field is ".".
    if input_content == ".":
        input_content = 0

    # Convert content into decimal
    try:
        input_content_dec = Decimal(input_content)
    except (TypeError, ValueError, InvalidOperation):
        raise ValueError(
            f"The field '{input_name.title()}' should contain a price separated "
            f"by dot."
        )

    return input_content_dec