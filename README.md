# tfsumpy - Terraform Plan Summary Tool

[![CI](https://github.com/rafaelherik/tfsumpy/actions/workflows/ci.yaml/badge.svg)](https://github.com/rafaelherik/tfsumpy/actions/workflows/ci.yaml)
[![PyPI](https://img.shields.io/pypi/v/tfsumpy.svg)](https://pypi.org/project/tfsumpy/)

tfsumpy is a Python-based tool that summarizes Terraform plan files to provide a clear overview of infrastructure changes. It helps DevOps teams review infrastructure changes more effectively by providing detailed plan summaries in different formats.

## Features

- 🔍 Detailed plan analysis with change breakdown
- 📊 Multiple output formats (default, markdown, JSON)
- 🔒 Automatic sensitive information redaction
- 🎨 Color-coded output for better readability
- 🔄 Detailed attribute change tracking
- ♻️ Replacement detection: flags resources being recreated and shows enforcing attributes
- 📝 Template-based markdown output
- 🔧 Extensible plugin system
- 🤖 AI-powered change summarization (OpenAI, Gemini, Anthropic)

## Installation

```bash
pip install tfsumpy
```

## Quick Start

1. Generate a Terraform plan JSON file:
```bash
terraform plan -out=tfplan
terraform show -json tfplan > plan.json
```

2. Analyze the plan:
```bash
# Basic summary
tfsumpy plan.json

# Hide attribute changes (optional)
tfsumpy plan.json --hide-changes

# Show detailed resource information (with attribute changes)
tfsumpy plan.json --detailed
```

## Output Formats

```bash
# Default console output
tfsumpy plan.json

# Markdown output
tfsumpy plan.json --output markdown

# JSON output
tfsumpy plan.json --output json
```

## AI Summarization

Enable AI-powered change summarization using OpenAI:

```bash
# Using OpenAI
tfsumpy plan.json --output markdown --ai openai YOUR_API_KEY

```

## Configuration

Create a `config.json` file to customize behavior:

```json
{
  "sensitive_patterns": [
    {
      "pattern": "\\b(?:password|secret|key)\\b",
      "replacement": "[REDACTED]"
    }
  ]
}
```

Use the configuration:
```bash
tfsumpy plan.json --config config.json
```

## Extending tfsumpy

tfsumpy supports plugins for custom analyzers and reporters. Create a Python file in the `plugins/` directory:

```python
from tfsumpy.analyzer import AnalyzerInterface, AnalyzerResult

class MyAnalyzer(AnalyzerInterface):
    @property
    def category(self):
        return "custom"
    
    def analyze(self, context, **kwargs):
        return AnalyzerResult(
            category="custom",
            data={"result": "analysis"}
        )

def register(context):
    context.register_analyzer(MyAnalyzer())
```

Load custom plugins:
```bash
tfsumpy plan.json --plugin-dir my_plugins/
```

## Development

This project uses [Taskfile](https://taskfile.dev) for development tasks:

```bash
# Install dependencies
task install

# Run tests
task test

# Run linting
task lint
```

## Documentation

For detailed documentation, visit our [documentation site](https://tfsumpy.readthedocs.io/).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
