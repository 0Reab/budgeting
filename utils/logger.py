

def log(log_type, func, message):
    # quick func call validation

    bad_call = f'Invalid log type for: {log_type} :with message: {message}'

    try:
        log_type = log_type.upper()

    except AttributeError as e:
        print(bad_call)
        return None

    log_levels = [ 'INFO', 'OK', 'FAIL' ]

    if log_type not in log_levels:
        print(bad_call) 
        return None

    # log output

    color = {
        'OK': '\033[92m',
        'FAIL': '\033[91m',
        'INFO': '\033[93m',
        'END': '\033[0m',
    }


    log_result = f'{color[log_type]}[{log_type}] in {func} - {message}{color['END']}'

    print(log_result)
    return True


# implement saving logs to a file