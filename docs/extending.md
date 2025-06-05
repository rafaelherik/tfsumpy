# Extending tfsumpy

## Overview

tfsumpy is designed to be extensible. You can add your own analyzers (to interpret Terraform plans in new ways) and reporters (to output results in custom formats or destinations). This page shows how to build and register your own extensions.

---

## Custom Analyzers

A custom analyzer lets you add new types of analysis to your Terraform plans. For example, you might want to:
- Estimate costs
- Enforce custom compliance rules
- Detect drift or other organization-specific patterns

### Example: Cost Estimation Analyzer

```python
from tfsumpy.analyzer import AnalyzerInterface, AnalyzerResult

class CostAnalyzer(AnalyzerInterface):
    @property
    def category(self) -> str:
        return "cost"

    def analyze(self, context, **kwargs) -> AnalyzerResult:
        # Your custom cost analysis logic here
        cost_summary = {"total_cost": 123.45}
        return AnalyzerResult(category="cost", data=cost_summary)
```

**Register your analyzer:**
```python
context.register_analyzer(CostAnalyzer())
```

---

## Custom Reporters

A custom reporter lets you control how results are displayed or sent elsewhere. For example, you might want to:
- Send results to Slack or email
- Output as HTML, JSON, or other formats
- Integrate with dashboards or ticketing systems

### Example: Slack Reporter

```python
from tfsumpy.reporter import ReporterInterface

def send_to_slack(message):
    # Implement your Slack integration here
    pass

class SlackReporter(ReporterInterface):
    @property
    def category(self) -> str:
        return "plan"  # or "cost" for your custom analyzer

    def print_report(self, data, **kwargs):
        # Format and send a message to Slack
        message = f"Terraform Plan Summary: {data['total_changes']} changes"
        send_to_slack(message)
```

**Register your reporter:**
```python
context.register_reporter(SlackReporter())
```

---

## Using Your Extensions

Once registered, your custom analyzers and reporters are used by the tfsumpy `Context` just like the built-in ones:

```python
context = Context()
context.register_analyzer(CostAnalyzer())
context.register_reporter(SlackReporter())

# Run your custom analysis
results = context.run_analyzers("cost", plan_path="plan.json")
context.run_reports("cost", results[0].data)
```

---

## Tips
- You can register multiple analyzers and reporters for the same category.
- Use the `category` property to control which analyzers/reporters are triggered for each type of analysis.
- See the [API Reference](api/analyzers.md) and [API Reference: Reporters](api/reporters.md) for more details.

---

## Need More?
If you have a use case not covered here, open an issue or contribute your extension to the project!

---

## Plugin System (Plug & Play)

tfsumpy supports plug-and-play extensions via plugins. Plugins are Python files placed in a `plugins/` directory (or a custom directory specified with `--plugin-dir`).

- Each plugin should define a `register(context)` function that registers analyzers/reporters.
- tfsumpy will automatically load and register all plugins in the directory at startup.

### Example Plugin

Create a file `plugins/my_cost_plugin.py`:

```python
from tfsumpy.analyzer import AnalyzerInterface, AnalyzerResult

class MyCostAnalyzer(AnalyzerInterface):
    @property
    def category(self):
        return "cost"
    def analyze(self, context, **kwargs):
        return AnalyzerResult(category="cost", data={"total_cost": 42})

def register(context):
    context.register_analyzer(MyCostAnalyzer())
```

### Using Plugins

- By default, tfsumpy loads plugins from the `plugins/` directory in your project.
- You can specify a different directory with the `--plugin-dir` CLI flag:

```bash
tfsumpy plan.json --plugin-dir my_plugins/
```

All plugins in the directory will be loaded and their analyzers/reporters registered automatically. 