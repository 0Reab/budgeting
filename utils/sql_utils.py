import sqlite3
from utils.logger import log
from utils.validation import has_dupes, valid_date, in_categories, validate_insert_params
from utils.validation import categories_expenses, categories_income, currencies


""" Module for: SQL queries, utilities, , formmated prints, DB connection object """


table_expenses = """
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        name TEXT,
        price REAL,
        amount REAL,
        date TEXT
    )"""

table_income = """
    CREATE TABLE IF NOT EXISTS income (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        description TEXT,
        converted_amount REAL,
        link TEXT,
        amount REAL,
        currency CHAR(3),
        date TEXT
    )"""


def sql() -> tuple:
    """ create cursor and SQL DB connection """

    conn = sqlite3.connect("data/budget.db", check_same_thread=False)
    return conn, conn.cursor()


def sql_error_handler(error) -> None:
    '''Creates default table on specific error, expand for other edge cases.'''
    conn, cursor = sql()

    if 'no such table: expenses' in str(error):
        cursor.execute(table_expenses)
        conn.commit()
        log('info', 'had to create default expenses table')

    elif 'no such table: income' in str(error):
        cursor.execute(table_income)
        conn.commit()
        log('info', 'had to create default income table')

    else:
        log('fail', 'unhandled sql error')
        raise Exception('database blew up.')


def execute(cursor, query, conn=None, data=None):
    try:
        if data:
            cursor.execute(query, data)
        else:
            cursor.execute(query)

    except sqlite3.OperationalError as e:
        sql_error_handler(error=e)

        if data:
            cursor.execute(query, data)
        else:
            cursor.execute(query)

    if conn:
        conn.commit()


def insert_expense(i: list) -> bool:
    """ add entry to DB table with last validation step """

    conn, cursor = sql()
    category, name, price, amount, date = i

    query = 'INSERT INTO expenses (category, name, price, amount, date) VALUES (?, ?, ?, ?, ?)'
    data = (category, name, price, amount, date)

    if validate_insert_params(category, name, price, amount, date, valid_categ=categories_expenses) is not True:
        log('fail', 'insert query validation')
        return False

    execute(cursor, query, conn, data)

    log('info', f'{name}')
    return True


def insert_income(category, description, converted_amount, link, amount, currency, date):
    #                            bug bounty  XSS         50,000           http  500      USD     2026...
    query = 'INSERT INTO income (category, description, converted_amount, link, amount, currency, date) VALUES (?, ?, ?, ?, ?, ?, ?)'
    conn, cursor = sql()

    valid = validate_insert_params(
        category=category,
        price=converted_amount,
        amount=amount,
        date=date,
        currency=currency,
        link=link,
        valid_categ=categories_income,
        name=description  # 100 char limit
    )

    if not valid:
        log('fail', 'Not inserting in DB, validation failed')
        return False

    date = f"{'.'.join(date.split('-')[::-1])}."  # convert date to dd.mm.yyyy. format
    data = (category, description, converted_amount, link, amount, currency, date)

    execute(cursor, query, conn, data)

    log('info', f'insert {category} of {amount} {currency}')
    return True


def db_delete(id: str) -> bool:
    """ delete DB table entry by ID or wildcard """
    # needs refactoring from CLI to Web app operations
    # could refactor into two functions, validation and delete.

    conn, cursor = sql()
    # user_input = input('Select ID number to delete an entry: ')

    if id == '*':
        cursor.execute("DELETE FROM expenses")
        log('ok', 'database wipe')
        return True
    else:
        try:
            cursor.execute("SELECT id FROM expenses")
            rows = cursor.fetchall()

            id_nums = [row[0] for row in rows]

            if int(id) not in id_nums:
                log('fail', f'not found id={id} in DB')
                return False

            cursor.execute("DELETE FROM expenses WHERE id = (?)", [id])

        except (sqlite3.ProgrammingError, ValueError, TypeError) as e:
            log('fail', f'query error with id={id} - {e}')
            return False

    conn.commit()
    log('ok', f'deleted entry ID {id}')

    return True


def show_db(table: str) -> list:
    """ formatted print of all table entries to stdout """

    if table not in ['expenses', 'income']:
        log('fail', f'{table} is not a valid table.')
        return []

    query = f'SELECT * FROM {table}'

    _conn, cursor = sql()

    execute(cursor, query)

    db = cursor.fetchall()
    result = []

    log('ok', 'print db')

    if table == 'expenses':
        for entry in db:
            id, categ, name, total, qty, date = entry  # should change these to classes yeh?
            line = f'ID - {id} | categ - {categ} | name - {name} | total - {total} | qty - {qty} | date - {date}'
            result.append(line)

    elif table == 'income':
        for entry in db:
            id, categ, desc, conver, link, amount, curr, date = entry  # should change these to classes yeh?
            line = f'ID - {id} | categ - {categ} | description - {desc} | converted_amount - {conver} | link - {link} | amount - {amount} | currency - {curr} | date - {date}'
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
    execute(cursor, query)


def show_categories() -> None:
    """ print global categories to stdout """

    log('ok', 'DB categories')

    for idx, cat in enumerate(categories_income):
        print(f'{cat} - {idx}')


def con_close():
    """ SQL connection closing """
    # need to learn when and if this is needed

    conn, _cursor = sql()
    conn.close()

    log('info', 'closing connection')
