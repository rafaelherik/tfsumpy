.PHONY: help install dev-install clean build test lint check release run-sample debug-sample venv

VERSION ?= $(error Please set VERSION variable to create a release: make release VERSION=0.1.0)
VENV = .venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip

help:
	@echo "Available commands:"
	@echo "  make venv         - Create virtual environment"
	@echo "  make install      - Install package in production mode"
	@echo "  make dev-install  - Install package in development mode with test dependencies"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linting checks"
	@echo "  make check        - Run all checks (lint + test)"
	@echo "  make clean        - Remove build artifacts"
	@echo "  make build        - Build the package"
	@echo "  make release      - Create a new release (requires VERSION=X.Y.Z)"
	@echo "  make run-sample   - Run bolwerk with sample1.json plan file"
	@echo "  make debug-sample - Run bolwerk with sample1.json plan file and custom config"

# Virtual environment
venv:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip

# Installation targets
install: venv
	$(PIP) install .

dev-install: venv
	$(PIP) install -e ".[dev]"
	$(PIP) install pytest pylint mypy

# Development commands
test: dev-install
	$(PYTHON) -m pytest tests/



lint: dev-install
	$(PYTHON) -m pylint bolwerk
	$(PYTHON) -m mypy bolwerk

check: lint test

# Build commands
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	$(PYTHON) -m build

# Sample commands
run-sample: install
	$(PYTHON) -m bolwerk samples/sample1.json --details --changes

debug-sample: install
	$(PYTHON) -m bolwerk samples/sample1.json --debug --config bolwerk/rules_config.json

# Release command (unchanged)
release: 
	@echo "Creating release for version $(VERSION)"
	@# Update version in __init__.py (works on both Linux and macOS)
	@sed -i.bak "s/__version__ = .*/__version__ = '$(VERSION)'/" bolwerk/__init__.py && rm -f bolwerk/__init__.py.bak
	@# Update version in setup.py if it exists
	@if grep -q "version=" setup.py; then \
		sed -i.bak "s/version=.*/version='$(VERSION)',/" setup.py && rm -f setup.py.bak; \
	fi
	@# Commit changes
	git add bolwerk/__init__.py setup.py
	git commit -m "Bump version to $(VERSION)"
	@# Create and push tag
	git tag -a v$(VERSION) -m "Release version $(VERSION)" --force
	git push origin main
	git push origin v$(VERSION)
	@echo "Release v$(VERSION) created and pushed. GitHub Actions will handle the rest."