==================
Markdown to e-book
==================

Requirements
============

* `Calibre <http://calibre-ebook.com/>`_  (especially its `command-line-interface tools <http://manual.calibre-ebook.com/cli/cli-index.html>`_)
* `Pandoc <http://johnmacfarlane.net/pandoc/>`_
* `Python <http://python.org/>`_
* `epubcheck <https://github.com/IDPF/epubcheck>`_ (this one's optional)

Please note that you need either **Calibre** or **Pandoc** (or both) to generate
EPUB files, but you need Calibre (and its CLI tools) to check the EPUB
conformity.

Installation
------------

Once the non-python requirements are installed, you can install system-wide, or
inside a virtualenv::

    pip install md2ebook


Usage
=====

to start a new book, just create a new project with the following command::

    md2ebook start

or, alternatively::

    md2ebook start directory-name

When you're done, you can move to this directory and use the ``build`` command::

    md2ebook build

This will build a HTML and a EPUB version of your book, as defined in the
``book.json`` file.

Extra commands
--------------

You can check your EPUB integrity using the following::

    md2ebook check

Options
-------

For more help on the md2ebook command, simply type::

    md2ebook --help

and you'll get extensive documentation about commands and their options.

Cover
-----

You can designate a cover for your ebook using one of the three options:

* Adding a ``--cover`` argument to the command line,
* Adding a ``cover`` key to your configuration file,
* Leaving a ``cover.(png|jpg|jpeg|svg)`` file at the root of your project, this
  one will be used as a cover.

If none of them leads to an existing file, the ugly default cover will be used.

Please note that the configuration option or the optional argument may be a
URL (yes, something like ``http://example.com/beautiful-cover.jpg``).

Configuration file
==================

At the root of your book directory, you have a ``book.json`` file which
contains your book configuration. This file is mandatory.

Here are its **mandatory** options, as a complete example:

::

    {
        "files": ["chapter1.md", "chapter2.md", "chapter3.md"],
        "author": "Joe A. Nonymous",
        "title": "What a beautiful title",
        "fileroot": "what-a-beautiful-title",
        "generator": "calibre"
    }

* ``files`` is a list of markdown files that live in your book root directory.
  They'll be processed in that specific order and compiled into a single ebook.
* ``author`` is the name of the author of the book.
* ``title`` is the title of the book, in its full glory.
* ``fileroot`` this string will serve as a *root* for the different outputs.
  Following the example, you'll produce ``what-a-beautiful-title.html`` and
  ``what-a-beautiful-title.epub`` in your book root directory.
* ``generator`` is either "calibre" or "pandoc". Pick the one you prefer (or
  the one that is available on your system).

Extra configuration
-------------------

* ``pdf``: triggers the PDF generation when using build. Set it to ``true`` or
  ``false``. If not set, the PDF won't be generated. Use the ``--with-pdf``
  option to override this settings.
* ``cover``: will set the path of your cover. this must lead to an existing file
  and if possible, an image (png, jpg, jpeg, or even SVG).
* ``extensions``: this list of strings defines the
  `Markdown Extensions <http://pythonhosted.org/Markdown/extensions/index.html>`_
  you can add to parse the Markdown files. Please refer to the Markdown
  extension to use the supported extensions.

Note about the Markdown extensions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Here's a list about the available extensions:

* Extra ("extra")

  * Abbreviations: ("abbr")
  * Attribute list: ("attr_list")
  * Definition Lists:  ("def_list")
  * Fenced Code Blocks:  ("fenced_code")
  * Footnotes: ("footnotes")
  * Tables: ("tables")
  * Smart Strong: ("smart_strong")

* Admonition: ("admonition")
* CodeHilite: ("codehilite")
* HeaderId: ("headerid")
* Meta-Data: ("meta")
* New Line to Break: ("nl2br")
* Sane Lists: ("sane_lists")
* Table of Contents: ("toc")
* WikiLinks: ("wikilinks")

Here's an example of config.json using the extensions::

    {
    "files": [
        "book.md"
    ],
    "title": "Les 3 Mousquetaires",
    "fileroot": "les-3-mousquetaires",
    "author": "Alexandre Dumas",
    "extensions": ["admonitions", "toc", "footnotes"],
    "generator": "pandoc"
    }

Extension parameters are set `as described in the docs <http://pythonhosted.org/Markdown/extensions/header_id.html>`_

::

    "extensions": ["headerid(level=3)"]

Credits
=======

This piece of software is Copyleft 2013 - Bruno Bord.

It is released under the terms of the MIT License, see LICENSE file for more
details.
