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

if sys.version_info >= (3, 0):
    IS_PYTHON3 = True
    IS_PYTHON2 = False
else:
    IS_PYTHON3 = False
    IS_PYTHON2 = True


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
    """Override ``librarypath`` to lazily load named library upon first use.

    This may be a toplevel module (i.e. ``"json"``) or a submodule (i.e.
    ``"lxml.etree"``). The named library is accessable via ``self.library``.

    Example::

        class XMLContentHandler(ContentHandler):
            librarypath = 'lxml.etree'

            def unmarshal_str(self, data):
                tree = self.library.Element(data)
                # ...
    """

    SUPPORT_NESTED_DICTS = True
    """Set to False if your content handler does not support nested
    dictionaries as used i.e. during user-creation."""

    _library = None

    @property
    def library(self):
        """Library configured with the ``librarypath`` class variable."""
        if self._library is None:
            if '.' in self.librarypath:
                mod, lib = self.librarypath.rsplit('.', 1)
                _temp = __import__(mod, fromlist=[lib])
                self._library = getattr(_temp, lib)
            else:
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
        if IS_PYTHON2 and isinstance(obj, unicode):
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
        :rtype: str in python3, unicode in python2
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

    .. seealso:: `Specification <http://www.json.org>`_, `WikiPedia
        <http://en.wikipedia.org/wiki/JSON>`_
    """

    mime = 'application/json'
    """The mime-type used by this content handler is 'application/json'."""

    SEPARATORS = (',', ':')

    class ByteEncoder(libjson.JSONEncoder):
        def default(self, obj):
            if IS_PYTHON3 and isinstance(obj, bytes):
                return obj.decode('utf-8')
            return libjson.JSONEncoder.default(self, obj)

    class ByteDecoder(libjson.JSONDecoder):
        def decode(self, obj):
            if IS_PYTHON3 and isinstance(obj, bytes):
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
            if IS_PYTHON2 and isinstance(string, str):
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
            if IS_PYTHON3:
                return dumped.encode('utf-8')
            else:
                return dumped
        except ValueError as e:
            raise error.MarshalError(e)

    def marshal_bool(self, obj):
        try:
            dumped = libjson.dumps(obj, separators=self.SEPARATORS,
                                 cls=self.ByteEncoder)
            if IS_PYTHON3:
                return dumped.encode('utf-8')
            else:
                return dumped
        except ValueError as e:
            raise error.MarshalError(e)

    def marshal_list(self, obj):
        try:
            dumped = libjson.dumps(obj, separators=self.SEPARATORS,
                                 cls=self.ByteEncoder)
            if IS_PYTHON3:
                return dumped.encode('utf-8')
            else:
                return dumped
        except ValueError as e:
            raise error.MarshalError(e)

    def marshal_dict(self, obj):
        try:
            dumped = libjson.dumps(obj, separators=self.SEPARATORS,
                                 cls=self.ByteEncoder)
            if IS_PYTHON3:
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
        if IS_PYTHON3:
            body = body.decode('utf-8')

        parsed_dict = parse_qs(body, True)
        ret_dict = {}
        for key, value in parsed_dict.items():
            if isinstance(value, list) and len(value) == 1:
                ret_dict[key] = value[0]
            else:
                ret_dict[key] = value

        if IS_PYTHON2:
            ret_dict = self._decode_dict(ret_dict)

        return ret_dict

    def unmarshal_list(self, body):
        if IS_PYTHON3:
            body = body.decode('utf-8')

        if body == '':
            return []

        parsed = parse_qs(body, True)['list']

        if IS_PYTHON2:
            parsed = [e.decode('utf-8') for e in parsed]
        return parsed

    def unmarshal_str(self, body):
        if IS_PYTHON3:
            body = body.decode('utf-8')

        parsed = parse_qs(body, True)['str'][0]
        if IS_PYTHON2:
            parsed = parsed.decode('utf-8')
        return parsed

    def marshal_str(self, obj):
        if IS_PYTHON2:
            obj = obj.encode('utf-8')
        if IS_PYTHON3:
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
        if IS_PYTHON2:
            obj = self._encode_dict(obj)

        # verify that no value is a dictionary, because the unmarshalling for
        # that doesn't work:
        for v in obj.values():
            if isinstance(v, dict):
                raise error.MarshalError(
                    "FormContentHandler doesn't support nested dictionaries.")
        if IS_PYTHON3:
            return urlencode(obj, doseq=True).encode('utf-8')
        else:
            return urlencode(obj, doseq=True)

    def marshal_list(self, obj):
        if IS_PYTHON2:
            obj = [e.encode('utf-8') for e in obj]
        if IS_PYTHON3:
            return urlencode({'list': obj}, doseq=True).encode('utf-8')
        else:
            return urlencode({'list': obj}, doseq=True)


class PickleContentHandler(ContentHandler):
    """Handler for pickle-encoded content.

    .. seealso:: `module documentation
       <http://docs.python.org/2/library/pickle.html>`_,
       `WikiPedia <http://en.wikipedia.org/wiki/Pickle_(Python)>`_
    """

    mime = 'application/pickle'
    """The mime-type used by this content handler is 'application/pickle'."""

    PROTOCOL = 2

    def marshal_str(self, obj):
        try:
            return pickle.dumps(obj, protocol=self.PROTOCOL)
        except pickle.PickleError as e:
            raise error.MarshalError(str(e))

    def marshal_dict(self, obj):
        try:
            return pickle.dumps(obj, protocol=self.PROTOCOL)
        except pickle.PickleError as e:
            raise error.MarshalError(str(e))

    def marshal_list(self, obj):
        try:
            return pickle.dumps(obj, protocol=self.PROTOCOL)
        except pickle.PickleError as e:
            raise error.MarshalError(str(e))

    def unmarshal_str(self, data):
        try:
            unpickled = pickle.loads(data)

            if IS_PYTHON3 and isinstance(unpickled, bytes):
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

class Pickle3ContentHandler(PickleContentHandler):
    """Handler for pickle-encoded content, protocol level version 3.

    This version is only supported by the Python3 version the pickle module,
    this ContentHandler is only usable in Python3.

    .. seealso:: `module documentation
       <http://docs.python.org/3/library/pickle.html>`_,
       `WikiPedia <http://en.wikipedia.org/wiki/Pickle_(Python)>`_
    """

    mime = 'application/pickle3'
    """The mime-type used by this content handler is 'application/pickle3'."""

    PROTOCOL = 3


class YAMLContentHandler(ContentHandler):
    """Handler for YAML encoded content.

    .. NOTE:: This ContentHandler requires `PyYAML library
       <http://pyyaml.org/>`_.

    .. seealso:: `Specification <http://www.yaml.org/>`_,
        `WikiPedia <http://en.wikipedia.org/wiki/YAML>`_
    """
    mime = 'application/yaml'
    """The mime-type used by this content handler is 'application/yaml'."""

    librarypath = 'yaml'

    def _marshal_str3(self, obj):
        return self.library.dump(obj).encode('utf-8')

    def _marshal_str2(self, obj):
        return self.library.dump(obj)

    def marshal_str(self, obj):
        try:
            return self._marshal_str(obj)
        except self.library.YAMLError as e:
            raise error.MarshalError(str(e))

    def _marshal_dict3(self, obj):
        return self.library.dump(obj).encode('utf-8')

    def _marshal_dict2(self, obj):
        return self.library.dump(obj)

    def marshal_dict(self, obj):
        try:
            return self._marshal_dict(obj)
        except self.library.YAMLError as e:
            raise error.MarshalError(str(e))

    def _marshal_list3(self, obj):
        return self.library.dump(obj).encode('utf-8')

    def _marshal_list2(self, obj):
        return self.library.dump(obj)

    def marshal_list(self, obj):
        try:
            return self._marshal_list(obj)
        except self.library.YAMLError as e:
            raise error.MarshalError(str(e))

    def _unmarshal_str3(self, unmarshalled):
        if unmarshalled is None:
            return ''
        if isinstance(unmarshalled, bytes):
            return unmarshalled.decode('utf-8')
        else:
            return unmarshalled

    def _unmarshal_str2(self, unmarshalled):
        if unmarshalled is None:
            return unicode('')
        return unmarshalled

    def unmarshal_str(self, data):
        try:
            unmarshalled = self.library.load(data)
            return self._unmarshal_str(unmarshalled)
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

    if IS_PYTHON3:
        _marshal_str = _marshal_str3
        _marshal_dict = _marshal_dict3
        _marshal_list = _marshal_list3
        _unmarshal_str = _unmarshal_str3
    else:
        _marshal_str = _marshal_str2
        _marshal_dict = _marshal_dict2
        _marshal_list = _marshal_list2
        _unmarshal_str = _unmarshal_str2


class XMLContentHandler(ContentHandler):
    """Future location of the XML content handler.

    .. NOTE:: This ContentHandler requires the `lxml library
        <http://lxml.de/>`_.
    """

    mime = 'application/xml'
    """The mime-type used by this content handler is 'application/xml'."""

    librarypath = 'lxml.etree'

    def unmarshal_str(self, data):
        text = self.library.fromstring(data).text
        if text is None:
            text = ''

        if not IS_PYTHON3:
            text = unicode(text)
        return text

    def _unmarshal_dict(self, tree):
        d = {}

        # find all strings
        for e in tree.iterfind('str'):
            if e.text is None:
                d[e.attrib['key']] = ''
            else:
                d[e.attrib['key']] = e.text

        # parse subdictionaries
        for subdict in tree.iterfind('dict'):
            d[subdict.attrib['key']] = self._unmarshal_dict(subdict)

        return d

    def unmarshal_dict(self, body):
        return self._unmarshal_dict(self.library.fromstring(body))

    def unmarshal_list(self, body):
        l = []
        for elem in self.library.fromstring(body).iterfind('str'):
            if elem.text is None:
                l.append('')
            else:
                l.append(elem.text)
        return l

    def marshal_str(self, obj):
        root = self.library.Element('str')
        if IS_PYTHON3 and isinstance(obj, bytes):
            obj = obj.decode('utf-8')
        root.text = obj
        return self.library.tostring(root)

    def marshal_list(self, obj):
        root = self.library.Element('list')
        for value in obj:
            elem = self.library.Element('str')
            elem.text = value
            root.append(elem)
        return self.library.tostring(root)

    def _marshal_dict(self, obj, key=None):
        root = self.library.Element('dict')
        if key is not None:
            root.attrib['key'] = key

        for key, value in obj.items():
            if isinstance(value, str):
                elem = self.library.Element('str', attrib={'key': key})
                elem.text = value
                root.append(elem)
            elif not IS_PYTHON3 and isinstance(value, unicode):
                elem = self.library.Element('str', attrib={'key': key})
                elem.text = value
                root.append(elem)
            elif isinstance(value, dict):
                root.append(self._marshal_dict(value, key=key))
            else:
                raise error.MarshalError('MarshalError (type %s): %s'
                                         % (type(value), value))
        return root

    def marshal_dict(self, obj):
        return self.library.tostring(self._marshal_dict(obj))


CONTENT_HANDLERS = {
    'application/json': JSONContentHandler,
    'application/pickle': PickleContentHandler,
    'application/pickle3': Pickle3ContentHandler,
    'application/x-www-form-urlencoded': FormContentHandler,
    'application/xml': XMLContentHandler,
    'application/yaml': YAMLContentHandler,
}
"""
Mapping of MIME types to their respective handler implemenation. You can use
this dictionary to dynamically look up a content handler if you do not know the
requested content type in advance.

================================= ===========================================
MIME type                         Handler
================================= ===========================================
application/json                  :py:class:`.handlers.JSONContentHandler`
application/x-www-form-urlencoded :py:class:`.handlers.FormContentHandler`
application/pickle                :py:class:`.handlers.PickleContentHandler`
application/pickle3               :py:class:`.handlers.Pickle3ContentHandler`
application/xml                   :py:class:`.handlers.XMLContentHandler`
application/yaml                  :py:class:`.handlers.YAMLContentHandler`
================================= ===========================================

If you want to provide your own implementation of a
:py:class:`.ContentHandler`, you can add it to this dictionary with the
appropriate MIME type as the key.
"""

# old names, for compatability:
content_handler = ContentHandler
json = JSONContentHandler
xml = XMLContentHandler
form = FormContentHandler

# 'YamlContentHandler' was introduced in 0.6.1 and renamed for consistency to
# 'YAMLContentHandler' in 0.6.2
YamlContentHandler = YAMLContentHandler
