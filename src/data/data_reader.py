import pandas as pd


def read_csv(file_path):
    """Read a CSV file and return a Pandas DataFrame."""
    return pd.read_csv(file_path)


def read_excel(file_path):
    """Read an Excel file and return a Pandas DataFrame."""
    return pd.read_excel(file_path)
    
def read_file(file_path):
    """Read a CSV or Excel file based on its extension."""

    if file_path.endswith(".csv"):
        return read_csv(file_path)

    elif file_path.endswith(".xlsx"):
        return read_excel(file_path)

    else:
        raise ValueError("Unsupported file format")