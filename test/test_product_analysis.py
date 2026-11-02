
import pandas as pd

from src.analytics.product_analysis import (
    revenue_by_product,
    units_sold_by_product,
    revenue_by_category
)


def test_revenue_by_product():
    df = pd.DataFrame({
        "Product": ["Laptop", "Mouse", "Laptop"],
        "Revenue": [750, 45, 1500]
    })

    result = revenue_by_product(df)

    assert result["Laptop"] == 2250
    assert result["Mouse"] == 45


def test_units_sold_by_product():
    df = pd.DataFrame({
        "Product": ["Laptop", "Mouse", "Laptop"],
        "Quantity": [1, 3, 2]
    })

    result = units_sold_by_product(df)

    assert result["Laptop"] == 3
    assert result["Mouse"] == 3


def test_revenue_by_category():
    df = pd.DataFrame({
        "Category": ["Electronics", "Accessories", "Electronics"],
        "Revenue": [750, 45, 1500]
    })

    result = revenue_by_category(df)

    assert result["Electronics"] == 2250
    assert result["Accessories"] == 45

