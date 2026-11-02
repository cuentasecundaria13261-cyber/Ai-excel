def calculate_kpis(df):
    """Calculate the main business KPIs."""

    total_revenue = df["Revenue"].sum()

    total_orders = df["Order_ID"].nunique()

    units_sold = df["Quantity"].sum()

    average_order_value = (
        total_revenue / total_orders
        if total_orders > 0
        else 0
    )

    kpis = {
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "units_sold": units_sold,
        "average_order_value": average_order_value
    }

    return kpis
