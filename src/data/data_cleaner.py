
import pandas as pd


def clean_missing_values(df, strategy="keep"):
    """Handle missing values using the selected strategy."""

    cleaned_df = df.copy()

    if strategy == "keep":
        return cleaned_df

    elif strategy == "drop":
        cleaned_df = cleaned_df.dropna()

    else:
        raise ValueError(
            "Invalid strategy. Choose 'keep' or 'drop'."
        )

    return cleaned_df


def clean_duplicates(df):
    """Remove exact duplicate rows."""

    cleaned_df = df.copy()
    cleaned_df = cleaned_df.drop_duplicates()

    return cleaned_df


def clean_data_types(df):
    """Convert important columns to their expected data types."""

    cleaned_df = df.copy()

    numeric_columns = [
        "Quantity",
        "Unit_Price",
        "Revenue"
    ]

    for column in numeric_columns:
        if column in cleaned_df.columns:
            cleaned_df[column] = pd.to_numeric(
                cleaned_df[column],
                errors="coerce"
            )

    if "Date" in cleaned_df.columns:
        cleaned_df["Date"] = pd.to_datetime(
            cleaned_df["Date"],
            errors="coerce"
        )

    return cleaned_df


def clean_business_values(df):
    """Replace invalid business values with missing values."""

    cleaned_df = df.copy()

    if "Quantity" in cleaned_df.columns:
        cleaned_df.loc[
            cleaned_df["Quantity"] <= 0,
            "Quantity"
        ] = float("nan")

    if "Unit_Price" in cleaned_df.columns:
        cleaned_df.loc[
            cleaned_df["Unit_Price"] < 0,
            "Unit_Price"
        ] = float("nan")

    if "Revenue" in cleaned_df.columns:
        cleaned_df.loc[
            cleaned_df["Revenue"] < 0,
            "Revenue"
        ] = float("nan")

    return cleaned_df


def clean_dataset(df, missing_strategy="keep"):
    """Apply all cleaning operations to a dataset."""

    cleaned_df = clean_duplicates(df)

    cleaned_df = clean_data_types(cleaned_df)

    cleaned_df = clean_business_values(cleaned_df)

    cleaned_df = clean_missing_values(
        cleaned_df,
        strategy=missing_strategy
    )

    return cleaned_df

