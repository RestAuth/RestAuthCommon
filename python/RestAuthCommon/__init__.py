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

