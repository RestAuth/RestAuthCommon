PY2VERS=$(shell pyversions -vs)
PY3VERS=$(shell py3versions -vs)
PYVERS=${PY2VERS} ${PY3VERS}

# location of your virtualenv python interpreters
PY2=py2/bin/python
PY3=py3/bin/python


VERSION=$(shell ${PY2} setup.py -q version)
VENVDIR=test/virtualenv

PREFIX=restauth-common-$(VERSION)
TARBALL=../${PREFIX}.tar.gz
CHECKSUMS=../${PREFIX}.checksums.txt

clean:
	${PY2} setup.py clean
	rm -rf test dist build *.egg-info
	rm -f ${TARBALL} ${CHECKSUMS}

${VENVDIR}/python%:
	virtualenv -p python$* ${VENVDIR}/python$*
	${VENVDIR}/python$*/bin/pip install -r requirements.txt

test-python%: ${VENVDIR}/python%
	${VENVDIR}/python$*/bin/python setup.py test

test: ${PYVERS:%=test-python%}

build-python%: ${VENVDIR}/python%
	${VENVDIR}/python$*/bin/python setup.py build

build: ${PYVERS:%=build-python%}

sdist-python%: ${VENVDIR}/python%
	${VENVDIR}/python$*/bin/python setup.py sdist -d dist/python$*

sdist: ${PYVERS:%=sdist-python%}

sdist-test-python%: ${VENVDIR}/python%
	${VENVDIR}/python$*/bin/pip install dist/python$*/RestAuthCommon-$(VERSION).tar.gz
	${VENVDIR}/python$*/bin/python -c 'import RestAuthCommon'
	${VENVDIR}/python$*/bin/python -c 'from RestAuthCommon.handlers import JSONContentHandler'

sdist-test: ${PYVERS:%=sdist-test-python%}

homepage:
	${PY2} setup.py build_doc

tarball:
	git archive --prefix=${PREFIX} master | gzip > ${TARBALL}

	# create checksums
	echo "Release: restauth-common" > ${CHECKSUMS}
	echo "Version: ${VERSION}" >> ${CHECKSUMS}
	echo "Date: $(shell date -R)" >> ${CHECKSUMS}
	echo "" >> ${CHECKSUMS}
	echo "MD5 checksums:" >> ${CHECKSUMS}
	echo "==============" >> ${CHECKSUMS}
	echo "" >> ${CHECKSUMS}
	md5sum ${TARBALL} | sed 's/\.\.\///' >> ${CHECKSUMS}
	echo "" >> ${CHECKSUMS}

	echo "SHA1 checksums:" >> ${CHECKSUMS}
	echo "===============" >> ${CHECKSUMS}
	echo "" >> ${CHECKSUMS}
	sha1sum ${TARBALL} | sed 's/\.\.\///'  >> ${CHECKSUMS}
	echo "" >> ${CHECKSUMS}

	echo "SHA256 checksums:" >> ${CHECKSUMS}
	echo "=================" >> ${CHECKSUMS}
	echo "" >> ${CHECKSUMS}
	sha256sum ${TARBALL} | sed 's/\.\.\///' >> ${CHECKSUMS}
	echo "" >> ${CHECKSUMS}
	
	echo "SHA512 checksums:" >> ${CHECKSUMS}
	echo "=================" >> ${CHECKSUMS}
	echo "" >> ${CHECKSUMS}
	sha512sum ${TARBALL} | sed 's/\.\.\///'  >> ${CHECKSUMS}
	echo "" >> ${CHECKSUMS}

	# sign checksum files:
	gpg --clearsign ${CHECKSUMS}
	mv ${CHECKSUMS}.asc ${CHECKSUMS}

release: clean test build sdist sdist-test homepage tarball
	# done
