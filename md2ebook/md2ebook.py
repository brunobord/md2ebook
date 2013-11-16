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
    return json.load(codecs.open(join(CWD, 'book.json'), encoding="utf"))


def load_cover(args, config):
    """Load the cover out of the config, options and conventions.
    Priority goes this way:

    1. if a --cover option is set, use it.
    2. if there's a "cover" key in the config file, use it.
    3. if a cover.(png|jpg|jpeg|svg) exists in the directory, use it.

    Once the choice is set, the program will check if the file exists before
    using it. If it doesn't exist, you'll be warned and the default (ugly)
    cover will be used.
    """
    filename = args.get('--cover', None) or config.get('cover', None) or None
    if not filename:
        for extension in ('png', 'jpg', 'jpeg', 'svg'):
            filename = 'cover.%s' % extension
            if exists(filename):
                break
    if filename:
        if not exists(filename):
            print error('The designated cover (%s) does not exists.'
                        ' Please check your settings.' % filename)
            filename = None
    if not filename:
        print warning('No cover is set, will use the default (ugly) one.')
        return False
    return abspath(filename)


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
    build_dir = join(CWD, 'build')
    # Reading markdown files
    for filename in config['files']:
        print success('Reading & converting %s...' % filename)
        with codecs.open(filename, encoding="utf") as fd:
            content.append(fd.read())
    content = '\n\n'.join(content)
    # Ready to convert to HTML
    body = markdown(content, output_format='html5')
    html = HTML_TEMPLATE % {'title': config['title'], 'body': body}
    html_file = u"%s.html" % config['fileroot']
    html_path = join(build_dir, html_file)
    with codecs.open(html_path, "w",
                     encoding="utf", errors="xmlcharrefreplace") as fd:
        fd.write(html)
    print success("Sucessfully published %s" % html_file)

    # Cover dance
    cover = load_cover(args, config)

    # EPUB
    epub_file = u"%s.epub" % config['fileroot']
    epub_path = join(build_dir, epub_file)
    epub_data = {
        'html_file': html_path,
        'epub_file': epub_path,
        'authors': u"%s" % config['author'],
        'title': u"%s" % config['title']
    }
    ebook_convert = [
        u'ebook-convert %(html_file)s %(epub_file)s',  # the actual command
        # options
        u'--remove-first-image',
        u'--authors="%(authors)s"',
        u"--chapter '//h:h1'",
        u"--level1-toc '//h:h1'",
        u"--level2-toc '//h:h2'",
        u'--title="%(title)s"',
    ]
    if cover:
        ebook_convert.append('--no-default-epub-cover')
        ebook_convert.append('--cover="%(cover)s"')
        epub_data['cover'] = abspath(cover)
    ebook_convert = u' '.join(ebook_convert)
    ebook_convert = ebook_convert % epub_data
    output = shell(ebook_convert.encode('utf'))
    if args.get('--verbose', False):
        for line in output.output():
            print warning(line)
    print success("Sucessfully published %s" % epub_file)

    # Shall we proceed to the PDF?
    if config.get('pdf', False) or args['--with-pdf']:
        pdf_file = u"%s.pdf" % config['fileroot']
        pdf_path = join(build_dir, pdf_file)
        pdf_data = {
            'html_file': html_path,
            'pdf_file': pdf_path,
            'authors': u"%s" % config['author'],
            'title': u"%s" % config['title']
        }
        ebook_convert = [
            u'ebook-convert %(html_file)s %(pdf_file)s',  # the actual command
            # options
            u'--authors="%(authors)s"',
            u"--chapter '//h:h1'",
            u"--level1-toc '//h:h1'",
            u"--level2-toc '//h:h2'",
            u'--title="%(title)s"',
        ]
        if cover:
            ebook_convert.append('--cover="%(cover)s"')
            pdf_data['cover'] = abspath(cover)
        ebook_convert = u' '.join(ebook_convert)
        ebook_convert = ebook_convert % pdf_data
        output = shell(ebook_convert.encode('utf'))
        if args.get('--verbose', False):
            for line in output.output():
                print warning(line)
        print success("Successfully published %s" % pdf_file)


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
