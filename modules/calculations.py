from modules import constants
import datetime as dt
import numpy
numpy.sum


def calculate_sums(accnts:str|list|None, 
                   start_date:dt.datetime, end_date:dt.datetime, 
                   currency:str='GBP', ignore_surpressed_accnts=True, 
                   ignore_surpressed_categories=True) -> tuple:
    """ 
    Sum of transaction amounts over a time period, in a given currency.

    Parameters
    ----------
    accnts : str, or list, or None
        Account or accounts to sum. All accounts if None given.
    start_date : Datetime Object
        Start point of sum, inclusive.
    end_date : Datetime Object
        End point of sum, inclusive.
    currency : str, optional
        Sum would be in this currency. Defaults to 'GBP'.
    ignore_surpressed_accnts : bool, optional
        Exclude surpressed accounts (eg savings accounts) from sum.
    ignore_surpressed_categories : bool, optional
        Exclude surpressed categories (eg '借款', '取钱') from sum.

    Returns
    -------
    (income_sum, expenditure_sum) : tuple
        Tuple of sum of incomes and expenditures.

    See Also
    --------
    TODO

    Notes
    -----
    TODO
    """

    # Initialise variables to be returned
    income_sum = 0
    expenditure_sum = 0

    # Prevent repeated un-pickling
    constants_currs = constants.currs()

    # Default currency to GBP
    currency = 'GBP' if currency not in constants_currs else currency

    # Create query for date range and accounts
    query = {
        "date": {"$gte": start_date, "$lte": end_date}
    }
    if accnts is not None:
        query['account'] = {"$in": accnts} if isinstance(accnts, list) else accnts

    # Iterate through found entries
    for entry in constants.entries_collection.find(query):
        amount = entry['amount']
        transaction_type = entry['transaction_type']
        original_currency = 'GBP' if currency not in constants_currs else entry['currency']
        exchange_rates:dict = entry.get('exchange_rates', {})

        # Accumulation
        if original_currency == currency:
            if transaction_type == '收入':
                income_sum += amount
            elif transaction_type == '支出':
                expenditure_sum += amount

        # Currency conversion and accumulation
        else:
            original_cny_rate = 1.0 if original_currency == 'CNY' else exchange_rates.get(f'{original_currency.lower()}_cny')
            target_cny_rate = 1.0 if currency == 'CNY' else exchange_rates.get(f'{currency.lower()}_cny')
            try:
                if transaction_type == '收入':
                    income_sum += amount * original_cny_rate / target_cny_rate
                elif transaction_type == '支出':
                    expenditure_sum += amount * original_cny_rate / target_cny_rate
            except TypeError:
                print(original_currency)
                print(exchange_rates.get(f'{original_currency.lower()}_cny'))
                print(original_cny_rate, target_cny_rate)

    return (income_sum, expenditure_sum)

