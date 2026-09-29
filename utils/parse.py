from bs4 import BeautifulSoup
from utils.logger import log
import requests
import re


""" Module for HTTP requests, HTML response parsing, extracting of data """


def validate_url(url: str) -> bool:
    """ origin and http parameter validation """
    # add more validation for http parameter part of the url

    valid = 'https://suf.purs.gov.rs/v/?vl='
    xss_strings = ''  # this check is not secure at all + false positives... xss_strings = r';%3B<>%3C%3E'

    if url is None:
        log('fail', "Didn't find URL in QR code.")
        return False

    if not url.startswith(valid):
        log('fail', f'Invalid url: {url}')
        return False

    for char in url:
        if char in xss_strings:
            log('fail', f'XSS str found in: {url}')
            return False

    log('ok', f'url validated: {url}')
    return True


def fetch(url: str) -> str | None:
    """ HTTP GET url response -> BeautifulSoup finds <pre> tags -> return string of tag values """

    if not validate_url(url):
        log('fail', f'failed validation url: {url}')
        return None

    try:
        result = requests.get(url).content
    except Exception as e:
        log('fail', f'URL get request failed with error - {e}')
        return None

    soup = BeautifulSoup(result, features="html.parser")
    response = soup.find_all("pre", {"style": "font-family:monospace"})

    log('ok', 'http response bs4')
    return response


def get_date(txt: str) -> str | None:
    """ parse receipt in text form to find date of issue """

    for ln in txt.split('\n'):
        if 'vreme:' in ln or 'време:' in ln:
            date = ln.split()[-2]

            log('ok', f'found date = {date}')
            return date

    log('fail', 'did not find date')
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
    if response is None:
        return None

    delimiter = '=' * 40
    response = str(response)
    raw = ''.join(response.split(delimiter)[1])

    date = get_date(response)

    if not date:
        return None

    try:
        lines = [i.strip() for i in raw.splitlines() if i.strip()]
        items = receit_regex(lines, date)

    except Exception as e:
        log('fail', f'html soupe parser failed, good luck - {e}')

    log('ok', 'receipt html soup parsed')
    return items


def parse_image_path(img: str) -> str | bool:
    """ validate file extension to a whitelist of allowed """
    # check path traversal with regex

    bad_chars = '$;|#&+"\n\r\t'

    for char in bad_chars:
        if char in img:
            log('fail', 'Image filepath contains possibly malicious chars.')
            return False

    try:
        img_ext = img.split('.')[-1]
        allowed_ext = ['jpg', 'png', 'jpeg']

        if img_ext not in allowed_ext or len(img) > 100:
            log('fail', f'Image {img} not jpg/jpeg/png')
            return False

    except Exception as e:
        log('fail', f'Image argument {img}: exception {e}')

    log('ok', 'valid extension')
    return img
