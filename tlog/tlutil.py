#tlutil.py
import hashlib

def digest(in_str, short=True):
    my_bytes = in_str.encode('utf-8')
    md5_of_bytes = hashlib.md5(my_bytes)
    hex_digest_of_md5_of_byte_encode_of_in_str = md5_of_bytes.hexdigest()
    if short:
        return hex_digest_of_md5_of_byte_encode_of_in_str[0:10]
    return hex_digest_of_md5_of_byte_encode_of_in_str

class TaskSourceException(Exception):
    'Task source exception indicates a failure in a data source for endeavors, stories,  etc '

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)