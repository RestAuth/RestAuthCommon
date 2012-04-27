# This file is part of RestAuthCommon.
#
#    RestAuthCommon is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    RestAuthCommon is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with RestAuthCommon.  If not, see <http://www.gnu.org/licenses/>.
"""
Classes and methods related to content handling.

.. moduleauthor:: Mathias Ertl <mati@restauth.net>
"""

import sys

try:
    from RestAuthCommon import error
except ImportError:
    # python2.5 and earlier
    import error

class content_handler(object):
    """
    This class is a common base class for all content handlers. If you
    want to implement your own content handler, you must subclass this
    class and implement all marshal_* and unmarshal_* methods.
    
    **Never use this class directly.** It does not marshal or unmarshal any content itself.
    """

    mime = None
    """Override this with the MIME type handled by your handler."""
    
    def marshal(self, obj):
        """
        Shortcut for marshalling just any object. 
        
        **Note:** If you know the type of **obj** in advance, you should
        use the marshal_* methods directly for improved speed.

        :param obj: The object to marshall.
        :return: The marshalled representation of the object.
        :rtype: str
        :raise error.MarshalError: If marshalling goes wrong in any way.
        """
        func_name = 'marshal_%s'%(obj.__class__.__name__)
        try:
            func = getattr(self, func_name)
            return func(obj)
        except error.MarshalError as e:
            raise e
        except Exception as e:
            raise error.MarshalError(e)

    def unmarshal(self, raw_data, typ):
        """
        Shortcut for unmarshalling a string to an object of type *typ*.
        
        **Note:** You may want to use the unmarshal_* methods directly
        for improved speed.

        :param raw_data: The string to unmarshall.
        :type  raw_data: str
        :param typ: The typ of the unmarshalled object.
        :type  typ: type
        :return: The unmarshalled object.
        :rtype: typ
        :raise error.UnmarshalError: If unmarshalling goes wrong in any way.
        """
        try:
            func = getattr(self, 'unmarshal_%s'%(typ.__name__))
            val = func(raw_data)
        except error.UnmarshalError as e:
            raise e
        except Exception as e:
            raise error.UnmarshalError(e)
        
        if val.__class__ != typ:
            raise error.UnmarshalError("Request body contained %s instead of %s"
                                    %(val.__class__, typ))
        return val

    def unmarshal_str(self, data):
        """
        Unmarshal a string.
        """
        pass
    
    def unmarshal_dict(self, body):
        """
        Unmarshal a dictionary.
        """
        pass
    def unmarshal_list(self, body):
        """
        Unmarshal a list.
        """
        pass
    
    def unmarshal_bool(self, body):
        """
        Unmarshal a boolean.
        """
        pass

    def marshal_str(self, obj):
        """
        Marshal a string.
        """
        pass
    
    def marshal_bool(self, obj):
        """
        Marshal a boolean.
        """
        pass
    
    def marshal_list(self, obj):
        """
        Marshal a list.
        """
        pass
    def marshal_dict(self, obj):
        """
        Marshal a dictionary.
        """
        pass
    
    def marshal_unicode(self, obj):
        return self.marshal_str(obj.encode('utf-8'))

class json(content_handler):
    """
    Concrete implementation of a :py:class:`content_handler` that uses JSON. This is the default
    content handler in both server and client library.
    """
    
    mime = 'application/json'
    """The mime-type used by this content handler is 'application/json'."""

    def __init__(self):
        import json
        self.json = json

    def unmarshal_str(self, body):
        try:
            pure = self.json.loads(body)
            if pure.__class__ != list or len(pure) != 1:
                raise error.UnmarshalError("Could not parse body as string")
        
            return pure[0]
        except ValueError:
            raise error.UnmarshalError(e)

    def unmarshal_dict(self, body):
        try:
            return self.json.loads(body)
        except ValueError as e:
            raise error.UnmarshalError(e)

    def unmarshal_list(self, body):
        try:
            return self.json.loads(body)
        except ValueError as e:
            raise error.UnmarshalError(e)

    def unmarshal_bool(self, body):
        try:
            return self.json.loads(body)
        except ValueError as e:
            raise error.UnmarshalError(e)
    
    def marshal_str(self, obj):
        try:
            return self.json.dumps([obj], separators=(',', ':'))
        except ValueError as e:
            raise error.MarshalError(e)

    def marshal_bool(self, obj):
        try:
            return self.json.dumps(obj, separators=(',', ':'))
        except ValueError as e:
            raise error.MarshalError(e)

    def marshal_list(self, obj):
        try:
            return self.json.dumps(obj, separators=(',', ':'))
        except ValueError as e:
            raise error.MarshalError(e)

    def marshal_dict(self, obj):
        try:
            return self.json.dumps(obj, separators=(',', ':'))
        except ValueError as e:
            raise error.MarshalError(e)
    
    def marshal_unicode(self, obj):
        try:
            return self.json.dumps([obj], separators=(',', ':'))
        except ValueError as e:
            raise error.MarshalError(e)

class form(content_handler):
    """
    Concrete implementation of a :py:class:`content_handler` that uses HTML forms. This content
    handler should not be used in any real world scenario, as it has many problems with unicode.
    """
    
    mime = 'application/x-www-form-urlencoded'
    """The mime-type used by this content handler is 'application/x-www-form-urlencoded'."""

    def __init__(self):
        try:
            from urllib.parse import parse_qs, urlencode
        except ImportError:
            from urlparse import parse_qs
            from urllib import urlencode
        self.parse_qs = parse_qs
        self.urlencode = urlencode

    def unmarshal_dict(self, body):
        return_dict = {}
        for key, value in self.parse_qs(body, True).iteritems():
            return_dict[key] = value[0]
        return return_dict

    def marshal_str(self, obj):
        return obj

    def marshal_bool(self, obj):
        if obj:
            return "1"
        else:
            return "0"

    def marshal_dict(self, obj):
        return self.urlencode(obj)

    def marshal_list(self, obj):
        d = dict([ ('key%s'%i, obj[i]) for i in range(0,len(obj)) ])
        return self.marshal_dict(d)

class xml(content_handler):
    """
    Future location of the XML content handler. This handler is not yet implemented!
    """
    mime = 'application/xml'
    
CONTENT_HANDLERS = { 'application/json': json, 
    'application/xml': xml,
    'application/x-www-form-urlencoded': form }
"""
Mapping of MIME types to their respective handler implemenation. You can use this dictionary to
dynamically look up a content handler if you do not know the requested content type in advance.

================================= ========================== =========================
MIME type                         handler                    notes
================================= ========================== =========================
application/json                  :py:class:`.handlers.json` default
application/x-www-form-urlencoded :py:class:`.handlers.form` Only use this for testing
application/xml                   :py:class:`.handlers.xml`  not yet implemented
================================= ========================== =========================

If you want to provide your own implementation of a :py:class:`.content_handler`, you can add it to
this dictionary with the appropriate MIME type as the key.
"""
