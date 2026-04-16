"""Phase 2: Dashboard API — Reporting endpoints."""
from fastapi import APIRouter

router = APIRouter(prefix="/reports", tags=["Reports"])

# Endpoints will be added in Phase 2:
# GET /{client_id}/report/weekly — get latest weekly report
# GET /{client_id}/report/metrics — get metrics for date range
# GET /{client_id}/report/attribution — revenue attribution summary
