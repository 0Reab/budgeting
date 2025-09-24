from qreader import QReader
from utils.logger import log
import cv2


""" Module for reading QR code from image """

qreader = QReader()


def scan(image_path) -> str:
    """ return URL from QR code in the image """
    # needs error handling and/or test?

    image = cv2.imread(image_path)
    decoded_text = qreader.detect_and_decode(image=image)

    log('ok', f'scan({image_path})', 'QR code scanned')
    log('ok', f'scan()', f'url = {decoded_text}')
    return decoded_text[0]