`actdiag` generate activity-diagram image file from spec-text file.

Features
========

* Generate activity-diagram from dot like text (basic feature).
* Multilingualization for node-label (utf-8 only).

You can get some examples and generated images on 
`tk0miya.bitbucket.org <http://tk0miya.bitbucket.org/actdiag/build/html/index.html>`_ .

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
`tk0miya.bitbucket.org <http://tk0miya.bitbucket.org/actdiag/build/html/index.html>`_ .

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

