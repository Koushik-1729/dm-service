"""Phase 2: Dashboard API — Lead management endpoints."""
from fastapi import APIRouter

router = APIRouter(prefix="/leads", tags=["Leads"])

# Endpoints will be added in Phase 2:
# GET /{client_id}/leads — list leads by client
# POST /{lead_id}/convert — mark lead as converted with revenue
# GET /{client_id}/leads/summary — leads by source summary
