categories = ['other', 'tool', 'food', 'transport', 'bill', 'cosmetic', 'nightout','hobby']


def show_categories():
    for idx, cat in enumerate(categories):
        print(f'{cat} - {idx}')


def in_categories(test):
    try:
        return categories[int(test)]

    except (TypeError, ValueError) as e:
        # is not an integer, match by string category name
        if test in categories:
            return test
        return False


def choose_category(item): # bug 1.
    user_categ = ''

    while not in_categories(user_categ):
        print(type(in_categories(user_categ)), in_categories(user_categ))
        show_categories()
        print(item, '\n', '-'*50)
        user_categ = input(f'Select category: ')

    return in_categories(user_categ)

item = "PIVO ZAJECARSKO CRNO 0.33L LIM (24) HEIN EKEN/KOM (Ђ)"
show_categories()
print(choose_category(item))