`actdiag` generate activity-diagram image file from spec-text file.

Features
========

* Generate activity-diagram from dot like text (basic feature).
* Multilingualization for node-label (utf-8 only).

You can get some examples and generated images on 
`blockdiag.com <http://blockdiag.com/actdiag/build/html/index.html>`_ .

Setup
=====

by easy_install
----------------
Make environment::

   $ easy_install actdiag

by buildout
------------
Make environment::

   $ hg clone http://bitbucket.org/tk0miya/actdiag
   $ cd actdiag
   $ python bootstrap.py
   $ bin/buildout

spec-text setting sample
========================

Few examples are available.
You can get more examples at
`blockdiag.com <http://blockdiag.com/actdiag/build/html/index.html>`_ .

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

* Python 2.4 or later (not support 3.x)
* Python Imaging Library 1.1.5 or later.
* funcparserlib 0.3.4 or later.
* setuptools or distribute.


License
=======
Apache License 2.0


History
=======

0.3.1 (2012-02-15)
------------------
* Add autolane plugin
* Update to new package structure (blockdiag >= 1.1.2)

0.3.0 (2011-11-19)
------------------
* Add fontfamily attribute for switching fontface
* Fix bugs

0.2.4 (2011-11-10)
------------------
* Fix dependencies (do not depend PIL directly for pillow users)

0.2.3 (2011-11-06)
------------------
* Add docutils exetension
* Fix bugs

0.2.2 (2011-11-01)
------------------
* Add class feature (experimental)

0.2.1 (2011-11-01)
------------------
* Follow blockdiag-0.9.7 interface

0.2.0 (2011-10-19)
------------------
* Follow blockdiag-0.9.5 interface 

0.1.9 (2011-10-11)
------------------
* Fix bugs

0.1.8 (2011-09-30)
------------------
* Add diagram attribute: default_text_color

0.1.7 (2011-07-05)
------------------
* Fix bugs

0.1.6 (2011-07-03)
------------------
* Support input from stdin

0.1.5 (2011-05-15)
------------------
* Fix bugs

0.1.4 (2011-05-14)
------------------
* Change license to Apache License 2.0
* Support blockdiag 0.8.1 core interface 

0.1.3 (2011-04-19)
------------------
* Fix bugs

0.1.2 (2011-04-11)
------------------
* Fix bugs

0.1.1 (2011-04-10)
------------------
* Fix bugs

0.1.0 (2011-04-09)
------------------
* First release

