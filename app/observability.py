"""
Observability setup: Metrics (Prometheus), Logs (Loguru), Tracing (OpenTelemetry)
"""
import os
import sys
import json
from fastapi import FastAPI, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from loguru import logger
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor, SpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# ====================================================================
# LOGS CONFIGURATION (Loguru)
# ====================================================================

def setup_logging():
    """Configure structured JSON logging with Loguru"""
    logger.remove()  # Remove default handler

    def json_formatter(record):
        log_entry = {
            "timestamp": record["time"].strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "level": record["level"].name,
            "message": record["message"],
            "module": record["module"],
            "function": record["function"],
            "line": record["line"],
        }
        if record["extra"]:
            log_entry.update(record["extra"])
        return json.dumps(log_entry)

    logger.add(
        sys.stdout,
        level="INFO",
        serialize=True  # Keep JSON formatting
    )
    logger.info("Structured logging initialized")


# ====================================================================
# METRICS CONFIGURATION (Prometheus)
# ====================================================================

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
    """Add /metrics endpoint for Prometheus"""
    @app.get("/metrics", include_in_schema=False)
    async def metrics():
        return Response(
            content=generate_latest(),
            media_type=CONTENT_TYPE_LATEST
        )
    logger.info("Prometheus metrics endpoint configured at /metrics")


def track_request(endpoint: str, duration: float, status: str):
    """Track request metrics"""
    REQUEST_COUNT.labels(endpoint=endpoint, status=status).inc()
    REQUEST_DURATION.labels(endpoint=endpoint).observe(duration)
    if status == "success":
        CONVERSION_COUNT.labels(conversion_type=endpoint).inc()


# ====================================================================
# TRACING CONFIGURATION (OpenTelemetry)
# ====================================================================

class DummyExporter(SpanExporter):
    """Exporter that discards spans (for testing)"""
    def export(self, spans):
        return trace.SpanExportResult.SUCCESS
    def shutdown(self):
        pass

def setup_tracing(app: FastAPI):
    """Configure OpenTelemetry tracing"""
    tracer_provider = TracerProvider()
    trace.set_tracer_provider(tracer_provider)

    # Use dummy exporter during tests to avoid stdout closed errors
    if os.environ.get("TESTING") == "1":
        exporter = DummyExporter()
    else:
        exporter = ConsoleSpanExporter()

    span_processor = BatchSpanProcessor(exporter)
    tracer_provider.add_span_processor(span_processor)

    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)

    logger.info("OpenTelemetry tracing configured")


def get_tracer(name: str):
    """Return a tracer instance for custom spans"""
    return trace.get_tracer(name)


# ====================================================================
# HELPER FUNCTION
# ====================================================================

def log_conversion(conversion_type: str, from_val: float, to_val: float,
                   from_unit: str, to_unit: str, duration: float):
    """Log a conversion with structured data"""
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


# Initialize logging immediately
setup_logging()
