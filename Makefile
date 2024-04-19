test-local:
	poetry run coverage run -m pytest -x tests/ && coverage report -m

