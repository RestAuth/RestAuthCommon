Error handling
==============

This module collects various exceptions that may be thrown when communication with a RestAuth
server. The exceptions are collected here because the `RestAuth server
<https://server.restauth.net>` also uses these exceptions for error handling. The multi-level
inheritance of the exceptions in these modules allows you to:

* catch all RestAuth related errors with :py:exc:`.RestAuthException`
* catch types of errors with i.e. :py:exc:`.RestAuthSetupException`
* catch individual errors with i.e. :py:exc:`.Unauthorized`.

Also see :ref:`below <error-Example>` for a full example.

RestAuthException
-----------------

In general, all exceptions thrown by code related to RestAuth are a subclass of this exception:

.. autoexception:: RestAuthCommon.error.RestAuthException
   :members:

RestAuthException subclasses
----------------------------

The direct subclasses of :py:exc:`.RestAuthException` represent different types of problems and are
never thrown directly. Instead, :ref:`subclasses <error-concrete_exceptions>` are thrown to indicate the
exact problem. You can use these exceptions to catch an entire type of problem and handle all
subclasses collectively. Please also see the :ref:`example <error-Example>`.

.. autoexception:: RestAuthCommon.error.RestAuthImplementationException
   :members:
   :show-inheritance:
.. autoexception:: RestAuthCommon.error.RestAuthSetupException
   :members:
   :show-inheritance:
.. autoexception:: RestAuthCommon.error.RestAuthError
   :members:
   :show-inheritance:
.. autoexception:: RestAuthCommon.error.RestAuthRuntimeException
   :members:
   :show-inheritance:
.. autoexception:: RestAuthCommon.error.ContentTypeException
   :members:
   :show-inheritance:

.. _error-concrete_exceptions:

Concrete exceptions
-------------------

.. automodule:: RestAuthCommon.error
   :members:
   :exclude-members: RestAuthException, RestAuthImplementationException, RestAuthSetupException, RestAuthError, RestAuthRuntimeException, ContentTypeException
   :show-inheritance:
   
.. _error-example:

Example
-------

Here is a detailed example showing the different granularity-levels you may use:

.. code-block:: python

   from RestAuthCommon import error

   try:
       # some code related to RestAuth:
       pass
       
   # catch some general types of errors:
   except error.RestAuthRuntimeException:
       print( "The authentication service suffers from internal problems." )
   except error.RestAuthSetupException:
       print( "Configuration error." )
       
   # do a more detailed report on data the user entered:
   except error.ResourceNotFound:
       print( "The resource addressed wasn't found" )
   except error.ResourceConflict:
       print( "Tried to create a resource that already exists" )
       
   # make sure that no RestAuthException propagates:
   except error.RestAuthException:
       print( "uncaught RestAuthException." )