'''
Main module of application
'''

from man_parser import ManParser
from html_maker import HTMLMaker
from text_attrs import Key, Layout, Paragraph

import argparse
import sys
import os


def main():
    filename = './texts/bash.txt'#sys.argv[1]
    parsed_man = ManParser(filename).parse()
    HTMLMaker(filename, parsed_man).man2html()


if __name__ == '__main__':
    main()
