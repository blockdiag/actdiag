`actdiag` generate activity-diagram image file from spec-text file.

.. image:: https://drone.io/bitbucket.org/blockdiag/actdiag/status.png
   :target: https://drone.io/bitbucket.org/blockdiag/actdiag
   :alt: drone.io CI build status

.. image:: https://pypip.in/v/actdiag/badge.png
   :target: https://pypi.python.org/pypi/actdiag/
   :alt: Latest PyPI version

.. image:: https://pypip.in/d/actdiag/badge.png
   :target: https://pypi.python.org/pypi/actdiag/
   :alt: Number of PyPI downloads


Features
========

* Generate activity-diagram from dot like text (basic feature).
* Multilingualization for node-label (utf-8 only).

You can get some examples and generated images on 
`blockdiag.com <http://blockdiag.com/actdiag/build/html/index.html>`_ .

Setup
=====

Use easy_install or pip::

   $ sudo easy_install actdiag

   Or

   $ sudo pip actdiag


spec-text setting sample
========================

Few examples are available.
You can get more examples at
`blockdiag.com`_ .

simple.diag
------------

simple.diag is simply define nodes and transitions by dot-like text format::

    diagram {
      A -> B -> C;
      lane you {
        A; B;
      }
      lane me {
        C;
      }
    }


Usage
=====

Execute actdiag command::

   $ actdiag simple.diag
   $ ls simple.png
   simple.png


Requirements
============
* Python 3.7 or later
* blockdiag 1.5.0 or later
* funcparserlib 0.3.6 or later
* reportlab (optional)
* wand and imagemagick (optional)
* setuptools


License
=======
Apache License 2.0
