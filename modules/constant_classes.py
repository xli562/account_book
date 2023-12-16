class currency:
    cny = 'CNY'
    gbp = 'GBP'

class account_type:
    cash = '现金'
    debit = '借记卡'
    credit = '信用卡'
    virtual = '虚拟账户'
    custom = '自定义资产'
def is_bank(teststr:str) -> bool:
    if teststr in (account_type.debit, account_type.credit):
        return True
    else:
        return False

class company:
    HSBC_UK = 'HSBC UK'

class virtual:
    wechat = '微信'
    alipay = '支付宝'


class entry_type:
    expense = 'expense'
    income = 'income'