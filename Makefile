## Delete all compiled Python files
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

## Lint using flake8
lint:
	flake8 stonks/

help:
	@echo "lint - calls flake8 linting"
	@echo "clean - deletes python compiled binaries"