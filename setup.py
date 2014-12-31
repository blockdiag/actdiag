# -*- coding: utf-8 -*-
import sys
from setuptools import setup, find_packages

sys.path.insert(0, 'src')
import actdiag

classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python",
    "Topic :: Software Development",
    "Topic :: Software Development :: Documentation",
    "Topic :: Text Processing :: Markup",
]

test_requires = ['nose',
                 'pep8>=1.3',
                 'reportlab',
                 'docutils']

# only for Python2.6
if sys.version_info > (2, 6) and sys.version_info < (2, 7):
    test_requires.append('unittest2')

setup(
    name='actdiag',
    version=actdiag.__version__,
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
    install_requires=[
        'setuptools',
        'blockdiag>=1.5.0',
         # -*- Extra requirements: -*-
    ],
    extras_require=dict(
        testing=test_requires,
        rst=[
            'docutils',
        ],
    ),
    test_suite='nose.collector',
    tests_require=test_requires,
    entry_points="""
       [console_scripts]
       actdiag = actdiag.command:main

       [blockdiag_plugins]
       autolane = actdiag.plugins.autolane
    """,
)
