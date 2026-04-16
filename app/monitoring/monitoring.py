import time
from typing import Callable, Tuple

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response as StarletteResponse

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource

from app.monitoring.metrics import REQUEST_COUNT, REQUEST_LATENCY


class PrometheusMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, app_name: str = "marketing-service"):
        super().__init__(app)
        self.app_name = app_name

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        response = await call_next(request)

        duration = time.time() - start_time
        endpoint = request.url.path
        method = request.method
        status_code = response.status_code

        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
        REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(duration)

        return response


def metrics_endpoint(request: Request) -> StarletteResponse:
    return StarletteResponse(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


def setting_otlp(app: FastAPI, app_name: str, endpoint: str) -> None:
    if not endpoint:
        return

    resource = Resource.create(attributes={"service.name": app_name})
    tracer_provider = TracerProvider(resource=resource)
    otlp_exporter = OTLPSpanExporter(endpoint=endpoint, insecure=True)
    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)
    trace.set_tracer_provider(tracer_provider)

    FastAPIInstrumentor.instrument_app(app, tracer_provider=tracer_provider)
