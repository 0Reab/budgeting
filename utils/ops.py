from utils.sql_utils import *
from utils.scanner import *
from utils.logger import *
from utils.parse import *



def extract_and_insert(data: dict):
    try:
        amount = int(data['qty'])
        name = data['name']
        price = float(data['total'].replace('.', '').replace(',','.'))

        category = choose_category(item=name)
        date = todays_date()

        if not validate(category, name, price, amount, date):
            return False

        log('ok', 'extract_and_insert()', 'data extraction')
        return insert(category, name, price, amount, date)


    except Exception as e:
        log('fail', 'extract_and_insert()', f'generic exception clause - {e}')


def image_scan():
    img = parse_image_path() # should validate return of this func for file ext...

    url = scan(img)
    data = fetch(url)
    result = parse(data)

    for line_data in result:
        extract_and_insert(line_data)

    log('ok', 'image_scan()', 'xd')
    return True


def choose_category(item): # bug 1.
    #user_categ = None

    #while not in_categories(user_categ):
    while True:
        show_categories()
        print(item, '\n', '-'*50)
        
        choice = input('Select category: ')
        user_categ = in_categories(choice)

        #print(type(in_categories(user_categ)), in_categories(user_categ), 'debug 1')

        if user_categ is not None:
            log('ok', 'choose_category()', f'user input {item}')
            return user_categ


def manual_entry():
    # completely manual entry in db
    return NotImplemented