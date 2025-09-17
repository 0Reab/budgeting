import sqlite3
import os
from logging import log


#categories = ['other', 'tool', 'food', 'transport', 'bill', 'cosmetic', 'nightout','hobby']

def user_confirm():
    answer = input('Are you sure you want delete the database?: y/n')

    if answer == 'y':
        log('info', 'user_confirm()', 'deleting the database')
        return 'delete'
    else:
        print('[INFO] abort db deletion... exiting')
        return


def delete_db():
    os.remove('budget.db')
    print('[OK] database deleted')


def reset():
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