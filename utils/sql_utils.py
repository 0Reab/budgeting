import sqlite3
import utils.scanner as scanner
from datetime import datetime
from utils.logger import log


conn = sqlite3.connect("budget.db")
cursor = conn.cursor()

categories = ['other', 'tool', 'food', 'transport', 'bill', 'cosmetic', 'nightout','hobby']


def todays_date():
    return datetime.today().strftime(r'%d-%m-%Y')


def in_categories(test):
    try:
        log('ok', 'in_categories()', 'validation')
        return categories[int(test)]

    except (TypeError, ValueError):
        if test in categories:
            log('ok', 'in_categories()', 'validation')
            return test

        log('fail', 'in_categories()', 'validation')
        return None


def validate(category, name, price, amount, date) -> bool:
    log_fail = lambda msg: log('fail', 'validate()', msg) 

    # return True for successful validation otherwise False
    try:
        if in_categories(category) is None:
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
    cursor.execute("INSERT INTO expenses (category, name, price, amount, date) VALUES (?, ?, ?, ?, ?)",
        (category, name, price, amount, date))

    conn.commit()
    log('info', 'insert()', 'SQL insert query')

    return True


def delete():
    user_input = input(f'Select ID number to delete an entry: ')

    if user_input == '*':

        check = input('Delete everything? y/n: ')

        if check == 'y':
            log('success', 'delete()', 'SQL database wipe')
            cursor.execute(f"DELETE * FROM expenses", (user_input))
        else:
            log('info', 'delete()', 'SQL delete query aborted')
            return 'abort delete'
    else:
        cursor.execute(f"DELETE FROM expenses WHERE id = (?)", (user_input))

    conn.commit()
    log('success', 'delete()', 'SQL deleted entry')

    return True


def show_db():
    cursor.execute("SELECT * FROM expenses")
    db = cursor.fetchall()

    log('info', 'show_db()', 'SQL print db')

    for entry in db:
        print(f'ID - {entry[0]} | categ - {entry[1]} | name - {entry[2]} | total - {entry[3]} | qty - {entry[4]} | date - {entry[5]}')


def show_categories():
    log('info', 'show_categories()', 'DB categories')

    for idx, cat in enumerate(categories):
        print(f'{cat} - {idx}')


def con_close():
    conn.close()

    log('info', 'con_close()', 'closing connection')
    exit()