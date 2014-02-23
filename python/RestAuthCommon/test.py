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
import sys
import unittest

from RestAuthCommon.error import MarshalError
from RestAuthCommon.error import UnmarshalError
from RestAuthCommon.handlers import ContentHandler
from RestAuthCommon.handlers import FormContentHandler
from RestAuthCommon.handlers import JSONContentHandler
from RestAuthCommon.handlers import PickleContentHandler
from RestAuthCommon.handlers import Pickle3ContentHandler
from RestAuthCommon.handlers import XMLContentHandler
from RestAuthCommon.handlers import YAMLContentHandler

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3


class TestHandler(ContentHandler):
    def __init__(self, librarypath):
        self.librarypath = librarypath
    pass


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

    def stringtest(self, strings, ucode=True):
        for teststr in strings:
            marshalled = self.handler.marshal_str(teststr)
            self.assertTrue(isinstance(marshalled, self.marshal_type), type(marshalled))

            unmarshalled = self.handler.unmarshal_str(marshalled)
            self.assertTrue(isinstance(unmarshalled, self.unmarshal_type))
            self.assertEqual(teststr, unmarshalled)

        # convert unicode to str in python2
        if PY2 and not ucode:
            for teststr in strings:
                rawstr = teststr.encode('utf-8')
                self.assertTrue(isinstance(rawstr, str))
                marshalled = self.handler.marshal_str(rawstr)

                # assert that serialization returns the same strings:
                self.assertEqual(marshalled, self.handler.marshal_str(teststr))

                self.assertTrue(isinstance(marshalled, self.marshal_type), type(marshalled))
                unmarshalled = self.handler.unmarshal_str(marshalled)
                self.assertTrue(isinstance(unmarshalled, self.unmarshal_type))
                self.assertEqual(teststr, unmarshalled)

        # convert strings to bytes in python3
        if PY3:
            for teststr in strings:
                bytestr = bytes(teststr, 'utf-8')
                self.assertTrue(isinstance(bytestr, bytes))
                marshalled = self.handler.marshal_str(bytestr)

                # assert that serialization returns the same strings:
                self.assertEqual(marshalled, self.handler.marshal_str(teststr))

                self.assertTrue(isinstance(marshalled, self.marshal_type), type(marshalled))
                unmarshalled = self.handler.unmarshal_str(marshalled)
                self.assertTrue(isinstance(unmarshalled, self.unmarshal_type), type(unmarshalled))
                self.assertEqual(teststr, unmarshalled)

    def test_str(self):
        self.stringtest(self.strings, ucode=False)
        if self.SUPPORT_UNICODE:
            self.stringtest(self.unicode_strings)

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

    def dicttest(self, dicts, ucode=True):
        for testdict in dicts:
            marshalled = self.handler.marshal_dict(testdict)
            self.assertTrue(isinstance(marshalled, self.marshal_type), type(marshalled))
            unmarshalled = self.handler.unmarshal_dict(marshalled)
            self.assertTrue(isinstance(unmarshalled, dict), (type(unmarshalled), testdict))
            self.assertEqual(testdict, unmarshalled)

        if PY2 and not ucode:
            for testdict in dicts:
                # convert dict keys/values to unicode
                strdict = self.strify_dict(testdict)
                marshalled = self.handler.marshal_dict(strdict)

                # assert that serialization returns the same strings:
                self.assertEqual(marshalled, self.handler.marshal_dict(testdict))

                self.assertTrue(isinstance(marshalled, self.marshal_type), type(marshalled))
                unmarshalled = self.handler.unmarshal_dict(marshalled)
                self.assertTrue(isinstance(unmarshalled, dict), type(unmarshalled))
                self.assertEqual(testdict, unmarshalled)
                self.assertUnicodeDict(unmarshalled)

        # convert strings to bytes in python3
        if PY3:
            for testdict in dicts:
                bytedict = self.byteify_dict(testdict)
                marshalled = self.handler.marshal_dict(bytedict)

                # assert that serialization returns the same strings:
                self.assertEqual(marshalled, self.handler.marshal_dict(testdict))

                self.assertTrue(isinstance(marshalled, self.marshal_type), type(marshalled))
                unmarshalled = self.handler.unmarshal_dict(marshalled)
                self.assertTrue(isinstance(unmarshalled, dict), type(unmarshalled))
                self.assertEqual(testdict, unmarshalled)
                self.assertStrDict(unmarshalled)


    def test_dict(self):
        self.dicttest(self.dicts, ucode=False)
        if self.SUPPORT_NESTED_DICTS:
            self.dicttest(self.nested_dicts)

        if self.SUPPORT_UNICODE:
            self.dicttest(self.unicode_dicts)

    def listtest(self, lists, ucode=True):
        for testlist in lists:
            marshalled = self.handler.marshal_list(testlist)
            self.assertTrue(isinstance(marshalled, self.marshal_type), type(marshalled))

            unmarshalled = self.handler.unmarshal_list(marshalled)
            self.assertTrue(isinstance(unmarshalled, list), type(unmarshalled))
            self.assertEqual(testlist, unmarshalled)

        if PY2 and not ucode:
            for testlist in lists:
                strlist = [e.encode('utf-8') for e in testlist]
                marshalled = self.handler.marshal_list(strlist)

                # assert that serialization returns the same strings:
                self.assertEqual(marshalled, self.handler.marshal_list(testlist))

                self.assertTrue(isinstance(marshalled, self.marshal_type), type(marshalled))
                unmarshalled = self.handler.unmarshal_list(marshalled)
                self.assertTrue(isinstance(unmarshalled, list), type(unmarshalled))
                self.assertEqual(testlist, unmarshalled)
                self.assertUnicodeList(unmarshalled)

        if PY3:
            for testlist in lists:
                bytelist = [e.encode('utf-8') for e in testlist]
                marshalled = self.handler.marshal_list(bytelist)

                # assert that serialization returns the same strings:
                self.assertEqual(marshalled, self.handler.marshal_list(testlist))

                self.assertTrue(isinstance(marshalled, self.marshal_type), type(marshalled))
                unmarshalled = self.handler.unmarshal_list(marshalled)
                self.assertTrue(isinstance(unmarshalled, list), type(unmarshalled))
                self.assertEqual(testlist, unmarshalled)
                self.assertStrList(unmarshalled)

    def test_list(self):
        self.listtest(self.lists, ucode=False)
        if self.SUPPORT_UNICODE:
            self.listtest(self.unicode_lists)

    def test_invalid(self):
        for typ, obj in self.INVALID:
            func = getattr(self.handler, 'unmarshal_%s' % typ.__name__)
            self.assertRaises(UnmarshalError, func, obj)

class TestJSONContentHandler(unittest.TestCase, TestContentHandler):
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
    def setUp(self):
        self.handler = YAMLContentHandler()

class TestXMLContentHandler(unittest.TestCase, TestContentHandler):
    def setUp(self):
        self.handler = XMLContentHandler()
