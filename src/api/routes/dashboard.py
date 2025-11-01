"""
Dashboard API endpoints and UI
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse, HTMLResponse
from src.data.repositories.request_repository import request_logger
from src.api.templates.dashboard import get_dashboard_html


router = APIRouter(tags=["dashboard"])


@router.get("/", response_class=HTMLResponse)
async def dashboard_home():
    """Main dashboard HTML page"""
    return HTMLResponse(content=get_dashboard_html())


@router.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    return request_logger.get_statistics()


@router.get("/api/dashboard/requests")
async def get_dashboard_requests(limit: int = 50):
    """Get recent requests"""
    return request_logger.get_recent_requests(limit=limit)


@router.get("/api/dashboard/request/{request_id}")
async def get_request_details(request_id: str):
    """Get detailed information about a specific request"""
    details = request_logger.get_request_details(request_id)
    if not details:
        return JSONResponse(
            status_code=404,
            content={"error": "Request not found"}
        )
    return details


@router.get("/api/dashboard/search")
async def search_requests(phone: str = None, status: str = None, limit: int = 50):
    """Search requests by criteria"""
    return request_logger.search_requests(
        sender_phone=phone,
        status=status,
        limit=limit
    )
