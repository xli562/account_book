from pymongo import MongoClient
from datetime import datetime

client = MongoClient('mongodb://localhost:27017/')
db = client.entries
collection = db.entries_collection

def sum_income_expenditure(account, year, month):
    # Start and end dates for the month
    start_date = datetime(year, month, 1)
    end_date = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)

    # Base query
    base_query = {"date": {"$gte": start_date, "$lt": end_date}}
    if account is not None:
        base_query["account"] = account

    # Aggregation pipeline
    pipeline = [
        {"$match": base_query},
        {"$group": {
            "_id": "$transaction_type",
            "total": {"$sum": "$amount"}
        }}
    ]

    # Perform aggregation
    result = collection.aggregate(pipeline)

    # Initialize sums
    income_sum = 0
    expenditure_sum = 0

    # Calculate sums
    for entry in result:
        if entry["_id"] == "收入":  # Assuming "收入" is the identifier for income
            income_sum = entry["total"]
        elif entry["_id"] == "支出":  # Assuming "支出" is the identifier for expenditure
            expenditure_sum = entry["total"]

    return income_sum, expenditure_sum

# Example usage
account_name = None  # Replace with account name or None
specified_year = 2023
specified_month = 10  # June
income, expenditure = sum_income_expenditure(account_name, specified_year, specified_month)
print(f"Income: {income}, Expenditure: {expenditure}")
