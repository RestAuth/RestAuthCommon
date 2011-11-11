Installation from source
========================

Requirements
------------

**RestAuthCommon** requires `Python 2.6 <http://www.python.org/>`_ or later.

Get source
----------

From git
++++++++

This project is developed on `git.fsinf.at <https://git.fsinf.at/>`_. You can view the source code
at `git.fsinf.at/restauth/restauth-common  <https://git.fsinf.at/restauth/restauth-common>`_. To
clone the repository to a directory named "RestAuthCommon", simply do:

.. code-block:: bash

   git clone http://git.fsinf.at/restauth/restauth-common.git RestAuthCommon

Older versions are marked as tags. You can view available tags with :command:`git tag -l`. You can
use any of those versions with :command:`git checkout`, for example :command:`git checkout 1.0`.
To move back to the newest version, use :command:`git checkout master`.

If you ever want to update the source code, just use:

.. code-block:: bash

   python setup.py clean
   git pull
   
... and do the same as if you where
:ref:`doing a new installation <install_from-source_installation>`.

Official releases
+++++++++++++++++

You can download official releases of RestAuth `here <https://common.restauth.net/download>`_. The
latest release is version |latest-release|.

.. _install_from-source_installation:

Installation
------------

Installation of **RestAuthCommon** is very easy. Just go to the directory where your source
is located ("RestAuthCommon" in the above example) and just run:

.. code-block:: bash

   python setup.py build
   python setup.py install

.. NOTE:: On most systems, the ``install`` command requires superuser privileges.


You can verify that the installation worked by running this command from your home directory:

.. code-block:: bash

   cd
   python -c "import RestAuthCommon"

This will throw an ImportError if RestAuthCommon was not installed successfully.

Build documentation
-------------------

To generate the most recent documentation (the newest version of the document you're currently
reading), just run:

.. code-block:: bash

   python setup.py build_doc