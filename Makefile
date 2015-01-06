APP=postdoc


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


# Well, this is dangerous. And I'm not sure if it's really a 'build'.
build:
	python setup.py sdist upload


# makes it easier to test setup.py's entry points
install:
	-pip uninstall $(APP) --yes
	pip install .
