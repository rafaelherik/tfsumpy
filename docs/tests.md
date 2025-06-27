# Adding and Updating Tests

New to pytest? Start here:

- [Official Quick Start (5-min read)](https://docs.pytest.org/en/stable/getting-started.html) – concise intro, test discovery rules, and basic assertions
- [Real Python “Getting Started With pytest”](https://realpython.com/pytest-python-testing/) – longer, example-driven walkthrough

## Project guidelines

1. Location & naming

- Put tests in the tests/ directory, mirroring the package layout.
- Filenames should start with test*, and test functions/classes with test*…, so pytest will auto-discover them.

2. Keep them simple

- Prefer plain assert statements—pytest rewrites them to show expressive failure messages.
- One logical assertion per test is ideal; use multiple tests rather than many asserts in one function.

3. Re-use set-up code with fixtures

- Place shared fixtures in conftest.py at the project root or the relevant sub-directory.
- Example:

```python
import pytest
from tfsumpy import SomeClass

@pytest.fixture
def sample_instance():
    return SomeClass(param="value")
```

4. Parametrize when inputs vary

```python
@pytest.mark.parametrize("raw,expected", [(1, "1"), (None, "")])
def test_coerce_to_str(raw, expected):
    assert utils.coerce_to_str(raw) == expected
```

5. Measure coverage locally

`task test` runs `pytest --cov=tfsumpy …`. Aim to increase the coverage number or at least keep it above 80 %.

6. Writing new tests

- Start by reproducing the current behaviour (red).
- Implement or fix code (green).
- Refactor while tests stay green (TDD cycle).

7. Run only what you need while developing:

```bash
# Single test file
pytest tests/test_utils.py

# Filter by keyword
pytest -k "coerce and str"
```
