APP=postdoc
VERSION=0.2.0


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


# Release Instructions:
#
# 1. bump version number at the top of this file
# 2. `make release`
#
# If this doesn't work, make sure you have wheels installed:
# pip install wheel
release:
	@sed -i -r /version/s/[0-9.]+/$(VERSION)/ setup.py
	@sed -i -r /version/s/[0-9]+\.[0-9]+\.[0-9]+/$(VERSION)/ postdoc.py
	@git commit -am "bump version to v$(VERSION)"
	@git tag v$(VERSION)
	python setup.py sdist bdist_wheel upload


# makes it easier to test setup.py's entry points
install:
	-pip uninstall $(APP) --yes
	pip install .
