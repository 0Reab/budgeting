import sqlite3
from utils.logger import log
# from datetime import datetime


""" Module for: SQL queries, utilities, validation, formmated prints, DB connection object """


categories_expenses = ['other', 'tool', 'food', 'transport', 'bill', 'cosmetic', 'nightout', 'hobby']
categories_income = ['bug bounty', 'photoshop', 'modoolar']
currencies = ['USD', 'GBP', 'RSD']  # USD, British pound, RSD


def sql() -> tuple:
    """ create cursor and SQL DB connection """

    conn = sqlite3.connect("budget.db", check_same_thread=False)
    return conn, conn.cursor()


def sql_error_handler(error) -> None:
    '''Creates default table on specific error, expand for other edge cases.'''
    conn, cursor = sql()

    if 'no such table: expenses' in str(error):
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            name TEXT,
            price REAL,
            amount REAL,
            date TEXT
        )
        """)

        conn.commit()
        log('info', 'sql_error_handler()',
            'SQL -> (had to create default expenses table)')

    elif 'no such table: income' in str(error):
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS income (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            description TEXT,
            converted_amount REAL,
            link TEXT,
            amount REAL,
            currency CHAR(3),
            date TEXT
        )
        """)

        conn.commit()
        log('info', 'sql_error_handler()',
            'SQL -> (had to create default income table)')
    else:
        log('fail', 'sql_error_handler()',
            'SQL -> unhandled sql error')
        raise Exception('database blew up.')


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

        log('fail', 'in_categories()', f'validate {test} ; {type(test)}')
        return None


def validate(category: str, name: str, price: float, amount: float, date: str, currency: str, link: str, valid_categ: list) -> bool:
    """
    Main validation func of all insert(i) parameters
    return True for successful validation otherwise False
    """

    log_fail = lambda msg: log('fail', 'validate()', msg)

    try:
        if in_categories(category, valid_categ) is None:
            log_fail(f'Failed category check {category}')
            return False

        if price <= 0 or amount <= 0:
            log_fail(f'Failed price or amount price={price} ; amount={amount}')
            return False

        if len(name) > 100 or len(date) != 11:
            log_fail(f'Failed name or date name={name} ; date={date}')
            return False

        if currency not in currencies:
            log_fail(f'Failed currency={currency} not in {currencies}')
            return False

        is_link = link.startswith('https://') or link.startswith('http://')

        # allow empty str, or if it starts as http URL
        if is_link or link != '':
            log_fail(f'Failed link={link} is not https or http')
            return False

    except Exception as e:
        log_fail(f'Other validation error - {e}')
        return False

    log('ok', 'validate()', f'{category} ; {name}')
    return True


def insert_expense(i: list) -> bool:
    """ add entry to DB table with last validation step """

    conn, cursor = sql()
    category, name, price, amount, date = i

    query = 'INSERT INTO expenses (category, name, price, amount, date) VALUES (?, ?, ?, ?, ?)'
    data = (category, name, price, amount, date)

    if validate(category, name, price, amount, date) is not True:
        log('fail', 'insert()', 'SQL insert query validation')
        return False
    try:
        cursor.execute(query, data)
        conn.commit()

    except sqlite3.OperationalError as e:
        sql_error_handler(error=e)

        cursor.execute(query, data)
        conn.commit()

    log('info', 'insert_expense()', f'SQL -> {name}')
    return True


def insert_income(category, description, converted_amount, link, amount, currency, date):
    #                            bug bounty  XSS         50,000           http  500      USD     2026...
    query = 'INSERT INTO income (category, description, converted_amount, link, amount, currency, date) VALUES (?, ?, ?, ?, ?, ?, ?)'
    data = (category, description, converted_amount, link, amount, currency, date)
    conn, cursor = sql()

    validate(
        category=category,
        price=converted_amount,
        amount=amount,
        date=date,
        currency=currency,
        link=link,
        valid_categ=categories_income,
        name=description  # 100 char limit
    )

    try:
        cursor.execute(query, data)
        conn.commit()

    except sqlite3.OperationalError as e:
        sql_error_handler(error=e)

        cursor.execute(query, data)
        conn.commit()

    log('info', 'insert_income()', f'SQL -> {category} of {amount} {currency}')
    return True


def db_delete(id: str) -> bool:
    """ delete DB table entry by ID or wildcard """
    # needs refactoring from CLI to Web app operations
    # could refactor into two functions, validation and delete.

    conn, cursor = sql()
    # user_input = input('Select ID number to delete an entry: ')

    if id == '*':
        cursor.execute("DELETE FROM expenses")
        log('ok', 'delete()', 'SQL database wipe')
        return True
    else:
        try:
            cursor.execute("SELECT id FROM expenses")
            rows = cursor.fetchall()

            id_nums = [row[0] for row in rows]

            if int(id) not in id_nums:
                log('fail', 'delete()', f'not found id={id} in DB')
                return False

            cursor.execute("DELETE FROM expenses WHERE id = (?)", [id])

        except (sqlite3.ProgrammingError, ValueError, TypeError) as e:
            log('fail', 'delete()', f'sql query error with id={id} - {e}')
            return False

    conn.commit()
    log('ok', 'delete()', f'SQL deleted entry ID {id}')

    return True


def show_db(table: str) -> list:
    """ formatted print of all table entries to stdout """

    if table not in ['expenses', 'income']:
        log('fail', 'show_db()', f'SQL print db table {table} is not a valid table.')
        return []

    query = f'SELECT * FROM {table}'

    _conn, cursor = sql()
    try:
        cursor.execute(query)

    except sqlite3.OperationalError as e:
        sql_error_handler(error=e)

        cursor.execute(query)

    db = cursor.fetchall()
    result = []

    log('ok', 'show_db()', 'SQL print db')

    if table == 'expenses':
        for entry in db:
            line = f'ID - {entry[0]} | categ - {entry[1]} | name - {entry[2]} | total - {entry[3]} | qty - {entry[4]} | date - {entry[5]}'
            result.append(line)

    elif table == 'income':
        for entry in db:
            line = f'ID - {entry[0]} | categ - {entry[1]} | description - {entry[2]} | converted_amount - {entry[3]} | link - {entry[4]} | amount - {entry[5]} | currency - {entry[6]} | date - {entry[7]}'
            result.append(line)

    # id, categ, desc, conv, link, amount, curr, date = entry
    return result


def show_sum_of(time_type: str, categories: list, count: int):
    ''' eg. count=12, time_type='monthly', categories=['food'] '''
    # last year of each month total spent on food.
    #
    # example db date -> 17.09.2026. TEXT
    # this ufnc return dict -> { jan: 50, feb: 60 ...}

    # get current date
    # default the day as 1 always.
    # subtract count arg from curr date - roll over to 12 again if hit 0 (also decrement year)
    # so if count=12 so entries from 1.9.2025 til today
    #
    # now how do i get all entries in between that first entry of date to today.
    # you could do by month then by year check for greater nubers in db?
    # so lets say years, any entry of year higher good to go.
    # and for months any month as farthes and higher if the year is not different
    #
    # but i also gotta sum each month - should be easy, *.9.2025 so anything that satisfies this i gues, take total values and sum

    query = 'SELECT FROM expenses WHERE date = (?)'

    _conn, cursor = sql()
    try:
        cursor.execute(query)

    except sqlite3.OperationalError as e:
        sql_error_handler(error=e)

        cursor.execute(query)


def show_categories() -> None:
    """ print global categories to stdout """

    log('ok', 'show_categories()', 'DB categories')
    print()

    for idx, cat in enumerate(categories_income):
        print(f'{cat} - {idx}')


def con_close():
    """ SQL connection closing """
    # need to learn when and if this is needed

    conn, _cursor = sql()
    conn.close()

    log('info', 'con_close()', 'closing connection')
