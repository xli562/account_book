# Data downloaded from www.chinamoney.com.cn

import pandas as pd
from datetime import datetime, timedelta
from pymongo import MongoClient
import numpy as np
import requests
import json

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client.entries
collection = db.entries_collection

def needed_dates_interval():
    """ Finds the date of the first entry with an empty exchange_rates field """
    # Query for the first document where 'exchange_rates' is empty
    query = {'$or': [{'exchange_rates': {'$exists': False}}, {'exchange_rates': {}}]}
    document = collection.find_one(query, sort=[('date', 1)])  # Sort by date ascending
    return datetime(2024,1,1) if document is None else document['date']

def get_rates(currency:str, start_date:datetime=needed_dates_interval(), end_date:datetime=datetime.now()) -> dict:
    """ Scrapes exchange rates from an online source. Cannot get data from 
    more than 1 year ago due to website restrictions.
    :param start_date: datetime, start date of desired data, inclusive
    :param end_date: datetime, end date of desired data, inclusive
    :param currency: str, e.g. 'GBP'.
    :return date_value_list: list, e.g. [{"date":"2024-04-09", "values":["9.0161"]}, ... ] """
    request_interval_size = 99

    def divide_into_intervals(start:datetime, end:datetime, interval:int) -> list:
        """ Divide the range from start to end into intervals of a specified length.

        :param start: datetime, The start date.
        :param end: datetime, The end date.
        :param interval: int, Length of each interval, in days.
        :return: A list of intervals represented as tuples (start, end). """
        intervals = []
        current_start = start
        
        while current_start < end:
            current_end = min(current_start + timedelta(days=interval) - timedelta(days=1), end)
            intervals.append((current_start, current_end))
            current_start = current_end + timedelta(days=1)
            
        return intervals

    date_value_list = []
    
    # Request head
    head = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.47'}
    # Separate requested interval into periods of 99 days, since the 
    # website cannot return more data than 99 days at a single request.
    for interval_start, interval_end in divide_into_intervals(start_date, end_date, request_interval_size):
        # Construct URL of the page
        interval_start = interval_start.strftime('%Y-%m-%d')
        interval_end = interval_end.strftime('%Y-%m-%d')
        url = f'https://www.chinamoney.com.cn/ags/ms/cm-u-bk-ccpr/CcprHisNew?startDate={interval_start}&endDate={interval_end}&currency={currency}/CNY&pageNum=1&pageSize={request_interval_size}'
        # Fetch the webpage
        response = requests.get(url, headers = head)
        response.raise_for_status()  # Raises an HTTPError if the response status code was not 200
        # Parse the HTML
        data = json.loads(response.text)
        date_value_list.extend(data["records"])
    return date_value_list

# Function to read the Excel file and create a date to exchange rate mapping
def read_exchange_rate(currency:str):
    """ Convert scraped dates to panda dataframe and interpolate missing dates """
    rates = get_rates(currency)
    df = pd.DataFrame({'date': [datetime.strptime(item['date'], '%Y-%m-%d') for item in rates],
                      'value': [float(item['values'][0]) for item in rates]})
    # Interpolate missing values
    df.interpolate(method='linear', inplace=True)
    return df['value'].to_dict()

gbp_cny_mapping = read_exchange_rate('GBP')
eur_cny_mapping = read_exchange_rate('EUR')


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
