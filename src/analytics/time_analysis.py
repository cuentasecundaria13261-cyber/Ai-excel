def revenue_by_month(df):
    """Calculate total revenue generated each month."""

    result = df.groupby(
        df["Date"].dt.to_period("M")
    )["Revenue"].sum()

    return result.sort_index()

def revenue_by_day(df):
    """Calculate total revenue generated each day."""

    result = df.groupby(
        df["Date"].dt.date
    )["Revenue"].sum()

    return result.sort_index()

def revenue_by_year(df):
    """Calculate total revenue generated each year."""

    result = df.groupby(
        df["Date"].dt.year
    )["Revenue"].sum()

    return result.sort_index()
