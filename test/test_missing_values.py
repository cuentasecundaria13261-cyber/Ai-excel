from src.data.data_reader import read_file
from src.data.data_validator import validate_missing_values


# Load the original dataset
df = read_file("data/sales_data.csv")

# Test 1: Original dataset
print("TEST 1 - Original dataset")
print(validate_missing_values(df))


# Test 2: Dataset with missing values
df.loc[0, "Product"] = None
df.loc[1, "Quantity"] = None

print("\nTEST 2 - Dataset with missing values")
print(validate_missing_values(df))