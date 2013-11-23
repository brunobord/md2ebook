from setuptools import setup

setup(
    name='md2ebook',
    version='0.1',
    description='Build e-books (EPUB or PDF) out of markdown files',
    long_description=open('README.rst').read(),
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
