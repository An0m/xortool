from docopt import docopt

from xortool.charset import get_charset
from xortool.routine import load_file

class ArgError(Exception):
    pass


def parse_char(ch):
    """
    'A' or '\x41' or '0x41' or '41'
    '\x00' or '0x00' or '00'
    """
    if ch is None:
        return None
    if len(ch) == 1:
        return ord(ch)
    if ch[0:2] in ("0x", "\\x"):
        ch = ch[2:]
    if not ch:
        raise ValueError("Empty char")
    if len(ch) > 2:
        raise ValueError("Char can be only a char letter or hex")
    return int(ch, 16)

def parse_int(i):
    if i is None:
        return None
    return int(i)

def parse_sbox(rawSBox:bytes):
    # First, let's parse the old sbox, so that no matter the format, we turn it into a usable list
    rawSBox = rawSBox.replace(b"[", b"").replace(b"]", b"").split(b"=")[-1]
    splitChar = b"," if b"," in rawSBox else b" "
    sbox = [int(v) for v in rawSBox.split(splitChar) if v]
    
    return sbox


def parse_parameters(doc, version):
    p = docopt(doc, version=version)
    p = {k.lstrip("-"): v for k, v in p.items()}
    sbox = parse_sbox(load_file(p["sbox"])) if p["sbox"] else list(range(256))
    try:
        return {
            "brute_chars": bool(p["brute-chars"]),
            "brute_printable": bool(p["brute-printable"]),
            "filename": p["FILE"] if p["FILE"] else "-",  # stdin by default
            "filter_output": bool(p["filter-output"]),
            "input_is_hex": bool(p["hex"]),
            "known_key_length": parse_int(p["key-length"]),
            "min_key_length": parse_int(p["min-keylen"]),
            "max_key_length": parse_int(p["max-keylen"]),
            "most_frequent_char": parse_char(p["char"]),
            "text_charset": get_charset(p["text-charset"], sbox),
            "sbox": sbox,
            "known_plain": p["known-plaintext"].encode() if p["known-plaintext"] else False,
        }
    except ValueError as err:
        raise ArgError(str(err))
