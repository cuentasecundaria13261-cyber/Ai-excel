
import pandas as pd

from src.analytics.time_analysis import (
    revenue_by_month,
    revenue_by_day,
    revenue_by_year
)


def test_revenue_by_month():
    df = pd.DataFrame({
        "Date": pd.to_datetime([
            "2026-01-05",
            "2026-01-20",
            "2026-02-10"
        ]),
        "Revenue": [100, 200, 300]
    })

    result = revenue_by_month(df)

    assert result["2026-01"] == 300
    assert result["2026-02"] == 300


def test_revenue_by_day():
    df = pd.DataFrame({
        "Date": pd.to_datetime([
            "2026-01-05",
            "2026-01-05",
            "2026-01-06"
        ]),
        "Revenue": [100, 200, 300]
    })

    result = revenue_by_day(df)

    assert result[pd.Timestamp("2026-01-05").date()] == 300
    assert result[pd.Timestamp("2026-01-06").date()] == 300


def test_revenue_by_year():
    df = pd.DataFrame({
        "Date": pd.to_datetime([
            "2025-01-05",
            "2025-06-10",
            "2026-02-10"
        ]),
        "Revenue": [100, 200, 300]
    })

    result = revenue_by_year(df)

    assert result[2025] == 300
    assert result[2026] == 300
