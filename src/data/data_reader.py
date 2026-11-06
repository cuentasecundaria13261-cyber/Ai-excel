import pandas as pd


def read_csv(file_path):
    """Read a CSV file and normalize its date column."""

    df = pd.read_csv(file_path)

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    return df


def read_excel(file_path):
    """Read an Excel file and return a Pandas DataFrame."""
    df = pd.read_excel(file_path)

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    return df

def read_file(file_path):
    """Read a CSV or Excel file from a path or uploaded file."""

    # Get the filename
    file_name = getattr(file_path, "name", file_path)

    # Identify the file format
    file_name = str(file_name).lower()

    if file_name.endswith(".csv"):
        return read_csv(file_path)

    elif file_name.endswith(".xlsx"):
        return read_excel(file_path)

    else:
        raise ValueError(
            "Unsupported file format. Use CSV or XLSX."
        )
