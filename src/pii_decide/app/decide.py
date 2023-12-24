"""
Command-line script to process data and perform PII decisions
"""

import sys
import argparse

from typing import List, Dict

from pii_data.helper.io import openfile, base_extension
from pii_data.helper.exception import InvArgException
from pii_data.types.piicollection import PiiCollectionLoader


from .. import VERSION
from ..api import PiiDecider


class Log:

    def __init__(self, verbose: bool):
        self._v = verbose

    def __call__(self, msg: str, *args):
        if self._v:
            print(msg, *args, file=sys.stderr)


def piic_format(filename: str) -> str:
    """
    Find out the desired file format for a PII Collection
    """
    ext = base_extension(filename)
    if ext == ".json":
        return "json"
    elif ext in (".ndjson", ".jsonl"):
        return "ndjson"
    else:
        raise InvArgException("cannot recognize piic output format for: {}",
                              filename)


def process(args: argparse.Namespace):

    log = Log(args.verbose)

    log(". Loading PII collection:", args.infile)
    piic_in = PiiCollectionLoader()
    piic_in.load(args.infile)

    dec = PiiDecider()

    log(". Processing and dumping to:", args.outfile)
    piic_out = dec(piic_in)

    if args.format is None:
        args.format = piic_format(args.outfile)

    with openfile(args.outfile, "w", encoding="utf-8") as f:
        piic_out.dump(f, format=args.format)



def parse_args(args: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=f"Perform decision on a collection of PII instances (version {VERSION})")

    g0 = parser.add_argument_group("Input/output paths")
    g0.add_argument("infile", help="source PII collection")
    g0.add_argument("outfile", help="destination PII collection")

    g2 = parser.add_argument_group("Input/output paths")
    g2.add_argument("--format", choices=("json", "jsonl"),
                    help="output format")

    g3 = parser.add_argument_group("Other")
    g3.add_argument("-q", "--quiet", action="store_false", dest="verbose")
    g3.add_argument('--reraise', action='store_true',
                    help='re-raise exceptions on errors')
    g3.add_argument("--show-stats", action="store_true", help="show statistics")

    return parser.parse_args(args)


def main(args: List[str] = None):
    if args is None:
        args = sys.argv[1:]
    args = parse_args(args)
    try:
        process(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.reraise:
            raise
        else:
            sys.exit(1)


if __name__ == "__main__":
    main()
