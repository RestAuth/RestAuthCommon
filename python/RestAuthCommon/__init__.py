# This file is part of RestAuthCommon.
#
#    RestAuthCommon is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Foobar is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with RestAuthCommon.  If not, see <http://www.gnu.org/licenses/>.
"""
A collection of functions used in both server and client reference implementations.

.. moduleauthor:: Mathias Ertl <mati@fsinf.at>
"""
try:
	from RestAuthCommon import handlers
except ImportError:
	# python2.5 and earlier
	import handlers

CONTENT_HANDLERS = { 'application/json': handlers.json, 
	'application/xml': handlers.xml,
	'application/x-www-form-urlencoded': handlers.form }
"""
Mapping of MIME types to their respective handler implemenation. You can use this dictionary to
dynamically look up a content handler if you do not know the requested content type in advance.

================================= ========================== =====
MIME type                         handler                    notes
================================= ========================== =====
application/json                  :py:class:`.handlers.json` default
application/x-www-form-urlencoded :py:class:`.handlers.form` Only use this for testing
application/xml	                  :py:class:`.handlers.xml`  not yet implemented
================================= ========================== =====

If you want to provide your own implementation of a :py:class:`.content_handler`, you can add it to
this dictionary with the appropriate MIME type as the key.
"""

def marshal( content_type, obj ):
	"""
	Marshal the object *obj* into a string of the MIME type *content_type*.
	
	This method is just intended as a shortcut for :py:meth:`.content_handler.unmarshal`. If you
	intend to use a handler multiple times, it is better to instantiate a specific handler
	directly to save dictionary lookups and object instantiations.

	:param content_type: The format that the object should be marshalled into. This has to be
		one of the keys defined in :py:obj:`.CONTENT_HANDLERS`.
	:type  content_type: str
	:param obj: The object to marshal.

	:return: The string representation of the object.
	:rtype:  str

	:raise error.MarshalError: When the handler could not marshal the object.
	:see also: :py:meth:`.content_handler.marshal`
	"""
	handler = CONTENT_HANDLERS[content_type]()
	return handler.marshal( obj )

def unmarshal( content_type, raw_data, typ ):
	"""
	Unmarshal the string *raw_data* into an object of type *typ*. The string is assumed to be of
	the MIME type *content_type*.

	This method is just intended as a shortcut for :py:meth:`.content_handler.unmarshal`. If you
	intend to use a handler multiple times, it is better to instantiate a specific handler
	directly to save dictionary lookups and object instantiations.
	
	:param content_type: The format that the object should be marshalled into. This has to be
		one of the keys defined in :py:obj:`.CONTENT_HANDLERS`.
	:type  content_type: str
	:param raw_data: The raw string that should be unmarshalled.
	:type  raw_data: str
	:param typ: The type the unmarshaled object should be of.
	
	:rtype: typ
	:return: The unmarshalled data. The object has the type specified by the I{typ} parameter.
	
	:raise error.UnmarshalError: When the handler was unable unmarshal the object.

	:see also: :py:meth:`.content_handler.unmarshal`
	"""
	handler = CONTENT_HANDLERS[content_type]()
	return handler.unmarshal( raw_data, typ )

def resource_validator( name ):
	"""
	Check the *name* of a resource for some really bad characters that shouldn't be used
	anywhere in RestAuth. 

	This filters names containing a slash ("/") or colon (":") and those starting with '.'. It
	also filters control characters etc., including those from unicode.
	
	:param str name: The name to validate
	:returns: False if the name contains any invalid characters, True otherwise.
	:rtype: boolean
	"""
	if '/' in name or ':' in name or '\\' in name or name.startswith( '.' ):
		return False

	# filter various dangerous characters
	import stringprep
	for enc_char in name:
		if enc_char.__class__ == str:
			enc_char = enc_char.decode( 'utf-8' )

		if stringprep.in_table_c21_c22( enc_char ):
			# control characters
			return False
		if stringprep.in_table_c3( enc_char ):
			return False
		if stringprep.in_table_c4( enc_char ):
			return False
		if stringprep.in_table_c5( enc_char ):
			return False
		if stringprep.in_table_c6( enc_char ):
			return False
		if stringprep.in_table_c7( enc_char ):
			return False
		if stringprep.in_table_c8( enc_char ):
			return False
		if stringprep.in_table_c9( enc_char ):
			return False

	return True