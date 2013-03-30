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

from RestAuthCommon.handlers import ContentHandler
from RestAuthCommon.handlers import JSONContentHandler


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
    strings = [
        '',
        'foobar',
        'whatever',
        'unicode1 \u6111',
        'unicode2 \u6155',
    ]

    def test_str(self):
        for teststr in self.strings:
            marshalled = self.handler.marshal_str(teststr)
            self.assertTrue(isinstance(marshalled, str))

            unmarshalled = self.handler.unmarshal_str(marshalled)
            self.assertEqual(teststr, unmarshalled)

        if sys.version_info < (3, 0):  # test for python2
            for teststr in self.strings:
                teststr = unicode(teststr)

                marshalled = self.handler.marshal_str(teststr)
                self.assertTrue(isinstance(marshalled, str))

                unmarshalled = self.handler.unmarshal_str(marshalled)
                self.assertEqual(teststr, unmarshalled)

        if sys.version_info > (3, 0):
            for teststr in self.strings:
                teststr = bytes(teststr, 'utf-8')

                marshalled = self.handler.marshal_str(teststr)
                self.assertTrue(isinstance(marshalled, str))
                unmarshalled = self.handler.unmarshal_str(marshalled)
                self.assertEqual(teststr.decode('utf-8'), unmarshalled)

    def test_dict(self):
        testdict = {'foo': 'bar', 'nested': {'foo': 'bar'}}

        marshalled = self.handler.marshal_dict(testdict)
        unmarshalled = self.handler.unmarshal_dict(marshalled)
        self.assertEqual(testdict, unmarshalled)


class TestJSONContentHandler(unittest.TestCase, TestContentHandler):
    def setUp(self):
        self.handler = JSONContentHandler()
