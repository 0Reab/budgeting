from utils.sql_utils import *
from utils.scanner import *
from utils.logger import *
from utils.parse import *



def extract(item):
    try:
        result = []

        for data in item:
            category = 'other'
            amount = int(data['qty'])
            price = float(data['total'].replace('.', '').replace(',','.'))
            name = data['name']

            date = todays_date() # replace with date from receipt

            if not validate(category, name, price, amount, date):
                return False

            result.append([category, name, price, amount, date])

        log('ok', 'extract()', 'data extraction')
        return result

    except Exception as e:
        log('fail', 'extract_and_insert()', f'generic exception clause - {e}')
        return None


def image_scan(img_path):
    img = parse_image_path(img_path) # should validate return of this func for file ext...

    url = scan(img)
    data = fetch(url)
    raw = parse(data)
    result = extract(raw)

    log('ok', 'image_scan()', 'xd')

    return result