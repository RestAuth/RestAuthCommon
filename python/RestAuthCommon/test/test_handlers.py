# -*- coding: utf-8 -*-
#
# This file is part of RestAuthCommon (https://common.restauth.net).
#
# RestAuthCommon is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# RestAuthCommon is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See
# the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with RestAuthCommon.  If
# not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

import json
import pickle
import sys
import unittest

import bson
import yaml

from RestAuthCommon.error import MarshalError
from RestAuthCommon.error import UnmarshalError
from RestAuthCommon.handlers import BSONContentHandler
from RestAuthCommon.handlers import ContentHandler
from RestAuthCommon.handlers import FormContentHandler
from RestAuthCommon.handlers import JSONContentHandler
from RestAuthCommon.handlers import MessagePackContentHandler
from RestAuthCommon.handlers import PickleContentHandler
from RestAuthCommon.handlers import Pickle3ContentHandler
from RestAuthCommon.handlers import XMLContentHandler
from RestAuthCommon.handlers import YAMLContentHandler

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3


class TestHandler(ContentHandler):
    def __init__(self, librarypath):
        self.librarypath = librarypath


class Unserializeable(object):
    """A class whose instances are completely unserializable."""

    def __repr__(self):  # breaks Form handlers in Python3
        raise Exception("Don't serialize!")

    def __str__(self):  # breaks most serialization
        raise Exception("Don't serialize!")

    def __getstate__(self):  # brakes Pickle
        raise Exception("Don't serialize!")


class TestLibraryImport(unittest.TestCase):
    def test_basicimport(self):
        handler = TestHandler('sys')
        self.assertEqual(handler.library, sys)

        handler = TestHandler('json')
        self.assertEqual(handler.library, json)

    def test_wrongimport(self):
        handler = TestHandler('foobar')

        try:
            handler.library
            self.fail("Access to self.library should throw an exception.")
        except ImportError:
            pass


class TestContentHandler(object):
    SUPPORT_UNICODE = True
    SUPPORT_NESTED_DICTS = True
    INVALID = []
    INVALID2 = []
    INVALID3 = []
    EQUIVALENT = {
        'a': str,
        ('a', 'b'): list,
        (('a', 'b'), ('c', 'd')): dict,
    }

    strings = [
        '',
        'foobar',
        'whatever',
    ]

    unicode_strings = [
        'unicode1 \u6111',
        'unicode2 \u6155',
    ]

    lists = [
        [],
        ['abc'],
        ['abc', 'def'],
        ['abc', ''],
    ]

    unicode_lists = [
        ['unicode1 \u6111'],
        ['unicode1 \u6111', 'unicode1 \u6155'],
        ['unicode1 \u6111', ''],
    ]

    dicts = [
        {},
        {'a': '1'},
        {'a': '1', 'b': '2'},
        {'a': '1', 'b': ''},
    ]

    unicode_dicts = [
        {'a': 'unicode1 \u6111'},
        {'a': 'unicode1 \u6111', 'b': ''},
    ]

    nested_dicts = [
        {'a': {'foo': 'bar'}},
        {'a': {'foo': 'bar'}, 'b': '2'},
        {'a': {'foo': ''}, 'b': '2'},
    ]

    if PY3:
        marshal_type = bytes
        unmarshal_type = str
    else:
        marshal_type = str
        unmarshal_type = unicode

    def stringtest(self, strings, ucode=True, handler_func='marshal_str'):
        marshal = getattr(self.handler, handler_func)

        for teststr in strings:
            marshalled = marshal(teststr)
            self.assertTrue(isinstance(marshalled, self.marshal_type), type(marshalled))

            unmarshalled = self.handler.unmarshal_str(marshalled)
            self.assertTrue(isinstance(unmarshalled, self.unmarshal_type), (type(unmarshalled),
                                                                            unmarshalled, teststr))
            self.assertEqual(teststr, unmarshalled)

        # convert unicode to str in python2
        if PY2 and not ucode:
            for teststr in strings:
                rawstr = teststr.encode('utf-8')
                self.assertTrue(isinstance(rawstr, str))
                marshalled = marshal(rawstr)

                # assert that serialization returns the same strings:
                self.assertEqual(marshalled, marshal(teststr))

                self.assertTrue(isinstance(marshalled, self.marshal_type), type(marshalled))
                unmarshalled = self.handler.unmarshal_str(marshalled)
                self.assertTrue(isinstance(unmarshalled, self.unmarshal_type))
                self.assertEqual(teststr, unmarshalled)

        # convert strings to bytes in python3
        if PY3:
            for teststr in strings:
                bytestr = bytes(teststr, 'utf-8')
                self.assertTrue(isinstance(bytestr, bytes))
                marshalled = marshal(bytestr)

                # assert that serialization returns the same strings:
                self.assertEqual(marshalled, marshal(teststr))

                self.assertTrue(isinstance(marshalled, self.marshal_type), type(marshalled))
                unmarshalled = self.handler.unmarshal_str(marshalled)
                self.assertTrue(isinstance(unmarshalled, self.unmarshal_type), type(unmarshalled))
                self.assertEqual(teststr, unmarshalled)

    def test_str(self, handler_func='marshal_str'):
        self.stringtest(self.strings, ucode=False, handler_func=handler_func)
        if self.SUPPORT_UNICODE:
            self.stringtest(self.unicode_strings, handler_func=handler_func)

    def strify_dict(self, d):
        """Convert a dict of unicode objects to str objects, e.g.::

            >>> strify_dict({u'foo': u'bar', u'bla': {u'foo': u'bar'}})
            {'foo': 'bar', 'bla': {'foo': 'bar'}})

        """
        testdict = dict((k.encode('utf-8'),
                         v.encode('utf8') if isinstance(v, unicode) else self.strify_dict(v))
                        for k, v in d.iteritems())
        return testdict

    def byteify_dict(self, d):
        """Convert a dict of str objects to bytes, only useful in python3."""
        testdict = dict((k.encode('utf-8'),
                         v.encode('utf8') if isinstance(v, str) else self.byteify_dict(v))
                        for k, v in d.items())
        return testdict

    def assertUnicodeList(self, l):
        """Assert that all items in a list are unicode objects."""
        for e in l:
            self.assertTrue(isinstance(e, unicode), (l))

    def assertUnicodeDict(self, d):
        """Assert that all keys/values are unicode"""
        for k, v in d.iteritems():
            self.assertTrue(isinstance(k, unicode), (type(k), d))

            if isinstance(v, dict):
                self.assertUnicodeDict(v)
            else:
                self.assertTrue(isinstance(k, unicode))

    def assertStrDict(self, d):
        """Assert that all keys/values are str"""
        for k, v in d.items():
            self.assertTrue(isinstance(k, str), (type(k), d))

            if isinstance(v, dict):
                self.assertStrDict(v)
            else:
                self.assertTrue(isinstance(k, str))

    def assertStrList(self, l):
        for e in l:
            self.assertTrue(isinstance(e, str))

    def dicttest(self, dicts, ucode=True, handler_func='marshal_dict'):
        marshal = getattr(self.handler, handler_func)

        for testdict in dicts:
            marshalled = marshal(testdict)
            self.assertTrue(isinstance(marshalled, self.marshal_type))
            unmarshalled = self.handler.unmarshal_dict(marshalled)
            self.assertTrue(isinstance(unmarshalled, dict))
            self.assertEqual(testdict, unmarshalled)

        if PY2 and not ucode:
            for testdict in dicts:
                # convert dict keys/values to unicode
                strdict = self.strify_dict(testdict)
                marshalled = marshal(strdict)

                # assert that serialization returns the same strings:
                self.assertEqual(marshalled, marshal(testdict))

                self.assertTrue(isinstance(marshalled, self.marshal_type))
                unmarshalled = self.handler.unmarshal_dict(marshalled)
                self.assertTrue(isinstance(unmarshalled, dict))
                self.assertEqual(testdict, unmarshalled)
                self.assertUnicodeDict(unmarshalled)

        # convert strings to bytes in python3
        if PY3:
            for testdict in dicts:
                bytedict = self.byteify_dict(testdict)
                marshalled = marshal(bytedict)

                # assert that serialization returns the same strings:
                self.assertEqual(marshalled, marshal(testdict))

                self.assertTrue(isinstance(marshalled, self.marshal_type), type(marshalled))
                unmarshalled = self.handler.unmarshal_dict(marshalled)
                self.assertTrue(isinstance(unmarshalled, dict), type(unmarshalled))
                self.assertEqual(testdict, unmarshalled)
                self.assertStrDict(unmarshalled)

    def test_dict(self, handler_func='marshal_dict'):
        self.dicttest(self.dicts, ucode=False, handler_func=handler_func)
        if self.SUPPORT_NESTED_DICTS:
            self.dicttest(self.nested_dicts, handler_func=handler_func)

        if self.SUPPORT_UNICODE:
            self.dicttest(self.unicode_dicts)

    def listtest(self, lists, ucode=True, handler_func='marshal_list'):
        marshal = getattr(self.handler, handler_func)

        for testlist in lists:
            marshalled = marshal(testlist)
            self.assertTrue(isinstance(marshalled, self.marshal_type), type(marshalled))

            unmarshalled = self.handler.unmarshal_list(marshalled)
            self.assertTrue(isinstance(unmarshalled, list), type(unmarshalled))
            self.assertEqual(testlist, unmarshalled)

        if PY2 and not ucode:
            for testlist in lists:
                strlist = [e.encode('utf-8') for e in testlist]
                marshalled = marshal(strlist)

                # assert that serialization returns the same strings:
                self.assertEqual(marshalled, marshal(testlist))

                self.assertTrue(isinstance(marshalled, self.marshal_type), type(marshalled))
                unmarshalled = self.handler.unmarshal_list(marshalled)
                self.assertTrue(isinstance(unmarshalled, list), type(unmarshalled))
                self.assertEqual(testlist, unmarshalled)
                self.assertUnicodeList(unmarshalled)

        if PY3:
            for testlist in lists:
                bytelist = [e.encode('utf-8') for e in testlist]
                marshalled = marshal(bytelist)

                # assert that serialization returns the same strings:
                self.assertEqual(marshalled, marshal(testlist))

                self.assertTrue(isinstance(marshalled, self.marshal_type), type(marshalled))
                unmarshalled = self.handler.unmarshal_list(marshalled)
                self.assertTrue(isinstance(unmarshalled, list), type(unmarshalled))
                self.assertEqual(testlist, unmarshalled)
                self.assertStrList(unmarshalled)

    def test_list(self, handler_func='marshal_list'):
        self.listtest(self.lists, ucode=False, handler_func=handler_func)
        if self.SUPPORT_UNICODE:
            self.listtest(self.unicode_lists, handler_func=handler_func)

    def test_marshal(self):
        """Test the generic marshal function, used by RestAuth server."""
        self.test_str(handler_func='marshal')
        self.test_dict(handler_func='marshal')
        self.test_list(handler_func='marshal')

        # test some unserializeable stuff:
        self.assertRaises(MarshalError, self.handler.marshal, (Unserializeable(), ))
        self.assertRaises(MarshalError, self.handler.marshal, [[Unserializeable(), ], ])

    def test_invalid(self):
        for typ, obj in self.INVALID:
            func = getattr(self.handler, 'unmarshal_%s' % typ.__name__)
            self.assertRaises(UnmarshalError, func, obj)

    def test_equivalent(self):
        if PY2 and hasattr(self, 'EQUIVALENT2_MAPPING'):
            for equiv, typ in self.EQUIVALENT.items():
                func = getattr(self.handler, 'unmarshal_%s' % typ.__name__)

                serialized = self.EQUIVALENT2_MAPPING[equiv]
                self.assertEqual(func(serialized), typ(equiv))

        if PY3 and hasattr(self, 'EQUIVALENT3_MAPPING'):
            for equiv, typ in self.EQUIVALENT.items():
                func = getattr(self.handler, 'unmarshal_%s' % typ.__name__)

                serialized = self.EQUIVALENT3_MAPPING[equiv]
                self.assertEqual(func(serialized), typ(equiv))

    def test_unserializable(self):
        self.assertRaises(MarshalError, self.handler.marshal_str, (Unserializeable(), ))
        self.assertRaises(MarshalError, self.handler.marshal_list, (Unserializeable(), ))
        self.assertRaises(MarshalError, self.handler.marshal_dict, (Unserializeable(), ))

    def test_constructor(self):
        handler = self.handler.__class__(foo='bar')
        self.assertEqual(handler.foo, 'bar')


class TestJSONContentHandler(unittest.TestCase, TestContentHandler):
    INVALID = [
        (str, '["foo"'),
        (str, '"rawstr"'),
        (list, '["foo"'),
        (dict, '["foo"'),
    ]
    if PY2:
        EQUIVALENT2_MAPPING = {
            'a': json.dumps([str('a')]),
            ('a', 'b'): json.dumps([str('a'), str('b')]),
            (('a', 'b'), ('c', 'd')): json.dumps({str('a'): str('b'), str('c'): str('d')}),
        }
    else:
        EQUIVALENT3_MAPPING = {
            'a': json.dumps([bytes('a', 'utf-8')], cls=JSONContentHandler.ByteEncoder),
            ('a', 'b'): json.dumps([bytes('a', 'utf-8'), bytes('b', 'utf-8')],
                                   cls=JSONContentHandler.ByteEncoder),
            (('a', 'b'), ('c', 'd')): json.dumps({bytes('a', 'utf-8'): bytes('b', 'utf-8'),
                                                  bytes('c', 'utf-8'): bytes('d', 'utf-8')},
                                                 cls=JSONContentHandler.ByteEncoder),
        }

    def setUp(self):
        self.handler = JSONContentHandler()


class TestFormContentHandler(unittest.TestCase, TestContentHandler):
    SUPPORT_NESTED_DICTS = False

    def setUp(self):
        self.handler = FormContentHandler()

    def test_nesteddicts(self):
        for testdict in self.nested_dicts:
            self.assertRaises(MarshalError, self.handler.marshal_dict, (testdict))


class TestPickleContentHandler(unittest.TestCase, TestContentHandler):
    INVALID = [
        (str, 'invalid'),
        (list, 'invalid'),
        (dict, 'invalid'),
    ]
    if PY2:
        EQUIVALENT2_MAPPING = {
            'a': pickle.dumps(str('a')),
            ('a', 'b'): pickle.dumps([str('a'), str('b')]),
            (('a', 'b'), ('c', 'd')): pickle.dumps({str('a'): str('b'), str('c'): str('d')}),
        }
    else:
        EQUIVALENT3_MAPPING = {
            'a': pickle.dumps(bytes('a', 'utf-8')),
            ('a', 'b'): pickle.dumps([bytes('a', 'utf-8'), bytes('b', 'utf-8')]),
            (('a', 'b'), ('c', 'd')): pickle.dumps({bytes('a', 'utf-8'): bytes('b', 'utf-8'),
                                                    bytes('c', 'utf-8'): bytes('d', 'utf-8')}),
        }

    def setUp(self):
        self.handler = PickleContentHandler()


if PY3:
    class TestPickle3ContentHandler(unittest.TestCase, TestContentHandler):
        def setUp(self):
            self.handler = Pickle3ContentHandler()


class TestYAMLContentHandler(unittest.TestCase, TestContentHandler):
    INVALID = [
        (str, '%invalid'),
        (list, '%invalid'),
        (dict, '%invalid'),
    ]
    if PY2:
        EQUIVALENT2_MAPPING = {
            'a': yaml.dump(str('a')),
            ('a', 'b'): yaml.dump([str('a'), str('b')]),
            (('a', 'b'), ('c', 'd')): yaml.dump({str('a'): str('b'), str('c'): str('d')}),
        }
    else:
        EQUIVALENT3_MAPPING = {
            'a': yaml.dump(bytes('a', 'utf-8')),
            ('a', 'b'): yaml.dump([bytes('a', 'utf-8'), bytes('b', 'utf-8')]),
            (('a', 'b'), ('c', 'd')): yaml.dump({bytes('a', 'utf-8'): bytes('b', 'utf-8'),
                                                 bytes('c', 'utf-8'): bytes('d', 'utf-8')}),
        }

    def setUp(self):
        self.handler = YAMLContentHandler()


class TestXMLContentHandler(unittest.TestCase, TestContentHandler):
    def setUp(self):
        self.handler = XMLContentHandler()


if PY2 or hasattr(bson, 'BSON'):  # the pure BSON module bson doesn't work with Python3
    class TestBSONContentHandler(unittest.TestCase, TestContentHandler):
        def setUp(self):
            self.handler = BSONContentHandler()

        def test_unserializable(self):  # bson just silently discards unserializeable objects
            pass

        def test_marshal(self):  # same as parent function, but doesn't test unserializeable data
            self.test_str(handler_func='marshal')
            self.test_dict(handler_func='marshal')
            self.test_list(handler_func='marshal')


class TestMessagePackContentHandler(unittest.TestCase, TestContentHandler):
    def setUp(self):
        self.handler = MessagePackContentHandler()