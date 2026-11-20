.DEFAULT_GOAL := help
.PHONY: help test run dryrun refresh refresh-movie refresh-series refresh-standup config config-check venv deps

CWD = $(shell pwd)
VENV = ./mediadb
PY   = $(VENV)/bin/python
PIP  = $(VENV)/bin/pip
IMDBINFO_REQUIREMENT = imdbinfo @ git+https://github.com/at1as/imdbinfo.git@8f9cc97ebd5c7557bed9f73ad8571c0ee043bfb1
TYPE ?= movie
COUNT ?= 10

help:
	@printf '%s\n' \
	  'Available commands' \
	  '  make help                              Show this command list' \
	  '  make venv                              Create the local virtual environment and upgrade pip' \
	  '  make deps                              Install or upgrade Python dependencies' \
	  '  make config                            Create conf.json from the template' \
	  '  make config-check                      Check that conf.json exists' \
	  '  make run                               Index new media and rebuild the site' \
	  '  make run COUNT=1                       Try up to one new title per enabled category' \
	  '  make dryrun                            Rebuild the site from saved metadata' \
	  '  make test                              Run the test suite' \
	  '  make refresh TYPE=movie COUNT=10        Refresh the oldest saved entries' \
	  '  make refresh-movie COUNT=10             Refresh the oldest movies' \
	  '  make refresh-series COUNT=10            Refresh series, prioritizing missing creators or descriptions' \
	  '  make refresh-standup COUNT=10           Refresh standup, prioritizing missing directors or descriptions'

venv:
	@test -d $(VENV) || python3 -m venv $(VENV)
	@$(PIP) install --upgrade pip

deps: venv
	@$(PIP) install --upgrade "$(IMDBINFO_REQUIREMENT)" jinja2 lxml requests pymediainfo

config:
	@test -f conf.json.template || (echo "conf.json.template is missing" && exit 1)
	@test ! -e conf.json || (echo "conf.json already exists; refusing to overwrite it" && exit 1)
	@cp conf.json.template conf.json

config-check:
	@test -f conf.json || (echo "conf.json is missing. Run 'make config' first." && exit 1)

test: config-check deps
		$(PY) -m unittest discover -s tests

run: export MEDIA_DATABASE_RUN_COUNT = $(COUNT)
run: config-check deps
		$(PY) run.py $(if $(filter-out file,$(origin COUNT)),--count "$$MEDIA_DATABASE_RUN_COUNT")

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
