#!/usr/bin/env python3

"""
usage: lolcat [options] [FILE]...

Concatenate FILE(s) to standard output.
With no FILE, or when FILE is -, read standard input.

options:
    -s, --seed=<k>      rainbow seed, -1 for random [default: -1]
    -f, --freq=<x>      rainbow frequency [default: 0.1]
    -S, --spread=<x>    rainbow spread [default: 3]
    -i, --inverse       invert foreground and background
    -F, --force         force color even when stdout is not a tty
    -h, --help          print this screen and exit
    -v, --version       print the version number and exit
"""

import math
import re
import sys
from random import randrange

from docopt import docopt


class Lol:
    STRIP_ANSI = re.compile("\033[[\d;]*[m|K]")

    def __init__(self, freq, spread, inverse=False, force=False):
        self._freq = freq
        self._spread = spread
        self._inverse = inverse
        self._force = force

    def rainbow(self, i):
        freq = self._freq
        return (
            math.sin(freq*i + 0) * 127 + 128,               # red
            math.sin(freq*i + 2*math.pi / 3) * 127 + 128,   # green
            math.sin(freq*i + 4*math.pi / 3) * 127 + 128,   # blue
        )

    def println(self, text, seed):
        spread = self._spread
        prefix = 48 if self._inverse else 38
        rainbow = self.rainbow

        if text and (sys.stdout.isatty() or self._force):
            text = self.STRIP_ANSI.sub("", text)
        text = text.replace("\t", "        ")

        for i, c in enumerate(text):
            code = rainbow(seed + i / spread)
            sys.stdout.write("\033[%d;2;%d;%d;%dm%s" % (prefix, *code, c))
        sys.stdout.write("\033[0m\n")

    def cat(self, fp, seed):
        for line in fp:
            seed += 1
            self.println(line.rstrip("\n"), seed)
        return seed


def parse_opts(args):
    opts = docopt(__doc__, args, help=False, version="lolcat 0.1")

    if opts["--help"]:
        import io
        lol = Lol(0.3, 8)
        seed = randrange(0, 256)
        usage = io.StringIO(__doc__)
        lol.cat(usage, seed)
        sys.exit()

    opts = {o.lstrip("-"): v for o, v in opts.items()}

    opts["freq"] = float(opts["freq"])
    opts["spread"] = float(opts["spread"])

    opts["seed"] = int(opts["seed"])
    if opts["seed"] < 0:
        opts["seed"] = randrange(0, 256)

    if not opts["FILE"]:
        opts["FILE"] = ["-"]

    return opts


def main(args):
    opts = parse_opts(args)

    lol = Lol(opts["freq"], opts["spread"], opts["inverse"], opts["force"])

    seed = opts["seed"]
    errors_happened = False
    for file in opts["FILE"]:
        if file != "-":
            try:
                fp = open(file)
            except OSError as e:
                print("lolcat: %s: %s" % (file, e.strerror))
                errors_happened = True
                continue
        else:
            fp = sys.stdin

        if sys.stdout.isatty() or opts["force"]:
            seed = lol.cat(fp, seed)
        elif fp.isatty():
            for line in fp:
                sys.stdout.write(line)
        else:
            chunk = fp.read(8192)
            while chunk:
                sys.stdout.write(chunk)
                chunk = fp.read(8192)

        # if file != "-":
        #     fp.close()

    return errors_happened

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
