.PHONY: test run

CWD = $(shell pwd)

test:
		python -m unittest discover -s tests

run:
		python run.py

