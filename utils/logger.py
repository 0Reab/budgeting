import inspect


""" Module for custom logging of application operations and errors """
# implement saving logs to a file


def log(log_type: str, message: str, **kwargs) -> bool | None:
    """
    main logging func - formatted and colored print: args -> function calls with log type and custom messages
    log_type = OK, FAIL, INFO, END, rest is arbitrary text.
    """
    suppress_print = kwargs.get('suppress_print', None)

    # get func name of the caller
    func = inspect.currentframe().f_back.f_code.co_name

    if not validate_call(log_type, message):
        return None

    color = {
        'OK': '\033[92m',
        'FAIL': '\033[91m',
        'INFO': '\033[93m',
        'END': '\033[0m',
    }

    log_type = log_type.upper()

    log_result = f'{color[log_type]}[{log_type}] in {func} - {message}{color["END"]}'

    if not suppress_print:
        print(log_result)
    return True


def validate_call(log_type: str, message: str) -> bool:
    """ log() argument validation """

    bad_call = f'Bad func call: Invalid log type for: {log_type} ; with message ; {message}'

    try:
        log_type = log_type.upper()

    except AttributeError as e:
        print(f'{bad_call} - {e}')
        return False

    log_levels = ['INFO', 'OK', 'FAIL']

    if log_type not in log_levels:
        print(bad_call)
        return False

    return True
