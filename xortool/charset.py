import string


class CharsetError(Exception):
    pass


CHARSETS = {
    "a": string.ascii_lowercase,
    "A": string.ascii_uppercase,
    "1": string.digits,
    "!": string.punctuation,
    "*": string.printable,
}

PREDEFINED_CHARSETS = {
    "base32":    CHARSETS["A"] + "234567=",
    "base64":    CHARSETS["a"] + CHARSETS["A"] + CHARSETS["1"] + "/+=",
    "printable": CHARSETS["*"],
}


def get_charset(name, sbox):
    name = name or "printable"
    charset = b""
    
    if name in PREDEFINED_CHARSETS:
        charset = PREDEFINED_CHARSETS[name].encode("ascii")
        
    else:
        try:
            for c in set(name):
                charset += CHARSETS[c].encode("ascii")
        except KeyError:
            raise CharsetError("Bad character set: ", name)
        
    return bytes([sbox[b] for b in charset])
