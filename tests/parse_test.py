from utils.parse import *


""" Tests for parsing functions """

fuzz = [ 'Not exist', 1, 0.55, True, False, '', 'http://', 'https://', 'http://www.']

def test_fetch():

    for url in fuzz:
        return_val = type(fetch(url=url))

        output_str = ''

        assert return_val 