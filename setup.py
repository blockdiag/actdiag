# -*- coding: utf-8 -*-
import sys
from setuptools import setup, find_packages

sys.path.insert(0, 'src')
import actdiag

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

setup(
    name='actdiag',
    version=actdiag.__version__,
    description='actdiag generates activity-diagram image from text',
    long_description=open("README.rst").read(),
    long_description_content_type='text/x-rst',
    classifiers=classifiers,
    keywords=['diagram', 'generator'],
    author='Takeshi Komiya',
    author_email='i.tkomiya@gmail.com',
    url='http://blockdiag.com/',
    download_url='http://pypi.python.org/pypi/actdiag',
    project_urls={
        "Code": "https://github.com/blockdiag/actdiag",
        "Issue tracker": "https://github.com/blockdiag/actdiag/issues",
    },
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
