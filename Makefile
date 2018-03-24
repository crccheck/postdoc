APP=postdoc
VERSION=1.0.0


help: ## Shows this help
	@echo "$$(grep -h '#\{2\}' $(MAKEFILE_LIST) | sed 's/: #\{2\} /	/' | column -t -s '	')"

clean: ## Clean project
	find . -name "*.pyc" -delete
	find . -name ".DS_Store" -delete
	rm -rf *.egg
	rm -rf *.egg-info
	rm -rf __pycache__
	rm -rf build
	rm -rf dist

test: ## Run test suite
	python setup.py test

version: ## Set version number
	@sed -i -r /version/s/[0-9.]+/$(VERSION)/ setup.py
	@sed -i -r /__version__\ =/s/[0-9.]+/$(VERSION)/ postdoc.py

# Release Instructions:
#
# 1. bump version number at the top of this file
# 2. `make release`
# 3. `git push origin master --tags`
release: clean version
	@git commit -am "v$(VERSION)"
	@git tag v$(VERSION)
	@-pip install wheel > /dev/null
	python setup.py sdist bdist_wheel upload

install: ## Install (makes it easier to test setup.py's entry points)
	-pip uninstall $(APP) --yes
	pip install .
