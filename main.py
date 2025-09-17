from utils.parse import parse, fetch
from utils.scanner import scan
from utils.sql_utils import *
from ops import *



def cmd():
    execute = input('''
        Enter a command:
        exit = "Q"
        QR image = "img"
        del entry = "del"
        show db = "get"
        ''')

    match execute:
        case 'q': con_close()
        case 'img': image_scan()
        case 'del': delete()
        case 'get': show_db()

    return


def main():
    while True:
        cmd()


if __name__ == '__main__':
    main()