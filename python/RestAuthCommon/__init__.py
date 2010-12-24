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

import handlers

CONTENT_HANDLERS = { 'application/json': handlers.json, 
	'application/xml': handlers.xml,
	'application/x-www-form-urlencoded': handlers.form }

def marshal( content_type, obj ):
	handler = CONTENT_HANDLERS[content_type]()
	return handler.marshal( obj )

def unmarshal( content_type, raw_data, typ ):
	handler = CONTENT_HANDLERS[content_type]()
	return handler.unmarshal( raw_data, typ )

def unmarshal_dict( content_type, raw_data, keys ):
	data = unmarshal( content_type, raw_data, dict )
	if sorted( keys ) != sorted( data.keys() ):
		raise MarshalError( "Did not find expected keys in string" ) 
	if len( keys ) == 1:
		return data[keys[0]]
	else:
		return [ data[key] for key in keys ]

