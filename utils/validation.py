from utils.logger import log


''' Module only for validation, to be used anywhere (needs more docstrings and robustnes)'''


currencies = ['USD', 'GBP', 'RSD']  # USD, British pound, RSD

categories_expenses = ['other', 'tool', 'food', 'transport', 'bill', 'cosmetic', 'nightout', 'hobby']
categories_income = ['bug bounty', 'photoshop', 'modoolar']

categories_all = [categories_expenses, categories_income]


def has_dupes(data: list) -> bool:
    ''' any dupes in a list '''
    return len(data) != len(set(data))


def in_categories(test, valid_categ: list):
    """ Validation - if arg is in whitelist of array categories """
    # potentialy introduced a bug with swappign to False instead of None on fail, check later
    if valid_categ not in categories_all:
        log('fail', f'validate {valid_categ} not found in all categs {categories_all}')
        return False

    try:
        idx = int(test)

        if len(valid_categ) <= idx:
            log('fail', f'validate {test}, categories[{idx}] out of range')
            return False

        return valid_categ[idx]

    except (TypeError, ValueError):
        if test in valid_categ:
            return test

        log('fail', f'validate {test} ; {type(test)}')
        return False


def valid_name(name: str) -> bool:
    if len(name) > 100:
        log('fail', f'Failed name={name}')
        return False

    return True


def valid_price(price: float) -> bool:
    if int(price) <= 0:
        log('fail', f'Failed price={price}')
        return False

    return True


def valid_amount(amount: float) -> bool:
    if int(amount) <= 0:
        log('fail', f'Failed amount={amount}')
        return False

    return True


def valid_date(date: str) -> bool:
    if len(date) == 10:  # case 2026-01-27 needs to be 27.01.2026
        date = f"{'.'.join(date.split('-')[::-1])}."

    if len(date) != 11:
        log('fail', f'Failed date={date}')
        return False

    int(date.replace('.', '').replace('0', ''))  # fails validation if it's not a valid integer aka only nums

    return True


def valid_currency(currency: str) -> bool:
    if currency not in currencies:
        log('fail', f'Failed currency={currency} not in {currencies}')
        return False

    return True


def valid_link(link: str) -> bool:
    ''' allow empty str, or if it starts as http URL '''

    is_link = link.startswith(('https://', 'http://'))

    if is_link or link != '':
        log('fail', f'Failed link={link} is not https or http')
        return False

    return True


def validate_insert_params(category: str, name: str, price: float, amount: float, date: str, currency: str = None, link: str = None, valid_categ: list = None) -> bool:
    """
    Main validation func of all insert(i) parameters
    return True for successful validation otherwise False
    """

    try:
        if not in_categories(category, valid_categ):
            return False

        if not valid_price(price):
            return False

        if not valid_amount(amount):
            return False

        if not valid_name(name):
            return False

        if not valid_date(date):
            return False

        skip_extra_checks = currency is None or link is None or valid_categ is None

        if not skip_extra_checks:
            if not valid_currency(currency):
                return False

            if not valid_link(link):
                return False

    except Exception as e:
        log('fail', f'Other validation error - {e}')
        return False

    log('ok', f'{category} ; {name}')
    return True
