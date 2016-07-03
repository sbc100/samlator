test: venv
	python samlator_test.py

setup: venv
	pip install -r requirements.txt

freeze: venv
	pip freeze > requirements.txt

docs/tests.md: venv *.py tests/*.py
	./samlator.py --list > $@

venv:
	virtualenv venv

.PHONY: freeze setup test freeze
