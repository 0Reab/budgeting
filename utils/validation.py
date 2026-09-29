from utils.logger import log


''' Module only for validation, to be used anywhere '''


categories_expenses = ['other', 'tool', 'food', 'transport', 'bill', 'cosmetic', 'nightout', 'hobby']
categories_income = ['bug bounty', 'photoshop', 'modoolar']
currencies = ['USD', 'GBP', 'RSD']  # USD, British pound, RSD


def has_dupes(data: list) -> bool:
    ''' any dupes in a list '''
    return len(data) != len(set(data))


def is_date() -> bool:
    return True


def in_categories(test, valid_categ: list) -> str | None:
    """ Validation - if arg is in whitelist of array categories """
    try:
        idx = int(test)

        if len(valid_categ) <= idx:
            log('fail', 'in_categories()', f'validate {test}, categories[{idx}] out of range')
            return None

        return valid_categ[idx]

    except (TypeError, ValueError):
        if test in valid_categ:
            return test

        log('fail', f'validate {test} ; {type(test)}')
        return None


def validate(category: str, name: str, price: float, amount: float, date: str, currency: str = None, link: str = None, valid_categ: list = None) -> bool:
    """
    Main validation func of all insert(i) parameters
    return True for successful validation otherwise False
    """

    # refactor into cleaner and decoupled logic pls
    # break it up kinda

    log_fail = lambda msg: log('fail', msg)

    try:
        if in_categories(category, valid_categ) is None:
            log_fail(f'Failed category check {category}')
            return False

        if int(price) <= 0 or int(amount) <= 0:
            log_fail(f'Failed price or amount price={price} ; amount={amount}')
            return False

        if len(date) == 10:  # case 2026-01-27 needs to be 27.01.2026
            date = f"{'.'.join(date.split('-')[::-1])}."

        if len(name) > 100 or len(date) != 11:
            log_fail(f'Failed name or date name={name} ; date={date}')
            return False

        # check date
        int(date.replace('.', '').replace('0', ''))  # fails validation if it's not a valid integer aka only nums

        skip_extra_checks = currency is None or link is None or valid_categ is None

        if not skip_extra_checks:
            if currency not in currencies:
                log_fail(f'Failed currency={currency} not in {currencies}')
                return False

            is_link = link.startswith(('https://', 'http://'))

            # allow empty str, or if it starts as http URL
            if is_link or link != '':
                log_fail(f'Failed link={link} is not https or http')
                return False

    except Exception as e:
        # [FAIL] in validate() - Other validation error - '<=' not supported between instances of 'str' and 'int'
        log_fail(f'Other validation error - {e}')
        return False

    log('ok', f'{category} ; {name}')
    return True
