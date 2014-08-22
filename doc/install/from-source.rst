Installation from source
========================

Requirements
------------

* **RestAuthCommon** requires `Python 2.7 <http://www.python.org/>`_ or later.
  On Python3, RestAuthCommon is tested with Python 3.2 and later.
* Some ContentHandlers require, if used, additional libraries:

  * The :py:class:`~.XMLContentHandler` requires the `lxml library
    <http://lxml.de/>`_.
  * The :py:class:`~.YAMLContentHandler` requires the `PyYAML library
    <http://pyyaml.org/>`_.
  * The :py:class:`~.BSONContentHandler` requires `PyMongo
    <http://api.mongodb.org/python/>`_.
  * The :py:class:`~.MessagePackContentHandler` requires `msgpack-python
    <https://pypi.python.org/pypi/msgpack-python>`_.
  * The :py:class:`~.Pickle3ContentHandler` requires Python3.

Get source
----------

From git
++++++++

This project is developed on `on GitHub <git_>`_. To clone the repository to a
directory named "RestAuthCommon", simply do:

.. code-block:: bash

   git clone https://github.com/RestAuth/restauth-common.git RestAuthCommon

Older versions are marked as tags. You can view available tags with
:command:`git tag -l`. You can use any of those versions with :command:`git
checkout <tag>`. To move back to the newest version, use :command:`git checkout
master`.

If you ever want to update the source code, just use:

.. code-block:: bash

   python setup.py clean
   git pull

... and do the same as if you where :ref:`doing a new installation
<install_from-source_installation>`.

Official releases
+++++++++++++++++

You can download official releases of RestAuthCommon `here
<download-releases_>`_.  The latest release is version
|latest-release|.

.. _install_from-source_installation:

Installation
------------

Installation of **RestAuthCommon** is very easy. Just go to the directory where
your source is located ("RestAuthCommon" in the above example) and run:

.. code-block:: bash

   python setup.py build
   python setup.py install

.. NOTE:: On most systems, the ``install`` command requires superuser privileges.


You can verify that the installation worked by running this command from your
home directory:

.. code-block:: bash

   cd
   python -c "import RestAuthCommon"

This will throw an ImportError if RestAuthCommon was not installed successfully.

Build documentation
-------------------

To generate the most recent documentation (the newest version of the document
you're currently reading), just run:

.. code-block:: bash

   python setup.py build_doc
