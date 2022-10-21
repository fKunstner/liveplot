.PHONY: help
.PHONY: install install-dev
.PHONY: test
.PHONY: format format-check
.PHONY: docs

.DEFAULT: help
help:
	@echo "test           Run pytest"
	@echo "format         Run formatting tools"
	@echo "lint           Run linters and formatting tools (no edits)"
	@echo "docs           Build the docs"

test:
	@pytest -vx tests --cov-report html:cov_html

format:
	@echo "Isort"
	@isort src
	@echo "Black"
	@black src

lint:
	@echo "Isort"
	@isort src --check
	@echo "Black"
	@black src --check
	@echo "Pylint"
	@pylint src
	@echo "PyDocStyle"
	@pydocstyle --count src
	@echo "Darglint"
	@darglint --verbosity 2 src

docs:
	@cd docs_src && make html