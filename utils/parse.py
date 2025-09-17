from bs4 import BeautifulSoup
from utils.logger import log
import requests
import re



def fetch(url):
    try:
        result = requests.get(url).content
    except Exception as e:
        log('fail', 'fetch()', f'URL get request failed with error - {e}')
        return None

    soup = BeautifulSoup(result, features="html.parser")
    response = soup.find_all("pre", {"style" : "font-family:monospace"})
    return response


def parse(response):
    delimiter = '=' * 40
    response = str(response)
    raw = ''.join(response.split(delimiter)[1])
    #print(raw)

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
                "total": total
            })
            current_name = []  # reset for next item
        elif not line.startswith("Назив") and "износ" not in line and "Платна" not in line:
            current_name.append(line)

    for item in items:
        pass
        #print(item)

    return items


def parse_image_path():
    # for now just image name in $pwd
    img = input('Enter image name: ')

    img_ext = img.split('.')[-1]
    allowed_ext = ['jpg', 'png']

    if img_ext not in allowed_ext:
        print(f'Image argument {img} not jpg or png filetype')
        return False
    
    return img