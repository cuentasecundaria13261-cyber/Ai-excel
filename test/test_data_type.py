import pandas as pd

from src.data.data_reader import read_file
from src.data.data_validator import validate_data_types


# Load original dataset
df = read_file("data/sales_data.xlsx")


# Test 1: Original dataset
print("TEST 1 - Original dataset")
print("Invalid columns:", validate_data_types(df))


# Test 2: Invalid Quantity type
invalid_df = df.copy()
invalid_df["Quantity"] = "two"

print("\nTEST 2 - Invalid data type")
print("Invalid columns:", validate_data_types(invalid_df))