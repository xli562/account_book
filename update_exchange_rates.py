import pandas as pd
from datetime import datetime
from pymongo import MongoClient
import numpy as np

# Function to read the Excel file and create a date to exchange rate mapping
def read_exchange_rate(file_path, rate_column):
    df = pd.read_excel(file_path)
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
    df.set_index('Date', inplace=True)
    df.sort_index(inplace=True)
    # Interpolate missing values
    df.interpolate(method='linear', inplace=True)
    return df[rate_column].to_dict()

# Read exchange rate data from Excel files
gbp_file_path = 'D:/Users/henry/Downloads/20220604-20240102_GBP to CNY.xlsx'
eur_file_path = 'D:/Users/henry/Downloads/20220604-20240102_EUR to CNY.xlsx'

gbp_cny_mapping = read_exchange_rate(gbp_file_path, 'Rates')
eur_cny_mapping = read_exchange_rate(eur_file_path, 'Rates')

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client.entries
collection = db.entries_collection

def update_exchange_rates():
    for doc in collection.find():
        # Parse the date in the document
        doc_date = doc['date']

        # Find the closest dates in the mappings
        closest_gbp_date = min(gbp_cny_mapping.keys(), key=lambda d: abs(d - doc_date))
        closest_eur_date = min(eur_cny_mapping.keys(), key=lambda d: abs(d - doc_date))

        # Get the exchange rates for the closest dates
        gbp_cny_rate = gbp_cny_mapping[closest_gbp_date]
        eur_cny_rate = eur_cny_mapping[closest_eur_date]

        # Update the document with the exchange rates
        exchange_rates = {
            'gbp_cny': gbp_cny_rate,
            'eur_cny': eur_cny_rate
        }
        collection.update_one({'_id': doc['_id']}, {'$set': {'exchange_rates': exchange_rates}})

update_exchange_rates()
