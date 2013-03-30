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

import json as libjson
import sys

try:
    from urllib.parse import parse_qs  # python3
    from urllib.parse import urlencode  # python3
except ImportError:
    from urlparse import parse_qs  # python2
    from urllib import urlencode  # python2

from RestAuthCommon import error


class ContentHandler(object):
    """
    This class is a common base class for all content handlers. If you
    want to implement your own content handler, you must subclass this
    class and implement all marshal_* and unmarshal_* methods.

    **Never use this class directly.** It does not marshal or unmarshal any
    content itself.  """

    mime = None
    """Override this with the MIME type handled by your handler."""

    librarypath = None
    """Override this with any 3rd-party library you do not want module-load
    time imports. Use self.load_library() to load that library into your
    namespace."""

    _library = None

    @property
    def library(self):
        """Library configured with the ``librarypath`` class variable."""
        if self._library is None:
            self._library = __import__(self.librarypath)
        return self._library

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
        func_name = 'marshal_%s' % (obj.__class__.__name__)
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
            func = getattr(self, 'unmarshal_%s' % (typ.__name__))
            val = func(raw_data)
        except error.UnmarshalError as e:
            raise e
        except Exception as e:
            raise error.UnmarshalError(e)

        if val.__class__ != typ:
            raise error.UnmarshalError(
                "Request body contained %s instead of %s" %
                (val.__class__, typ)
            )
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


class JSONContentHandler(ContentHandler):
    """
    Concrete implementation of a :py:class:`ContentHandler` that uses JSON.
    This is the default content handler in both server and client library.
    """

    mime = 'application/json'
    """The mime-type used by this content handler is 'application/json'."""

    SEPARATORS = (',', ':')

    class ByteEncoder(libjson.JSONEncoder):
        def default(self, obj):
            if sys.version_info >= (3, 0) and isinstance(obj, bytes):
                return obj.decode('utf-8')
            return json.JSONEncoder.default(self, obj)

    def unmarshal_str(self, body):
        try:
            pure = libjson.loads(body)
            if pure.__class__ != list or len(pure) != 1:
                raise error.UnmarshalError("Could not parse body as string")

            return pure[0]
        except ValueError:
            raise error.UnmarshalError(e)

    def unmarshal_dict(self, body):
        try:
            return libjson.loads(body)
        except ValueError as e:
            raise error.UnmarshalError(e)

    def unmarshal_list(self, body):
        try:
            return libjson.loads(body)
        except ValueError as e:
            raise error.UnmarshalError(e)

    def unmarshal_bool(self, body):
        try:
            return libjson.loads(body)
        except ValueError as e:
            raise error.UnmarshalError(e)

    def marshal_str(self, obj):
        try:
            return libjson.dumps([obj], separators=self.SEPARATORS,
                                 cls=self.ByteEncoder)
        except ValueError as e:
            raise error.MarshalError(e)

    def marshal_bool(self, obj):
        try:
            return libjson.dumps(obj, separators=self.SEPARATORS,
                                 cls=self.ByteEncoder)
        except ValueError as e:
            raise error.MarshalError(e)

    def marshal_list(self, obj):
        try:
            return libjson.dumps(obj, separators=self.SEPARATORS,
                                 cls=self.ByteEncoder)
        except ValueError as e:
            raise error.MarshalError(e)

    def marshal_dict(self, obj):
        try:
            return libjson.dumps(obj, separators=self.SEPARATORS,
                                 cls=self.ByteEncoder)
        except ValueError as e:
            raise error.MarshalError(e)


class FormContentHandler(ContentHandler):
    """Handler for HTML Form urlencoded content.

    .. WARNING:: Because of the limitations of urlencoded forms, this handler
       does not support nested dictionaries.
    """

    mime = 'application/x-www-form-urlencoded'
    """The mime-type used by this content handler is
    'application/x-www-form-urlencoded'."""

    def _decode_dict(self, d):
        decoded = {}
        for key, value in d.items():
            key = key.decode('utf-8')
            if isinstance(value, (str, unicode)):
                decoded[key] = value.decode('utf-8')
            elif isinstance(value, list):
                decoded[key] = [e.decode('utf-8') for e in value]
            elif isinstance(value, dict):
                decoded[key] = self._decode_dict(value)

        return decoded

    def unmarshal_dict(self, body):
        parsed_dict = parse_qs(body, True)
        ret_dict = {}
        for key, value in parsed_dict.items():
            if isinstance(value, list) and len(value) == 1:
                ret_dict[key] = value[0]
            else:
                ret_dict[key] = value

        if sys.version_info < (3, 0):
            ret_dict = self._decode_dict(ret_dict)

        return ret_dict

    def unmarshal_list(self, body):
        if body == '':
            return []

        parsed = parse_qs(body, True)['list']

        if sys.version_info < (3, 0):
            parsed = [e.decode('utf-8') for e in parsed]
        return parsed

    def unmarshal_str(self, body):
        parsed = parse_qs(body, True)['str'][0]
        if sys.version_info < (3, 0):
            parsed = parsed.decode('utf-8')
        return parsed

    def marshal_str(self, obj):
        if sys.version_info < (3, 0):
            obj = obj.encode('utf-8')
        return urlencode({'str': obj})

    def marshal_bool(self, obj):
        if obj:
            return "1"
        else:
            return "0"

    def _encode_dict(self, d):
        encoded = {}
        for key, value in d.items():
            key = key.encode('utf-8')
            if isinstance(value, (str, unicode)):
                encoded[key] = value.encode('utf-8')
            elif isinstance(value, list):
                encoded[key] = [e.encode('utf-8') for e in value]
            elif isinstance(value, dict):
                encoded[key] = self._encode_dict(value)

        return encoded

    def marshal_dict(self, obj):
        if sys.version_info < (3, 0):
            obj = self._encode_dict(obj)

        # verify that no value is a dictionary, because the unmarshalling for
        # that doesn't work:
        for v in obj.values():
            if isinstance(v, dict):
                raise error.MarshalError(
                    "FormContentHandler doesn't support nested dictionaries.")
        return urlencode(obj, doseq=True)

    def marshal_list(self, obj):
        if sys.version_info < (3, 0):
            obj = [e.encode('utf-8') for e in obj]
        return urlencode({'list': obj}, doseq=True)


class PickleContentHandler(ContentHandler):
    mime = 'application/pickle'


class YamlContentHandler(ContentHandler):
    mime = 'application/yaml'


class XMLContentHandler(ContentHandler):
    """
    Future location of the XML content handler. This handler is not yet
    implemented!  """
    mime = 'application/xml'


CONTENT_HANDLERS = {
    'application/json': JSONContentHandler,
    'application/pickle': PickleContentHandler,
    'application/x-www-form-urlencoded': FormContentHandler,
    'application/xml': XMLContentHandler,
    'application/yaml': YamlContentHandler,
}
"""
Mapping of MIME types to their respective handler implemenation. You can use
this dictionary to dynamically look up a content handler if you do not know the
requested content type in advance.

================================= ======================================== =================
MIME type                         handler                    notes
================================= ======================================== =================
application/json                  :py:class:`.handlers.JSONContentHandler` default
application/x-www-form-urlencoded :py:class:`.handlers.FormContentHandler` Only use this for
                                                             testing
application/xml                   :py:class:`.handlers.XMLContentHandler`  not yet
                                                                           implemented
================================= ======================================== =================

If you want to provide your own implementation of a
:py:class:`.ContentHandler`, you can add it to this dictionary with the
appropriate MIME type as the key.
"""

# old names, for compatability:
json = JSONContentHandler
xml = XMLContentHandler
form = FormContentHandler
