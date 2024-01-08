''' 从已有数据倒推计算之前的monthly balances '''

from pymongo import MongoClient
from datetime import datetime, timedelta
from collections import defaultdict

client = MongoClient('mongodb://localhost:27017/')
db = client.entries

entries_collection = db.entries_collection
balances_collection = db.monthly_balances
balances_collection.delete_many({
            'month': {'$lte': datetime(2023,11,1)}
        })

def update_monthly_balances():
    entries_collection = db.entries_collection
    balances_collection = db.monthly_balances

    # Fetch the starting balance for December 2023
    december_2023_balance = balances_collection.find_one({'month': datetime(2023, 12, 1)})
    if not december_2023_balance:
        raise Exception("Starting balance for December 2023 not found.")

    # Iterate backward from December 2023 to June 2022
    current_month = datetime(2023, 12, 1)
    start_month = datetime(2022, 6, 1)
    # Initialize balances for previous month
    monthly_balances = defaultdict(float, december_2023_balance['balances'])
    while current_month >= start_month:
        previous_month = current_month - timedelta(days=1)
        previous_month = previous_month.replace(day=1)

        

        # Find transactions for the current month
        transactions = entries_collection.find({
            'date': {'$gte': previous_month, '$lt': current_month}
        })

        # Adjust balances based on transactions
        for trans in transactions:
            amount = trans['amount'] * (-1 if trans['transaction_type'] == '支出' else 1)
            monthly_balances[trans['account']] -= amount
        monthly_balances[trans['account']] = round(monthly_balances[trans['account']], 2)

        # Insert or update the balance document for the previous month
        balances_collection.update_one(
            {'month': previous_month},
            {'$set': {'balances': dict(monthly_balances)}},
            upsert=True
        )

        # Move to previous month
        current_month = previous_month

update_monthly_balances()
