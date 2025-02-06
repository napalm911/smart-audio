.PHONY: install run lint test

install:
	poetry install

run:
	poetry run python -m main

lint:
	poetry run flake8 main

test:
	poetry run pytest -v
