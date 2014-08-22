PY2VERS=$(shell pyversions -vs)
PY3VERS=$(shell py3versions -vs)
PYVERS=${PY2VERS} ${PY3VERS}

# location of your virtualenv python interpreters
PY2=py2/bin/python
PY3=py3/bin/python


VERSION=$(shell ${PY2} setup.py -q version)
VENVDIR=test/virtualenv

TARPREFIX=restauth-common-$(VERSION)
TARBALL=../${TARPREFIX}.tar.gz

clean:
	${PY2} setup.py clean
	rm -rf test dist build *.egg-info

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
	git archive --prefix=${TARPREFIX} master | gzip > ${TARBALL}
	md5sum ${TARBALL} > ${TARBALL}.md5
	sha1sum ${TARBALL} > ${TARBALL}.sha1
	sha512sum ${TARBALL} > ${TARBALL}.sha512

release: clean test build sdist sdist-test homepage tarball
	# done
