"""Phase 2: Dashboard API — Content management endpoints."""
from fastapi import APIRouter

router = APIRouter(prefix="/content", tags=["Content"])

# Endpoints will be added in Phase 2:
# GET /{client_id}/content — list content by client
# POST /{client_id}/content/approve — approve content batch
# POST /{client_id}/content/regenerate — regenerate content
