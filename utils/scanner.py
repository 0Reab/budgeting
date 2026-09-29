from qreader import QReader
from utils.logger import log
import cv2


""" Module for reading QR code from image """

# qreader = QReader() # for GPU processing
qreader = QReader(min_confidence=0.2, model_size="l")  # for CPU processing (n/s/m/l model sizes)


def scan(image_path: str) -> str | None:
    """ return URL from QR code in the image """
    try:
        image = cv2.imread(image_path)
        decoded_text = qreader.detect_and_decode(image=image)

        log('ok', f'QR code scanned {image_path} ; url = {decoded_text}')

        return decoded_text[0]

    except Exception as e:
        log('fail', f'url = {decoded_text} exception: {e}')
        return None
