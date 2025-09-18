from utils.sql_utils import *
from utils.scanner import *
from utils.logger import *
from utils.parse import *



def extract(item):
    try:
        result = []

        for data in item:
            amount = int(data['qty'])
            name = data['name']
            price = float(data['total'].replace('.', '').replace(',','.'))

            category = choose_category(item=name)
            date = todays_date()

            if not validate(category, name, price, amount, date):
                return False

            result.append([category, name, price, amount, date])
        log('ok', 'extract()', 'data extraction')

        return result


    except Exception as e:
        log('fail', 'extract_and_insert()', f'generic exception clause - {e}')


def image_scan(img_path):
    img = parse_image_path(img_path) # should validate return of this func for file ext...

    url = scan(img)
    data = fetch(url)
    raw = parse(data)
    result = extract(raw)

    #for line_data in result:
    #    extract_and_insert(line_data)

    log('ok', 'image_scan()', 'xd')

    return result


def choose_category(item): # bug 1.
    while True:
        # show_categories() # TEMPORARY
        print(item, '\n', '-'*50)
        
        choice = 'other' # input('Select category: ') # TEMPORARY
        #choice = manual_entry()
        user_categ = in_categories(choice)

        if user_categ is not None:
            log('ok', 'choose_category()', f'categ {choice} for item -> {item}')
            return user_categ


def manual_entry():
    # completely manual entry in db
    return NotImplemented