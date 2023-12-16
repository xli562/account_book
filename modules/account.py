from modules.constant_classes import *
from modules.entry import *

class account:
    def __init__(self, name:str, currency:currency, account_type:account_type, company:company='', last_4_digits:str='', comments:str=''):
        self._name = name
        self._currency = currency
        self._account_type = account_type
        self._conpany = company
        self._last_4_digits = last_4_digits
        self._comments = comments

        self.entries = [
            entry('10月19号到今天公交费用', entry_category.公共交通, entry_type.expense, 5, '2023-10-28 Sat'),
            entry('橘子两袋', entry_category.健康零食, entry_type.expense, 4, '2023-10-28 Sat'),
            entry('葡萄', entry_category.健康零食, entry_type.expense, 2.5, '2023-10-28 Sat'),
            entry('创建账户时的余额',entry_category.对账差额, entry_type.income, 102.18, '2023-10-28 Sat')
        ]


    def __str__(self) -> str:
        ''' 借记卡: HSBC(7476) 英国卡, 余额 81.35 GBP'''
        retstr = f'{self._account_type}: {self._name}'
        if is_bank(self._account_type):
            retstr += f'({self._last_4_digits})'
        retstr += f' {self._comments}, 余额{self.get_balance()} {self._currency}'
        return retstr

    def get_balance(self) -> float:
        return 81.35
    
    def print_all_entries(self) -> None:
        for entry in self.entries:
            print(entry)

    def add_expense(self):
        pass