class MarshalError( Exception ): pass
class UnmarshalError( Exception ): pass

class content_handler( object ):

	def marshal( self, obj ):
		func_name = 'marshal_%s'%(obj.__class__.__name__)
		try:
			func = getattr( self, func_name )
			return func( obj )
		except MarshalError as e:
			raise e
		except Exception as e:
			raise MarshalError( e )

	def unmarshal( self, data, typ ):
		try:
			func = getattr( self, 'unmarshal_%s'%(typ.__name__) )
			val = func( data )
		except UnmarshalError as e:
			raise e
		except Exception as e:
			raise UnmarshalError( e )
		
		if val.__class__ != typ:
			raise UnmarshalError( "Request body contained %s instead of %s"
			                        %(val.__class__, typ) )
		return val

	def unmarshal_str( self, data ): pass
	def unmarshal_dict( self, body ): pass
	def unmarshal_list( self, body ): pass
	def unmarshal_bool( self, body ): pass

	def marshal_str( self, obj ): pass
	def marshal_bool( self, obj ): pass
	def marshal_list( self, obj ): pass
	def marshal_dict( self, obj ): pass
	
	def marshal_unicode( self, obj ):
		return self.marshal_str( str( obj ) )

class json_handler( content_handler ):
	def __init__( self ):
		import json
		self.json = json

	def unmarshal_str( self, body ):
		return self.json.loads( body )

	def unmarshal_dict( self, body ):
		return self.json.loads( body )

	def unmarshal_list( self, body ):
		return self.json.loads( body )

	def unmarshal_bool( self, body ):
		return self.json.loads( body )
	
	def marshal_str( self, obj ):
		return self.json.dumps( obj )

	def marshal_bool( self, obj ):
		return self.json.dumps( obj )

	def marshal_list( self, obj ):
		return self.json.dumps( obj )

	def marshal_dict( self, obj ):
		return self.json.dumps( obj )

class form_handler( content_handler ):
	def unmarshal_dict( self, body ):
		# TODO: this doesn't work, QueryDict is not defined
		return QueryDict( body, encoding=request.encoding)

	def marshal_str( self, obj ):
		return obj

	def marshal_bool( self, obj ):
		if obj:
			return "1"
		else:
			return "0"

	def marshal_dict( self, obj ):
		# TODO: this doesn't work, QueryDict is not defined
		d = QueryDict('', True )
		d.update( obj )
		return d.urlencode()

	def marshal_list( self, obj ):
		d = dict( [ ('key%s'%i, obj[i]) for i in range(0,len(obj)) ] )
		return self.marshal_dict( d )

class xml_handler( content_handler ):
	pass

CONTENT_HANDLERS = { 'application/json': json_handler, 
	'application/xml': xml_handler,
	'application/x-www-form-urlencoded': form_handler }

def unmarshal_dict( content_type, raw_data, keys ):
	data = unmarshal( content_type, raw_data, dict )
	if sorted( keys ) != sorted( data.keys() ):
		raise MarshalError( "Did not find expected keys in string" ) 
	if len( keys ) == 1:
		return data[keys[0]]
	else:
		return [ data[key] for key in keys ]

def marshal( content_type, obj ):
	handler = CONTENT_HANDLERS[content_type]()
	return handler.marshal( obj )

def unmarshal( content_type, raw_data, typ ):
	handler = CONTENT_HANDLERS[content_type]()
	return handler.unmarshal( raw_data, typ )
