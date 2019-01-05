import argparse
import logging
import sys

parser = argparse.ArgumentParser(description = "Generate word lists for Drawful 2")
parser.add_argument("room", help = "room id")
parser.add_argument("-v", "--verbose", action = 'store_true', help = "show logging messages")
args = parser.parse_args()

if args.verbose:
    for l in ["websockets", "drawful2"]:
        logger = logging.getLogger(l)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging.StreamHandler())

from drawful2 import create_wordlist
from words import *

create_wordlist(args.room, "Redewendungen", redewendungen(50))
