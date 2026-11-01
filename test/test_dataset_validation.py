import pandas as pd

from src.data.data_reader import read_file
from src.data.data_validator import validate_dataset


# Load original dataset
df = read_file("data/sales_data.csv")

print("TEST 1 - Original dataset")

report = validate_dataset(df)

for validation, result in report.items():
    print(f"\n{validation}:")
    print(result)


# Create invalid dataset
invalid_df = df.copy()

invalid_df.loc[0, "Quantity"] = 0
invalid_df.loc[1, "Product"] = None

print("\nTEST 2 - Invalid dataset")

report = validate_dataset(invalid_df)

for validation, result in report.items():
    print(f"\n{validation}:")
    print(result)

# TEST 3 - Invalid date
invalid_date_df = df.copy()

# Convert dates to strings temporarily
invalid_date_df["Date"] = invalid_date_df["Date"].astype(str)

# Insert an invalid date
invalid_date_df.loc[0, "Date"] = "not-a-date"

# Convert dates back to datetime
invalid_date_df["Date"] = pd.to_datetime(
    invalid_date_df["Date"],
    format="%Y-%m-%d",
    errors="coerce"
)

print("\nTEST 3 - Invalid date")

report = validate_dataset(invalid_date_df)

print("Missing values:")
print(report["missing_values"])