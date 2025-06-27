# Contributing Guidelines

## Code Style

- Follow [PEP 8 guidelines](https://peps.python.org/pep-0008/)
- Use [type hints](https://docs.python.org/3/library/typing.html) for better code clarity and IDE support
- Write docstrings for all public methods following [PEP 257](https://peps.python.org/pep-0257/) conventions
- Keep functions focused and small

## Documentation

- Update documentation for new features
- Include [docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) in code (Google style preferred)
- Update example usage in README.md
- Add type hints to function signatures

## Making Changes

1. Review [open issues](https://github.com/rafaelherik/tfsumpy/issues) and [pull requests](https://github.com/rafaelherik/tfsumpy/pulls) to see if there is any related work that's already in progress
2. Get or update your own copy of the project to work with
3. Write new and/or update existing tests for your changes
4. Develop and implement your changes
5. Commit your changes in small, useful chunks
6. Ensure all tests pass
7. Update documentation as needed
8. Push your changes to your fork
9. Create a Pull Request

## Getting Started

1. Fork the repository
2. Clone your fork:

    ```bash
    git clone https://github.com/your-username/tfsumpy.git
    ```

3. Set up development environment:

    This project uses [Task](https://taskfile.dev/) to run set up, and run linting, and testing tasks consistently with how they are run in CI. Start by making sure you have [Task](https://taskfile.dev/) installed.

    Running the `task install` command will create a local virtual environment, install dev requirements and then execute the individual tools.  Running these commands in the [Taskfile](Taskfile.yml) guarantees that everyone, including CI workflows, uses the same versions and settings.

    ```bash
    task install
    ```

## Development Process

### Creating a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### Testing

- **Unit Tests**: Required for all new features and bug fixes
  - Follow our [Testing Guide](tests.md) for best practices
  - Use [pytest](https://docs.pytest.org/)-style tests with `assert` statements
  - Maintain test coverage above 80%
  - Run tests with `task test` (executes `pytest` with coverage)

- **Test-Driven Development (TDD)**:
  - Write tests first, then implementation
  - Follow the [TDD workflow](https://realpython.com/test-driven-development-python/)
  - Keep tests focused and fast

- **Test Types**:
  - Unit tests for individual functions/classes
  - Integration tests for component interactions
  - See [Testing Guide](tests.md) for detailed patterns

### Linting

Linting and static analysis are automated in GitHub Actions. To help you get an approval for your pull request, you'll need to have all Actions workflow checks pass. To run the same tools locally you can use the [Taskfile](Taskfile.yml) to achieve the same results. First make sure you have the [Task](https://taskfile.dev/) runner [installed](https://taskfile.dev/#/installation).

```bash
cd tfsumpy
# Run ruff, mypy and bandit (fails on any issues)
task lint

# Optionally, auto-fix style issues detected by ruff
task lint-fix
```

The Taskfile will create a local virtual environment if needed, install all dev requirements and then execute the individual tools.  Running the tasks guarantees that everyone uses the same versions and settings.

### Running Tests

Automated tests run in GitHub Actions. To help you get an approval for your pull request, you'll need to have all Actions workflow checks pass. To run the same tests locally you can use the [Taskfile](Taskfile.yml) to achieve the same results. First make sure you have the [Task](https://taskfile.dev/) runner [installed](https://taskfile.dev/#/installation).

```bash
# Run pytest with coverage threshold enforcement (mirrors CI)
task test
```

This task sets up the virtual-env if necessary, installs all dev dependencies, then executes

```bash
pytest --cov=tfsumpy --cov-report=term && coverage report --fail-under=80
```

so you get quick feedback on both test failures and coverage.

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
