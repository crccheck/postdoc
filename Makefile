clean:
	find . -name "*.pyc" -delete
	find . -name ".DS_Store" -delete
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info


test:
	python setup.py test


# Well, this is dangerous. And I'm not sure if it's really a 'build'.
build:
	python setup.py sdist upload
