# This file is part of RestAuthCommon.
#
#    RestAuthClient.py is free software: you can redistribute it and/or modify
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
#    along with RestAuthClient.py.  If not, see <http://www.gnu.org/licenses/>.
"""
This module provides easy marshalling and unmarshalling of objects, used by the
RestAuth reference client and server implementations.
"""
import handlers
CONTENT_HANDLERS = { 'application/json': handlers.json, 
	'application/xml': handlers.xml,
	'application/x-www-form-urlencoded': handlers.form }
"""
Mapping of MIME types to their respective handlers.
"""

def marshal( content_type, obj ):
	"""
	Marshal the object I{obj} into a string of the MIME type
	I{content_type}.
	
	This method is just intended as a shortcut for
	L{content_handler.marshal<handlers.content_handler.marshal>}. If you
	intend to use a handler multiple times, it is better to instantiate a
	specific handler directly to save dictionary lookups and object
	instantiations.

	@param content_type: The format that the object should be marshalled
		into. This has to be one of the keys defined in
		L{CONTENT_HANDLERS}.
	@type  content_type: str
	@param obj: The object to marshal.

	@return: The string representation of the object.
	@rtype:  str

	@raise handlers.MarshalError: When the handler could not marshal the
		object.
	@see: L{content_handler.marshal<handlers.content_handler.marshal>}
	"""
	handler = CONTENT_HANDLERS[content_type]()
	return handler.marshal( obj )

def unmarshal( content_type, raw_data, typ ):
	"""
	Unmarshal the string I{raw_data} into an object of type I{typ}. The
	string is assumed to be of the MIME type I{content_type}.

	This method is just intended as a shortcut for
	L{content_handler.unmarshal<handlers.content_handler.unmarshal>}. If you
	intend to use a handler multiple times, it is better to instantiate a
	specific handler directly to save dictionary lookups and object
	instantiations.
	
	@param content_type: The format that the object should be marshalled
		into. This has to be one of the keys defined in 
		L{CONTENT_HANDLERS}.
	@type  content_type: str
	@param raw_data: The raw string that should be unmarshalled.
	@type  raw_data: str
	@param typ: The type the unmarshaled object should be of.

	@rtype: typ
	@return: The unmarshalled data. The object has the type specified by the
		I{typ} parameter.

	@raise handlers.UnmarshalError: When the handler was unable unmarshal
		the object.

	@see: L{content_handler.unmarshal<handlers.content_handler.unmarshal>}
	"""
	handler = CONTENT_HANDLERS[content_type]()
	return handler.unmarshal( raw_data, typ )

def unmarshal_dict( content_type, raw_data, keys ):
	"""
	Unmarshal the string I{raw_data} in the format I{content_type} into a 
	dictionary and verify that this dictionary only contains the specified
	I{keys}. If I{keys} only contains one element, this method returns just
	the string, otherwise it returns the unmarshalled dictionary.

	This method primarily exists as as a means to ensure standars compliance
	of clients in the reference service implementation. Using this method,
	the server will throw an error if the client sends any unknown keys.

	@param content_type: The format that the object should be marshalled
		into. This has to be one of the keys defined in
		L{CONTENT_HANDLERS}.
	@type  content_type: str
	@param raw_data: The raw string that should be unmarshalled.
	@type  raw_data: str
	@param keys: The keys that the dictionary should contain.
	@type  keys: list

	@return: Either the unmarshalled dictionary or the value if I{keys}
		contains just one value.
	@rtype: dict/str

	@raise handlers.UnmarshalError: When the handler was unable unmarshal
		the object.
	"""
	data = unmarshal( content_type, raw_data, dict )
	if sorted( keys ) != sorted( data.keys() ):
		raise handlers.MarshalError( "Did not find expected keys in string" ) 
	if len( keys ) == 1:
		return data[keys[0]]
	else:
		return [ data[key] for key in keys ]

