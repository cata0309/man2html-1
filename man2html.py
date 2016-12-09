from man_parser import ManParser

import argparse
import sys
import os


def man2html(parsed_man):
    pass


def main():
    filename = sys.argv[1]
    man_parser = ManParser(filename)
    man_parser.parse()


if __name__ == '__main__':
    main()
