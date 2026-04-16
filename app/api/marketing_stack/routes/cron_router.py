from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from app.core.marketing_stack.services.optimization_service import OptimizationService
from app.core.marketing_stack.services.execution_service import ExecutionService
from app.core.marketing_stack.services.lead_service import LeadService
from app.core.marketing_stack.outbound.repositories.client_repository import ClientRepository
from app.api.marketing_stack.marketing_dependencies import (
    get_optimization_service,
    get_execution_service,
    get_lead_service,
    get_client_repository,
)

router = APIRouter(prefix="/cron", tags=["Cron Triggers"])


@router.post("/weekly-reports")
async def trigger_weekly_reports(
    optimization: OptimizationService = Depends(get_optimization_service),
    client_repo: ClientRepository = Depends(get_client_repository),
) -> dict:
    """Send weekly performance reports to all active clients. Triggered every Monday 9 AM."""
    clients = await client_repo.list_active()
    sent = 0
    failed = 0

    for client in clients:
        try:
            await optimization.send_weekly_report(client)
            sent += 1
        except Exception as e:
            logger.error(f"Weekly report failed for {client.id}: {e}")
            failed += 1

    logger.info(f"Weekly reports: sent={sent}, failed={failed}, total={len(clients)}")
    return {"sent": sent, "failed": failed, "total": len(clients)}


@router.post("/revenue-check")
async def trigger_revenue_check(
    optimization: OptimizationService = Depends(get_optimization_service),
    client_repo: ClientRepository = Depends(get_client_repository),
) -> dict:
    """Send revenue confirmation check to all active clients. Triggered every Monday 10 AM."""
    clients = await client_repo.list_active()
    sent = 0

    for client in clients:
        try:
            await optimization.send_revenue_check(client)
            sent += 1
        except Exception as e:
            logger.error(f"Revenue check failed for {client.id}: {e}")

    return {"sent": sent, "total": len(clients)}


@router.post("/execute-scheduled")
async def trigger_scheduled_execution(
    execution: ExecutionService = Depends(get_execution_service),
    client_repo: ClientRepository = Depends(get_client_repository),
) -> dict:
    """Execute all approved/scheduled content. Triggered daily at posting times."""
    clients = await client_repo.list_active()
    total_campaigns = 0

    for client in clients:
        try:
            campaigns = await execution.execute_approved_content(client)
            total_campaigns += len(campaigns)
        except Exception as e:
            logger.error(f"Execution failed for client {client.id}: {e}")

    logger.info(f"Scheduled execution: {total_campaigns} campaigns launched")
    return {"campaigns_launched": total_campaigns, "clients_processed": len(clients)}


@router.post("/auto-followup")
async def trigger_auto_followup(
    lead_service: LeadService = Depends(get_lead_service),
    client_repo: ClientRepository = Depends(get_client_repository),
) -> dict:
    """Auto-followup on leads that haven't been contacted. Triggered every 2 hours."""
    clients = await client_repo.list_active()
    followups_sent = 0

    for client in clients:
        try:
            leads = await lead_service.get_leads_needing_followup(client.id)
            for lead in leads:
                await lead_service.auto_followup(lead, client.business_name or "Our business")
                followups_sent += 1
        except Exception as e:
            logger.error(f"Auto-followup failed for client {client.id}: {e}")

    logger.info(f"Auto-followup: {followups_sent} followups sent")
    return {"followups_sent": followups_sent}
