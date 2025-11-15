"""
Unit Converter API - Main application
FastAPI REST API for converting units (length, weight, temperature, currency)
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal
import time

from app.config import settings
from app.converters import (
    convert_length,
    convert_weight,
    convert_temperature,
    get_currency_rate
)
from app.observability import (
    setup_metrics,
    setup_tracing,
    track_request,
    log_conversion,
    logger
)


# ============================================================================
# PYDANTIC MODELS (Request/Response schemas)
# ============================================================================

class ConversionRequest(BaseModel):
    """Request model for unit conversion"""
    value: float = Field(..., description="Value to convert", example=100.0)
    from_unit: str = Field(..., description="Source unit", example="meter")
    to_unit: str = Field(..., description="Target unit", example="foot")
    
    class Config:
        schema_extra = {
            "example": {
                "value": 100,
                "from_unit": "meter",
                "to_unit": "foot"
            }
        }


class ConversionResponse(BaseModel):
    """Response model for unit conversion"""
    original_value: float = Field(..., description="Original value")
    converted_value: float = Field(..., description="Converted value")
    from_unit: str = Field(..., description="Source unit")
    to_unit: str = Field(..., description="Target unit")
    
    class Config:
        schema_extra = {
            "example": {
                "original_value": 100.0,
                "converted_value": 328.084,
                "from_unit": "meter",
                "to_unit": "foot"
            }
        }


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: float


# ============================================================================
# FASTAPI APPLICATION SETUP
# ============================================================================

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware (allow all origins for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup observability
setup_metrics(app)
setup_tracing(app)

logger.info(f"Starting {settings.API_TITLE} v{settings.API_VERSION}")


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/", tags=["General"])
async def root():
    """Root endpoint with API information"""
    logger.info("Root endpoint accessed")
    return {
        "message": f"{settings.API_TITLE}",
        "version": settings.API_VERSION,
        "documentation": "/docs",
        "health": "/health",
        "metrics": "/metrics"
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """Health check endpoint for monitoring"""
    return HealthResponse(
        status="healthy",
        version=settings.API_VERSION,
        timestamp=time.time()
    )


@app.post(
    "/convert/length",
    response_model=ConversionResponse,
    tags=["Conversions"],
    summary="Convert length units",
    description="Convert between meter, kilometer, foot, inch, mile, yard, etc."
)
async def convert_length_endpoint(request: ConversionRequest):
    """
    Convert length between different units
    
    Supported units: meter, kilometer, centimeter, millimeter, 
                    mile, yard, foot, inch
    """
    start_time = time.time()
    
    try:
        result = convert_length(
            request.value,
            request.from_unit,
            request.to_unit
        )
        
        duration = time.time() - start_time
        track_request("length", duration, "success")
        log_conversion(
            "length",
            request.value,
            result,
            request.from_unit,
            request.to_unit,
            duration
        )
        
        return ConversionResponse(
            original_value=request.value,
            converted_value=result,
            from_unit=request.from_unit,
            to_unit=request.to_unit
        )
    
    except ValueError as e:
        duration = time.time() - start_time
        track_request("length", duration, "error")
        logger.error(f"Length conversion error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post(
    "/convert/weight",
    response_model=ConversionResponse,
    tags=["Conversions"],
    summary="Convert weight units",
    description="Convert between kilogram, gram, pound, ounce, ton, etc."
)
async def convert_weight_endpoint(request: ConversionRequest):
    """
    Convert weight between different units
    
    Supported units: kilogram, gram, milligram, pound, ounce, ton
    """
    start_time = time.time()
    
    try:
        result = convert_weight(
            request.value,
            request.from_unit,
            request.to_unit
        )
        
        duration = time.time() - start_time
        track_request("weight", duration, "success")
        log_conversion(
            "weight",
            request.value,
            result,
            request.from_unit,
            request.to_unit,
            duration
        )
        
        return ConversionResponse(
            original_value=request.value,
            converted_value=result,
            from_unit=request.from_unit,
            to_unit=request.to_unit
        )
    
    except ValueError as e:
        duration = time.time() - start_time
        track_request("weight", duration, "error")
        logger.error(f"Weight conversion error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post(
    "/convert/temperature",
    response_model=ConversionResponse,
    tags=["Conversions"],
    summary="Convert temperature units",
    description="Convert between Celsius, Fahrenheit, and Kelvin"
)
async def convert_temperature_endpoint(request: ConversionRequest):
    """
    Convert temperature between different units
    
    Supported units: celsius, fahrenheit, kelvin
    """
    start_time = time.time()
    
    try:
        result = convert_temperature(
            request.value,
            request.from_unit,
            request.to_unit
        )
        
        duration = time.time() - start_time
        track_request("temperature", duration, "success")
        log_conversion(
            "temperature",
            request.value,
            result,
            request.from_unit,
            request.to_unit,
            duration
        )
        
        return ConversionResponse(
            original_value=request.value,
            converted_value=result,
            from_unit=request.from_unit,
            to_unit=request.to_unit
        )
    
    except ValueError as e:
        duration = time.time() - start_time
        track_request("temperature", duration, "error")
        logger.error(f"Temperature conversion error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post(
    "/convert/currency",
    response_model=ConversionResponse,
    tags=["Conversions"],
    summary="Convert currency",
    description="Convert between currencies using live exchange rates"
)
async def convert_currency_endpoint(request: ConversionRequest):
    """
    Convert currency using live exchange rates
    
    Uses exchangerate-api.com for real-time rates.
    Supports major currencies: USD, EUR, GBP, TND, etc.
    """
    start_time = time.time()
    
    try:
        result = get_currency_rate(
            request.value,
            request.from_unit,
            request.to_unit
        )
        
        duration = time.time() - start_time
        track_request("currency", duration, "success")
        log_conversion(
            "currency",
            request.value,
            result,
            request.from_unit,
            request.to_unit,
            duration
        )
        
        return ConversionResponse(
            original_value=request.value,
            converted_value=result,
            from_unit=request.from_unit,
            to_unit=request.to_unit
        )
    
    except Exception as e:
        duration = time.time() - start_time
        track_request("currency", duration, "error")
        logger.error(f"Currency conversion error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# STARTUP/SHUTDOWN EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Actions to perform on application startup"""
    logger.info("Application startup complete")
    logger.info(f"Documentation available at /docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Actions to perform on application shutdown"""
    logger.info("Application shutting down")