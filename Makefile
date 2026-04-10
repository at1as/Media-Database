.PHONY: test run dryrun refresh refresh-movie refresh-series refresh-standup venv deps

CWD = $(shell pwd)
VENV = ./mediadb
PY   = $(VENV)/bin/python
PIP  = $(VENV)/bin/pip
TYPE ?= movie
COUNT ?= 10

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

refresh: deps
		$(PY) run.py --refresh $(TYPE) $(COUNT)

refresh-movie: deps
		$(PY) run.py --refresh movie $(COUNT)

refresh-series: deps
		$(PY) run.py --refresh series $(COUNT)

refresh-standup: deps
		$(PY) run.py --refresh standup $(COUNT)
