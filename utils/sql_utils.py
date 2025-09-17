import sqlite3
import utils.scanner as scanner
from datetime import datetime


conn = sqlite3.connect("budget.db")
cursor = conn.cursor()

categories = ['other', 'tool', 'food', 'transport', 'bill', 'cosmetic', 'nightout','hobby']


def todays_date():
    return datetime.today().strftime(r'%d-%m-%Y')


def in_categories(test):
    try:
        return categories[int(test)]

    except (TypeError, ValueError):
        if test in categories:
            return test
        return None


def validate(category, name, price, amount, date) -> bool:

    # return True for successful validation otherwise False
    try:
        if in_categories(category) is None:
            print('Failed category', f'category = {category} -> in_categories(category)')
            return False

        if price <= 0 or amount <= 0:
            print('Failed price and mount')
            return False

        if len(name) > 100 or len(date) != 10:
            print('Failed name and date')
            return False

    except Exception as e:
        print(f'Validation Error - {e}')
        return False

    return True


def insert(category, name, price, amount, date):
    cursor.execute("INSERT INTO expenses (category, name, price, amount, date) VALUES (?, ?, ?, ?, ?)",
        (category, name, price, amount, date))

    conn.commit()

    return True


def delete():
    user_input = input(f'Select ID number to delete an entry: ')

    if user_input == '*':

        check = input('Delete everything? y/n: ')

        if check == 'y':
            cursor.execute(f"DELETE * FROM expenses", (user_input))
        else:
            return 'abort delete'
    else:
        cursor.execute(f"DELETE FROM expenses WHERE id = (?)", (user_input))

    conn.commit()

    return True


def show_db():
    cursor.execute("SELECT * FROM expenses")
    db = cursor.fetchall()

    for entry in db:
        print(f'ID - {entry[0]} | categ - {entry[1]} | name - {entry[2]} | total - {entry[3]} | qty - {entry[4]} | date - {entry[5]}')


def show_categories():
    for idx, cat in enumerate(categories):
        print(f'{cat} - {idx}')


def con_close():
    conn.close()
    exit()