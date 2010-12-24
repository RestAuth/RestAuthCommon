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

class json( content_handler ):
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

class form( content_handler ):
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

class xml( content_handler ):
	pass
