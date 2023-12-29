template = {
    '_id': ObjectId('...'),
    'date':'2022年6月4日 星期六',
    'transaction_type': '收入',
    'category': '还钱',
    'amount': 15,
    'account': '未指定',
    'currency': '未指定',
    
    # Optional:
    'remarks': '借潘屹饭卡还钱',    # short, for display
    'details': '...',   # long but can be left empty most of the time, for if I want to add anything that's too long to fit inside 'remarks'
    'time': '19:45',
    'location': [122.02222, 111.01111]
}