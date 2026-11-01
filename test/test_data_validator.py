import pandas as pd

from src.data.data_reader import read_file
from src.data.data_validator import validate_columns


# Test 1: Valid dataset
df = read_file("data/sales_data.csv")

missing = validate_columns(df)

print("TEST 1 - Valid dataset")
print("Missing columns:", missing)


# Test 2: Dataset with a missing column
invalid_df = df.drop(columns=["Order_ID"])

missing = validate_columns(invalid_df)

print("\nTEST 2 - Missing column")
print("Missing columns:", missing)