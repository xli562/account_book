import pymongo


from modules.account import *
from modules.constant_classes import *
from modules.entry_category import *
from modules.entry import *

account_1 = account('HSBC', currency.gbp, account_type.debit, company.HSBC_UK, '7476', '英国卡')
account_2 = account('现金', currency.gbp, account_type.cash, comments='英镑')
print(account_1)
print(account_2)