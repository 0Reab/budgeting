from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
from utils.logger import log
from backend import *
import os


app = Flask(__name__, template_folder='pages')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'images')
items = []


def read_key():
    """ read flask key from file """
    with open('key.txt', 'r') as f:
        key = f.read()
    return key


def allowed_file(filename):
    """ file extension validation """
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.errorhandler(405)
def method_not_allowed():
    return render_template('home.html', err='Wrong HTTP method')


@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')


@app.route('/health', methods=['GET'])
def health():
    # add more checks, then return 200 OK
    # maybe file integrity, DB test...
    return 'STATUS=OK', 200


@app.route('/stats')
def stats():
    '''Fetch entries based on a timeframe'''

    time = request.args.get('time_scale', default='month', type=str)
    categories = request.args.get('categories', default=None, type=NoneType)

    # result = db_

    return 'test', 200  # jsonify(result)


@app.route('/saved', methods=['GET'])
def saved():
    """ display DB entries """

    msg = 'All database entries.'
    entries = show_db()

    return render_template('home.html', db_result=entries, msg=msg)


@app.route('/categories', methods=['POST'])
def categories_post():
    """ parse user selected categories from POST data to annotate global 'items' SQL query """

    global items
    err_msg = "Error in data insertion, try again."
    err_status = 400

    user_categs = request.form.getlist("categories[]")
    msg = 'Success :)'

    # prevent insert when item buffer is empty (global var)
    # or item tags length do not match with items

    if not items or len(items) != len(user_categs) or '' in user_categs:
        log('fail', 'categories_post()', f'invalid data in user_categs = {user_categs}')
        return render_template('home.html', db_result=items, msg=err_msg, edit='yes', categories=categories), err_status

    for item in items:
        # update category with user input and insert in db
        item[0] = user_categs[0]
        user_categs.pop(0)
        insert(item)

    items = []  # clear global buffer

    return render_template('home.html', msg=msg)


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
        return run_backend(file)


def run_backend(file):
    """ image processing and calling backend processor """

    filename = secure_filename(file.filename)
    img_path = app.config['UPLOAD_FOLDER']

    os.makedirs(img_path, exist_ok=True)
    file.save(os.path.join(img_path, filename))

    log('ok', 'upload()', 'Image post request')

    filepath = f'{img_path}/{filename}'
    global items
    items = image_scan(filepath)

    if items is None:
        return render_template('home.html', err="No URL found in QR code.")

    print(f'DEBUGGING -> {items}')

    result = []
    for entry in items:
        line = f'ID - / | categ - {entry[0]} | name - {entry[1]} | total - {entry[2]} | qty - {entry[3]} | date - {entry[4]}'
        result.append(line)

    return render_template(
        'home.html', db_result=result, msg='Success', edit='yes', categories=categories)


if __name__ == '__main__':
    app.secret_key = read_key()
    port = int(os.environ.get('PORT', 1337))
    app.run(host='0.0.0.0', port=port, debug=True)
