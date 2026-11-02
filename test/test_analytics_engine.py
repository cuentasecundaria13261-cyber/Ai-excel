from src.data.data_reader import read_file
from src.analytics.analytics_engine import analyze_dataset


def test_analyze_dataset():
    df = read_file("data/sales_data.csv")

    results = analyze_dataset(df)

    # Check all four main sections
    assert "kpis" in results
    assert "products" in results
    assert "time" in results
    assert "regions" in results

    # Check KPI results
    assert results["kpis"]["total_revenue"] == 3265
    assert results["kpis"]["total_orders"] == 10

    # Check regional results
    assert results["regions"]["revenue_by_region"]["Colon"] == 1745

    # Check product results
    assert "revenue_by_product" in results["products"]

    # Check time results
    assert "revenue_by_month" in results["time"]
