from qreader import QReader
import cv2

qreader = QReader()

def scan(image_path):
    image = cv2.imread(image_path)
    decoded_text = qreader.detect_and_decode(image=image)

    return decoded_text[0]
