.PHONY: help
.PHONY: install install-dev
.PHONY: test
.PHONY: format format-check
.PHONY: docs

.DEFAULT: help
help:
	@echo "test           Run pytest"
	@echo "format         Run formatting tools"
	@echo "check          Run style and type checkers (no edits)"
	@echo "lint           Run pylint"

test:
	@pytest -vx tests --cov-report html:cov_html

format:
	@echo "Isort"
	@isort src
	@isort tests
	@echo "Black"
	@black src
	@black tests

check:
	@echo "Isort"
	@isort src --check
	@echo "Black"
	@black src --check
	@echo "mypy"
	@mypy src
	@mypy tests

lint:
	@echo "Pylint"
	@pylint src
