from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
from utils.logger import log
from backend import *
import os


app = Flask(__name__, template_folder='pages')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'images')


def read_key():
    with open('key.txt', 'r') as f:
        key = f.read()
    return key


def allowed_file(filename):
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
    if request.method == 'GET':
        msg = 'All database entries.'
        entries = show_db()
        return render_template('home.html', db_result=entries, msg=msg)
    else:
        return render_template('home_error.html')


@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':

        if 'file' not in request.files:
            flash('No file part')
            return redirect('/')

        file = request.files['file']

        if file.filename == '':
            flash('No selected file')
            return redirect('/')

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            img_path = app.config['UPLOAD_FOLDER']

            file.save(os.path.join(img_path, filename))

            log('ok', 'upload()', 'Image post request')
            
            filepath = f'{img_path}/{filename}'
            items = image_scan(filepath)


            print('Show database...')

            return render_template('home.html', db_result=items, msg='Success')

    else:
        log('fail', 'upload()', 'Image post request')
        return render_template('home_error.html')



if __name__ == '__main__':
    app.secret_key = read_key()
    port = int(os.environ.get('PORT', 1337))
    app.run(host='0.0.0.0', port=port)