from src.data.data_reader import read_file


# Automatically read CSV
csv_data = read_file("data/sales_data.csv")

print("CSV shape:", csv_data.shape)


# Automatically read Excel
excel_data = read_file("data/sales_data.xlsx")

print("Excel shape:", excel_data.shape)


# Test unsupported format
try:
    read_file("data/example.txt")
except ValueError as error:
    print("Error handled:", error)