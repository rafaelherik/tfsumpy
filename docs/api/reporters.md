# Reporters API Reference

## Overview

Reporters in **tfsumpy** are responsible for formatting and displaying the results of plan analysis. Each reporter implements a specific output format (e.g., CLI, Markdown, JSON). The primary built-in reporter is the `PlanReporter`, which provides human-friendly and Markdown output for Terraform plan summaries.

---

## Base Reporter Interface

All reporters must implement the `ReporterInterface`:

```python
from abc import ABC, abstractmethod

class ReporterInterface(ABC):
    @property
    @abstractmethod
    def category(self) -> str:
        """Return the reporter category (e.g., 'plan')."""
        pass

    @abstractmethod
    def print_report(self, data: Any, **kwargs) -> None:
        """
        Format and print the analysis results.

        Args:
            data: The analysis results (typically a dict)
            **kwargs: Additional display options (e.g., show_changes, show_details)
        """
        pass
```

---

## PlanReporter

The `PlanReporter` is the default reporter for plan summaries. It supports both colorized CLI output and Markdown output for sharing or documentation.

**Example usage:**

```python
from tfsumpy.plan.reporter import PlanReporter

reporter = PlanReporter()
reporter.print_report(plan_results, show_changes=True)
reporter.print_report_markdown(plan_results, show_changes=True)
```

**Parameters:**
- `data`: The analysis results (from `PlanAnalyzer`)
- `show_changes`: Show detailed attribute changes (bool)
- `show_details`: Show full resource details (bool)

**Output:**
- Prints formatted summary to stdout (or to a file/stream if specified)
- Markdown output is suitable for PRs, documentation, or compliance

---

## Extending: Custom Reporters

You can create your own reporter by subclassing `ReporterInterface` (optionally inheriting from `BaseReporter` for convenience):

```python
from tfsumpy.reporter import ReporterInterface
from tfsumpy.reporters.base_reporter import BaseReporter

class MyCustomReporter(BaseReporter, ReporterInterface):
    @property
    def category(self) -> str:
        return "custom"

    def print_report(self, data: Any, **kwargs) -> None:
        # Custom formatting logic here
        self._write("My Custom Report\n")
        self._write("=================\n")
        # ...
```

Register your custom reporter with the tfsumpy `Context` to use it in your workflow.

---

## Notes
- The `PlanReporter` supports both CLI and Markdown output.
- You can direct output to a file or stream by passing a custom `output` to `BaseReporter`.
- See the [Models API](models.md) for details on the data structures passed to reporters.
