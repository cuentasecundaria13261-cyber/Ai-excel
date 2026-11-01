import pandas as pd

from src.data.data_reader import read_file
from src.data.data_validator import validate_duplicates


# Load original dataset
df = read_file("data/sales_data.csv")


# Test 1: Original dataset
print("TEST 1 - Original dataset")

duplicates = validate_duplicates(df)

print(duplicates)


# Test 2: Add a duplicate record
duplicate_row = df.iloc[[0]]

df_with_duplicates = pd.concat(
    [df, duplicate_row],
    ignore_index=True
)

print("\nTEST 2 - Dataset with duplicates")

duplicates = validate_duplicates(df_with_duplicates)

print(duplicates)