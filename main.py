import datetime as dt
from calendar import monthrange

def start_of_month(day: dt.datetime) -> tuple:
    ''' Takes a datetime object, Returns start and end of the natural month. '''
    start_of_month = dt.datetime(day.year, day.month, 1)
    end_of_month_day = monthrange(day.year, day.month)[1]
    end_of_month = dt.datetime(day.year, day.month, end_of_month_day)

    return (start_of_month, end_of_month)

# Example usage
day = dt.datetime(2023, 2, 15)
start, end = start_of_month(day)
print("Start of Month:", start)
print("End of Month:", end)
