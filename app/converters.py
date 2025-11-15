"""
Unit conversion logic for length, weight, temperature, and currency
"""
import requests
from typing import Dict, Optional
from app.config import settings


# Conversion factors to base units (meters for length, kilograms for weight)
LENGTH_FACTORS: Dict[str, float] = {
    "meter": 1.0,
    "kilometer": 1000.0,
    "centimeter": 0.01,
    "millimeter": 0.001,
    "mile": 1609.34,
    "yard": 0.9144,
    "foot": 0.3048,
    "inch": 0.0254,
}

WEIGHT_FACTORS: Dict[str, float] = {
    "kilogram": 1.0,
    "gram": 0.001,
    "milligram": 0.000001,
    "pound": 0.453592,
    "ounce": 0.0283495,
    "ton": 1000.0,
}

# In-memory cache for currency rates
_CURRENCY_CACHE: Dict[str, float] = {}


def convert_length(value: float, from_unit: str, to_unit: str) -> float:
    """
    Convert length between different units
    
    Args:
        value: The numeric value to convert
        from_unit: Source unit (e.g., 'meter', 'foot')
        to_unit: Target unit (e.g., 'kilometer', 'inch')
    
    Returns:
        Converted value rounded to 6 decimal places
    
    Raises:
        ValueError: If units are not supported
    
    Example:
        >>> convert_length(1000, "meter", "kilometer")
        1.0
        >>> convert_length(1, "foot", "meter")
        0.3048
    """
    from_unit = from_unit.lower()
    to_unit = to_unit.lower()
    
    if from_unit not in LENGTH_FACTORS:
        raise ValueError(
            f"Invalid source unit '{from_unit}'. "
            f"Supported: {', '.join(LENGTH_FACTORS.keys())}"
        )
    
    if to_unit not in LENGTH_FACTORS:
        raise ValueError(
            f"Invalid target unit '{to_unit}'. "
            f"Supported: {', '.join(LENGTH_FACTORS.keys())}"
        )
    
    # Convert to base unit (meters), then to target unit
    meters = value * LENGTH_FACTORS[from_unit]
    result = meters / LENGTH_FACTORS[to_unit]
    
    return round(result, 6)


def convert_weight(value: float, from_unit: str, to_unit: str) -> float:
    """
    Convert weight between different units
    
    Args:
        value: The numeric value to convert
        from_unit: Source unit (e.g., 'kilogram', 'pound')
        to_unit: Target unit (e.g., 'gram', 'ounce')
    
    Returns:
        Converted value rounded to 6 decimal places
    
    Raises:
        ValueError: If units are not supported
    
    Example:
        >>> convert_weight(1, "kilogram", "gram")
        1000.0
        >>> convert_weight(1, "pound", "kilogram")
        0.453592
    """
    from_unit = from_unit.lower()
    to_unit = to_unit.lower()
    
    if from_unit not in WEIGHT_FACTORS:
        raise ValueError(
            f"Invalid source unit '{from_unit}'. "
            f"Supported: {', '.join(WEIGHT_FACTORS.keys())}"
        )
    
    if to_unit not in WEIGHT_FACTORS:
        raise ValueError(
            f"Invalid target unit '{to_unit}'. "
            f"Supported: {', '.join(WEIGHT_FACTORS.keys())}"
        )
    
    # Convert to base unit (kilograms), then to target unit
    kilograms = value * WEIGHT_FACTORS[from_unit]
    result = kilograms / WEIGHT_FACTORS[to_unit]
    
    return round(result, 6)


def convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
    """
    Convert temperature between Celsius, Fahrenheit, and Kelvin
    
    Args:
        value: The temperature value to convert
        from_unit: Source unit ('celsius', 'fahrenheit', 'kelvin')
        to_unit: Target unit ('celsius', 'fahrenheit', 'kelvin')
    
    Returns:
        Converted temperature rounded to 2 decimal places
    
    Raises:
        ValueError: If units are not supported
    
    Example:
        >>> convert_temperature(0, "celsius", "fahrenheit")
        32.0
        >>> convert_temperature(273.15, "kelvin", "celsius")
        0.0
    """
    from_unit = from_unit.lower()
    to_unit = to_unit.lower()
    
    valid_units = {"celsius", "fahrenheit", "kelvin"}
    
    if from_unit not in valid_units:
        raise ValueError(
            f"Invalid source unit '{from_unit}'. "
            f"Supported: {', '.join(valid_units)}"
        )
    
    if to_unit not in valid_units:
        raise ValueError(
            f"Invalid target unit '{to_unit}'. "
            f"Supported: {', '.join(valid_units)}"
        )
    
    # Same unit, no conversion needed
    if from_unit == to_unit:
        return round(value, 2)
    
    # Conversion logic
    if from_unit == "celsius":
        if to_unit == "fahrenheit":
            result = (value * 9/5) + 32
        else:  # to kelvin
            result = value + 273.15
    
    elif from_unit == "fahrenheit":
        if to_unit == "celsius":
            result = (value - 32) * 5/9
        else:  # to kelvin
            result = (value - 32) * 5/9 + 273.15
    
    else:  # from kelvin
        if to_unit == "celsius":
            result = value - 273.15
        else:  # to fahrenheit
            result = (value - 273.15) * 9/5 + 32
    
    return round(result, 2)


def get_currency_rate(
    value: float, 
    from_currency: str, 
    to_currency: str
) -> float:
    """
    Convert currency using live exchange rates
    
    Args:
        value: Amount to convert
        from_currency: Source currency code (e.g., 'USD', 'EUR')
        to_currency: Target currency code (e.g., 'TND', 'GBP')
    
    Returns:
        Converted amount rounded to 2 decimal places
    
    Raises:
        Exception: If API call fails or currency not found
    
    Example:
        >>> get_currency_rate(100, "USD", "EUR")
        # Returns current exchange rate * 100
    """
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()
    
    # Check cache first
    cache_key = f"{from_currency}_{to_currency}"
    if cache_key in _CURRENCY_CACHE:
        return round(value * _CURRENCY_CACHE[cache_key], 2)
    
    try:
        # Call external API
        url = f"{settings.CURRENCY_API_URL}/{from_currency}"
        response = requests.get(url, timeout=settings.CURRENCY_API_TIMEOUT)
        response.raise_for_status()
        
        data = response.json()
        
        if "rates" not in data:
            raise Exception("Invalid API response format")
        
        if to_currency not in data["rates"]:
            raise ValueError(
                f"Currency '{to_currency}' not found in exchange rates"
            )
        
        # Get and cache the rate
        rate = data["rates"][to_currency]
        _CURRENCY_CACHE[cache_key] = rate
        
        return round(value * rate, 2)
    
    except requests.exceptions.Timeout:
        raise Exception(
            f"Currency API timeout after {settings.CURRENCY_API_TIMEOUT}s"
        )
    except requests.exceptions.RequestException as e:
        raise Exception(f"Currency API request failed: {str(e)}")
    except Exception as e:
        raise Exception(f"Currency conversion failed: {str(e)}")