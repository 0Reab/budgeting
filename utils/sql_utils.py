import sqlite3
from utils.logger import log
from utils.validation import has_dupes, valid_date, in_categories, validate_insert_params
from utils.validation import categories_expenses, categories_income, currencies, wallet_types, valid_amount


""" Module for: SQL queries, utilities, , formmated prints, DB connection object """


table_users = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        password_hash TEXT UNIQUE
    )"""

table_wallets = """
    CREATE TABLE IF NOT EXISTS wallets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        amount REAL DEFAULT 0,
        currency CHAR(3),
        user_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )"""

# this table is missing currency column
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

    elif 'no such table: wallets' in str(error):
        cursor.execute(table_wallets)
        log('info', 'had to create default wallets table')
    else:
        log('fail', 'unhandled sql error')
        raise Exception(f'database blew up. good luck -> {error}')

    conn.commit()
    conn.close()


def execute(query, data=None) -> list:
    ''' run sql query '''
    # im not sure on best return type beacuse this does read/write/delete
    # successful fetch returns a list from data, write/delete returns what? [] or None? or object
    # returns None on fail at the moment and list/tuple on
    # also returning ([]) just gives me a headache for indexing later and loopoing, fix this then
    # the code using unpacking as a bandaid for this

    conn, cursor = sql()

    def exec():
        result = None

        if data:
            result = cursor.execute(query, data)
        else:
            result = cursor.execute(query)

        result = cursor.fetchall()

        if result == [] or result == () or result == {}:
            result = None

        log('info', f'SQL -> {(query, data, result)}')
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

    user_id = get_user_row('user', user, 'id')

    if add_user_wallet(user_id) is not None:
        log('info', f'created wallet for user {user} id={user_id}')
    else:
        log('fail', f'failed to create wallet for user {user} id={user_id}')

    return True


def add_user_wallet(user_id, name='bank', amount=0):
    ''' wallet name will have all currencies created '''
    # possibly refactor this to be atomic, in case of errors.
    # expected failure is with bad function call, so ill add better validation of args.

    if amount not in range(1000000):
        log('fail', f'amount ({amount} not in range of 0-1M')
        return False

    if name not in wallet_types:
        log('fail', f'invalid wallet type {name}')
        return False

    for currency in currencies:  # creates for eg. 3x bank wallets of all currencies
        data = (name, amount, currency, user_id)
        query = 'INSERT INTO wallets (name, amount, currency, user_id) VALUES (?, ?, ?, ?)'
        execute(query, data)


def user_exists(user: str) -> bool:
    query = "SELECT 1 FROM users WHERE user = ? LIMIT 1"

    result = execute(query, (user,))
    log('info', f'result={result}')

    if result is not None:
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
    allow = ['id', 'user', 'password_hash']
    log('ok', 'init')

    type_fail = query_type not in allow
    allow.append('all')
    retrive_fail = retrieve not in allow

    if type_fail or retrive_fail:
        log('fail', 'usage of this func')

    query = f"SELECT id, user, password_hash FROM users WHERE {query_type} = ?"
    data = (query_value,)
    result = execute(query, data)

    log('info', result)
    if result is None:
        return None

    row = result[0]  # unpack nested data struct
    match retrieve:
        case 'all': return row
        case 'id': return row[0]
        case 'user': return row[1]
        case 'password_hash': return row[2]


def update_wallet(increase, amount, user_id, wallet_type=None, currency=None):
    ''' call this on each add expense or add income func, to update the budget accordingly '''
    # only update the wallet amount.
    # based on user_id choose a row to update.
    # take the existing amount and add/subtract based on increase=True / False

    if not valid_amount(amount):
        return False

    if wallet_type not in wallet_types:
        log('fail', f'wallet type {wallet_type} not accepted in {wallet_types}')
        return False

    if currency not in currencies:
        log('fail', f'currency {currency} not accepted in {currencies}')
        return False

    data = (user_id, wallet_type, currency)

    fetch_query = 'SELECT amount FROM wallets WHERE user_id = (?) AND name = (?) AND currency = (?) LIMIT 1'
    current_amount = execute(fetch_query, data)[0][0]  # for some reason it returned as this [(0.0,)] so acting accordingly rip (will fix this one day)

    if current_amount is None:
        log('fail', 'error current amount is None.')
        return False

    if increase:
        current_amount += float(amount)  # fix this if DB type switches to INT type, and below too
    else:
        current_amount -= float(amount)

    data = (current_amount, user_id, wallet_type, currency)

    update_query = 'UPDATE wallets SET amount = (?) WHERE user_id = (?) AND name = (?) AND currency = (?)'
    return execute(update_query, data)


def insert_expense(item: list, user_id: str) -> bool:
    """ add entry to DB table with last validation step """
    data = [category, name, price, amount, date] = item
    data.append(user_id)

    query = 'INSERT INTO expenses (category, name, price, amount, date, user_id) VALUES (?, ?, ?, ?, ?, ?)'

    if validate_insert_params(category, name, price, amount, date, valid_categ=categories_expenses, user_id=user_id) is not True:
        log('fail', 'insert query validation')
        return False

    execute(query, data)

    log('info', f'insert expese {category} of {amount}')
    update_wallet(False, amount, user_id, 'bank', 'RSD')
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

    log('info', f'insert income {category} of {amount} {currency}')
    update_wallet(True, amount, user_id, 'bank', currency)
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

    fetch = get_item(item_id, user_id, table)

    # income conversion not implemented - ingore for now
    log('debug', f'get_item={fetch}')

    # another reason to use classes
    if table == 'income':
        amount = fetch[5]
        currency = fetch[6]
    elif table == 'expenses':
        amount = fetch[3]
        currency = 'RSD'  # bug because table doesn't have this col in expenses...

    execute(query, [item_id])
    log('ok', f'deleted entry ID {item_id}')

    match table:  # hardcoded bank here for now.
        case 'income': update_wallet(False, amount, user_id, 'bank', currency)
        case 'expenses': update_wallet(True, amount, user_id, 'bank', currency)

    return True


def get_item(item_id, user_id, table):
    ''' fetch row from given table '''
    query = f'SELECT * FROM {table} WHERE user_id = (?) AND id = (?)'
    data = (user_id, item_id)

    if not user_owned(user_id, item_id, table):
        return False
    return execute(query, data)[0]


def show_budget_sum(user_id):
    ''' For UI to always display - this is placeholder func, does not work properly atm '''
    data = (user_id,)
    query = 'SELECT * FROM wallets WHERE user_id = (?)'

    rows = execute(query, data)
    if rows is None:
        return []

    total = 0
    for row in rows:
        total += row[2]

    return total


def show_db(table: str, user_id: str) -> list:
    """ formatted string of all table entries """

    if table not in ['expenses', 'income', 'wallets']:
        log('fail', f'{table} is not a valid table.')
        return []

    # should be safe since table and user_id are not user input
    query = f'SELECT * FROM {table} WHERE user_id = {user_id}'

    db = execute(query)

    if db is None:
        log('fail', 'no data fetched')
        return []

    log('ok', 'print db')

    result = []

    for entry in db:
        match table:
            case 'expenses':  # could use classes here
                id, categ, name, total, qty, date, user_id = entry
                line = f'ID - {id} | categ - {categ} | name - {name} | total - {total} | qty - {qty} | date - {date}'

            case 'income':
                id, categ, desc, conver, link, amount, curr, date, user_id = entry
                line = f'ID - {id} | categ - {categ} | description - {desc} | converted_amount - {conver} | link - {link} | amount - {amount} | currency - {curr} | date - {date}'

            case 'wallets':
                id, name, amount, curr, user_id = entry
                line = f'ID - {id} | name - {name} | amount - {amount} | currency - {curr}'

        result.append(line)
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
