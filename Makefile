.PHONY: install run test lint format clean bump-major bump-minor bump-patch tdd test-watch

install:
	pip install -e .

run:
	uv run app.py

test:
	pytest --cov=hillbot --cov-report term-missing --cov-report html

test-watch:
	watchmedo shell-command --patterns="*.py" --recursive --command='clear && make test' hillbot/

tdd:
	watchmedo shell-command --patterns="*.py" --recursive --command='clear && make test' hillbot/

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

bump-major:
	bump-my-version bump major

bump-minor:
	bump-my-version bump minor

bump-patch:
	bump-my-version bump patch
