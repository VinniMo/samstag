PYTHON ?= python3.12
VENV ?= .venv
VENV_PYTHON := $(VENV)/bin/python

.PHONY: setup dev test e2e check report lock

setup:
	SAMSTAG_VENV="$(VENV)" $(PYTHON) scripts/project.py setup

dev:
	$(VENV_PYTHON) scripts/project.py dev

test:
	$(VENV_PYTHON) scripts/project.py test

e2e:
	$(VENV_PYTHON) scripts/project.py e2e $(E2E_ARGS)

check:
	$(VENV_PYTHON) scripts/project.py check

report:
	$(VENV_PYTHON) scripts/project.py report

lock:
	$(VENV_PYTHON) -m piptools compile --resolver=backtracking --strip-extras --output-file=requirements.lock requirements.in
	$(VENV_PYTHON) -m piptools compile --resolver=backtracking --strip-extras --allow-unsafe --output-file=requirements-dev.lock requirements-dev.in
