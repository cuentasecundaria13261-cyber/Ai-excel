import pandas as pd

from src.data.data_reader import read_file
from src.data.data_cleaner import (
    clean_missing_values,
    clean_duplicates,
    clean_data_types,
    clean_business_values,
    clean_dataset
)

# Load original dataset
df = read_file("data/sales_data.csv")

# Introduce missing values
df.loc[0, "Product"] = None
df.loc[1, "Quantity"] = None


print("TEST 1 - Keep missing values")

cleaned_keep = clean_missing_values(df)

print("Original rows:", len(df))
print("Cleaned rows:", len(cleaned_keep))
print("Missing values:", cleaned_keep.isnull().sum().sum())


print("\nTEST 2 - Drop missing values")

cleaned_drop = clean_missing_values(df, strategy="drop")

print("Original rows:", len(df))
print("Cleaned rows:", len(cleaned_drop))
print("Missing values:", cleaned_drop.isnull().sum().sum())


print("\nTEST 3 - Original data remains unchanged")

print("Original missing values:", df.isnull().sum().sum())

# TEST 4 - Remove exact duplicate rows

duplicate_df = df.copy()

# Duplicate the first row
duplicate_df = pd.concat(
    [duplicate_df, duplicate_df.iloc[[0]]],
    ignore_index=True
)

print("\nTEST 4 - Remove duplicates")

cleaned_duplicates = clean_duplicates(duplicate_df)

print("Rows before cleaning:", len(duplicate_df))
print("Rows after cleaning:", len(cleaned_duplicates))
print("Original rows:", len(df))

# TEST 5 - Clean data types

invalid_type_df = df.copy()

invalid_type_df["Quantity"] = invalid_type_df["Quantity"].astype(str)
invalid_type_df.loc[0, "Quantity"] = "unknown"

invalid_type_df["Unit_Price"] = invalid_type_df["Unit_Price"].astype(str)
invalid_type_df.loc[1, "Unit_Price"] = "invalid-price"

print("\nTEST 5 - Clean data types")

cleaned_types = clean_data_types(invalid_type_df)

print("Quantity type:", cleaned_types["Quantity"].dtype)
print("Unit_Price type:", cleaned_types["Unit_Price"].dtype)
print("Invalid Quantity:", cleaned_types.loc[0, "Quantity"])
print("Invalid Unit_Price:", cleaned_types.loc[1, "Unit_Price"])

# TEST 6 - Clean business values

invalid_business_df = df.copy()

invalid_business_df.loc[0, "Quantity"] = 0
invalid_business_df.loc[1, "Unit_Price"] = -15
invalid_business_df.loc[2, "Revenue"] = -100

print("\nTEST 6 - Clean business values")

cleaned_business = clean_business_values(invalid_business_df)

print("Invalid Quantity:", cleaned_business.loc[0, "Quantity"])
print("Invalid Unit_Price:", cleaned_business.loc[1, "Unit_Price"])
print("Invalid Revenue:", cleaned_business.loc[2, "Revenue"])

print(
    "Original Quantity:",
    invalid_business_df.loc[0, "Quantity"]
)

# TEST 7 - Clean complete dataset

print("\nTEST 7 - Clean complete dataset")

cleaned_all = clean_dataset(df, missing_strategy="keep")

print("Original rows:", len(df))
print("Cleaned rows:", len(cleaned_all))
print("Missing values:", cleaned_all.isnull().sum().sum())
print("Original missing values:", df.isnull().sum().sum())

# TEST 8 - Clean complete dataset and drop missing values

print("\nTEST 8 - Clean complete dataset (drop)")

cleaned_all_drop = clean_dataset(df, missing_strategy="drop")

print("Original rows:", len(df))
print("Cleaned rows:", len(cleaned_all_drop))
print("Missing values:", cleaned_all_drop.isnull().sum().sum())
print("Original rows after cleaning:", len(df))
