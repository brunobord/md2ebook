#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""Markdown to Book.

Usage:
  md2ebook start [<name>] [--overwrite] [--bookname=<bookname>]
  md2ebook build [--with-pdf] [--verbose] [--cover=<cover>]
  md2ebook check
  md2ebook --version

Commands:
  start     Start a blank project, using the default template
  build     Generates HTML and EPUB. Optionally PDF
  check     Checks for the EPUB integrity. Needs epubcheck.

Options:
  -h --help                Show this screen.
  --version                Show version.
  --overwrite              Will overwrite the project directory.
                           Handle with care.
  --bookname=<bookname>    Will set the name of the initial Markdown file.
  --verbose                Will display ebook-convert output.
  --with-pdf               Will generate the PDF along with the HTML and EPUB.
  --cover=<cover>          File path or URL for a cover that would override the
                           configuration (or default standard).

"""

from docopt import docopt

from .commander import Commander
from .checkers import check_dependencies


def main():
    "Main program"
    check_dependencies()
    args = docopt(__doc__, version='md2ebook 0.0.1-dev')
    commander = Commander(args)
    commander.handle()

if __name__ == '__main__':
    main()
