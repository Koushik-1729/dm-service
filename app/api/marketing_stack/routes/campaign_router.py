"""Phase 2: Dashboard API — Campaign endpoints."""
from fastapi import APIRouter

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])

# Endpoints will be added in Phase 2:
# GET /{client_id}/campaigns — list campaigns
# POST /{campaign_id}/pause — pause campaign
# POST /{campaign_id}/resume — resume campaign
