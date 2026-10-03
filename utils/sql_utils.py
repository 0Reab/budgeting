import sqlite3
from utils.logger import log
from utils.validation import has_dupes, valid_date, in_categories, validate_insert_params
from utils.validation import categories_expenses, categories_income, currencies


""" Module for: SQL queries, utilities, , formmated prints, DB connection object """


table_users = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        password_hash TEXT UNIQUE
    )"""

table_expenses = """
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        name TEXT,
        price REAL,
        amount REAL,
        date TEXT,
        user_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES users(id)
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
        date TEXT,
        user_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES users(id)
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
        log('info', 'had to create default expenses table')

    elif 'no such table: income' in str(error):
        cursor.execute(table_income)
        log('info', 'had to create default income table')

    elif 'no such table: users' in str(error):
        cursor.execute(table_users)
        log('info', 'had to create default users table')
    else:
        log('fail', 'unhandled sql error')
        raise Exception(f'database blew up. good luck -> {error}')

    conn.commit()
    conn.close()


def execute(query, data=None) -> list:
    ''' run sql query '''
    # im not sure on best return type beacuse this does read/write/delete
    # successful fetch returns a list from data, write/delete returns what? [] or None? or object
    conn, cursor = sql()

    def exec():
        if data:
            cursor.execute(query, data)
            result = cursor.fetchall()
            log('info', f'SQL -> {(query, data, result)}')
        else:
            result = cursor.execute(query)
            log('info', f'SQL -> {(query, data, result)}')

        if result == [] or result == () or result == {}:
            result = None

        return result

    try:
        return exec()

    except sqlite3.OperationalError as e:
        sql_error_handler(error=e)

        return exec()

    finally:
        if conn:
            conn.commit()
            conn.close()


def register(user: str, password_hash: str) -> bool:
    data = (user, password_hash)
    query = 'INSERT into users (user, password_hash) VALUES (?, ?)'

    # do validation here
    if user_exists(user):
        log('fail', f'user {user} already exists')
        return False

    execute(query, data)
    log('info', f'registered user {user}')
    return True


def user_exists(user: str) -> bool:
    query = "SELECT 1 FROM users WHERE user = ? LIMIT 1"

    if execute(query, (user,)) is not None:
        return True


def login(user: str, password_hash: str) -> bool:
    data = (user, password_hash)
    query = 'SELECT 1 FROM users WHERE user = (?) AND password_hash = (?)'

    # do validation here
    # return False

    log('info', f'try login user {user}')
    execute(query, data)
    log('info', f'logged in user {user}')
    return True


def get_user_row(query_type, query_value, retrieve='all'):
    ''' fetch user data via args like query (id/user/hash) and its value, and declare return type in (retreive)'''
    conn, cursor = sql()
    allow = ['id', 'user', 'password_hash']
    log('ok', 'init')

    type_fail = query_type not in allow
    allow.append('all')
    retrive_fail = retrieve not in allow

    if type_fail or retrive_fail:
        log('fail', 'usage of this func')

    cursor.execute(f"SELECT id, user, password_hash FROM users WHERE {query_type} = ?", (query_value,))

    try:
        row = cursor.fetchone()
        log('info', row)
        if row is None:
            return None

        match retrieve:
            case 'all': return row
            case 'id': return row[0]
            case 'user': return row[1]
            case 'password_hash': return row[2]
    finally:
        conn.close()


def insert_expense(item: list, user_id: str) -> bool:
    """ add entry to DB table with last validation step """
    data = [category, name, price, amount, date] = item
    data.append(user_id)

    query = 'INSERT INTO expenses (category, name, price, amount, date, user_id) VALUES (?, ?, ?, ?, ?, ?)'

    if validate_insert_params(category, name, price, amount, date, valid_categ=categories_expenses, user_id=user_id) is not True:
        log('fail', 'insert query validation')
        return False

    execute(query, data)

    log('info', f'{name}')
    return True


def insert_income(category, description, converted_amount, link, amount, currency, date, user_id):
    #                            bug bounty  XSS         50,000           http  500      USD     2026...
    query = 'INSERT INTO income (category, description, converted_amount, link, amount, currency, date, user_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)'

    valid = validate_insert_params(
        category=category,
        price=converted_amount,
        amount=amount,
        date=date,
        currency=currency,
        link=link,
        valid_categ=categories_income,
        name=description,  # 100 char limit
        user_id=user_id
    )

    if not valid:
        log('fail', 'Not inserting in DB, validation failed')
        return False

    date = f"{'.'.join(date.split('-')[::-1])}."  # convert date to dd.mm.yyyy. format
    data = (category, description, converted_amount, link, amount, currency, date, user_id)

    execute(query, data)

    log('info', f'insert {category} of {amount} {currency}')
    return True


def user_owned(user_id: str, item_id: str, table: str) -> bool:
    ''' check if user owns given item from the table '''
    if table not in ['expenses', 'income']:
        log('fail', 'usage: wrong table arg.')
        return False

    data = (user_id, item_id)
    query = f'SELECT 1 FROM {table} WHERE user_id = (?) AND id = (?) LIMIT 1'

    result = execute(query, data)

    if result is None:
        log('fail', f'User user_id={user_id} is NOT owner of item_id={item_id}, or item does not exist.')
    else:
        log('info', f'User user_id={user_id} OWNS item_id={item_id}')

    return result is not None


def db_delete(item_id: str, user_id: str, table: str) -> bool:
    """ delete DB table entry by ID or wildcard """
    query = f'DELETE FROM {table} WHERE id = (?)'

    if not user_owned(user_id, item_id, table):
        return False

    execute(query, [item_id])
    log('ok', f'deleted entry ID {item_id}')

    return True


def show_db(table: str, user_id: str) -> list:
    """ formatted string of all table entries """

    if table not in ['expenses', 'income']:
        log('fail', f'{table} is not a valid table.')
        return []

    # should be safe since table and user_id are not user input
    query = f'SELECT * FROM {table} WHERE user_id = {user_id}'

    conn, cursor = sql()
    db = None
    try:
        cursor.execute(query)
        db = cursor.fetchall()
    except Exception as e:
        sql_error_handler(e)
    finally:
        conn.close()

    if db is None:
        log('fail', 'no data fetched')
        return []

    result = []

    log('ok', 'print db')

    if table == 'expenses':
        for entry in db:
            id, categ, name, total, qty, date, user_id = entry  # should change these to classes yeh?
            line = f'ID - {id} | categ - {categ} | name - {name} | total - {total} | qty - {qty} | date - {date}'
            result.append(line)

    elif table == 'income':
        for entry in db:
            id, categ, desc, conver, link, amount, curr, date, user_id = entry  # should change these to classes yeh?
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
    execute(query)
