.PHONY: lint

lint:
	pipenv run ruff format .
	pipenv run ruff check --fix
