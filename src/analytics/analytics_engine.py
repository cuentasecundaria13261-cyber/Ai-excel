from src.analytics.kpi import calculate_kpis

from src.analytics.product_analysis import (
    revenue_by_product,
    units_sold_by_product,
    revenue_by_category
)

from src.analytics.time_analysis import (
    revenue_by_month,
    revenue_by_day,
    revenue_by_year
)

from src.analytics.region_analysis import (
    revenue_by_region,
    orders_by_region,
    average_order_value_by_region
)


def analyze_dataset(df):
    """Run all analytics operations on a dataset."""

    analytics = {
        "kpis": calculate_kpis(df),

        "products": {
            "revenue_by_product": revenue_by_product(df),
            "units_sold_by_product": units_sold_by_product(df),
            "revenue_by_category": revenue_by_category(df)
        },

        "time": {
            "revenue_by_month": revenue_by_month(df),
            "revenue_by_day": revenue_by_day(df),
            "revenue_by_year": revenue_by_year(df)
        },

        "regions": {
            "revenue_by_region": revenue_by_region(df),
            "orders_by_region": orders_by_region(df),
            "average_order_value_by_region": average_order_value_by_region(df)
        }
    }

    return analytics
