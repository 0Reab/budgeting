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


@app.route('/', methods=['GET'])
def home():
    if request.method == 'GET':
        return render_template('home.html')
    else:
        return render_template('home_error.html')


@app.route('/saved', methods=['GET'])
def saved():
    """ display DB entries """

    if request.method == 'GET':
        msg = 'All database entries.'
        entries = show_db()
        return render_template('home.html', db_result=entries, msg=msg)
    else:
        return render_template('home_error.html')


@app.route('/categories', methods=['POST'])
def categories_post():
    """ parse user selected categories from POST data to annotate global 'items' SQL query """

    if request.method == 'POST':
        global items
        err_msg = "Error in data insertion, try again."
        err_status = 400

        user_categs = request.form.getlist("categories[]")
        msg = 'Success :)'

        def error():
            log('fail', 'categories_post()', f'invalid data in user_categs = {user_categs}')
            return render_template('home.html', db_result=items, msg=err_msg, edit='yes', categories=categories)
            #return render_template('home.html', msg=err_msg), err_status

        # prevent insert when item buffer is empty (global var)
        # or item tags length do not match with items

        if not items or len(items) != len(user_categs) or '' in user_categs:
            return error()

        for item in items:
            # update category with user input and insert in db
            item[0] = user_categs[0] 
            user_categs.pop(0) 
            insert(item)

        items = [] # clear global buffer

        return render_template('home.html', msg=msg)
    else:
        return render_template('home_error.html')


@app.route('/upload', methods=['POST'])
def upload():
    """ image upload endpoint with processing """

    if request.method == 'POST':

        if 'file' not in request.files:
            flash('No file part')
            return redirect('/')

        file = request.files['file']

        if file.filename == '':
            flash('No selected file')
            return redirect('/')

        if file and allowed_file(file.filename):
            return run_backend(file)
    else:
        log('fail', 'upload()', 'Image post request')
        return render_template('home_error.html')


def run_backend(file):
    """ image processing and calling backend processor """

    filename = secure_filename(file.filename)
    img_path = app.config['UPLOAD_FOLDER']

    file.save(os.path.join(img_path, filename))

    log('ok', 'upload()', 'Image post request')
    
    filepath = f'{img_path}/{filename}'
    global items
    items = image_scan(filepath)

    return render_template('home.html', db_result=items, msg='Success', edit='yes', categories=categories)


if __name__ == '__main__':
    app.secret_key = read_key()
    port = int(os.environ.get('PORT', 1337))
    app.run(host='0.0.0.0', port=port)