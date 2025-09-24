
""" Module for custom logging of application operations and errors """
# implement saving logs to a file


def log(log_type, func, message):
    """ main logging func - formatted and colored print: args -> function calls with log type and custom messages"""
    # "func" argument is a hardcoded string which can be inaccurate if actual func name is changed. 
    # for eg. log('ok', 'parser()', 'parsing of text') is bad if parser() was renamed into parsing_text().

    if not validate_call(log_type, message):
        return None

    # log output

    color = {
        'OK': '\033[92m',
        'FAIL': '\033[91m',
        'INFO': '\033[93m',
        'END': '\033[0m',
    }

    log_type = log_type.upper()

    log_result = f'{color[log_type]}[{log_type}] in {func} - {message}{color['END']}'

    print(log_result)
    return True


def validate_call(log_type, message) -> bool:
    """ log() argument validation """

    bad_call = f'Invalid log type for: {log_type} :with message: {message}'

    def fail():
        print(bad_call)
        return None

    try:
        log_type = log_type.upper()

    except AttributeError as e:
        return fail()

    log_levels = [ 'INFO', 'OK', 'FAIL' ]

    if log_type not in log_levels:
        print(bad_call) 
        return None

    return True