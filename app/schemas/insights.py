from pydantic import BaseModel


class SalesSummary(BaseModel):
    total_sales: float
    total_orders: int
    average_order_value: float
