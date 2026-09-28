from utils.sql_utils import validate, categories_expenses
from utils.scanner import scan
from utils.logger import log
from utils.parse import parse, parse_image_path, fetch


""" Module for last steps in receipt processing 'extract()'. And wrapper func for server to call 'image_scan()' """


def extract(item) -> list | None:
    """ data extraction of receipt of parsed receipt """

    try:
        result = []

        for data in item:
            try:
                amount = int(data['qty'])
            except Exception as e:
                amount = float(data['qty'].replace(',', '.'))

            category = 'other'
            price = float(data['total'].replace('.', '').replace(',', '.'))
            name = data['name']
            date = data['date']

            if validate(category, name, price, amount, date, valid_categ=categories_expenses) is False:
                log('fail', 'extract()', 'data validation')
                return None

            result.append([category, name, price, amount, date])

        log('ok', 'extract()', 'data extraction')
        return result

    except Exception as e:
        log('fail', 'extract()', f'generic exception clause - {e}')
        return None


def image_scan(img_path: str) -> list:
    """ wrapper for the whole backedend image processing and data parsing """
    # not robust enough, no validation & err handling

    img = parse_image_path(img_path)  # should validate return of this func for file ext...

    url = scan(img)
    data = fetch(url)

    if data is None:
        return None

    raw = parse(data)
    result = extract(raw)

    log('ok', 'image_scan()', 'xd')

    return result
