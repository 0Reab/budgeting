from bs4 import BeautifulSoup
from utils.logger import log
import requests
import re


""" Module for HTTP requests, HTML response parsing, extracting of data """


def fetch(url) -> str | None:
    """ HTTP GET url from QR image scan -> BeautifulSoup finds <pre> tags -> return string of tags """

    try:
        result = requests.get(url).content
    except Exception as e:
        log('fail', 'fetch()', f'URL get request failed with error - {e}')
        return None

    soup = BeautifulSoup(result, features="html.parser")
    response = soup.find_all("pre", {"style" : "font-family:monospace"})

    log('ok', 'fetch()', 'http response bs4')
    return response


def get_date(txt: str) -> str | None:
    """ parse receipt in text form to find date of issue """

    for ln in txt.split('\n'):
        if 'vreme:' in ln or 'време:' in ln:
            date = ln.split()[-2]

            log('ok', 'get_date()', f'found date = {date}')
            return date 

    log('fail', 'get_date()', 'did not find date')
    return None


def parse(response: str) -> list[dict[str, str]] | None:
    """ parse receipt in text form to extract bought items and other info """
    # maybe refactor into two func, parse() and regex with items as return?

    delimiter = '=' * 40
    response = str(response)
    raw = ''.join(response.split(delimiter)[1])

    date = get_date(response)

    if not date:
        return None

    try:
        lines = [l.strip() for l in raw.splitlines() if l.strip()]

        items, current_name = [], []

        for line in lines:
            # Match rows that look like "price qty total"
            if re.match(r'^[\d\., ]+\d$', line):
                parts = line.split()
                price, qty, total = parts
                items.append({
                    "name": " ".join(current_name),
                    "price": price,
                    "qty": qty,
                    "total": total,
                    "date": date
                })
                current_name = []  # reset for next item
            elif not line.startswith("Назив") and "износ" not in line and "Платна" not in line:
                current_name.append(line)



    except Exception as e:
        log('fail', 'parse()', f'html soupe parser failed, good luck - {e}')

    log('ok', 'parse()', 'receipt html soup parsed')
    return items


def parse_image_path(img: str) -> str | bool:
    """ validate file extension to a whitelist of allowed """
    # needs more validation and and maybe error handling

    img_ext = img.split('.')[-1]
    allowed_ext = ['jpg', 'png']

    if img_ext not in allowed_ext:
        log('fail', 'parse_image_path()', f'Image argument {img} not jpg or png filetype')
        return False
    
    log('ok', 'parse_image_path()', 'valid extension')
    return img