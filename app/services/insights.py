from app.schemas.insights import SalesSummary


def get_sales_summary() -> SalesSummary:
    """Return placeholder metrics until processed data is connected."""
    total_sales = 0.0
    total_orders = 0
    average_order_value = 0.0

    return SalesSummary(
        total_sales=total_sales,
        total_orders=total_orders,
        average_order_value=average_order_value,
    )
