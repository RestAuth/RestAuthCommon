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
A collection of functions used in both server and client reference
implementations.

.. moduleauthor:: Mathias Ertl <mati@restauth.net>
"""

import stringprep


def resource_validator(name):
    """
    Check the *name* of a resource for some really bad characters that
    shouldn't be used anywhere in RestAuth.

    This filters names containing a slash ("/") or colon (":") and those
    starting with '.'. It also filters control characters etc., including those
    from unicode.

    :param str name: The name to validate
    :returns: False if the name contains any invalid characters, True
        otherwise.
    :rtype: bool
    """
    if '/' in name or ':' in name or '\\' in name or name.startswith('.'):
        return False

    # filter various dangerous characters
    for enc_char in name:
        if enc_char.__class__ == str:
            enc_char = enc_char.decode('utf-8')

        if stringprep.in_table_c21_c22(enc_char):
            # control characters
            return False
        if stringprep.in_table_c3(enc_char):
            return False
        if stringprep.in_table_c4(enc_char):
            return False
        if stringprep.in_table_c5(enc_char):
            return False
        if stringprep.in_table_c6(enc_char):
            return False
        if stringprep.in_table_c7(enc_char):
            return False
        if stringprep.in_table_c8(enc_char):
            return False
        if stringprep.in_table_c9(enc_char):
            return False

    return True
