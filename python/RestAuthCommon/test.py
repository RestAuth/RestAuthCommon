# This file is part of RestAuthCommon.
#
# RestAuthCommon is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# RestAuthCommon is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with RestAuthCommon.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

import json
import sys
import unittest

from RestAuthCommon.error import MarshalError
from RestAuthCommon.handlers import ContentHandler
from RestAuthCommon.handlers import FormContentHandler
from RestAuthCommon.handlers import JSONContentHandler
from RestAuthCommon.handlers import PickleContentHandler
from RestAuthCommon.handlers import Pickle3ContentHandler
from RestAuthCommon.handlers import XMLContentHandler
from RestAuthCommon.handlers import YAMLContentHandler


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

    if sys.version_info >= (3, 0):
        marshal_type = bytes
        unmarshal_type = str
    else:
        marshal_type = str
        unmarshal_type = unicode

    def stringtest(self, strings):
        for teststr in strings:
            marshalled = self.handler.marshal_str(teststr)
            self.assertTrue(isinstance(marshalled, self.marshal_type),
                            type(marshalled))

            unmarshalled = self.handler.unmarshal_str(marshalled)
            self.assertTrue(isinstance(unmarshalled, self.unmarshal_type),
                            '"%s" is %s, not %s' % (teststr, type(unmarshalled), self.unmarshal_type))
            self.assertEqual(teststr, unmarshalled)

        # convert strings to unicodes in python2
        if sys.version_info < (3, 0):
            for teststr in strings:
                teststr = unicode(teststr)

                marshalled = self.handler.marshal_str(teststr)
                self.assertTrue(isinstance(marshalled, self.marshal_type),
                                type(marshalled))

                unmarshalled = self.handler.unmarshal_str(marshalled)
                self.assertTrue(isinstance(unmarshalled, self.unmarshal_type),
                                type(unmarshalled))
                self.assertEqual(teststr, unmarshalled)

        # convert strings to bytes in python3
        if sys.version_info >= (3, 0):
            for teststr in strings:
                bytestr = bytes(teststr, 'utf-8')

                marshalled = self.handler.marshal_str(bytestr)
                self.assertTrue(isinstance(marshalled, self.marshal_type),
                                type(marshalled))
                unmarshalled = self.handler.unmarshal_str(marshalled)
                self.assertTrue(isinstance(unmarshalled, self.unmarshal_type),
                                type(unmarshalled))
                self.assertEqual(teststr, unmarshalled)

    def test_str(self):
        self.stringtest(self.strings)
        if self.SUPPORT_UNICODE:
            self.stringtest(self.unicode_strings)

    def dicttest(self, dicts):
        for testdict in dicts:
            marshalled = self.handler.marshal_dict(testdict)
            self.assertTrue(isinstance(marshalled, self.marshal_type), type(marshalled))
            unmarshalled = self.handler.unmarshal_dict(marshalled)
            self.assertTrue(isinstance(unmarshalled, dict), type(unmarshalled))
            self.assertEqual(testdict, unmarshalled)

    def test_dict(self):
        self.dicttest(self.dicts)
        if self.SUPPORT_NESTED_DICTS:
            self.dicttest(self.nested_dicts)

        if self.SUPPORT_UNICODE:
            self.dicttest(self.unicode_dicts)

    def listtest(self, lists):
        for testlist in lists:
            marshalled = self.handler.marshal_list(testlist)
            self.assertTrue(isinstance(marshalled, self.marshal_type), type(marshalled))

            unmarshalled = self.handler.unmarshal_list(marshalled)
            self.assertTrue(isinstance(unmarshalled, list), type(unmarshalled))
            self.assertEqual(testlist, unmarshalled)

    def test_list(self):
        self.listtest(self.lists)
        if self.SUPPORT_UNICODE:
            self.listtest(self.unicode_lists)


class TestJSONContentHandler(unittest.TestCase, TestContentHandler):
    def setUp(self):
        self.handler = JSONContentHandler()


class TestFormContentHandler(unittest.TestCase, TestContentHandler):
    SUPPORT_NESTED_DICTS = False

    def setUp(self):
        self.handler = FormContentHandler()

    def test_nesteddicts(self):
        for testdict in self.nested_dicts:
            self.assertRaises(MarshalError,
                              self.handler.marshal_dict, (testdict))


class TestPickleContentHandler(unittest.TestCase, TestContentHandler):
    def setUp(self):
        self.handler = PickleContentHandler()


if sys.version_info >= (3, 0):
    class TestPickle3ContentHandler(unittest.TestCase, TestContentHandler):
        def setUp(self):
            self.handler = Pickle3ContentHandler()


class TestYAMLContentHandler(unittest.TestCase, TestContentHandler):
    def setUp(self):
        self.handler = YAMLContentHandler()

class TestXMLContentHandler(unittest.TestCase, TestContentHandler):
    def setUp(self):
        self.handler = XMLContentHandler()
