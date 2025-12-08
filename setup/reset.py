import sqlite3
import os
from logging import log

""" Script for debugging / testing - delete DB and create new, with the same table structure """

def user_confirm():
    """ confirmed only if user input is 'y'
    return 'delete' upon success
    """

    answer = input('Are you sure you want delete the database?: y/n')

    if answer == 'y':
        return 'delete'
    else:
        print('[INFO] abort db deletion... exiting')
        return


def delete_db():
    """ delete database file """

    os.remove('budget.db')
    print('[OK] database deleted')


def reset():
    """ main - wrapper for functions """

    if user_confirm() == 'delete':
        delete_db()

    print('database init...')
    c = sqlite3.connect("budget.db")
    cu = c.cursor()

    cu.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        name TEXT,
        price REAL,
        amount REAL,
        date TEXT
    )
    """)

    print('created table')

    c.close()

#reset()