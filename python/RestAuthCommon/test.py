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

import json
import sys
import unittest

from RestAuthCommon.handlers import ContentHandler

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
