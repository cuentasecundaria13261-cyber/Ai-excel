import pandas as pd

from src.analytics.region_analysis import (
    revenue_by_region,
    orders_by_region,
    average_order_value_by_region
)


def create_test_data():
    return pd.DataFrame({
        "Order_ID": [1, 2, 3, 4, 5],
        "Region": [
            "Colon",
            "Colon",
            "Panama City",
            "Panama City",
            "David"
        ],
        "Revenue": [300, 200, 400, 200, 150],
    })


def test_revenue_by_region():
    df = create_test_data()

    result = revenue_by_region(df)

    assert result["Colon"] == 500
    assert result["Panama City"] == 600
    assert result["David"] == 150


def test_orders_by_region():
    df = create_test_data()

    result = orders_by_region(df)

    assert result["Colon"] == 2
    assert result["Panama City"] == 2
    assert result["David"] == 1


def test_average_order_value_by_region():
    df = create_test_data()

    result = average_order_value_by_region(df)

    assert result["Colon"] == 250
    assert result["Panama City"] == 300
    assert result["David"] == 150
