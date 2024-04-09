import pandas as pd
from pymongo import MongoClient
from datetime import datetime, timedelta
import locale

import constants


filename = ''
def import_from_shark_csv(filename:str) -> list:
    """ Imports transaction history from a shark csv.
    Entries are deemed repeated if they have the same date, account
    and comments.
    Does not import repeated entries.
    
    :param filename: str, path to the csv file. 
    
    :return repeated_entries: list, repeated entries (empty list if 
    no repeated entry). 
    :return unrecognised_accnts: list, accounts that are not stored 
    in settings. """
    # Set the locale to Chinese
    locale.setlocale(locale.LC_TIME, 'Chinese')

    accnts = constants.accnts()

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
    df = pd.read_excel(filename)
    df['账户'].fillna('未指定', inplace=True)

    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client.entries

    repeated_entries = []
    unrecognised_accnts = []
    for index, row in df.iterrows():
        parsed_date = parse_date(row['日期'])

        # If account is nopt recognised, append to unrecognised_accnts
        # and skip the loop.
        accnt = row['账户']
        if not accnt in accnts:
            unrecognised_accnts.append(accnt)
            continue
        currency = constants.accnts_to_currs()[accnt]
        
        # Make sure repeated entries are not imported
        repeated_documents = db.entries_collection.find({
            'date': parsed_date,
            'remarks': row['备注'],
            'account': accnt
        })
        repeated_documents = list(repeated_documents)
        if repeated_documents:
            print(0)
            for doc in repeated_documents:
                repeated_entries.append(doc)
        else:
            print(1)
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
            print('inserted')

    return repeated_entries, unrecognised_accnts

print(import_from_shark_csv(r'D:\MyCodes\MyPythonCodes\PersonalProjects\Convenience_and_Service\account_book\至2024年04月09号_鲨鱼记账明细.xlsx'))