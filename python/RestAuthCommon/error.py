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
Exceptions related to RestAuth communication.

.. moduleauthor:: Mathias Ertl <mati@restauth.net>
"""


class RestAuthException(Exception):
    """
    Common base class for all RestAuth related exceptions. All exceptions in
    this module are a subclass of this exception.
    """
    response_code = 500


class RestAuthImplementationException(RestAuthException):
    """
    Base class for errors that should not occur in a production environment. If
    you ever catch such an exception, it is most likely due to a buggy client
    or server implementation.
    """


class BadRequest(RestAuthImplementationException):
    """
    Thrown when RestAuth was unable to parse/find the required request
    parameters.

    On a protocol level, this represents HTTP status code 400.
    """
    response_code = 400


class MarshalError(RestAuthImplementationException):
    """Thrown if data can't be marshalled."""
    response_code = 400


class UnmarshalError(RestAuthImplementationException):
    """Thrown if data can't be unmarshalled."""
    response_code = 400


class RestAuthSetupException(RestAuthException):
    """
    Base class for errors that should not occur in a production environment
    that is correctly configured.
    """
    pass


class Unauthorized(RestAuthSetupException):
    """
    Thrown when service authentication failed.

    On a protocol level, this represents HTTP status code 401.
    """
    response_code = 401


class Forbidden(RestAuthSetupException):
    """
    Thrown when service authentication succeeded, but the client is not allowed
    to perform such a request.

    On a protocol level, this represents HTTP status code 403.
    """
    response_code = 403


class ContentTypeException(RestAuthSetupException):
    """
    Meta-class for Content-Type related exceptions.
    """
    pass


class NotAcceptable(ContentTypeException):
    """
    The current content type is not acceptable to the RestAuth service.

    On a protocol level, this represents HTTP status code 406.
    """
    response_code = 406


class UnsupportedMediaType(ContentTypeException):
    """
    The RestAuth service does not support the media type used by this client
    implementation.

    On a protocol level, this represents HTTP status code 415.
    """
    response_code = 415


class RestAuthRuntimeException(RestAuthException):
    """
    Base class for exceptions that may occur at runtime but are not related to
    user input. Any subclass of this exception may be thrown by every method
    that interacts with the RestAuth service.
    """
    pass


class InternalServerError(RestAuthRuntimeException):
    """
    Thrown when the RestAuth service has an Internal Server Error (HTTP
    status code 500).
    """
    response_code = 500


class RestAuthError(RestAuthException):
    """
    Base class for exceptions related to input coming from the client
    application.
    """
    pass


class ResourceNotFound(RestAuthError):
    """
    Thrown when a queried resource is not found.
    """
    response_code = 404

    def __init__(self, response):
        self.response = response

    def get_type(self):
        """
        Get the type of the queried resource that wasn't found.

        See the `specification
        <https://restauth.net/wiki/Specification#Resource-Type_header>`_ for
        possible values.

        :return: The resource type that causes this exception.
        :rtype: str
        """
        return self.response.getheader('Resource-Type')


class ResourceConflict(RestAuthError):
    """
    Thrown when trying to create a resource that already exists.

    On a protocol level, this represents HTTP status code 409.
    """
    response_code = 409


class PreconditionFailed(RestAuthError):
    """
    Thrown when the submitted data was unacceptable to the system. This
    usually occurs when the username is invalid or the password is to short.

    On a protocol level, this represents HTTP status code 412.
    """
    response_code = 412
