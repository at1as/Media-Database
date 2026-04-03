.PHONY: test run dryrun venv deps

CWD = $(shell pwd)
VENV = ./mediadb
PY   = $(VENV)/bin/python
PIP  = $(VENV)/bin/pip

venv:
	@test -d $(VENV) || python3 -m venv $(VENV)
	@$(PIP) install --upgrade pip

deps: venv
	@$(PIP) install --upgrade imdbinfo jinja2 lxml requests pymediainfo

test: deps
		$(PY) -m unittest discover -s tests

run: deps
		$(PY) run.py

dryrun: deps
		$(PY) run.py --dry-run
