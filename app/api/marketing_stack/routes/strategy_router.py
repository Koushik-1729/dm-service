"""Phase 2: Dashboard API — Strategy endpoints."""
from fastapi import APIRouter

router = APIRouter(prefix="/strategies", tags=["Strategies"])

# Endpoints will be added in Phase 2:
# GET /{client_id}/strategy — get active strategy
# POST /{client_id}/strategy/regenerate — regenerate strategy
