#!/usr/bin/env python3
from xortool import __version__
__doc__ = f"""
xortool-xor {__version__}
xor strings
options:
    -s  -  string with \\xAF escapes
    -r  -  raw string
    -h  -  hex-encoded string (non-letterdigit chars are stripped)
    -f  -  read data from file (- for stdin)

    --newline -  newline at the end (default)
    -n / --no-newline -  no newline at the end
    --cycle - do not pad (default)
    --sbox  -  path to a file containing an sbox to be applied before xoring
    --nc / --no-cycle -  pad smaller strings with null bytes
    -x / --hex  -  return the final output as an hex encoded string
example: xor -s lol -h 414243 -f /etc/passwd -x
"""

import getopt
import sys


def main():
    cycle = True
    newline = True
    try:
        opts, _ = getopt.getopt(
            sys.argv[1:], "xhns:r:h:f:",
            ["cycle", "no-cycle", "nc", "no-newline", "newline", "sbox=", "hex"])
        datas:list[bytes] = []
        sbox = list(range(256))
        for c, val in opts:
            if c == "--cycle":
                cycle = True
            elif c in ("--no-cycle", "--nc"):
                cycle = False
            elif c == "--newline":
                newline = True
            elif c in ("-n", "--no-newline"):
                newline = False
            elif c == "--sbox":
                sbox = parse_sbox(from_file(val))
            elif c in ("-x", "--hex"):
                hexOutput = True
            else:
                datas.append(arg_data(c, val))
        if not datas:
            raise getopt.GetoptError("no data given")
    except getopt.GetoptError as e:
        print("error:", e, file=sys.stderr)
        print(__doc__, file=sys.stderr)
        quit()

    out = xor(datas, sbox, cycle=cycle)
    
    if hexOutput: print(out.hex(), end="")
    else: sys.stdout.buffer.write(out)
    if newline:
        sys.stdout.buffer.write(b"\n")

def parse_sbox(rawSBox:bytes):
    rawSBox = rawSBox.replace(b"[", b"").replace(b"]", b"").split(b"=")[-1]
    splitChar = b"," if b"," in rawSBox else b" "
    sbox = [int(v) for v in rawSBox.split(splitChar) if v]
    
    return sbox


def xor(args:list[bytes], sbox, cycle=True):
    # Sort by len DESC
    args.sort(key=len, reverse=True)
    res = bytearray(sbox[b] for b in args.pop(0)) # The longer one
    maxlen = len(res)

    for s in args:
        slen = len(s)
        for i in range(maxlen if cycle else slen):
            res[i] ^= s[i % slen]
    return res


def from_str(s):
    res = b''
    for char in s.encode("utf-8").decode("unicode_escape"):
        res += bytes([ord(char)])
    return res


def from_file(s):
    if s == "-":
        s = sys.stdin.fileno()
    with open(s, "rb") as f:
        return f.read()


def arg_data(opt, s):
    if opt == "-s":
        return from_str(s)
    if opt == "-r":
        return str.encode(s)
    if opt == "-h":
        return bytes.fromhex(s)
    if opt == "-f":
        return from_file(s)
    raise getopt.GetoptError("unknown option -%s" % opt)


if __name__ == '__main__':
    main()
