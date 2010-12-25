This directory contains files used by multiple other parts of the RestAuth
system.

= Install =
To install the library, just execute (as root):
	python setup.py install

This package has no build dependencies.

=== RestAuthCommon ===
The python/ directory contains the RestAuthCommon library, which includes code
used by both the reference client and server implementation.

The JSON marshaller/unmarshaller requires python2.6 or later if used. The
reference server implementation will only use it when receiving data encoded in
JSON, the reference client library provides an option to use a different format
or your own implementation of a JSON marshaller/unmarshaller - see the
respective documentation for details.

=== Documentation ===
To build the library documentation, execute python setup.py build_doc. This
command requires epydoc to be installed.
