.PHONY: help test clean build release

VERSION ?= $(error Please set VERSION variable to create a release: make release VERSION=0.1.0)

help:
	@echo "Available commands:"
	@echo "  make test      - Run tests"
	@echo "  make clean     - Remove build artifacts"
	@echo "  make build     - Build the package"
	@echo "  make release   - Create a new release (requires VERSION=X.Y.Z)"

test:
	pytest

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

release: test clean
	@echo "Creating release for version $(VERSION)"
	@# Update version in __init__.py (works on both Linux and macOS)
	@sed -i.bak "s/__version__ = .*/__version__ = '$(VERSION)'/" tfsumpy/__init__.py && rm -f tfsumpy/__init__.py.bak
	@# Update version in setup.py if it exists
	@if grep -q "version=" setup.py; then \
		sed -i.bak "s/version=.*/version='$(VERSION)',/" setup.py && rm -f setup.py.bak; \
	fi
	@# Commit changes
	git add tfsumpy/__init__.py setup.py
	git commit -m "Bump version to $(VERSION)"
	@# Create and push tag
	git tag -a v$(VERSION) -m "Release version $(VERSION)"
	git push origin main
	git push origin v$(VERSION)
	@echo "Release v$(VERSION) created and pushed. GitHub Actions will handle the rest."