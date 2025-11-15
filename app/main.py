from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict
import time
from contextlib import asynccontextmanager

from app.config import settings
from app.converters import convert_length, convert_weight, convert_temperature, get_currency_rate
from app.observability import setup_metrics, setup_tracing, track_request, log_conversion, logger

# ============================================================================ 
# PYDANTIC MODELS
# ============================================================================

class ConversionRequest(BaseModel):
    value: float = Field(..., description="Value to convert")
    from_unit: str = Field(..., description="Source unit")
    to_unit: str = Field(..., description="Target unit")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {"value": 100, "from_unit": "meter", "to_unit": "foot"}
        }
    )

class ConversionResponse(BaseModel):
    original_value: float
    converted_value: float
    from_unit: str
    to_unit: str
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "original_value": 100.0,
                "converted_value": 328.084,
                "from_unit": "meter",
                "to_unit": "foot"
            }
        }
    )

class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: float

# ============================================================================ 
# FASTAPI APPLICATION + LIFESPAN
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup complete")
    logger.info(f"Documentation available at /docs")
    yield
    logger.info("Application shutting down")

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
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
    return HealthResponse(
        status="healthy",
        version=settings.API_VERSION,
        timestamp=time.time()
    )

# ============================================================================ 
# Conversion endpoints
# ============================================================================

async def handle_conversion(conversion_type: str, request: ConversionRequest, converter):
    start_time = time.time()
    try:
        result = converter(request.value, request.from_unit, request.to_unit)
        duration = time.time() - start_time
        track_request(conversion_type, duration, "success")
        log_conversion(conversion_type, request.value, result, request.from_unit, request.to_unit, duration)
        return ConversionResponse(
            original_value=request.value,
            converted_value=result,
            from_unit=request.from_unit,
            to_unit=request.to_unit
        )
    except Exception as e:
        duration = time.time() - start_time
        track_request(conversion_type, duration, "error")
        logger.error(f"{conversion_type.capitalize()} conversion error: {str(e)}")
        raise HTTPException(
            status_code=400 if conversion_type != "currency" else 500,
            detail=str(e)
        )

@app.post("/convert/length", response_model=ConversionResponse, tags=["Conversions"])
async def convert_length_endpoint(request: ConversionRequest):
    return await handle_conversion("length", request, convert_length)

@app.post("/convert/weight", response_model=ConversionResponse, tags=["Conversions"])
async def convert_weight_endpoint(request: ConversionRequest):
    return await handle_conversion("weight", request, convert_weight)

@app.post("/convert/temperature", response_model=ConversionResponse, tags=["Conversions"])
async def convert_temperature_endpoint(request: ConversionRequest):
    return await handle_conversion("temperature", request, convert_temperature)

@app.post("/convert/currency", response_model=ConversionResponse, tags=["Conversions"])
async def convert_currency_endpoint(request: ConversionRequest):
    return await handle_conversion("currency", request, get_currency_rate)
