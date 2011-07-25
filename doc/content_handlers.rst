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
   marshalled = handler.marshal_dict( data )

   # unmarshal some data (for received data):
   unmarshalled = handler.unmarshal_dict( marshalled )

   # this should always be the same:
   print( unmarshalled == data )
   
You can also use this feature to implement your own content handlers. This is useful if your setup
includes software that encodes or decodes data in a way not understood by the other side of the
communication. Please see the respective documentation of the `RestAuth server
<https://server.restauth.net/config/content_handlers>`__ and of `RestAuthClient
<https://python.restauth.net/guide/content_handlers>`__ for more information.

API documentation
-----------------

.. automodule:: RestAuthCommon.handlers
   :members:
