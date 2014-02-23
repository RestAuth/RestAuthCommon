Content handlers
================

This module collects code related to *marshalling* and *unmarshalling* data. Marshalling objects
transforms them to serializable strings that can be sent over the network while unmarshalling does
the exact opposite: it transforms a string into a python object.

Both the `RestAuth server <https://server.restauth.net>`_ and `RestAuthClient
<https://python.restauth.net>`_ use concrete implementations of the :py:class:`~.content_handler`
class to (un)marshal data. To use such a content handler, simply create an instance of the content
handler:

.. code-block:: python

   import RestAuthCommon

   # some example data:
   data = {"foo": "bar"}

   # lookup handler:
   handler_class = RestAuthCommon.CONTENT_HANDLERS['application/json']
   handler = handler_class()

   # marshal some data (to send it)
   marshalled = handler.marshal_dict(data)

   # unmarshal some data (for received data):
   unmarshalled = handler.unmarshal_dict(marshalled)

   # this should always be the same:
   print(unmarshalled == data)

You can also use this feature to implement your own content handlers. This is useful if your setup
includes software that encodes or decodes data in a way not understood by the other side of the
communication. Please see the respective documentation of the `RestAuth server
<https://server.restauth.net/config/content_handlers>`__ and of `RestAuthClient
<https://python.restauth.net/guide/content_handlers>`__ for more information.

Existing content handlers
-------------------------

.. automodule:: RestAuthCommon.handlers
   :members:
   :exclude-members: ContentHandler

Custom handlers
---------------

To implement your own content handler, simply subclass :py:class:`Contenthandler`. Note that
serialization should be agnostic of input types, deserialization should return the same type
regardless of the type: In Python 2 all strings should be ``unicode`` (and not ``str``) objects, in
Python3 all strings should be ``str`` (and not ``byte``) objects, this includes elements of lists
and keys/values in dictionaries.

For example, the following should always be True in Python2::

   >>> h = YourHandler()
   >>> h.marshal_str('foo') == h.marshal_str(u'foo')
   True
   >>> h.unmarshal_str(h.marshal_str('foo')) == h.unmarshal_str(h.marshal_str(u'foo'))
   True
   >>> h.unmarshal_list(h.marshal_list(['foo', ]))
   [u'foo', ]
   >>> h.unmarshal_list(h.marshal_list([u'foo', ]))
   [u'foo', ]

... while the same goes for Python3::

   >>> h = YourHandler()
   >>> h.marshal_str('foo') == h.marshal_str(b'foo')
   True
   >>> h.unmarshal_str(h.marshal_str('foo')) == h.unmarshal_str(h.marshal_str(b'foo'))
   True
   >>> h.unmarshal_list(h.marshal_list(['foo', ]))
   ['foo', ]
   >>> h.unmarshal_list(h.marshal_list([b'foo', ]))
   ['foo', ]

and the same goes for composite types (e.g. ``[b'foo', ]`` and ``['foo', ]`` in Python3).

.. autoclass:: RestAuthCommon.handlers.ContentHandler
   :members:

   .. method:: normalize_dict(d)

      Normalizes a dictionary to the correct type, works with either Python2 or Python3. In
      Python2, you will get::

         >> h.normalize_dict({u'foo': 'bar', 'bla': u'blabla'})
         {u'foo': u'bar', u'bla': u'blabla'}

      ... while in Python3 you will get::

         >> h.normalize_dict({b'foo': 'bar', 'bla': b'blabla'})
         {'foo': 'bar', 'bla': 'blabla'}

   .. method:: normalize_list(l):

      Like :py:func:`~normalize_dict`, but for lists.

      .. method:: normalize_str(s):

      Like :py:func:`~normalize_dict`, but for strings.
