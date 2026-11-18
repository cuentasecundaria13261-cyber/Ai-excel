"""Sample sales data so visitors can try the app without having a file.

The data is made up and generated the same way every time. It tells a small
story that shows what the dashboard can do: one product stops selling, one
region slows down, and one day is unusually big.
"""

import numpy as np
import pandas as pd

SAMPLE_FILE_NAME = "sample_sales.csv"

_PRODUCTS = {
    # name: (unit price, category, popularity weight)
    "Laptop": (900, "Electronics", 0.22),
    "Phone": (600, "Electronics", 0.20),
    "Headphones": (80, "Accessories", 0.22),
    "Mouse": (25, "Accessories", 0.18),
    "Desk Lamp": (40, "Home Office", 0.18),
}
_REGIONS = ["North", "South", "East", "West"]
_PAYMENTS = ["Card", "Cash", "Transfer"]


class SampleUpload:
    """Behaves like an uploaded file (name and getvalue), so pages treat it the same way."""

    def __init__(self, name, data):
        self.name = name
        self._data = data

    def getvalue(self):
        return self._data


def make_sample_sales(seed=42, days=180, end="2026-10-31"):
    """Return a made-up sales table with the same columns the classic page expects."""
    rng = np.random.default_rng(seed)
    names = list(_PRODUCTS)
    weights = np.array([_PRODUCTS[n][2] for n in names])
    weights = weights / weights.sum()

    all_days = pd.date_range(end=end, periods=days)
    last_day = all_days[-1]

    rows = []
    order_id = 1000
    for day in all_days:
        # busier weekends
        orders_today = int(rng.integers(5, 10)) + (3 if day.dayofweek >= 5 else 0)
        for _ in range(orders_today):
            product = str(rng.choice(names, p=weights))

            # Story 1: Desk Lamp stops selling in the last 5 weeks.
            if product == "Desk Lamp" and day > last_day - pd.Timedelta(days=35):
                continue

            # Story 2: the South region slows down in the last 30 days.
            region = str(rng.choice(_REGIONS))
            if region == "South" and day > last_day - pd.Timedelta(days=30) and rng.random() < 0.6:
                continue

            price, category, _ = _PRODUCTS[product]
            quantity = int(rng.integers(1, 4))
            order_id += 1
            rows.append(
                [order_id, day.strftime("%Y-%m-%d"), product, category, quantity, price,
                 region, str(rng.choice(_PAYMENTS)), quantity * price]
            )

    df = pd.DataFrame(
        rows,
        columns=["Order_ID", "Date", "Product", "Category", "Quantity",
                 "Unit_Price", "Region", "Payment_Method", "Revenue"],
    )

    # Story 3: one unusually big day (a large company order) about 3 months back.
    big_day = (last_day - pd.Timedelta(days=95)).strftime("%Y-%m-%d")
    big_rows = pd.DataFrame(
        [[order_id + 1 + i, big_day, "Laptop", "Electronics", 40, 900, "East", "Transfer", 40 * 900]
         for i in range(3)],
        columns=df.columns,
    )
    return pd.concat([df, big_rows], ignore_index=True)


def sample_upload():
    """The sample as an upload-like object."""
    data = make_sample_sales().to_csv(index=False).encode("utf-8")
    return SampleUpload(SAMPLE_FILE_NAME, data)
