from fastapi import APIRouter

from app.schemas.insights import SalesSummary
from app.services.insights import get_sales_summary

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/sales-summary", response_model=SalesSummary)
def sales_summary() -> SalesSummary:
    """Return a starter sales summary."""
    return get_sales_summary()
