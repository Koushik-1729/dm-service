from typing import Dict
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.config.db import get_db

health_router = APIRouter(tags=["Health"])


@health_router.get("/health")
async def health_root():
    return {"status": "healthy"}


@health_router.get("/health/status")
async def health_check() -> Dict[str, str]:
    return {"status": "healthy"}


@health_router.get("/health/ready")
async def readiness_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ready"}


@health_router.get("/health/live")
async def liveness_check():
    return {"status": "live"}
