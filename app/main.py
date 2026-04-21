from fastapi import FastAPI

from app.routes.analytics import router as analytics_router
from app.routes.health import router as health_router

app = FastAPI(
    title="Retail Insights API",
    description="A starter API for simple retail data insights.",
    version="0.1.0",
)

app.include_router(health_router)
app.include_router(analytics_router)
