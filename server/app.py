import os
from flask import render_template, request, flash, redirect, jsonify, url_for

from utils.sql_utils import show_db, insert_expense, categories_expenses, categories_income, show_sum_of, db_delete, insert_income
from utils.backend_utils import read_key, allowed_file, run_backend
from utils.logger import log
from flask import Flask


# mr global variable -> refactor later
items = []

app = Flask(__name__, template_folder='pages')
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'images')


@app.errorhandler(405)
def method_not_allowed():
    return render_template('home.html', err='Error 405: Method not allowed.'), 405


@app.errorhandler(404)
def not_found(error):
    return render_template('home.html', err='Error 404: Not found.'), 404


@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')


@app.route('/health', methods=['GET'])
def health():
    # add more checks, then return 200 OK
    # maybe file integrity, DB test...
    return 'STATUS=OK', 200


@app.route('/api/stats/month', methods=['GET'])
def stats():
    '''Fetch entries based on a timeframe'''

    count = request.args.get('count', default=1, type=int)
    selected_categories = request.args.getlist('categories', default=categories_expenses)

    for categ in set(selected_categories):
        if categ not in categories_expenses:
            return jsonify({'error': f'parameter category {categ} not available.'}), 400

    if not (0 < count < 9999):
        return jsonify({'error': 'parameter count out of accepted range.'}), 400

    return jsonify(show_sum_of(
        time_type='monthly',
        categories=selected_categories,
        count=count
    ))


@app.route('/add-income', methods=['GET'])
def income_template():
    ''' Show form for adding income '''
    # broken atm need to figure out the form submit flow and not have it change href to /api
    # but stay rather and refresh template
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

    ok = insert_income(
        category,
        description,
        converted_amount,
        link,
        amount,
        currency,
        date
    )

    msg = 'Successful submit.' if ok else ''
    # msg = f'{'ok' if ok else 'error'}'
    # return jsonify(
    #     {'status': msg}
    # )

    # return render_template('home.html', msg=msg)
    return redirect(url_for('show_table_data', table='income', status=msg))


@app.route('/api/delete', methods=['DELETE'])
def delete_entry():
    '''Delete database entries with given ID'''

    id_list = request.args.getlist("id")

    if len(id_list) != len(set(id_list)):
        return jsonify({'error': "There are duplicate IDs in your query."}), 400

    if len(id_list) > 50 or len(id_list) <= 0:
        return jsonify({'error': "Amount of IDs to delete must be x > 0 and x < 50"}), 400

    # add tons of validation of user input from id_list later

    errors = []

    for id in id_list:
        if db_delete(id) is False:
            errors.append(f'Failed to delete id: {id}')

    msg = 'error' if errors else 'ok'

    return jsonify(
        {'status': msg, msg: errors}
    )


@app.route('/show/<table>', methods=['GET'])
def show_table_data(table):
    """ display DB entries """

    if table not in ['expenses', 'income']:
        return render_template('home.html', err_msg=f"Table {table} doesn't exist")

    status = request.args.get('status')

    msg = 'Success :)' if status else f'Showing {table}'
    entries = show_db(table)

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
        log('fail', 'categories_post()', f'invalid data in user_categs = {user_categs}')
        print(f'debugging :c -> len(items)={len(items)} ; len(user_categs)={len(user_categs)}')
        return render_template('home.html', db_result=items, msg=err_msg, edit='yes', categories=categories_expenses), 400

    for item in items:
        # update category with user input and insert in db
        item[0] = user_categs[0]
        user_categs.pop(0)
        insert_expense(item)

    items = []  # clear global buffer

    # return render_template('home.html', msg='Success :)')
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
        result = run_backend(file)

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
            return render_template('home.html', err="No URL found in QR code.")


if __name__ == '__main__':
    app.secret_key = read_key()
    port = int(os.environ.get('PORT', '1337'))
    app.run(host='0.0.0.0', port=port, debug=True)
