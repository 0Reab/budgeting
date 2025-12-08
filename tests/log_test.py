from utils.logger import log


""" Tests for logging function """


log_levels = [
     'INFO', 'OK', 'FAIL' 
]

fuzz_data = [
    123, 0.5, 'test string', True, False, None, ''
]


def test_log():
    """ must run log with correct log_level argument """

    for level in log_levels:
        for data in fuzz_data:

            return_val = log(log_type=level, func=data, message=data, suppress_print=True)

            output_str = f'log(level, data, data) ; level = {level}, data = {data} ; {return_val}'

            assert return_val, f"Log [OK]- returned True - {output_str}"