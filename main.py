from pymongo import MongoClient
from datetime import datetime
import re

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client.entries
collection = db.entries_collection  # Replace with your collection name


def find_documents(account, year, month):
    # Start and end dates for the month
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)  # Handle December case
    else:
        end_date = datetime(year, month + 1, 1)

    # Query for documents with the specified account and date range
    query = {
        "account": account,
        "date": {"$gte": start_date, "$lt": end_date}
    }

    return list(collection.find(query))

# Example usage
account_name = "微信零钱"
specified_year = 2023
specified_month = 1  # June
documents = find_documents(account_name, specified_year, specified_month)
for doc in documents:
    print(doc)
