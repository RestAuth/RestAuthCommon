``RestAuthCommon`` provides a few shared libraries for `RestAuth
<https://server.restauth.net>`_ (`git <https://github.com/RestAuth/server>`_)
and `RestAuthClient <https://python.restauth.net>`_ (`git
<https://github.com/RestAuth/RestAuthClient>`_), most prominently
content handlers for JSON, YAML, Pickle and XML.

For detailed source code documentation please see https://common.restauth.net.

Installation
____________

RestAuthCommon is usually installed automatically when a project depends on it.
If you want to install it manually, you can always do::

   pip install RestAuthCommon

If you want to use the XML and/or YAML content handler, you have to install
pyyaml and/or lxml::

   pip install lxml PyYAML

You can also download releases as tarballs at
https://common.restauth.net/download.
