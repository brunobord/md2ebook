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
  --bookname=<bookname>    Will set the name of the initial Markdown file
  --verbose                Will display ebook-convert output
  --with-pdf               Will generate the PDF along with the HTML and EPUB

"""
import os
import json
from os.path import abspath, exists, join
import codecs
import sys
import shutil
from functools import wraps

from colors import red as error, yellow as warning, green as success
from docopt import docopt
from shell import shell
from unidecode import unidecode

from .ui import yesno, ask
from .generators import HTMLGenerator, CalibreEPUBGenerator, CalibrePDFGenerator


CWD = os.getcwd()


def check_dependency_epubcheck():
    try:
        shell('epubcheck')
    except OSError:
        print warning("Warning: missing epubcheck. You'll be able to run"
                      " md2ebook but you won't be able to check your EPUB "
                      " integrity.")
        print
        return False
    return True


def check_dependencies():
    "Check external dependecies"
    try:
        shell('ebook-convert')
    except OSError:
        sys.exit(error('ebook-convert missing, you cannot use md2ebook.'))
    check_dependency_epubcheck()


def check_current_directory(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        if not exists(join(CWD, 'book.json')):
            sys.exit(error("You are not in a book root directory."
                     " Please `cd` to your book directory and run this again"))
        return func(*args, **kwargs)
    return wrapped


def load_config():
    return json.load(codecs.open(join(CWD, 'book.json'), encoding="utf"))


def start(args):
    "Start the project on the directory"
    bookname = args.get('--bookname', None)
    if not bookname:
        bookname = 'book.md'
    project_dir = args.get('<name>', None)
    if not project_dir:
        project_dir = CWD
    project_dir = abspath(project_dir)

    # create the working dir?
    if not exists(project_dir) or args['--overwrite']:
        if exists(project_dir):
            if yesno(warning(
                    'Are you sure you want to remove `%s`? ' % project_dir)):
                shutil.rmtree(project_dir)
            else:
                sys.exit(error('Operation aborted'))
        os.makedirs(project_dir)
        os.makedirs(join(project_dir, 'build'))
        with codecs.open(
                join(project_dir, bookname), 'w', encoding="utf") as fd:
            fd.write('''# This is your book
You can start it right now and publish it away!
''')
    # What shall we do with the configuration file?
    config_file = join(project_dir, 'book.json')
    rewrite_config_file = True
    if exists(config_file) and not args['--overwrite']:
        print('A config file already exists. This step is skipped')
        rewrite_config_file = False

    if rewrite_config_file:
        with codecs.open(config_file, 'w', encoding="utf") as fd:
            data = {
                'files': ['%s' % bookname],
                'author': "%s" % ask("What is your name? "),
                'title': '%s' % ask("E-book title, please? "),
            }
            data['fileroot'] = unidecode(data['title']).lower() \
                .replace(' ', '-')
            json.dump(data, fd, indent=4, encoding="utf")

    # Game over
    print
    sys.exit(success('Now you can go to `%s` and start editing your book...'
             % project_dir))


@check_current_directory
def build(args):
    "Build your book"
    config = load_config()
    html_generator = HTMLGenerator(CWD, config)
    html_generator.build()

    # Cover dance
    epub_generator = CalibreEPUBGenerator(CWD, config, args)
    epub_generator.build()

    # Shall we proceed to the PDF?
    if config.get('pdf', False) or args['--with-pdf']:
        pdf_generator = CalibrePDFGenerator(CWD, config, args)
        pdf_generator.build()


@check_current_directory
def check(args):
    "Checks EPUB integrity"
    if not check_dependency_epubcheck():
        sys.exit(error('Unavailable command.'))
    config = load_config()
    epub_file = u"%s.epub" % config['fileroot']
    epub_path = join(CWD, 'build', epub_file)
    print success("Starting to check %s..." % epub_file)
    epubcheck = u'epubcheck %s' % epub_path
    epubcheck = shell(epubcheck.encode())
    for line in epubcheck.errors():
        print error(line)
    for line in epubcheck.output():
        print line


def main():
    "Main program"
    check_dependencies()
    args = docopt(__doc__, version='mdbeook 0.0.1-dev')

    if args['start']:
        start(args)
    elif args['build']:
        build(args)
    elif args['check']:
        check(args)
    else:
        sys.exit(error('Error: the <%s> command is not a md2ebook command. '
                 'Please use the `md2ebook --help` option to see available '
                 'options.'))

if __name__ == '__main__':
    main()
