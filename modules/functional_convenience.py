from modules import constants
import datetime as dt
from calendar import monthrange





def start_and_end_of_month(day:dt.datetime) -> tuple:
    """ Takes a datetime object,
        Returns start and end of the natural month. """
    start_of_month = dt.datetime(day.year, day.month, 1)
    end_of_month_day = monthrange(day.year, day.month)[1]
    end_of_month = dt.datetime(day.year, day.month, end_of_month_day)

    return (start_of_month, end_of_month)




def colour_print(colour:str, text:str, to_screen=False):
    """prints with colour"""
    text = str(text)
    if to_screen == True:
        constants.print_sig.sig.emit(text)
    if colour == 'orange':
        print('\033[38;5;202m'+text+'\033[0m')
    if colour == 'light blue':
        print('\033[94m'+text+'\033[0m')
    if colour == 'magenta':
        print('\033[35m'+text+'\033[0m')
    if colour == 'pink':
        print('\033[95m'+text+'\033[0m')
    if colour == 'yellow':
        print('\033[33m'+text+'\033[0m')