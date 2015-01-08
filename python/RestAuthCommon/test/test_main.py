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

import sys
import unittest

from RestAuthCommon import resource_validator

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

username1 = "mati1 愑"  # \u6111
username2 = "mati2 愒"  # \u6112


class validator_tests(unittest.TestCase):
    def test_ok(self):
        self.assertTrue(resource_validator(username1))
        self.assertTrue(resource_validator(username2))
        self.assertTrue(resource_validator(str('foobar')))

    def test_stringprep(self):
        self.assertFalse(resource_validator('foo\u2000bar'))  # C.1.2 Non-ASCII space characters
        self.assertFalse(resource_validator('foo\u0002bar'))  # C.2.1 ASCII control characters
        self.assertFalse(resource_validator('foo\u001Fbar'))  # C.2.1 ASCII control characters
        self.assertFalse(resource_validator('foo\u180Ebar'))  # C.2.2 Non-ASCII control characters
        self.assertFalse(resource_validator('foo\uE000bar'))  # C.3 Private use
        self.assertFalse(resource_validator('foo\uFDD0bar'))  # C.4 Non-character code points
        self.assertFalse(resource_validator('foo\uD800bar'))  # C.5 Surrogate codes
        self.assertFalse(resource_validator('foo\uFFFDbar'))  # C.6 Inappropriate for plain text
        self.assertFalse(resource_validator('foo\u2FF0bar'))  # C.7 Inappropriate for canonical representation
        self.assertFalse(resource_validator('foo\u0340bar'))  # C.8 Change display properties or are deprecated
        self.assertFalse(resource_validator('foo\uE0001bar'))  # C.9 Tagging characters
        self.assertFalse(resource_validator('foo\U000E0001bar'))  # C.9 Tagging characters
