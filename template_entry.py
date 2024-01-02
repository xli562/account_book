template = {
    '_id': ObjectId('...'),
    'date': datetime.datetime(2023, 1, 31, 0, 0),
    'transaction_type': '收入',
    'category': '还钱',
    'amount': 15.0,
    'account': '未指定',
    'currency': '未指定',
    'exchange_rates': {
        'gbp_cny': 8.5,
        'eur_cny': 7.5
    },
    
    # Optional:
    'remarks': '借潘屹饭卡还钱',    # short, for display
    'details': '...',   # long but can be left empty most of the time, for if I want to add anything that's too long to fit inside 'remarks'
    'time': '19:45',
    'location': [122.02222, 111.01111]
}