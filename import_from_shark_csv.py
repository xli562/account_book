import pandas as pd
from pymongo import MongoClient
from datetime import datetime
import locale

# Set the locale to Chinese
locale.setlocale(locale.LC_TIME, 'Chinese')


def parse_date(date_str):
    try:
        # Parse the date from the given format
        date_obj = datetime.strptime(date_str, '%Y年%m月%d日')

        # Map weekday number to Chinese weekday name
        weekdays = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
        weekday_str = weekdays[date_obj.weekday()]

        # Construct the formatted date string
        formatted_date = f"{date_obj.year}年{date_obj.month}月{date_obj.day}日 {weekday_str}"

        return formatted_date
    except ValueError as e:
        print(f"Error parsing date: {date_str} - {e}")
        return None



# Read the CSV file
df = pd.read_csv('2023鲨鱼记账明细.csv', sep='\t', encoding='utf-16')

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client.entries

for index, row in df.iterrows():
    parsed_date = parse_date(row['日期'])
    document = {
        'date': parsed_date,
        'transaction_type': row['收支类型'],
        'category': row['类别'],
        'amount': row['金额'],
        'remarks': row['备注'],
        'account': '未指定',
        'currency': '未指定'
    }
    db.entries_collection.insert_one(document)

print("Data insertion complete.")
