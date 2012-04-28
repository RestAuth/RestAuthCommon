# -*- coding: utf-8 -*-
#
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

name = 'RestAuthCommon'
url = 'https://common.restauth.net'

import os, re, sys, shutil, time
from os.path import exists
from distutils.core import setup, Command
from subprocess import Popen, PIPE
from distutils.command.clean import clean as _clean
#from distutils.command.build import build as _build

LATEST_RELEASE = '0.5.1'

class build_doc(Command):
    description = "Build API documentation."
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        command = self.get_command_name()

    def run(self):
        version = get_version()
        os.environ['SPHINXOPTS'] = '-D release=%s -D version=%s'%(version, version)
        os.environ['LATEST_RELEASE'] = LATEST_RELEASE
        
        cmd = [ 'make', '-C', 'doc', 'html' ]
        p = Popen(cmd)
        p.communicate()

def get_version():
    version = LATEST_RELEASE
    if exists('.version'):
        version = open('.version').readlines()[0]
    elif os.path.exists('.git'): # get from git
        date = time.strftime('%Y.%m.%d')
        cmd = [ 'git', 'describe', 'master' ]
        p = Popen(cmd, stdout=PIPE)
        version = p.communicate()[0].decode('utf-8')
    elif os.path.exists('debian/changelog'): # building .deb
        f = open('debian/changelog')
        version = re.search('\((.*)\)', f.readline()).group(1)
        f.close()
        
        if ':' in version: # strip epoch:
            version = version.split(':', 1)[1]
        version = version.rsplit('-', 1)[0] # strip debian revision
    return version.strip()

class version(Command):
    description = "Print version and exit."
    user_options = []

    def initialize_options(self): pass
    def finalize_options(self): pass
    def run(self):
        print(get_version())
        
class prepare_debian_changelog(Command):
    description = "prepare debian/changelog file"
    user_options = []
    
    def initialize_options(self): pass
    def finalize_options(self): pass
    def run(self):
        if not os.path.exists('debian/changelog'):
            sys.exit(0)
        
        version = get_version()
        cmd = ['sed', '-i', '1s/(.*)/(%s-1)/' % version, 'debian/changelog']
        p = Popen(cmd)
        p.communicate()

class clean(_clean):
    def run(self):
        cmd = [ 'make', '-C', 'doc', 'clean' ]
        p = Popen(cmd, stdout=PIPE)
        version = p.communicate()[0].decode('utf-8')
        
        if os.path.exists('build'):
            shutil.rmtree('build')
        if os.path.exists('dist'):
            shutil.rmtree('dist')
        if os.path.exists('MANIFEST'):
            os.remove('MANIFEST')
            
        _clean.run(self)

setup(
    name = name,
    version = str(get_version()),
    description = 'RestAuth shared library',
    author = 'Mathias Ertl',
    author_email='mati@restauth.net',
    url = url,
    download_url = 'http://git.fsinf.at/restauth/restauth-common',
    package_dir = {'': 'python'},
    packages = ['RestAuthCommon'],
    keywords = [],
    requires = [],
    license = "GNU General Public License (GPL) v3",
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Environment :: Other Environment",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Systems Administration :: Authentication/Directory",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Environment :: Web Environment",
    ],
    cmdclass = {'build_doc': build_doc, 'clean': clean, 
        'version': version, 'prepare_debian_changelog': prepare_debian_changelog,
    },
    long_description = """RestAuthCommon is a small set of classes used by both `RestAuth server
<https://server.restauth.net>`_ and `RestAuthClient <https://python.restauth.net>`_
(`PyPI <http://pypi.python.org/pypi/RestAuthClient/>`_).
"""
)
