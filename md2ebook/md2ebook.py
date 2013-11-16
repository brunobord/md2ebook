#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""Markdown to Book.

Usage:
  md2ebook start [<name>] [--overwrite] [--bookname=<bookname>]
  md2ebook build
  md2ebook check
  md2ebook --version

Options:
  -h --help     Show this screen.
  --version     Show version.

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
from markdown import markdown
from unidecode import unidecode

CWD = os.getcwd()
HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>%(title)s</title>
</head>
<body>
%(body)s
</body>
</html>
"""


def yesno(question):
    "Return true if the answer is 'yes'"
    answer = raw_input(question).lower()
    return answer in ('y', 'yes')


def ask(question, escape=True):
    "Return the answer"
    answer = raw_input(question)
    if escape:
        answer.replace('"', '\\"')
    return answer.decode('utf')


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
    return json.load(
        codecs.open(join(CWD, 'book.json'), encoding="utf"))


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
            data['fileroot'] = unidecode(data['title']).lower()
            json.dump(data, fd, indent=4, encoding="utf")

    # Game over
    print
    sys.exit(success('Now you can go to `%s` and start editing your book...'
             % project_dir))


@check_current_directory
def build(args):
    "Build your book"
    config = load_config()
    content = []
    for filename in config['files']:
        print success('Reading & converting %s...' % filename)
        with codecs.open(filename, encoding="utf") as fd:
            content.append(fd.read())
    content = '\n\n'.join(content)
    # Ready to convert to HTML
    body = markdown(content, output_format='html5')
    html = HTML_TEMPLATE % {'title': config['title'], 'body': body}
    html_file = u"%s.html" % config['fileroot']
    html_path = join(CWD, 'build', html_file)
    with codecs.open(html_path, "w",
                     encoding="utf", errors="xmlcharrefreplace") as fd:
        fd.write(html)
    print success("Sucessfully published %s" % html_file)
    # EPUB
    epub_file = u"%s.epub" % config['fileroot']
    epub_path = join(CWD, 'build', epub_file)
    epub_data = {
        'html_file': html_path,
        'epub_file': epub_path,
        'authors': u"%s" % config['author'],
        'title': u"%s" % config['title']
    }
    ebook_convert = u'ebook-convert %(html_file)s %(epub_file)s' \
                    u' --remove-first-image' \
                    u' --authors="%(authors)s"' \
                    u' --title="%(title)s"' % epub_data
    shell(ebook_convert.encode('utf'))
    print success("Sucessfully published %s" % epub_file)


@check_current_directory
def check(args):
    "Checks EPUB integrity"
    if not check_dependency_epubcheck():
        sys.exit(error('Unavailable command.'))
    config = load_config()
    epub_file = u"%s.epub" % config['fileroot']
    print success("Starting to check %s..." % epub_file)
    epubcheck = u'epubcheck %s' % epub_file
    epubcheck = shell(epubcheck.encode())
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
