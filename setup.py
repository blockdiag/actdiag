# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Topic :: Software Development",
    "Topic :: Software Development :: Documentation",
    "Topic :: Text Processing :: Markup",
]


def get_version():
    """Get version number of the package from version.py without importing core module."""
    package_dir = os.path.abspath(os.path.dirname(__file__))
    version_file = os.path.join(package_dir, 'src/actdiag/__init__.py')

    namespace = {}
    with open(version_file, 'r') as f:
        exec(f.read(), namespace)

    return namespace['__version__']


setup(
    name='actdiag',
    version=get_version(),
    description='actdiag generates activity-diagram image from text',
    long_description=open("README.rst").read(),
    classifiers=classifiers,
    keywords=['diagram', 'generator'],
    author='Takeshi Komiya',
    author_email='i.tkomiya at gmail.com',
    url='http://blockdiag.com/',
    download_url='http://pypi.python.org/pypi/actdiag',
    license='Apache License 2.0',
    py_modules=['actdiag_sphinxhelper'],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    package_data={'': ['buildout.cfg']},
    include_package_data=True,
    python_requires=">=3.5",
    install_requires=['blockdiag >= 1.5.0'],
    extras_require=dict(
        rst=[
            'docutils',
        ],
        testing=[
            'nose',
            'pep8 >=1.3',
            'reportlab',
            'docutils',
            'flake8',
            'flake8-coding',
            'flake8-copyright',
        ],
    ),
    test_suite='nose.collector',
    entry_points="""
       [console_scripts]
       actdiag = actdiag.command:main

       [blockdiag_plugins]
       autolane = actdiag.plugins.autolane
    """,
)
