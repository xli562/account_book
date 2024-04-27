""" 从已有数据倒推计算之前的monthly balances """

from pymongo import MongoClient
from datetime import datetime, timedelta, time
from collections import defaultdict

client = MongoClient('mongodb://localhost:27017/')
db = client.entries

# Get the previous and current months
now = datetime.now()
current_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
previous_month = current_month - timedelta(days=5)
previous_month = datetime(previous_month.year, previous_month.month, 1)

entries_collection = db.entries_collection
balances_collection = db.monthly_balances
balances_collection.delete_many({
            'month': {'$lte': previous_month}
        })

def update_monthly_balances(current_month=current_month):
    
    entries_collection = db.entries_collection
    balances_collection = db.monthly_balances
    # monthly_balances = {
    #         '工商银行(3029)':1419.95,
    #         '广州银行(2300)':4074.32,
    #         'HSBC(7476)':720.45,
    #         'Lloyds(3719)':138.72,
    #         '现金(英镑)':540.19,
    #         'HSBC活期':2152.23,
    #         'Lloyds ISA':58.58,
    #         '微信零钱':6047.28,
    #         '未指定':0.0
    #     }
    # balances_collection.update_one(
    #         {'month': current_month},
    #         {'$set': {'balances': dict(monthly_balances)}},
    #         upsert=True
    #     )
    # return

    # Fetch the starting balance for December 2023
    current_month_balance = balances_collection.find_one({'month': current_month})
    if not current_month_balance:
        raise Exception("Starting balance for the current month not found.")

    # Iterate backward from December 2023 to June 2022
    start_month = datetime(2022, 6, 1)
    # Initialize balances for previous month
    monthly_balances = defaultdict(float, current_month_balance['balances'])
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
