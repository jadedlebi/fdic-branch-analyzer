.PHONY: help install test clean build deploy

help: ## Show this help message
	@echo "FDIC Branch Analyzer - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install the package in development mode
	pip install -e .

install-deps: ## Install dependencies only
	pip install -r requirements.txt

test: ## Run all tests
	python -m pytest tests/ -v

test-quick: ## Run quick tests
	python tests/test_setup.py
	python tests/test_claude_integration.py

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -delete
	find . -name "*.pyc" -delete

build: clean ## Build the package
	python setup.py sdist bdist_wheel

deploy: build ## Deploy to PyPI (requires credentials)
	twine upload dist/*

format: ## Format code with black
	black src/ tests/

lint: ## Lint code with flake8
	flake8 src/ tests/

check: format lint test ## Run all checks

demo: ## Run a quick demo
	python main.py

docs: ## Build documentation
	@echo "Documentation is in README.md and docs/ directory"

setup-dev: install-deps install ## Setup development environment
	@echo "Development environment ready!"

setup-user: ## Setup for end users
	@echo "For end users, run: ./install.sh (Linux/Mac) or install.bat (Windows)" 