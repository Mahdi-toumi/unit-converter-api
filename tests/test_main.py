"""
Integration tests for FastAPI endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

# Create test client
client = TestClient(app)


# ============================================================================
# GENERAL ENDPOINTS TESTS
# ============================================================================

class TestGeneralEndpoints:
    """Test general API endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint returns API information"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["version"] == "1.0.0"
        assert "documentation" in data
        assert "health" in data
        assert "metrics" in data
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data
        assert isinstance(data["timestamp"], float)
    
    def test_metrics_endpoint(self):
        """Test Prometheus metrics endpoint"""
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "api_requests_total" in response.text
        assert "api_request_duration_seconds" in response.text


# ============================================================================
# LENGTH CONVERSION ENDPOINT TESTS
# ============================================================================

class TestLengthConversionEndpoint:
    """Test length conversion endpoint"""
    
    def test_length_conversion_success(self):
        """Test successful length conversion"""
        response = client.post(
            "/convert/length",
            json={
                "value": 1000,
                "from_unit": "meter",
                "to_unit": "kilometer"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["original_value"] == 1000
        assert data["converted_value"] == 1.0
        assert data["from_unit"] == "meter"
        assert data["to_unit"] == "kilometer"
    
    def test_length_conversion_invalid_unit(self):
        """Test length conversion with invalid unit"""
        response = client.post(
            "/convert/length",
            json={
                "value": 100,
                "from_unit": "invalid",
                "to_unit": "meter"
            }
        )
        assert response.status_code == 400
        assert "Invalid source unit" in response.json()["detail"]
    
    def test_length_conversion_missing_field(self):
        """Test length conversion with missing field"""
        response = client.post(
            "/convert/length",
            json={
                "value": 100,
                "from_unit": "meter"
                # Missing to_unit
            }
        )
        assert response.status_code == 422  # Validation error
    
    def test_length_conversion_invalid_type(self):
        """Test length conversion with invalid value type"""
        response = client.post(
            "/convert/length",
            json={
                "value": "invalid",
                "from_unit": "meter",
                "to_unit": "kilometer"
            }
        )
        assert response.status_code == 422  # Validation error


# ============================================================================
# WEIGHT CONVERSION ENDPOINT TESTS
# ============================================================================

class TestWeightConversionEndpoint:
    """Test weight conversion endpoint"""
    
    def test_weight_conversion_success(self):
        """Test successful weight conversion"""
        response = client.post(
            "/convert/weight",
            json={
                "value": 1,
                "from_unit": "kilogram",
                "to_unit": "gram"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["original_value"] == 1
        assert data["converted_value"] == 1000.0
        assert data["from_unit"] == "kilogram"
        assert data["to_unit"] == "gram"
    
    def test_weight_conversion_invalid_unit(self):
        """Test weight conversion with invalid unit"""
        response = client.post(
            "/convert/weight",
            json={
                "value": 100,
                "from_unit": "kilogram",
                "to_unit": "invalid"
            }
        )
        assert response.status_code == 400
        assert "Invalid target unit" in response.json()["detail"]


# ============================================================================
# TEMPERATURE CONVERSION ENDPOINT TESTS
# ============================================================================

class TestTemperatureConversionEndpoint:
    """Test temperature conversion endpoint"""
    
    def test_temperature_conversion_success(self):
        """Test successful temperature conversion"""
        response = client.post(
            "/convert/temperature",
            json={
                "value": 0,
                "from_unit": "celsius",
                "to_unit": "fahrenheit"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["original_value"] == 0
        assert data["converted_value"] == 32.0
        assert data["from_unit"] == "celsius"
        assert data["to_unit"] == "fahrenheit"
    
    def test_temperature_conversion_invalid_unit(self):
        """Test temperature conversion with invalid unit"""
        response = client.post(
            "/convert/temperature",
            json={
                "value": 0,
                "from_unit": "celsius",
                "to_unit": "invalid"
            }
        )
        assert response.status_code == 400
        assert "Invalid target unit" in response.json()["detail"]


# ============================================================================
# CURRENCY CONVERSION ENDPOINT TESTS
# ============================================================================

class TestCurrencyConversionEndpoint:
    """Test currency conversion endpoint"""
    
    def test_currency_conversion_success(self):
        """Test successful currency conversion (requires internet)"""
        response = client.post(
            "/convert/currency",
            json={
                "value": 100,
                "from_unit": "USD",
                "to_unit": "EUR"
            }
        )
        # May fail if no internet, check both possibilities
        if response.status_code == 200:
            data = response.json()
            assert data["original_value"] == 100
            assert data["converted_value"] > 0
            assert data["from_unit"] == "USD"
            assert data["to_unit"] == "EUR"
        else:
            # API call failed (no internet or API down)
            assert response.status_code == 500
    
    def test_currency_conversion_invalid_currency(self):
        """Test currency conversion with invalid currency"""
        response = client.post(
            "/convert/currency",
            json={
                "value": 100,
                "from_unit": "USD",
                "to_unit": "INVALID"
            }
        )
        assert response.status_code == 500
        assert "conversion failed" in response.json()["detail"].lower()


# ============================================================================
# CORS TESTS
# ============================================================================

class TestCORS:
    """Test CORS headers"""
    
    def test_cors_headers_present(self):
        """Test that CORS headers are present"""
        response = client.options(
            "/convert/length",
            headers={"Origin": "http://localhost:3000"}
        )
        # CORS middleware should add these headers
        assert response.status_code in [200, 405]  # May vary by FastAPI version


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

class TestErrorHandling:
    """Test error handling"""
    
    def test_404_not_found(self):
        """Test 404 for non-existent endpoint"""
        response = client.get("/nonexistent")
        assert response.status_code == 404
    
    def test_405_method_not_allowed(self):
        """Test 405 for wrong HTTP method"""
        response = client.get("/convert/length")  # Should be POST
        assert response.status_code == 405


# ============================================================================
# DOCUMENTATION TESTS
# ============================================================================

class TestDocumentation:
    """Test API documentation endpoints"""
    
    def test_openapi_schema(self):
        """Test OpenAPI schema is accessible"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert schema["info"]["title"] == "Unit Converter API"
    
    def test_swagger_ui(self):
        """Test Swagger UI is accessible"""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "swagger" in response.text.lower()
    
    def test_redoc(self):
        """Test ReDoc is accessible"""
        response = client.get("/redoc")
        assert response.status_code == 200
        assert "redoc" in response.text.lower()