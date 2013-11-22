#!/usr/bin/env python
#-*- coding: utf-8 -*-
"Commander module. The true master here"
import os
from os.path import abspath, exists, join
import sys
import json
import codecs
import shutil
from functools import wraps

from unidecode import unidecode
from shell import shell

from .ui import error, success, warning, yesno, ask
from .generators import HTMLGenerator
from .generators import CalibreEPUBGenerator, CalibrePDFGenerator
from .generators import PandocEPUBGenerator, PandocPDFGenerator
from .checkers import check_dependency_epubcheck
from .exceptions import ConfigurationError

CWD = os.getcwd()


def check_current_directory(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        if not exists(join(CWD, 'book.json')):
            sys.exit(error("You are not in a book root directory."
                     " Please `cd` to your book directory and run this again"))
        return func(*args, **kwargs)
    return wrapped


class Commander(object):

    def __init__(self, args, generators):
        self.args = args
        self.generators = generators
        self.cwd = CWD

    def load_config(self):
        return json.load(
            codecs.open(join(self.cwd, 'book.json'), encoding="utf"))

    def start(self):
        "Start the project on the directory"
        bookname = self.args.get('--bookname', None)
        if not bookname:
            bookname = 'book.md'
        project_dir = self.args.get('<name>', None)
        if not project_dir:
            project_dir = join(self.cwd, 'Book')
        project_dir = abspath(project_dir)

        # create the working dir?
        if not exists(project_dir) or self.args['--overwrite']:
            if exists(project_dir):
                if yesno(warning(
                        'Are you sure you want to remove `%s`? '
                        % project_dir)):
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
        if exists(config_file) and not self.args['--overwrite']:
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
                # pick a generator
                if len(self.generators) == 1:
                    data['generator'] = self.generators[0]
                else:
                    picked_generator = None
                    while not picked_generator:
                        picked_generator = ask(
                            "Which generator? [%s] "
                            % ', '.join(self.generators)
                        )
                        if picked_generator not in self.generators:
                            print warning(
                                'Wrong answer. Please pick one on the list')
                            picked_generator = None
                    # fine, we have one.
                    data['generator'] = picked_generator
                json.dump(data, fd, indent=4, encoding="utf")

        # Game over
        print
        sys.exit(
            success('Now you can go to `%s` and start editing your book...'
                    % project_dir))

    @check_current_directory
    def build(self):
        "Build your book"
        config = self.load_config()
        html_generator = HTMLGenerator(self.cwd, config)
        html_generator.build()

        if self.args.get('--generator', None):
            generator = self.args.get('--generator')
        else:
            generator = config.get('generator')

        if generator == 'calibre':
            EPUBClass = CalibreEPUBGenerator
            PDFClass = CalibrePDFGenerator
        elif generator == 'pandoc':
            EPUBClass = PandocEPUBGenerator
            PDFClass = PandocPDFGenerator
        else:
            raise ConfigurationError(
                "Wrong configuration. Please check your config.json file.")

        # EPUB Generation
        epub_generator = EPUBClass(self.cwd, config, self.args)
        epub_generator.build()

        # Shall we proceed to the PDF?
        if config.get('pdf', False) or self.args['--with-pdf']:
            pdf_generator = PDFClass(self.cwd, config, self.args)
            pdf_generator.build()

    @check_current_directory
    def check(self):
        "Checks EPUB integrity"
        config = self.load_config()
        if not check_dependency_epubcheck():
            sys.exit(error('Unavailable command.'))
        epub_file = u"%s.epub" % config['fileroot']
        epub_path = join(CWD, 'build', epub_file)
        print success("Starting to check %s..." % epub_file)
        epubcheck = u'epubcheck %s' % epub_path
        epubcheck = shell(epubcheck.encode())
        for line in epubcheck.errors():
            print error(line)
        for line in epubcheck.output():
            print line

    def handle(self):
        if self.args['start']:
            self.start()
        elif self.args['build']:
            self.build()
        elif self.args['check']:
            self.check()
        else:
            sys.exit(
                error('Error: the <%s> command is not a md2ebook command. '
                      'Please use the `md2ebook --help` option to see '
                      'available options.'))
