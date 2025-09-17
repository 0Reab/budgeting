import sqlite3
import utils.scanner as scanner
from datetime import datetime
from utils.logger import log


categories = ['other', 'tool', 'food', 'transport', 'bill', 'cosmetic', 'nightout','hobby']


def sql():
    conn = sqlite3.connect("budget.db", check_same_thread=False)
    return conn, conn.cursor()


def todays_date():
    return datetime.today().strftime(r'%d-%m-%Y')


def in_categories(test):
    try:
        idx = int(test)

        if len(categories) <= idx:
            log('fail', 'in_categories()', f'validate {test}, categories[{idx}] out of range')
            return None

        return categories[idx]

    except (TypeError, ValueError):
        if test in categories:
            return test

        log('fail', 'in_categories()', f'validate {test}')
        return None


def validate(category, name, price, amount, date) -> bool:
    log_fail = lambda msg: log('fail', 'validate()', msg) 

    # return True for successful validation otherwise False
    try:
        if in_categories(category) == None:
            log_fail('Failed category check')
            return False

        if price <= 0 or amount <= 0:
            log_fail('Failed price and amount')
            return False

        if len(name) > 100 or len(date) != 10:
            log_fail('Failed name and date')
            return False

    except Exception as e:
        log_fail(f'Other validation error - {e}')
        return False

    log('ok', 'validate()', 'validation')
    return True


def insert(category, name, price, amount, date):
    conn, cursor = sql()

    cursor.execute("INSERT INTO expenses (category, name, price, amount, date) VALUES (?, ?, ?, ?, ?)",
        (category, name, price, amount, date))

    conn.commit()
    log('info', 'insert()', 'SQL insert query')

    return True


def delete():
    conn, cursor = sql()
    user_input = input(f'Select ID number to delete an entry: ')

    if user_input == '*':

        check = input('Delete everything? y/n: ')

        if check == 'y':
            cursor.execute("DELETE FROM expenses")
            log('ok', 'delete()', 'SQL database wipe')
            return True
        else:
            log('info', 'delete()', 'SQL delete query aborted')
            return 'abort delete'
    else:
        try:
            cursor.execute("SELECT id FROM expenses")
            rows = cursor.fetchall()

            id_nums = [ row[0] for row in rows]

            if int(user_input) not in id_nums:
                log('fail', 'delete()', f'not found id={user_input} in DB')
                return None

            cursor.execute(f"DELETE FROM expenses WHERE id = (?)", [user_input])

        except (sqlite3.ProgrammingError, ValueError, TypeError) as e:
            log('fail', 'delete()', f'sql query error with id={user_input} - {e}')
            return None

    conn.commit()
    log('ok', 'delete()', 'SQL deleted entry')

    return True


def show_db():
    conn, cursor = sql()
    cursor.execute("SELECT * FROM expenses")
    db = cursor.fetchall()

    log('ok', 'show_db()', 'SQL print db')

    for entry in db:
        print(f'ID - {entry[0]} | categ - {entry[1]} | name - {entry[2]} | total - {entry[3]} | qty - {entry[4]} | date - {entry[5]}')


def show_categories():
    log('ok', 'show_categories()', 'DB categories')
    print()

    for idx, cat in enumerate(categories):
        print(f'{cat} - {idx}')


def con_close():
    # peak programming right here
    conn, cursor = sql()
    conn.close()

    log('info', 'con_close()', 'closing connection')
    exit()