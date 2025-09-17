from utils.logger import log


log_levels = [
     'INFO', 'ERROR', 'CRITICAL', 'OK', 'FAIL' 
]

fuzz_data = [
    123, 0.5, 'test string', True, False, None, ''
]


def test_log():
    for level in log_levels:
        for data in fuzz_data:

            return_val = log(log_type=level, func=data, message=data)

            output_str = f'log(level, data, data) ; level = {level}, data = {data} ; {return_val}'

            assert return_val, f"Log [OK]- returned True - {output_str}"
            

    print("All log tests passed")