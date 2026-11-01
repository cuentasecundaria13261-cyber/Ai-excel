from src.data.data_reader import read_file
from src.data.data_validator import validate_business_values


# Load original dataset
df = read_file("data/sales_data.csv")

print("TEST 1 - Original dataset")
print(validate_business_values(df))


# Create invalid data
invalid_df = df.copy()

invalid_df.loc[0, "Quantity"] = 0
invalid_df.loc[1, "Unit_Price"] = -15
invalid_df.loc[2, "Revenue"] = -100

print("\nTEST 2 - Invalid business values")

results = validate_business_values(invalid_df)

for error_type, rows in results.items():
    print(f"\n{error_type}:")
    print(rows)