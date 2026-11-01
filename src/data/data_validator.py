import pandas as pd


REQUIRED_COLUMNS = [
    "Order_ID",
    "Date",
    "Product",
    "Category",
    "Quantity",
    "Unit_Price",
    "Region",
    "Payment_Method",
    "Revenue"
]


def validate_columns(df):
    """Check whether all required columns exist."""

    missing_columns = []

    for column in REQUIRED_COLUMNS:
        if column not in df.columns:
            missing_columns.append(column)

    return missing_columns

def validate_missing_values(df):
    """Identify missing values in each column."""

    missing_values = df.isnull().sum()

    return missing_values[missing_values > 0]

def validate_duplicates(df):
    """Identify duplicate order IDs."""

    duplicates = df[df.duplicated(subset=["Order_ID"], keep=False)]

    return duplicates

def validate_data_types(df):
    """Check the data types of important columns."""

    expected_types = {
        "Quantity": "number",
        "Unit_Price": "number",
        "Revenue": "number",
        "Date": "datetime"
    }

    invalid_columns = []

    for column, expected_type in expected_types.items():

        if column not in df.columns:
            continue

        if expected_type == "number":
            if not pd.api.types.is_numeric_dtype(df[column]):
                invalid_columns.append(column)

        elif expected_type == "datetime":
            if not pd.api.types.is_datetime64_any_dtype(df[column]):
                invalid_columns.append(column)

    return invalid_columns

def validate_business_values(df):
    """Check for invalid quantities and prices."""

    invalid_rows = {}

    if "Quantity" in df.columns:
        invalid_rows["invalid_quantity"] = df[df["Quantity"] <= 0]

    if "Unit_Price" in df.columns:
        invalid_rows["invalid_price"] = df[df["Unit_Price"] < 0]

    if "Revenue" in df.columns:
        invalid_rows["invalid_revenue"] = df[df["Revenue"] < 0]

    return invalid_rows

def validate_dataset(df):
    """Run all dataset validation checks and return one report."""

    report = {
        "missing_columns": validate_columns(df),
        "missing_values": validate_missing_values(df),
        "duplicate_orders": (
            validate_duplicates(df)
            if "Order_ID" in df.columns
            else None
        ),
        "invalid_data_types": validate_data_types(df),
        "invalid_business_values": validate_business_values(df)
    }

    return report