from modules.constant_classes import *
from modules.entry_category import *
from modules.functional_convenience import *


class entry:
    def __init__(self, name:str, category:entry_category, entry_type:entry_type, value:float, date:str):
        self._name = name
        self._category = category
        self._entry_type = entry_type
        self._value = value
        self._date = date

    def __str__(self) -> str:
        return tabulate()
