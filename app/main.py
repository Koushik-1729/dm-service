from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.config.app_config import app_config
from app.config.logging_config import setup_logging
from app.common.global_exception_handler import global_exception_handler
from app.middleware.logging import LoggingMiddleware
from app.middleware.context import ContextMiddleware
from app.monitoring.health import health_router
from app.monitoring.monitoring import PrometheusMiddleware, metrics_endpoint, setting_otlp
from app.api.marketing_stack.routes.webhook_router import router as webhook_router
from app.api.marketing_stack.routes.cron_router import router as cron_router

# Setup logging
setup_logging()

# Create FastAPI app
app = FastAPI(
    title="Marketing Service API",
    description="AI Digital Marketing Automation — Revenue OS for SMBs",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─── Middleware (order matters: last added = first executed) ─────────
app.add_middleware(PrometheusMiddleware, app_name=app_config.project_name)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggingMiddleware)
app.add_middleware(ContextMiddleware)

# ─── OpenTelemetry ──────────────────────────────────────────────────
if app_config.otlp_grpc_endpoint:
    setting_otlp(app, app_config.project_name, app_config.otlp_grpc_endpoint)

# ─── Exception Handlers ─────────────────────────────────────────────
app.add_exception_handler(Exception, global_exception_handler)

# ─── Routes ─────────────────────────────────────────────────────────
BASE_PREFIX = app_config.base_path

# Health (no prefix — accessible at /marketing-service/health)
app.include_router(health_router, prefix="/marketing-service")

# Metrics endpoint
app.add_api_route("/metrics", metrics_endpoint, methods=["GET"], include_in_schema=False)

# WhatsApp webhook
app.include_router(webhook_router, prefix=BASE_PREFIX)

# Cron triggers
app.include_router(cron_router, prefix=BASE_PREFIX)

# Phase 2: Dashboard routes (uncomment when ready)
# from app.api.marketing_stack.routes.client_router import router as client_router
# from app.api.marketing_stack.routes.report_router import router as report_router
# app.include_router(client_router, prefix=BASE_PREFIX)
# app.include_router(report_router, prefix=BASE_PREFIX)
