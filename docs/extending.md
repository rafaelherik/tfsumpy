# Extending tfsumpy

This guide explains how to extend tfsumpy with custom analyzers and reporters.

## Plugin System

tfsumpy uses a plugin system that allows you to add custom analyzers and reporters. Plugins are Python files placed in a `plugins/` directory (or a custom directory specified with `--plugin-dir`).

## Creating Custom Analyzers

Analyzers process Terraform plan data and produce analysis results. Here's how to create a custom analyzer:

```python
from tfsumpy.analyzer import AnalyzerInterface, AnalyzerResult, AnalyzerCategory

class MyAnalyzer(AnalyzerInterface):
    @property
    def category(self) -> AnalyzerCategory:
        return AnalyzerCategory.PLAN  # or your custom category
    
    def analyze(self, context, **kwargs) -> AnalyzerResult:
        # Your analysis logic here
        return AnalyzerResult(
            category=self.category,
            data={"result": "analysis"}
        )

def register(context):
    context.register_analyzer(MyAnalyzer())
```

### Example: Cost Analyzer

```python
from tfsumpy.analyzer import AnalyzerInterface, AnalyzerResult, AnalyzerCategory

class CostAnalyzer(AnalyzerInterface):
    @property
    def category(self) -> AnalyzerCategory:
        return AnalyzerCategory.COST
    
    def analyze(self, context, **kwargs) -> AnalyzerResult:
        plan_data = context.get_plan_data()
        # Calculate costs based on plan data
        cost_summary = {
            "total_cost": 123.45,
            "resources": {
                "aws_instance": 100.00,
                "aws_s3_bucket": 23.45
            }
        }
        return AnalyzerResult(
            category=self.category,
            data=cost_summary
        )

def register(context):
    context.register_analyzer(CostAnalyzer())
```

## Creating Custom Reporters

Reporters format and output analysis results. Here's how to create a custom reporter:

```python
from tfsumpy.reporter import ReporterInterface
from tfsumpy.analyzer import AnalyzerCategory

class MyReporter(ReporterInterface):
    @property
    def category(self) -> AnalyzerCategory:
        return AnalyzerCategory.PLAN  # or your custom category
    
    def print_report(self, data, **kwargs):
        # Your reporting logic here
        print(f"Custom Report: {data}")

def register(context):
    context.register_reporter(MyReporter())
```

### Example: Slack Reporter

```python
from tfsumpy.reporter import ReporterInterface
from tfsumpy.analyzer import AnalyzerCategory

class SlackReporter(ReporterInterface):
    @property
    def category(self) -> AnalyzerCategory:
        return AnalyzerCategory.PLAN
    
    def print_report(self, data, **kwargs):
        # Format message for Slack
        message = f"*Terraform Plan Summary*\n"
        message += f"Total Changes: {data['total_changes']}\n"
        message += f"Create: {data['create']}\n"
        message += f"Update: {data['update']}\n"
        message += f"Delete: {data['delete']}"
        
        # Send to Slack (implement your Slack integration)
        send_to_slack(message)

def register(context):
    context.register_reporter(SlackReporter())
```

## Using Your Plugins

1. Create a directory for your plugins:
```bash
mkdir my_plugins
```

2. Create your plugin file:
```bash
touch my_plugins/my_analyzer.py
```

3. Add your analyzer/reporter code to the file

4. Use your plugins:
```bash
tfsumpy plan.json --plugin-dir my_plugins/
```

## Best Practices

1. **Error Handling**: Always handle potential errors in your analyzers and reporters
2. **Logging**: Use the context's logger for consistent logging
3. **Configuration**: Use the context's configuration for customizable behavior
4. **Testing**: Write tests for your plugins
5. **Documentation**: Document your plugin's functionality and requirements

## API Reference

- [Analyzers API](api/analyzers.md): Detailed analyzer interface documentation
- [Reporters API](api/reporters.md): Detailed reporter interface documentation
- [Models API](api/models.md): Data structures and types 