"""
Health check endpoint
"""
from fastapi import APIRouter
from datetime import datetime


router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
