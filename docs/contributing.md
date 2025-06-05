# Contributing to tfsumpy

## Getting Started

1. Fork the repository
2. Clone your fork:
```bash
git clone https://github.com/your-username/tfsumpy.git
```

3. Set up development environment:
```bash
cd tfsumpy
pip install -e ".[dev]"
```

## Development Process

### Creating a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### Running Tests

```bash
pytest
```

### Running Linting

```bash
pylint tfsumpy
mypy tfsumpy
```

### Making Changes

1. Write tests for your changes
2. Implement your changes
3. Ensure all tests pass
4. Update documentation if needed

### Committing Changes

```bash
git add .
git commit -m "Description of your changes"
git push origin feature/your-feature-name
```

## Pull Request Process

1. Update the README.md with details of changes if needed
2. Update the documentation if needed
3. Ensure all tests pass
4. Create a Pull Request with a clear description of changes

## Code Style

- Follow PEP 8 guidelines
- Use type hints
- Write docstrings for all public methods
- Keep functions focused and small

## Testing

- Write unit tests for new functionality
- Maintain test coverage above 80%
- Include integration tests where appropriate

## Documentation

- Update documentation for new features
- Include docstrings in code
- Update example usage in README.md
- Add type hints to function signatures 