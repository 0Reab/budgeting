import os

from flask_bcrypt import Bcrypt

from flask import Flask, session
from flask import render_template, request, flash, redirect, jsonify, url_for

from utils.sql_utils import show_db, insert_expense, categories_expenses, categories_income, show_sum_of, db_delete, insert_income, user_exists, get_user_row, register, login, show_budget_sum
from utils.backend_utils import read_key, allowed_file, process_image
from utils.logger import log
from utils.validation import has_dupes, valid_user_id


# mr global variable -> refactor later
items = []

app = Flask(__name__, template_folder='pages')
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'images')
bcrypt = Bcrypt(app)


def basic(code=200, msg=None, err='Route not found.'):
    ''' Wrapper for ease of use '''
    # 399, range() is not inclusive
    if code in range(400):
        return render_template('home.html', msg=msg), code
    else:
        return render_template('home.html', err=f'Error: {code} {err}'), code


@app.template_global()
def show_user_name():
    if session:
        return session.get('name')


@app.template_global()
def show_budget():
    if session:
        return show_budget_sum(session.get('id'))


@app.before_request
def check_session():
    path_no_auth = request.path.startswith(('/login', '/register', '/static'))
    no_session = session.get('id') is None
    path = request.path

    if no_session and not path_no_auth:
        session.clear()
        return render_template('login.html', err=f'You need to be logged in to access {path}.')


@app.errorhandler(405)
def method_not_allowed(*args, **kwargs):
    return basic(405)


@app.errorhandler(404)
def not_found(error):
    return basic(404, err=f'route {request.path} not found.')


@app.route('/', methods=['GET'])
def home():
    msg = f'Welcome {session.get('name')}!'
    return basic(msg=msg)


@app.route('/health', methods=['GET'])
def health():
    # add more checks, then return 200 OK
    # maybe file integrity, DB test...
    return 'STATUS=OK', 200


@app.route('/debug', methods=['GET'])
def debug_route():
    user = session.get('name')
    id = session.get('id')

    return f'user={user} ; id={id}', 200


@app.route('/logout', methods=['GET'])
def logut_route():
    session.clear()
    return redirect(url_for('login_route'))


@app.route('/login', methods=['GET', 'POST'])
def login_route():
    if request.method == 'POST':
        user = request.form['username']
        password = request.form['password']

        log('ok', 'login attempt init')
        hash_in_db = get_user_row('user', user, 'password_hash')
        log('info', f'hash in db debug {hash_in_db}')

        if hash_in_db is None:
            log('info', 'User does not exist.')
            return render_template('login.html', err=f'User {user} does not exist.')

        hash_in_db = hash_in_db.encode('utf8')
        log('info', f'hash in db encoded debug {hash_in_db}')

        log('ok', 'checking password')
        try:
            if bcrypt.check_password_hash(hash_in_db, password):
                log('info', 'password passed check.')
                session.clear()
                login(user, hash_in_db)
                user_id = get_user_row('user', user, retrieve='id')
                session['name'] = user
                session['id'] = user_id

                return redirect(url_for('home'))
            else:
                log('info', 'Wrong password')
                return render_template('login.html', err='Incorrect password.')

        except ValueError as e:
            log('fail', f'bad user input {e}')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register_route():
    if request.method == 'POST':
        user = request.form['username']
        password = request.form['password']
        password_hash = bcrypt.generate_password_hash(password).decode('utf8')

        if register(user, password_hash):
            return render_template('login.html', msg=f'User {user} registered.')
        else:
            return render_template('register.html', err=f'User {user} already exists.')

    return render_template('register.html')


@app.route('/api/stats/month', methods=['GET'])
def stats():
    '''Fetch entries based on a timeframe'''

    count = request.args.get('count', default=1, type=int)
    selected_categories = request.args.getlist('categories', default=categories_expenses)

    for categ in set(selected_categories):
        if categ not in categories_expenses:
            return jsonify({'error': f'parameter category {categ} not available.'}), 400

    if count not in range(9999):
        return {'error': 'parameter count out of accepted range.'}, 400

    return jsonify(show_sum_of(
        time_type='monthly',
        categories=selected_categories,
        count=count
    ))


@app.route('/add-income', methods=['GET'])
def income_template():
    ''' Show form for adding income '''
    referer = request.headers.get("Referer")

    msg = 'Succes! Add more income.' if referer == '/api/insert/income' else 'Add income.'

    return render_template(
        'home.html',
        categories_income=categories_income,
        msg=msg,
        section_header='Income',
        section_header_msg='Add your income details.'
    )


@app.route('/api/insert/income', methods=['POST'])
def income():
    ''' Add data to income table. NEED TO CHECK IF DATE FORMAT IS THE SAME AS RECEIPTS! -> frontend form is mm/dd/yyy'''

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

    msg = 'Successful submit.' if ok else ''

    return redirect(url_for('show_table_data', table='income', status=msg))


@app.route('/api/delete', methods=['DELETE'])
def delete_entry():
    '''Delete database entries with given ID'''

    id_list = request.args.getlist("id")
    referrer = request.referrer.split('/')[-1]
    table = ''

    if '?' in referrer:
        table = referrer.split('?')[0]
    else:
        table = referrer

    if table not in ('expenses', 'income'):
        err = 'Table not allowed.'
        log('fail', table)
        return {'error': table}, 400

    # move off the validation to is module log there and return json here ye?

    if has_dupes(id_list):
        err = 'There are duplicate IDs in your query.'
        log('fail', err)
        return {'error': err}, 400

    if id_list in range(50 + 1):
        err = 'Amount of IDs to delete must be 1-50.'
        log('fail', err)
        return {'error': err}, 400

    # add tons of validation of user input from id_list later

    errors = []

    user_id = session.get('id')

    if not valid_user_id(user_id):
        return {'status': 'error', 'error': f'Failed to delete id: {user_id} ; Invalid user session'}

    for item_id in id_list:
        if db_delete(item_id, user_id, table) is False:
            errors.append(f'Failed to delete id: {user_id}')

    msg = 'error' if errors else 'ok'

    return {'status': msg, msg: errors}, 200


@app.route('/show/<table>', methods=['GET'])
def show_table_data(table):
    """ display DB entries """

    if table not in ['expenses', 'income']:
        return render_template('home.html', err_msg=f"Table {table} doesn't exist")

    status = request.args.get('status')
    user_id = session.get('id')

    msg = 'Success :)' if status else f'Showing {table}'

    if not valid_user_id(user_id):
        return basic(400)

    entries = show_db(table, user_id=user_id)

    return render_template(
        'home.html',
        db_result=entries,
        msg=msg,
        section_header=table.capitalize(),
        section_header_msg=f'View your {table} details.'
    )


@app.route('/categories', methods=['POST'])
def categories_post():
    """ parse user selected categories from POST data to annotate global 'items' SQL query """

    global items
    err_msg = "Error in data insertion, try again."

    user_categs = request.form.getlist("categories[]")

    # prevent insert when item buffer is empty (global var)
    # or item tags length do not match with items

    if not items or len(items) != len(user_categs) or '' in user_categs:

        log('fail', f'invalid data in user_categs = {user_categs} ; items = {items}')

        return render_template(
            'home.html',
            db_result=items,
            msg=err_msg,
            edit='yes',
            categories=categories_expenses
        ), 400

    user_id = session.get('id')

    if not valid_user_id(user_id):
        return basic(400, err='Authorization error.')

    for item in items:
        # update category with user input and insert in db
        item[0] = user_categs[0]
        user_categs.pop(0)
        insert_expense(item, user_id)

    items = []  # clear global buffer

    msg = 'Successful submit.'
    return redirect(url_for('show_table_data', table='expenses', status=msg))


@app.route('/upload', methods=['POST'])
def upload():
    """ image upload endpoint with processing """

    if 'file' not in request.files:
        flash('No file part')
        return redirect('/')

    file = request.files['file']

    if file.filename == '':
        flash('No selected file')
        return redirect('/')

    if file and allowed_file(file.filename):
        result = process_image(file)

        if result:
            global items
            db, items = result[0], result[1]
            return render_template(
                'home.html',
                db_result=db,
                msg='Success',
                edit='yes',
                categories=categories_expenses,
                section_header='Categorize entries',
                section_header_msg='Choose a category from the dropdown menu.'
            )
        else:
            return basic(400, err="No URL found in QR code")


if __name__ == '__main__':
    debug = True
    host = '0.0.0.0'
    cert = ['data/cert.pem', 'data/key.pem']

    app.secret_key = read_key()
    port = int(os.environ.get('PORT', '1337'))

    try:
        log('info', 'using self signed cert, SSL/TLS is available.')

        app.run(ssl_context=(cert[0], cert[1]), host=host, port=port, debug=debug)

    except FileNotFoundError:
        log('info', 'did not find self signed cert, SSL/TLS not available.')

        app.run(host=host, port=port, debug=debug)

