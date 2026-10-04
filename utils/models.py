''' Every DB table has a static model method, members as DB cols, and format_str for debugging '''


class User:
    def __init__(self, id, name, password_hash):
        self.id = id
        self.name = name
        self.password_hash = password_hash

    @staticmethod
    def db_model():
        return '''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT,
                password_hash TEXT UNIQUE
        )'''

    def format_str(self):
        return f'ID - {self.id} | name - {self.name} | password_hash - {self.password_hash}'

    def render_table(self):
        data = vars(self).copy()
        data.pop('password_hash', None)
        return data


class Wallet:
    def __init__(self, id, name, amount, user_id, currency):
        self.id = id
        self.name = name
        self.amount = amount
        self.user_id = user_id
        self.currency = currency

    @staticmethod
    def db_model():
        return '''
            CREATE TABLE IF NOT EXISTS wallets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                amount REAL DEFAULT 0,
                currency CHAR(3),
                user_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )'''

    def format_str(self):
        return f'ID - {id} | name - {self.name} | amount - {self.amount} | currency - {self.currency} | user_id'


'''
@app.route('/api/insert/income', methods=['POST'])
def income():
    converted_amount = request.form['converted_amount']
    description = request.form['description']
    category = request.form['category']
    currency = request.form['currency']
    amount = request.form['amount']
    link = request.form['link']
    date = request.form['date']
    user_id = session.get('id')

    ok = insert_income(
        category,
        description,
        converted_amount,
        link,
        amount,
        currency,
        date,
        user_id
    )
'''


class Income:
    def __init__(self, id, date, link, amount, user_id, category, currency, converted, description):
        self.id = id
        self.date = date
        self.link = link
        self.amount = amount
        self.user_id = user_id
        self.category = category
        self.currency = currency
        self.converted = converted
        self.description = description

    @staticmethod
    def db_model():
        return '''
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
            )'''

    def format_str(self):
        return f'ID - {id} | categ - {self.category} | description - {self.description} | converted_amount - {self.converted} | link - {self.link} | amount - {self.amount} | currency - {self.currency} | date - {self.date}'


class Expense:
    def __init__(self, id, date, total, user_id, quantity, category, currency, converted):
        self.id = id
        self.date = date
        self.total = total
        self.user_id = user_id
        self.quantity = quantity
        self.category = category
        self.currency = currency
        self.converted = converted

    @staticmethod
    def db_model():  # this table is missing currency column
        return '''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                name TEXT,
                price REAL,
                amount REAL,
                date TEXT,
                user_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )'''

    def format_str(self):
        return f'ID - {self.id} | categ - {self.category} | name - {self.name} | total - {self.total} | qty - {self.qty} | date - {self.date}'
