.PHONY: test run dryrun refresh refresh-movie refresh-series refresh-standup config config-check venv deps

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

config:
	@test -f conf.json.template || (echo "conf.json.template is missing" && exit 1)
	@test ! -e conf.json || (echo "conf.json already exists; refusing to overwrite it" && exit 1)
	@cp conf.json.template conf.json

config-check:
	@test -f conf.json || (echo "conf.json is missing. Run 'make config' first." && exit 1)

test: config-check deps
		$(PY) -m unittest discover -s tests

run: config-check deps
		$(PY) run.py

dryrun: config-check deps
		$(PY) run.py --dry-run

refresh: config-check deps
		$(PY) run.py --refresh $(TYPE) $(COUNT)

refresh-movie: config-check deps
		$(PY) run.py --refresh movie $(COUNT)

refresh-series: config-check deps
		$(PY) run.py --refresh series $(COUNT)

refresh-standup: config-check deps
		$(PY) run.py --refresh standup $(COUNT)
