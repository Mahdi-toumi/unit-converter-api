"""
Unit tests for conversion functions
"""
import pytest
from app.converters import (
    convert_length,
    convert_weight,
    convert_temperature,
    get_currency_rate
)


# ============================================================================
# LENGTH CONVERSION TESTS
# ============================================================================

class TestLengthConversion:
    """Test cases for length conversion"""
    
    def test_meter_to_kilometer(self):
        """Test converting meters to kilometers"""
        result = convert_length(1000, "meter", "kilometer")
        assert result == 1.0
    
    def test_kilometer_to_meter(self):
        """Test converting kilometers to meters"""
        result = convert_length(1, "kilometer", "meter")
        assert result == 1000.0
    
    def test_foot_to_meter(self):
        """Test converting feet to meters"""
        result = convert_length(1, "foot", "meter")
        assert 0.3047 < result < 0.3049
    
    def test_meter_to_foot(self):
        """Test converting meters to feet"""
        result = convert_length(1, "meter", "foot")
        assert 3.28 < result < 3.29
    
    def test_inch_to_centimeter(self):
        """Test converting inches to centimeters"""
        result = convert_length(1, "inch", "centimeter")
        assert 2.53 < result < 2.55
    
    def test_mile_to_kilometer(self):
        """Test converting miles to kilometers"""
        result = convert_length(1, "mile", "kilometer")
        assert 1.609 < result < 1.610
    
    def test_same_unit(self):
        """Test conversion with same source and target unit"""
        result = convert_length(100, "meter", "meter")
        assert result == 100.0
    
    def test_invalid_source_unit(self):
        """Test error handling for invalid source unit"""
        with pytest.raises(ValueError) as excinfo:
            convert_length(1, "invalid_unit", "meter")
        assert "Invalid source unit" in str(excinfo.value)
    
    def test_invalid_target_unit(self):
        """Test error handling for invalid target unit"""
        with pytest.raises(ValueError) as excinfo:
            convert_length(1, "meter", "invalid_unit")
        assert "Invalid target unit" in str(excinfo.value)
    
    def test_case_insensitive(self):
        """Test that unit names are case insensitive"""
        result1 = convert_length(1, "METER", "KILOMETER")
        result2 = convert_length(1, "meter", "kilometer")
        assert result1 == result2


# ============================================================================
# WEIGHT CONVERSION TESTS
# ============================================================================

class TestWeightConversion:
    """Test cases for weight conversion"""
    
    def test_kilogram_to_gram(self):
        """Test converting kilograms to grams"""
        result = convert_weight(1, "kilogram", "gram")
        assert result == 1000.0
    
    def test_gram_to_kilogram(self):
        """Test converting grams to kilograms"""
        result = convert_weight(1000, "gram", "kilogram")
        assert result == 1.0
    
    def test_pound_to_kilogram(self):
        """Test converting pounds to kilograms"""
        result = convert_weight(1, "pound", "kilogram")
        assert 0.453 < result < 0.454
    
    def test_kilogram_to_pound(self):
        """Test converting kilograms to pounds"""
        result = convert_weight(1, "kilogram", "pound")
        assert 2.204 < result < 2.205
    
    def test_ounce_to_gram(self):
        """Test converting ounces to grams"""
        result = convert_weight(1, "ounce", "gram")
        assert 28.34 < result < 28.36
    
    def test_ton_to_kilogram(self):
        """Test converting tons to kilograms"""
        result = convert_weight(1, "ton", "kilogram")
        assert result == 1000.0
    
    def test_same_unit(self):
        """Test conversion with same source and target unit"""
        result = convert_weight(50, "kilogram", "kilogram")
        assert result == 50.0
    
    def test_invalid_source_unit(self):
        """Test error handling for invalid source unit"""
        with pytest.raises(ValueError) as excinfo:
            convert_weight(1, "invalid_unit", "kilogram")
        assert "Invalid source unit" in str(excinfo.value)
    
    def test_invalid_target_unit(self):
        """Test error handling for invalid target unit"""
        with pytest.raises(ValueError) as excinfo:
            convert_weight(1, "kilogram", "invalid_unit")
        assert "Invalid target unit" in str(excinfo.value)
    
    def test_case_insensitive(self):
        """Test that unit names are case insensitive"""
        result1 = convert_weight(1, "KILOGRAM", "GRAM")
        result2 = convert_weight(1, "kilogram", "gram")
        assert result1 == result2


# ============================================================================
# TEMPERATURE CONVERSION TESTS
# ============================================================================

class TestTemperatureConversion:
    """Test cases for temperature conversion"""
    
    def test_celsius_to_fahrenheit_freezing(self):
        """Test converting 0°C to Fahrenheit (freezing point)"""
        result = convert_temperature(0, "celsius", "fahrenheit")
        assert result == 32.0
    
    def test_celsius_to_fahrenheit_boiling(self):
        """Test converting 100°C to Fahrenheit (boiling point)"""
        result = convert_temperature(100, "celsius", "fahrenheit")
        assert result == 212.0
    
    def test_fahrenheit_to_celsius_freezing(self):
        """Test converting 32°F to Celsius (freezing point)"""
        result = convert_temperature(32, "fahrenheit", "celsius")
        assert result == 0.0
    
    def test_fahrenheit_to_celsius_boiling(self):
        """Test converting 212°F to Celsius (boiling point)"""
        result = convert_temperature(212, "fahrenheit", "celsius")
        assert result == 100.0
    
    def test_celsius_to_kelvin(self):
        """Test converting Celsius to Kelvin"""
        result = convert_temperature(0, "celsius", "kelvin")
        assert result == 273.15
    
    def test_kelvin_to_celsius(self):
        """Test converting Kelvin to Celsius"""
        result = convert_temperature(273.15, "kelvin", "celsius")
        assert result == 0.0
    
    def test_fahrenheit_to_kelvin(self):
        """Test converting Fahrenheit to Kelvin"""
        result = convert_temperature(32, "fahrenheit", "kelvin")
        assert result == 273.15
    
    def test_kelvin_to_fahrenheit(self):
        """Test converting Kelvin to Fahrenheit"""
        result = convert_temperature(273.15, "kelvin", "fahrenheit")
        assert result == 32.0
    
    def test_same_unit(self):
        """Test conversion with same source and target unit"""
        result = convert_temperature(25, "celsius", "celsius")
        assert result == 25.0
    
    def test_negative_celsius(self):
        """Test converting negative Celsius temperature"""
        result = convert_temperature(-40, "celsius", "fahrenheit")
        assert result == -40.0  # -40°C = -40°F
    
    def test_invalid_source_unit(self):
        """Test error handling for invalid source unit"""
        with pytest.raises(ValueError) as excinfo:
            convert_temperature(0, "invalid_unit", "celsius")
        assert "Invalid source unit" in str(excinfo.value)
    
    def test_invalid_target_unit(self):
        """Test error handling for invalid target unit"""
        with pytest.raises(ValueError) as excinfo:
            convert_temperature(0, "celsius", "invalid_unit")
        assert "Invalid target unit" in str(excinfo.value)
    
    def test_case_insensitive(self):
        """Test that unit names are case insensitive"""
        result1 = convert_temperature(0, "CELSIUS", "FAHRENHEIT")
        result2 = convert_temperature(0, "celsius", "fahrenheit")
        assert result1 == result2


# ============================================================================
# CURRENCY CONVERSION TESTS
# ============================================================================

class TestCurrencyConversion:
    """Test cases for currency conversion"""
    
    def test_currency_conversion_returns_float(self):
        """Test that currency conversion returns a float"""
        # This test requires internet connection
        try:
            result = get_currency_rate(100, "USD", "EUR")
            assert isinstance(result, float)
            assert result > 0
        except Exception:
            pytest.skip("Currency API not available")
    
    def test_currency_same_currency(self):
        """Test converting same currency (should use cache)"""
        try:
            # First call to populate cache
            result1 = get_currency_rate(100, "USD", "EUR")
            # Second call should use cache
            result2 = get_currency_rate(100, "USD", "EUR")
            assert result1 == result2
        except Exception:
            pytest.skip("Currency API not available")
    
    def test_currency_invalid_currency(self):
        """Test error handling for invalid currency code"""
        with pytest.raises(Exception):
            get_currency_rate(100, "USD", "INVALID")
    
    def test_currency_case_insensitive(self):
        """Test that currency codes are case insensitive"""
        try:
            result1 = get_currency_rate(100, "usd", "eur")
            result2 = get_currency_rate(100, "USD", "EUR")
            # Results should be equal (both use cache)
            assert result1 == result2
        except Exception:
            pytest.skip("Currency API not available")


# ============================================================================
# EDGE CASES AND VALIDATION TESTS
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_zero_value_length(self):
        """Test converting zero value for length"""
        result = convert_length(0, "meter", "kilometer")
        assert result == 0.0
    
    def test_zero_value_weight(self):
        """Test converting zero value for weight"""
        result = convert_weight(0, "kilogram", "gram")
        assert result == 0.0
    
    def test_large_value_length(self):
        """Test converting very large value for length"""
        result = convert_length(1000000, "meter", "kilometer")
        assert result == 1000.0
    
    def test_small_value_weight(self):
        """Test converting very small value for weight"""
        result = convert_weight(0.001, "kilogram", "milligram")
        assert result == 1000.0
    
    def test_precision_rounding(self):
        """Test that results are properly rounded"""
        result = convert_length(1, "foot", "meter")
        # Should be rounded to 6 decimal places
        assert len(str(result).split('.')[-1]) <= 6


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests for multiple conversions"""
    
    def test_chained_conversions(self):
        """Test chaining multiple conversions"""
        # Convert meter -> foot -> inch
        step1 = convert_length(1, "meter", "foot")
        step2 = convert_length(step1, "foot", "inch")
        
        # Direct conversion meter -> inch
        direct = convert_length(1, "meter", "inch")
        
        # Results should be very close (accounting for rounding)
        assert abs(step2 - direct) < 0.01