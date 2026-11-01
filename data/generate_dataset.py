
import pandas as pd

# Sample online store sales data
data = {
    "Order_ID": [
        "ORD-001", "ORD-002", "ORD-003", "ORD-004",
        "ORD-005", "ORD-006", "ORD-007", "ORD-008",
        "ORD-009", "ORD-010"
    ],

    "Date": [
        "2026-01-05", "2026-01-08", "2026-01-12",
        "2026-02-03", "2026-02-10", "2026-02-15",
        "2026-03-02", "2026-03-08", "2026-03-14",
        "2026-03-20"
    ],

    "Product": [
        "Laptop", "Mouse", "Keyboard", "Monitor",
        "Laptop", "Headphones", "Mouse", "Monitor",
        "Keyboard", "Headphones"
    ],

    "Category": [
        "Electronics", "Accessories", "Accessories",
        "Electronics", "Electronics", "Accessories",
        "Accessories", "Electronics", "Accessories",
        "Accessories"
    ],

    "Quantity": [
        1, 3, 2, 1, 2, 2, 5, 1, 3, 2
    ],

    "Unit_Price": [
        750, 15, 35, 200, 750, 80, 15, 200, 35, 80
    ],

    "Region": [
        "Panama City", "Colon", "Panama City", "David",
        "Colon", "Panama City", "David", "Colon",
        "Panama City", "David"
    ],

    "Payment_Method": [
        "Card", "Cash", "Card", "Transfer",
        "Card", "Cash", "Transfer", "Card",
        "Cash", "Card"
    ]
}

# Convert the dictionary into a DataFrame
df = pd.DataFrame(data)

# Convert Date from text into datetime
df["Date"] = pd.to_datetime(df["Date"])

# Calculate revenue for each order
df["Revenue"] = df["Quantity"] * df["Unit_Price"]

# Save the dataset
df.to_csv("data/sales_data.csv", index=False)
df.to_excel("data/sales_data.xlsx", index=False)

print("Dataset created successfully!")
print(df.head())
