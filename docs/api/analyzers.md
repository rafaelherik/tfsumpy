# Analyzers API Reference

## Overview

Analyzers in **tfsumpy** are responsible for processing and interpreting Terraform plan files. Each analyzer implements a specific type of analysis. The primary built-in analyzer is the `PlanAnalyzer`, which summarizes resource changes in a Terraform plan.

---

## Base Analyzer Interface

All analyzers must implement the `AnalyzerInterface`:

```python
from abc import ABC, abstractmethod
from tfsumpy.analyzer import AnalyzerResult

class AnalyzerInterface(ABC):
    @property
    @abstractmethod
    def category(self) -> str:
        """Return the analyzer category (e.g., 'plan')."""
        pass

    @abstractmethod
    def analyze(self, context: 'Context', **kwargs) -> AnalyzerResult:
        """
        Perform analysis and return results.

        Args:
            context: The tfsumpy Context object
            **kwargs: Additional arguments (e.g., plan_path)
        Returns:
            AnalyzerResult: The result of the analysis
        """
        pass
```

---

## PlanAnalyzer

The `PlanAnalyzer` is the default analyzer for Terraform plan files. It parses the plan JSON and produces a summary of all resource changes.

**Example usage:**

```python
from tfsumpy.plan.analyzer import PlanAnalyzer
from tfsumpy.context import Context

context = Context()
plan_analyzer = PlanAnalyzer(context)
result = plan_analyzer.analyze(context, plan_path="plan.json")

print(result.data["total_changes"])
print(result.data["resources"])  # List of resource change dicts
```

**Parameters:**
- `context`: The tfsumpy Context object (handles config, redaction, etc.)
- `plan_path`: Path to the Terraform plan JSON file

**Returns:**
- `AnalyzerResult` with a summary of changes, including:
  - `total_changes`: int
  - `change_breakdown`: dict (create/update/delete counts)
  - `resources`: list of resource change dicts

---

## Extending: Custom Analyzers

You can create your own analyzer by subclassing `AnalyzerInterface`:

```python
from tfsumpy.analyzer import AnalyzerInterface, AnalyzerResult

class MyCustomAnalyzer(AnalyzerInterface):
    @property
    def category(self) -> str:
        return "custom"

    def analyze(self, context, **kwargs) -> AnalyzerResult:
        # Custom analysis logic here
        return AnalyzerResult(category="custom", data={"result": "ok"})
```

Register your custom analyzer with the tfsumpy `Context` to use it in your workflow.

---

## Notes
- All analyzers should return an `AnalyzerResult`.
- The `PlanAnalyzer` is the main entry point for plan file analysis.
- See the [Models API](models.md) for details on the data structures returned by analyzers.
