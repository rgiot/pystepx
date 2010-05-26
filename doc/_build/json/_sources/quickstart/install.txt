.. sectionauthor: Romain giot <romain.giot@ensicaen.fr>

Installing pySTEP
=================

Since version 1.3.0, pySTEP no more relies on a list of scripts parametrized by the settings.py file.
It consists of a library build with the distutils framework.

Pre-requisite
-------------

Unlike most Python software, pySTEP required a C compiler to be present on the system. 
This is due to the fact of using Cython to improve speed. 
So, you have to install Cython (http://docs.cython.org/src/quickstart/install.html), before trying to install pySTEP.

The easiest way to install Cython is:

.. code-block:: sh

        easy_install cython

Installation
------------
To install pySTEP, you need to unpack the archive, enter the directory, and then run:

.. code-block:: sh

        python setup.py build_ext --inplace 
        python setup.py install


Testing the Installation
------------------------

After having install pySTEP, you can test it with: ::

>>> import pystepx.tutorials.Tutorial
>>> t = pystepx.tutorials.Tutorial.Tutorial1()
>>> t.run()
