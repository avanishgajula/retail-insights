from fastapi.testclient import TestClient

from app.main import app
from app.routes import analytics as analytics_routes
from app.services.analytics import AnalyticsError

client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_kpis(monkeypatch) -> None:
    monkeypatch.setattr(
        analytics_routes.analytics,
        "get_total_sales",
        lambda: {"total_sales": 123.45},
    )

    response = client.get("/kpis")

    assert response.status_code == 200
    assert response.json() == {"total_sales": 123.45}


def test_trends(monkeypatch) -> None:
    monkeypatch.setattr(
        analytics_routes.analytics,
        "get_monthly_sales_trend",
        lambda: [{"month": "2026-01", "total_sales": 100.0}],
    )

    response = client.get("/trends")

    assert response.status_code == 200
    assert response.json() == [{"month": "2026-01", "total_sales": 100.0}]


def test_analytics_error_returns_json(monkeypatch) -> None:
    def raise_error() -> None:
        raise AnalyticsError("Database not found: analytics.db")

    monkeypatch.setattr(analytics_routes.analytics, "get_total_sales", raise_error)

    response = client.get("/kpis")

    assert response.status_code == 503
    assert response.json() == {"detail": "Database not found: analytics.db"}
