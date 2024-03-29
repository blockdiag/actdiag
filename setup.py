# -*- coding: utf-8 -*-
import os

from setuptools import find_packages, setup

classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
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
    packages=find_packages('src'),
    package_dir={'': 'src'},
    package_data={'': ['buildout.cfg']},
    include_package_data=True,
    python_requires=">=3.7",
    install_requires=['blockdiag >= 3.0.0'],
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
            'flake8-isort',
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
