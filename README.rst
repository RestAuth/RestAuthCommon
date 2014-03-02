**RestAuthCommon** provides code shared between `RestAuth <https://server.restauth.net>`_ (`git
<https://github.com/RestAuth/server>`_) and `RestAuthClient <https://python.restauth.net>`_ (`git
<https://github.com/RestAuth/RestAuthClient>`_), most prominently content handlers for JSON, YAML,
Pickle, BSON, MessagePack and XML.

For detailed source code documentation please see `our homepage`_.

Installation
____________

RestAuthCommon is usually installed automatically when a project depends on it.
If you want to or have to install it manually, you can always do::

   pip install RestAuthCommon

If you want to use the YAML and/or XML content handlers, you have to install the appropriate
libraries, e.g.::

   pip install lxml PyYAML pymongo msgpack-python

**Note:** The pymongo_ package provides BSON support, but you can also use the bson_ package
instaed, if you use Python 2 and want a library written in pure Python.

You can also download `release tarballs`_. We also provide packages for other distributions, please
see `our homepage`_ for more information.

Requirements
____________

* **RestAuthCommon** requires Python 2.6 or later or Python 3.2 or later.
* The ``bson`` content handler does not work with Python 3, because bson_ is not compatible.

.. _our homepage: https://common.restauth.net
.. _release tarballs: https://common.restauth.net/download
.. _lxml: https://pypi.python.org/pypi/lxml
.. _PyYAML: https://pypi.python.org/pypi/PyYAML
.. _bson: https://pypi.python.org/pypi/bson
.. _pymongo: https://pypi.python.org/pypi/pymango
