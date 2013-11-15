==================
Markdown to e-book
==================

Requirements
============

* `Calibre <http://calibre-ebook.com/>`_  (especially its `command-line-interface tools <http://manual.calibre-ebook.com/cli/cli-index.html>`_)
* `epubcheck <https://github.com/IDPF/epubcheck>`_
* `Python <http://python.org/>`_

Installation
------------

Once the non-python requirements are installed, you can install system-wide, or
inside a virtualenv::

    pip install -e ./


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
        "fileroot": "what-a-beautiful-title"
    }

* ``files`` is a list of markdown files that live in your book root directory.
  They'll be processed in that specific order and compiled into a single ebook.
* ``author`` is the name of the author of the book.
* ``title`` is the title of the book, in its full glory.
* ``fileroot`` this string will serve as a *root* for the different outputs.
  Following the example, you'll produce ``what-a-beautiful-title.html`` and
  ``what-a-beautiful-title.epub`` in your book root directory.
