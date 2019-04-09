.PHONY: clean-pyc clean-build docs clean test

help:
	@echo "clean        - remove all build, test, coverage and Python artifacts"
	@echo "clean-build  - remove build artifacts"
	@echo "clean-pyc    - remove Python file artifacts"
	@echo "clean-test   - remove test and coverage artifacts"
	@echo "lint         - check style with flake8"
	@echo "test         - run tests quickly with the default Python"
	@echo "coverage     - check code coverage quickly with the default Python"
	@echo "docs         - generate Sphinx HTML documentation, including API docs"
	@echo "release      - package and upload a release"
	@echo "test-release - package and upload a release to testpy repository"
	@echo "dist         - package"
	@echo "install      - install the package to the active Python's site-packages"

clean: clean-build clean-pyc clean-test

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -fr {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/

lint:
	flake8 github_ssh_auth tests

test:
	python setup.py test

coverage:
	coverage run --source github_ssh_auth setup.py test
	coverage report -m
	coverage html
	xdg-open htmlcov/index.html

docs:
	rm -f docs/*.rst
	# cd docs && $(MAKE) $@
	sphinx-apidoc -o docs/ github_ssh_auth
	open docs/_build/html/index.html

test-release: dist
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

release: dist
	twine upload dist/*

dist: clean
	python setup.py sdist bdist_wheel
	ls -l dist

install: clean
	python setup.py install
