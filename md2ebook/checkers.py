import sys
from shell import shell
from .ui import warning, error


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
