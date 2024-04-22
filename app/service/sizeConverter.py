def format_file_size(bytes):
    if bytes < 1024:
        return str(bytes) + ' bytes'
    elif bytes < 1024 * 1024:
        return '{:.2f} KB'.format(bytes / 1024)
    else:
        return '{:.2f} MB'.format(bytes / (1024 * 1024))

