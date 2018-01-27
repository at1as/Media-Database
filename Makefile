.PHONY: test run

CWD = $(shell pwd)

test:
		python -m unittest discover -s tests

run:
		python run.py

dryrun:
		python run.py --dry-run

