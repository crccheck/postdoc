APP=postdoc
VERSION=0.4.0


clean:
	find . -name "*.pyc" -delete
	find . -name ".DS_Store" -delete
	rm -rf *.egg
	rm -rf *.egg-info
	rm -rf __pycache__
	rm -rf build
	rm -rf dist


test:
	python setup.py test


# Set the version. Done this way to avoid fancy, brittle Python import magic
version:
	@sed -i -r /version/s/[0-9.]+/$(VERSION)/ setup.py
	@sed -i -r /__version__\ =/s/[0-9.]+/$(VERSION)/ postdoc.py


# Release Instructions:
#
# 1. bump version number at the top of this file
# 2. `make release`
# 3. `git push origin master --tags`
release: clean version
	@git commit -am "bump version to v$(VERSION)"
	@git tag v$(VERSION)
	@-pip install wheel > /dev/null
	python setup.py sdist bdist_wheel upload


# makes it easier to test setup.py's entry points
install:
	-pip uninstall $(APP) --yes
	pip install .
