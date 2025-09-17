

def log(log_type, func, message):
    # quick func call validation

    bad_call = f'Invalid log type for: {log_type} :with message: {message}'

    try:
        log_type = log_type.upper()

    except AttributeError as e:
        print(bad_call)
        return None

    log_levels = [ 'INFO', 'ERROR', 'CRITICAL', 'OK', 'FAIL', 'SUCCESS' ]

    if log_type not in log_levels:
        print(bad_call) 
        return None

    # log output

    log_result = f'[{log_type}] in {func} - {message}'

    print(log_result)
    return True


# implement saving logs to a file