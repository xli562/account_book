import pandas as pd
from pymongo import MongoClient
from datetime import datetime, timedelta

client = MongoClient('mongodb://localhost:27017/')
monthly_balances = client.entries.monthly_balances


start_month = datetime(2023, 12, 1)
end_month = datetime(2022, 6, 1)

current_month = start_month
for i in range(start_month.month - end_month.month):
    current_month -= 


document = {
    'month': datetime(2023,12,1),
    'balances': {
        'HSBC(7476)':347.7,
        'HSBC活期':2408.51,
        'Lloyds ISA':10098.06,
        'Lloyds(3719)':58.58,
        '工商银行(3029)':2652.29,
        '广州银行(2300)':8720.97,
        '微信零钱':490.44,
        '未指定':0.0,
        '现金(英镑)':477.85
    }
}

# template = {
#     # '_id': ObjectId('...'),
#     'date': datetime(2023, 12, 21),
#     'transaction_type': '收入',
#     'category': '理财',
#     'amount': 4.59,
#     'account': '广州银行(2300)',
#     'currency': 'CNY',
#     'exchange_rates': {
#         'gbp_cny': 8.9858,
#         'eur_cny': 7.7775
#     },
    
#     # Optional:
#     'remarks': '存钱利息',    # short, for display
#     'details': '',   # long but can be left empty most of the time, for if I want to add anything that's too long to fit inside 'remarks'
#     'time': '',
#     'location': []
# }

monthly_balances.insert_one(document)
monthly_balances.upd()
# entries_collection.insert_one(template)

print("Data insertion complete.")
