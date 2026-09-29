import os
from utils.ops import image_scan
from utils.logger import log
from flask import current_app
from werkzeug.utils import secure_filename


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def read_key():
    """ read flask key from file """
    with open('key.txt', 'r') as f:
        key = f.read()
    return key


def allowed_file(filename):
    """ file upload extension validation """
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def run_backend(file) -> bool | list:
    """ image processing and calling backend processor """

    filename = secure_filename(file.filename)
    img_path = current_app.config['UPLOAD_FOLDER']

    os.makedirs(img_path, exist_ok=True)
    file.save(os.path.join(img_path, filename))

    log('ok', 'upload()', 'Image post request')

    # global items
    filepath = f'{img_path}/{filename}'
    items = image_scan(filepath)

    if items is None:
        return False

    # print(f'DEBUGGING -> {items}')

    result = []
    for entry in items:
        line = f'ID - / | categ - {entry[0]} | name - {entry[1]} | total - {entry[2]} | qty - {entry[3]} | date - {entry[4]}'
        result.append(line)

    return result, items
