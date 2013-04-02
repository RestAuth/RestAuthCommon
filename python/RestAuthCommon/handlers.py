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
import pickle
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

    SUPPORT_NESTED_DICTS = True
    """Set to False if your content handler does not support nested
    dictionaries as used i.e. during user-creation."""

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
        if isinstance(obj, (bytes, str)):
            func_name = 'marshal_str'
        if sys.version_info < (3, 0) and isinstance(obj, unicode):
            func_name = 'marshal_str'
        else:
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
        """Unmarshal a string.

        :param data: Data to unmarshal.
        :type  data: bytes in python3, str in python2
        :rtype: str
        """
        pass

    def unmarshal_dict(self, body):
        """Unmarshal a dictionary.

        :param data: Data to unmarshal.
        :type  data: bytes in python3, str in python2
        :rtype: dict
        """
        pass

    def unmarshal_list(self, body):
        """Unmarshal a list.

        :param data: Data to unmarshal.
        :type  data: bytes in python3, str in python2
        :rtype: list
        """
        pass

    def unmarshal_bool(self, body):
        """Unmarshal a boolean.

        :param data: Data to unmarshal.
        :type  data: bytes in python3, str in python2
        :rtype: str
        """
        pass

    def marshal_str(self, obj):
        """Marshal a string.

        :param obj: Data to marshal.
        :type  obj: str, bytes, unicode
        :rtype: bytes in python3, str in python2
        """
        pass

    def marshal_bool(self, obj):
        """
        Marshal a boolean.
        """
        pass

    def marshal_list(self, obj):
        """Marshal a list.

        :param obj: Data to marshal.
        :type  obj: list
        :rtype: bytes in python3, str in python2
        """
        pass

    def marshal_dict(self, obj):
        """Marshal a dictionary.

        :param obj: Data to marshal.
        :type  obj: dict
        :rtype: bytes in python3, str in python2
        """
        pass


class JSONContentHandler(ContentHandler):
    """Handler for JSON encoded content.

    .. seealso:: http://www.json.org, http://en.wikipedia.org/wiki/JSON
    """

    mime = 'application/json'
    """The mime-type used by this content handler is 'application/json'."""

    SEPARATORS = (',', ':')

    class ByteEncoder(libjson.JSONEncoder):
        def default(self, obj):
            if sys.version_info >= (3, 0) and isinstance(obj, bytes):
                return obj.decode('utf-8')
            return libjson.JSONEncoder.default(self, obj)

    class ByteDecoder(libjson.JSONDecoder):
        def decode(self, obj):
            if sys.version_info >= (3, 0) and isinstance(obj, bytes):
                obj = obj.decode('utf-8')
            return libjson.JSONDecoder.decode(self, obj)

    def unmarshal_str(self, body):
        try:
            pure = libjson.loads(body, cls=self.ByteDecoder)
            if not isinstance(pure, list) or len(pure) != 1:
                raise error.UnmarshalError("Could not parse body as string")

            string = pure[0]

            # In python 2.7.1 (not 2.7.2) json.loads("") returns a str and
            # not unicode.
            if sys.version_info <= (3, 0) and isinstance(string, str):
                return unicode(string)

            return string
        except ValueError as e:
            raise error.UnmarshalError(e)

    def unmarshal_dict(self, body):
        try:
            return libjson.loads(body, cls=self.ByteDecoder)
        except ValueError as e:
            raise error.UnmarshalError(e)

    def unmarshal_list(self, body):
        try:
            return libjson.loads(body, cls=self.ByteDecoder)
        except ValueError as e:
            raise error.UnmarshalError(e)

    def unmarshal_bool(self, body):
        try:
            return libjson.loads(body)
        except ValueError as e:
            raise error.UnmarshalError(e)

    def marshal_str(self, obj):
        try:
            dumped = libjson.dumps([obj], separators=self.SEPARATORS,
                                 cls=self.ByteEncoder)
            if sys.version_info >= (3, 0):
                return dumped.encode('utf-8')
            else:
                return dumped
        except ValueError as e:
            raise error.MarshalError(e)

    def marshal_bool(self, obj):
        try:
            dumped = libjson.dumps(obj, separators=self.SEPARATORS,
                                 cls=self.ByteEncoder)
            if sys.version_info >= (3, 0):
                return dumped.encode('utf-8')
            else:
                return dumped
        except ValueError as e:
            raise error.MarshalError(e)

    def marshal_list(self, obj):
        try:
            dumped = libjson.dumps(obj, separators=self.SEPARATORS,
                                 cls=self.ByteEncoder)
            if sys.version_info >= (3, 0):
                return dumped.encode('utf-8')
            else:
                return dumped
        except ValueError as e:
            raise error.MarshalError(e)

    def marshal_dict(self, obj):
        try:
            dumped = libjson.dumps(obj, separators=self.SEPARATORS,
                                 cls=self.ByteEncoder)
            if sys.version_info >= (3, 0):
                return dumped.encode('utf-8')
            else:
                return dumped
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

    SUPPORT_NESTED_DICTS = False

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
        if sys.version_info >= (3, 0):
            body = body.decode('utf-8')

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
        if sys.version_info >= (3, 0):
            body = body.decode('utf-8')

        if body == '':
            return []

        parsed = parse_qs(body, True)['list']

        if sys.version_info < (3, 0):
            parsed = [e.decode('utf-8') for e in parsed]
        return parsed

    def unmarshal_str(self, body):
        if sys.version_info >= (3, 0):
            body = body.decode('utf-8')

        parsed = parse_qs(body, True)['str'][0]
        if sys.version_info < (3, 0):
            parsed = parsed.decode('utf-8')
        return parsed

    def marshal_str(self, obj):
        if sys.version_info < (3, 0):
            obj = obj.encode('utf-8')
        if sys.version_info >= (3, 0):
            return urlencode({'str': obj}).encode('utf-8')
        else:
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
        if sys.version_info >= (3, 0):
            return urlencode(obj, doseq=True).encode('utf-8')
        else:
            return urlencode(obj, doseq=True)

    def marshal_list(self, obj):
        if sys.version_info < (3, 0):
            obj = [e.encode('utf-8') for e in obj]
        if sys.version_info >= (3, 0):
            return urlencode({'list': obj}, doseq=True).encode('utf-8')
        else:
            return urlencode({'list': obj}, doseq=True)


class PickleContentHandler(ContentHandler):
    """Handler for pickle-encoded content.

    .. seealso:: http://docs.python.org/2/library/pickle.html,
       http://en.wikipedia.org/wiki/Pickle_(Python)
    """

    mime = 'application/pickle'
    """The mime-type used by this content handler is 'application/pickle'."""

    def marshal_str(self, obj):
        try:
            return pickle.dumps(obj, protocol=2)
        except pickle.PickleError as e:
            raise error.MarshalError(str(e))

    def marshal_dict(self, obj):
        try:
            return pickle.dumps(obj, protocol=2)
        except pickle.PickleError as e:
            raise error.MarshalError(str(e))

    def marshal_list(self, obj):
        try:
            return pickle.dumps(obj, protocol=2)
        except pickle.PickleError as e:
            raise error.MarshalError(str(e))

    def unmarshal_str(self, data):
        try:
            unpickled = pickle.loads(data)

            if sys.version_info >= (3, 0) and isinstance(unpickled, bytes):
                # if bytes were pickled, we have to decode them
                unpickled = unpickled.decode('utf-8')
            return unpickled
        except pickle.PickleError as e:
            raise error.UnmarshalError(str(e))

    def unmarshal_list(self, data):
        try:
            return pickle.loads(data)
        except pickle.PickleError as e:
            raise error.UnmarshalError(str(e))

    def unmarshal_dict(self, data):
        try:
            return pickle.loads(data)
        except pickle.PickleError as e:
            raise error.UnmarshalError(str(e))


class YamlContentHandler(ContentHandler):
    """Handler for YAML encoded content.

    .. NOTE:: This handler requires the third-party py-yaml library.

    .. seealso:: http://www.yaml.org/, http://en.wikipedia.org/wiki/YAML
    """
    mime = 'application/yaml'
    """The mime-type used by this content handler is 'application/yaml'."""

    librarypath = 'yaml'

    def marshal_str(self, obj):
        try:
            if sys.version_info >= (3, 0):
                return self.library.dump(obj).encode('utf-8')
            else:
                return self.library.dump(obj)
        except self.library.YAMLError as e:
            raise error.MarshalError(str(e))

    def marshal_dict(self, obj):
        try:
            if sys.version_info >= (3, 0):
                return self.library.dump(obj).encode('utf-8')
            else:
                return self.library.dump(obj)
        except self.library.YAMLError as e:
            raise error.MarshalError(str(e))

    def marshal_list(self, obj):
        try:
            if sys.version_info >= (3, 0):
                return self.library.dump(obj).encode('utf-8')
            else:
                return self.library.dump(obj)
        except self.library.YAMLError as e:
            raise error.MarshalError(str(e))

    def unmarshal_str(self, data):
        try:
            unmarshalled = self.library.load(data)
            if unmarshalled is None:
                return ''
            if sys.version_info >= (3, 0) and isinstance(unmarshalled, bytes):
                return unmarshalled.decode('utf-8')
            else:
                return unmarshalled
        except self.library.YAMLError as e:
            raise error.UnmarshalError(str(e))

    def unmarshal_list(self, data):
        try:
            return self.library.load(data)
        except self.library.YAMLError as e:
            raise error.UnmarshalError(str(e))

    def unmarshal_dict(self, data):
        try:
            return self.library.load(data)
        except self.library.YAMLError as e:
            raise error.UnmarshalError(str(e))


class XMLContentHandler(ContentHandler):
    """Future location of the XML content handler.

    .. WARNING:: This handler is not yet implemented!
    """
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

================================= ==========================================
MIME type                         Handler
================================= ==========================================
application/json                  :py:class:`.handlers.JSONContentHandler`
application/x-www-form-urlencoded :py:class:`.handlers.FormContentHandler`
application/pickle                :py:class:`.handlers.PickleContentHandler`
application/xml                   :py:class:`.handlers.XMLContentHandler`
application/yaml                  :py:class:`.handlers.YamlContentHandler`
================================= ==========================================

If you want to provide your own implementation of a
:py:class:`.ContentHandler`, you can add it to this dictionary with the
appropriate MIME type as the key.
"""

# old names, for compatability:
content_handler = ContentHandler
json = JSONContentHandler
xml = XMLContentHandler
form = FormContentHandler
