#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""Generators
"""
from os.path import join, abspath, exists
import codecs

from markdown import markdown
from shell import shell

from .ui import error, warning, success

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


class Generator(object):
    def __init__(self, cwd, config, args=None):
        self.cwd = cwd
        self.config = config
        self.args = args
        self.build_dir = join(self.cwd, 'build')

    @property
    def html_file(self):
        return u"%s.html" % self.config['fileroot']

    @property
    def html_path(self):
        return join(self.build_dir, self.html_file)

    @property
    def epub_file(self):
        return u"%s.epub" % self.config['fileroot']

    @property
    def epub_path(self):
        return join(self.build_dir, self.epub_file)

    @property
    def pdf_file(self):
        return u"%s.pdf" % self.config['fileroot']

    @property
    def pdf_path(self):
        return join(self.build_dir, self.pdf_file)

    @property
    def core_data(self):
        data = {
            'html_file': self.html_path,
            'epub_file': self.epub_path,
            'pdf_file': self.pdf_path,
            'authors': u"%s" % self.config['author'],
            'title': u"%s" % self.config['title']
        }
        if self.cover:
            data['cover'] = self.cover
        return data

    @property
    def cover(self):
        if not hasattr(self, '_cover'):
            self._cover = self.load_cover()
        return self._cover

    def load_cover(self):
        """Load the cover out of the config, options and conventions.
        Priority goes this way:

        1. if a --cover option is set, use it.
        2. if there's a "cover" key in the config file, use it.
        3. if a cover.(png|jpg|jpeg|svg) exists in the directory, use it.

        Once the choice is set, the program will check if the file exists
        before using it. If it doesn't exist, you'll be warned and the default
        (ugly) cover will be used.
        """
        if not self.args:
            return False
        filename = self.args.get('--cover', None) \
            or self.config.get('cover', None) \
            or None
        if not filename:
            for extension in ('png', 'jpg', 'jpeg', 'svg'):
                temp_filename = 'cover.%s' % extension
                if exists(temp_filename):
                    filename = temp_filename
                    break
        if filename:
            if filename.startswith('http://') or \
               filename.startswith('https://'):
                return filename
            if not exists(filename):
                print error('The designated cover (%s) does not exists.'
                            ' Please check your settings.' % filename)
                filename = None
        if not filename:
            print warning('No cover is set, will use the default (ugly) one.')
            return False
        return abspath(filename)


class HTMLGenerator(Generator):
    "HTML Generator, out of the Markdown files defined in the config file."

    def build(self):
        content = []
        for filename in self.config['files']:
            print success('Reading & converting %s...' % filename)
            with codecs.open(filename, encoding="utf") as fd:
                content.append(fd.read())
        content = '\n\n'.join(content)
        # Ready to convert to HTML
        body = markdown(content, output_format='html5')
        html = HTML_TEMPLATE % {
            'title': self.config['title'],
            'body': body}

        with codecs.open(self.html_path, "w",
                         encoding="utf", errors="xmlcharrefreplace") as fd:
            fd.write(html)
        print success("Sucessfully published %s" % self.html_file)


class CalibreGenerator(Generator):
    "Generic Calibre generator"

    def build(self):
        options = u' '.join(self.options)
        ebook_convert = self.command + u' ' + options
        ebook_convert = ebook_convert % self.core_data
        output = shell(ebook_convert.encode('utf'))
        if self.args.get('--verbose', False):
            for line in output.output():
                print warning(line)
            for line in output.errors():
                print error(line)
        print success("Sucessfully published %s" % self.result_file)


class CalibreEPUBGenerator(CalibreGenerator):
    "Calibre EPUB Generator"

    command = u'ebook-convert %(html_file)s %(epub_file)s'

    @property
    def result_file(self):
        return self.epub_file

    @property
    def options(self):
        options = [
            u'--remove-first-image',
            u'--authors="%(authors)s"',
            u"--chapter '//h:h1'",
            u"--level1-toc '//h:h1'",
            u"--level2-toc '//h:h2'",
            u'--title="%(title)s"',
        ]
        if self.cover:
            options.append('--no-default-epub-cover')
            options.append('--cover="%(cover)s"')
        return options


class CalibrePDFGenerator(CalibreGenerator):
    "Calibre PDF Generator"
    command = u'ebook-convert %(html_file)s %(pdf_file)s'

    @property
    def result_file(self):
        return self.pdf_file

    @property
    def options(self):
        data = [
            u'--authors="%(authors)s"',
            u"--chapter '//h:h1'",
            u"--level1-toc '//h:h1'",
            u"--level2-toc '//h:h2'",
            u'--title="%(title)s"',
        ]
        if self.cover:
            data.append('--cover="%(cover)s"')
        return data
