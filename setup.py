from setuptools import setup
from os.path import join, dirname, abspath


def read_relative_file(filename):
    """Returns contents of the given file, whose path is supposed relative
    to this module."""
    with open(join(dirname(abspath(__file__)), filename)) as f:
        return f.read()

setup(
    name='md2ebook',
    version='0.1.1',
    description='Build e-books (EPUB or PDF) out of markdown files',
    long_description=read_relative_file('README.rst'),
    url='https://github.com/brunobord/md2ebook/',
    license='MIT',
    author='Bruno Bord',
    author_email='bruno@jehaisleprintemps.net',
    py_modules=['md2ebook'],
    include_package_data=True,
    install_requires=(
        'docopt',
        'markdown',
        'shell',
        'ansicolors',
        'unidecode',
    ),
    entry_points={'console_scripts': ['md2ebook=md2ebook.md2ebook:main']},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Topic :: Text Processing',
        'Topic :: Text Processing :: Markup',
    ],
)
