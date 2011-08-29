# This file is part of RestAuthCommon.
#
#    RestAuthClient.py is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Foobar is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with RestAuthClient.py.  If not, see <http://www.gnu.org/licenses/>.

name = 'RestAuthCommon'
url = 'https://fs.fsinf.at/wiki/RestAuth/RestAuthCommon'

import os, sys, shutil, time
from os.path import exists
from distutils.core import setup, Command
from subprocess import Popen, PIPE
from distutils.command.clean import clean as _clean

class build_doc( Command ):
	description = "Build API documentation."
	user_options = []

	def initialize_options( self ):
		pass

	def finalize_options( self ):
		command = self.get_command_name()
		options = self.distribution.command_options[ command ]

	def run( self ):
		cmd = [ 'make', '-C', 'doc', 'html' ]
		p = Popen( cmd )
		p.communicate()

def get_version():
	version = '0.5.0'
	if exists( '.version' ):
		version = open( '.version' ).readlines()[0]
	elif os.path.exists( '.git' ): # get from git
		date = time.strftime( '%Y.%m.%d' )
		cmd = [ 'git', 'describe' ]
		p = Popen( cmd, stdout=PIPE )
		version = p.communicate()[0].decode( 'utf-8' )
	return version.strip()

class version( Command ):
	description = "Print version and exit."
	user_options = []

	def initialize_options( self ): pass
	def finalize_options( self ): pass
	def run( self ):
		print( get_version() )

class clean( _clean ):
	def run( self ):
		cmd = [ 'make', '-C', 'doc', 'clean' ]
		p = Popen( cmd, stdout=PIPE )
		version = p.communicate()[0].decode( 'utf-8' )
			
		_clean.run( self )

setup(
	name = name,
	version = get_version(),
	description = 'RestAuth shared library',
	author = 'Mathias Ertl',
	author_email='mati@fsinf.at',
	url = url,
	package_dir = {'': 'python'},
	packages = ['RestAuthCommon'],
	cmdclass = { 'build_doc': build_doc, 'clean': clean, 
		'version': version }
)
