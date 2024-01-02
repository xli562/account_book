import pandas as pd
from pymongo import MongoClient
from datetime import datetime, timedelta
import locale

# Set the locale to Chinese
locale.setlocale(locale.LC_TIME, 'Chinese')


def excel_serial_date_to_datetime(serial_date):
    base_date = datetime(1899, 12, 30)  # Excel's base date (considering leap year bug)
    delta = timedelta(days=serial_date)
    return base_date + delta

def parse_date(date_str):
    try:
        # Parse the date from the given format
        # date_obj = datetime.strptime(date_str, '%Y年%m月%d日')
        return excel_serial_date_to_datetime(date_str)
    except ValueError as e:
        print(f"Error parsing date: {date_str} - {e}")
        return None



# Read the CSV file
df = pd.read_excel('全部_鲨鱼记账明细.xlsx')
df['账户'].fillna('未指定', inplace=True)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client.entries

for index, row in df.iterrows():
    parsed_date = parse_date(row['日期'])

    accnt = row['账户']
    currency = 'CNY' if accnt in ('微信零钱', '工商银行(3029)', '广州银行(2300)') else 'GBP'

    document = {
        'date': parsed_date,
        'transaction_type': row['收支类型'],
        'category': row['类别'],
        'amount': row['金额'],
        'remarks': row['备注'],
        'account': accnt,
        'currency': currency,
        'details': '',
        'time':'',
        'location':[],
    }
    db.entries_collection.insert_one(document)

print("Data insertion complete.")
