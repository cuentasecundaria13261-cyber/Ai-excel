import pandas as pd
from src.analytics.kpi import calculate_kpis


def test_calculate_kpis():
    df = pd.DataFrame({
        "Order_ID": ["A", "B", "C"],
        "Quantity": [2, 3, 5],
        "Revenue": [20, 30, 50]
    })

    result = calculate_kpis(df)

    assert result["total_revenue"] == 100
    assert result["total_orders"] == 3
    assert result["units_sold"] == 10
    assert result["average_order_value"] == 100 / 3
