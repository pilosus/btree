.DEFAULT_GOAL := all
.PHONY: format lint types all

format:
	@echo "Run code formatters"
	uv run ruff format

lint:
	@echo "Run linters"
	uv run ruff check

types:
	@echo "Run type checkers"
	uv run mypy src/

all: format lint types
