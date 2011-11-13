Installation on Debian/Ubuntu
=============================

.. NOTE:: If you just want to install the `RestAuth server <https://server.restauth.net>`_ or
   `RestAuthClient <https://python.restauth.net>`_ via APT, you do not have to seperately install
   this library, as it will be automatically installed.

The RestAuth project provides APT repositories for all software it maintains. Repositories are
available for all distributions that are currently maintained by the Debian project and Canonical
respectively except Debian 5.0 ("*lenny*") and Ubuntu 8.04 (*Hardy Heron*).

Adding our APT repository
-------------------------
To add the repositories, simply add this line to your :file:`/etc/apt/sources.list` file::
   
   deb http://apt.fsinf.at <dist> restauth
   
... where :samp:`{<dist>}` is any of the supported distributions. At the time of writing, possible
values are ``lucid``, ``maverick``, ``natty``, ``oneiric``, ``squeeze`` or ``wheezy``. Please see
the WikiPedia pages for `Ubuntu
<http://en.wikipedia.org/wiki/List_of_Ubuntu_releases#Table_of_versions>`_ and `Debian
<http://en.wikipedia.org/wiki/Debian#Release_history>`_ to see how they map to your installation.
You can also check the `APT repository itself <http://apt.fsinf.at/dists>`_ for a list of available
distributions (don't forget to check the 'Last modified' timestamp!).

Once you added the repository, you have to install the fsinf GPG keyring used for signing the
repositories, so you won't get any warnings when updating. You can either install the
``fsinf-keyring`` package using:

.. code-block:: bash

   apt-get update
   apt-get install fsinf-keyring
   apt-get update

or download and add the key directly using:

.. code-block:: bash

   wget -O - http://packages.spectrum.im/keys/apt-repository@fsinf.at | apt-key add -

Install RestAuthCommon
----------------------

Once you have added the repositories, installing RestAuthCommon is as simple as

.. code-block:: bash

   apt-get install restauth-common
   