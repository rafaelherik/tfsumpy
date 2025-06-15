# Reporters API Reference

## Overview

Reporters in **tfsumpy** are responsible for formatting and displaying the results of plan analysis. Each reporter implements a specific output format (e.g., CLI, Markdown, JSON). The primary built-in reporter is the `PlanReporter`, which provides multiple output formats for Terraform plan summaries.

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

The `PlanReporter` is the default reporter for plan summaries. It supports three output formats:
- Console output (default)
- Markdown output (template-based)
- JSON output (structured)

**Example usage:**

```python
from tfsumpy.plan.reporter import PlanReporter

reporter = PlanReporter()

# Console output
reporter.print_report(plan_results, show_changes=True)

# Markdown output
reporter.print_report_markdown(plan_results, show_changes=True)

# JSON output
reporter.print_report_json(plan_results, show_changes=True)
```

**Parameters:**
- `data`: The analysis results (from `PlanAnalyzer`)
- `show_changes`: Show detailed attribute changes (bool)
- `show_details`: Show full resource details (bool)

**Output Formats:**

1. Console Output:
   - Color-coded text
   - Human-readable format
   - Interactive terminal display

2. Markdown Output:
   - Template-based formatting
   - Summary statistics
   - Resource changes
   - Detailed information (if enabled)
   - Timestamp and metadata

3. JSON Output:
   - Structured data format
   - Metadata (timestamp, version)
   - Summary statistics
   - Resource changes
   - Detailed information (if enabled)
   - Analysis results (if available)

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
- The `PlanReporter` supports three output formats: console, markdown, and JSON.
- You can direct output to a file or stream by passing a custom `output` to `BaseReporter`.
- Markdown output uses Jinja2 templates for consistent formatting.
- JSON output provides a structured format suitable for integration with other tools.
- See the [Models API](models.md) for details on the data structures passed to reporters.
