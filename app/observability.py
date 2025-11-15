"""
Observability setup: Metrics (Prometheus), Logs (Loguru), Tracing (OpenTelemetry)
"""
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import FastAPI, Response
from loguru import logger
import sys
import json
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor


# ============================================================================
# LOGS CONFIGURATION (Loguru)
# ============================================================================

def setup_logging():
    """Configure structured JSON logging with Loguru"""
    
    # Remove default handler
    logger.remove()
    
    # Add custom JSON formatter
    def json_formatter(record):
        """Format logs as JSON for easy parsing"""
        log_entry = {
            "timestamp": record["time"].strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "level": record["level"].name,
            "message": record["message"],
            "module": record["module"],
            "function": record["function"],
            "line": record["line"],
        }
        
        # Add extra fields if present
        if record["extra"]:
            log_entry.update(record["extra"])
        
        return json.dumps(log_entry)
    
    # Add handler with JSON format
    logger.add(
        sys.stdout,
        level="INFO",
        serialize=True,  # We handle JSON ourselves
    )
    
    logger.info("Structured logging initialized")


# ============================================================================
# METRICS CONFIGURATION (Prometheus)
# ============================================================================

# Define Prometheus metrics
REQUEST_COUNT = Counter(
    'api_requests_total',
    'Total number of API requests',
    ['endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'api_request_duration_seconds',
    'API request duration in seconds',
    ['endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
)

CONVERSION_COUNT = Counter(
    'conversions_total',
    'Total number of conversions performed',
    ['conversion_type']
)


def setup_metrics(app: FastAPI):
    """
    Add /metrics endpoint to expose Prometheus metrics
    
    Args:
        app: FastAPI application instance
    """
    @app.get("/metrics", include_in_schema=False)
    async def metrics():
        """Prometheus metrics endpoint"""
        return Response(
            content=generate_latest(),
            media_type=CONTENT_TYPE_LATEST
        )
    
    logger.info("Prometheus metrics endpoint configured at /metrics")


def track_request(endpoint: str, duration: float, status: str):
    """
    Track request metrics
    
    Args:
        endpoint: API endpoint name (e.g., 'length', 'temperature')
        duration: Request duration in seconds
        status: Request status ('success' or 'error')
    """
    REQUEST_COUNT.labels(endpoint=endpoint, status=status).inc()
    REQUEST_DURATION.labels(endpoint=endpoint).observe(duration)
    
    if status == "success":
        CONVERSION_COUNT.labels(conversion_type=endpoint).inc()


# ============================================================================
# TRACING CONFIGURATION (OpenTelemetry)
# ============================================================================

def setup_tracing(app: FastAPI):
    """
    Configure OpenTelemetry distributed tracing
    
    Args:
        app: FastAPI application instance
    """
    # Set up tracer provider
    trace.set_tracer_provider(TracerProvider())
    
    # Configure span processor (console exporter for development)
    # In production, use Jaeger or Zipkin exporter
    span_processor = BatchSpanProcessor(ConsoleSpanExporter())
    trace.get_tracer_provider().add_span_processor(span_processor)
    
    # Instrument FastAPI automatically
    FastAPIInstrumentor.instrument_app(app)
    
    logger.info("OpenTelemetry tracing configured")


def get_tracer(name: str):
    """
    Get a tracer instance for creating custom spans
    
    Args:
        name: Name of the tracer (usually module name)
    
    Returns:
        OpenTelemetry Tracer instance
    """
    return trace.get_tracer(name)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def log_conversion(conversion_type: str, from_val: float, to_val: float, 
                   from_unit: str, to_unit: str, duration: float):
    """
    Log a conversion with structured data
    
    Args:
        conversion_type: Type of conversion (length, weight, etc.)
        from_val: Original value
        to_val: Converted value
        from_unit: Source unit
        to_unit: Target unit
        duration: Processing time in seconds
    """
    logger.info(
        f"{conversion_type.capitalize()} conversion completed",
        extra={
            "conversion_type": conversion_type,
            "from_value": from_val,
            "to_value": to_val,
            "from_unit": from_unit,
            "to_unit": to_unit,
            "duration_seconds": round(duration, 4)
        }
    )


# Initialize logging when module is imported
setup_logging()