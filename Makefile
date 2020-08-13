SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
MAKEFLAGS += --warn-undefined-variables --no-builtin-rules

PACKAGE=az_audit

.PHONY: help

.DEFAULT_GOAL := help

help:
	@grep -E '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) |\
		 awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m\
		 %s\n", $$1, $$2}'

################
# Installation #
################

.PHONY: install develop

install: ## Install for the current user using the default python command
	python -m pip install -r requirements.txt
	python setup.py install --user

develop: ## Install in editable mode using pip for development
	python -m pip install -r requirements.txt
	python -m pip install -e .

################
# Distribution #
################

.PHONY: dist

dist: ## Make Python source distribution
	python setup.py sdist

###########
# Testing #
###########

.PHONY: test cov-report

test: ## Run test suite and generage coverage.py html
	python -m coverage run -m pytest -vvv && coverage html

cov-report: ## View coverage.py html report in a browser window
	open htmlcov/index.html

############
# Clean up #
############

.PHONY: clean

clean:  ## Clean build dist and egg directories after install
	rm .coverage
	rm -rf ./dist
	rm -rf ./build
	rm -rf ./$(PACKAGE).egg-info
	find . -type f -iname '*.pyc' -delete
	find . -type f -iname '*.html' -delete
	find . -type f -iname '*.js' -delete
	find . -type f -iname '*.png' -delete
	find . -type f -iname '*.css' -delete
	find . -type f -iname '*.json' -delete
	find . -type d -name '__pycache__' -empty -delete
	find . -type d -name '.pytest_cache' -empty -delete
	find . -type d -name 'htmlcov' -empty -delete
