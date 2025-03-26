.PHONY: install run test lint format clean

install:
	pip install -e .

run:
	uv run app.py

test:
	pip install -e .[dev]
	pytest --cov=hillbot

lint:
	flake8 hillbot/
	isort hillbot/ --check
	black hillbot/ --check

format:
	isort hillbot/
	black hillbot/

clean:
	rm -rf __pycache__
	rm -rf hillbot.egg-info
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
