from bs4 import BeautifulSoup
from utils.logger import log
import requests
import re


""" Module for HTTP requests, HTML response parsing, extracting of data """


def validate_url(url: str) -> bool:
    """ origin and http parameter validation """
    # add more validation for http parameter part of the url 

    valid = 'https://suf.purs.gov.rs/v/?vl='
    xss_strings = r';%3B<>%3C%3E'

    if not url.startswith(valid):
        log('fail', 'validate_url()', f'Invalid url: {url}')
        return False
    
    for char in url:
        if char in xss_strings:
            log('fail', 'validate_url()', f'XSS strings found in: {url}')
            return False

    log('ok', 'validate_url()', f'url validated: {url}')
    return True


def fetch(url: str) -> str | None:
    """ HTTP GET url response -> BeautifulSoup finds <pre> tags -> return string of tag values """

    if not validate_url(url):
        log('fail', 'fetch()', f'failed vaildation')
        return None

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


def receit_regex(lines: list, date: str) -> list:
    """ receit ascii regex parser for bought items """

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
    
    return items


def parse(response: str) -> list[dict[str, str]] | None:
    """ parse receipt in text form to extract bought items and other info """

    delimiter = '=' * 40
    response = str(response)
    raw = ''.join(response.split(delimiter)[1])

    date = get_date(response)

    if not date:
        return None

    try:
        lines = [l.strip() for l in raw.splitlines() if l.strip()]
        items = receit_regex(lines, date)

    except Exception as e:
        log('fail', 'parse()', f'html soupe parser failed, good luck - {e}')

    log('ok', 'parse()', 'receipt html soup parsed')
    return items


def parse_image_path(img: str) -> str | bool:
    """ validate file extension to a whitelist of allowed """
    # check path traversal with regex

    bad_chars = '$;|#&+"'

    for char in img:
        if char in bad_chars:
            log('fail', 'parse_image_path()', 'Image filepath contains possibly malicious characters')
            return False

    try:
        img_ext = img.split('.')[-1]
        allowed_ext = ['jpg', 'png']

        if img_ext not in allowed_ext or len(img) > 100:
            log('fail', 'parse_image_path()', f'Image argument {img} not jpg or png filetype')
            return False
    
    except Exception as e:
        log('fail', 'parse_image_path()', f'Image argument {img}: caused undefined exception {e}')

    log('ok', 'parse_image_path()', 'valid extension')
    return img