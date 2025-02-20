import hashlib

def md5_util(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest()