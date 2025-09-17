from qreader import QReader
from utils.logger import log
import cv2

qreader = QReader()

def scan(image_path):
    image = cv2.imread(image_path)
    decoded_text = qreader.detect_and_decode(image=image)

    log('success', f'scan({image_path})', 'QR code scanned')
    return decoded_text[0]
