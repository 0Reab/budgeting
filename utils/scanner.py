from qreader import QReader
from utils.logger import log
import cv2


""" Module for reading QR code from image """

qreader = QReader()


def scan(image_path: str) -> str | None:
    """ return URL from QR code in the image """

    try:
        image = cv2.imread(image_path)
        decoded_text = qreader.detect_and_decode(image=image)

        log('ok', f'scan({image_path})', 'QR code scanned')
        log('ok', 'scan()', f'url = {decoded_text}')

        return decoded_text[0]
    
    except Exception as e:
        log('fail', 'scan()', f'url = {decoded_text} undefined exception: {e}')
        return None