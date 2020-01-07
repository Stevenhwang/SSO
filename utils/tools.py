import hashlib


def gen_md5(pd: str):
    m = hashlib.md5()
    m.update(pd.encode("utf-8"))
    return m.hexdigest()
