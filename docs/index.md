# tfsumpy Documentation

Welcome to the tfsumpy documentation. This guide will help you understand how to use and extend tfsumpy effectively.

## Quick Links

- [Getting Started](getting_started.md): Installation and basic usage
- [Features](features/): Core features and capabilities
- [API Reference](api/): Detailed API documentation
- [Extending](extending.md): Creating custom analyzers and reporters

## Core Features

- **Plan Analysis**: Detailed analysis of Terraform plan files
- **Multiple Output Formats**: Console, Markdown, and JSON output
- **Sensitive Data Protection**: Automatic redaction of sensitive values
- **AI Integration**: AI-powered change summarization
- **Plugin System**: Extensible architecture for custom analyzers and reporters

## Getting Started

For a complete guide to getting started with tfsumpy, including installation, basic usage, and common scenarios, see our [Getting Started Guide](getting_started.md).

### Basic Usage

1. Generate a Terraform plan JSON file:
```bash
terraform plan -out=tfplan
terraform show -json tfplan > plan.json
```

2. Analyze the plan:
```bash
tfsumpy plan.json
```

## Output Formats

### Console Output (Default)
```bash
tfsumpy plan.json
```

### Markdown Output
```bash
tfsumpy plan.json --output markdown
```

### JSON Output
```bash
tfsumpy plan.json --output json
```

## AI Integration

tfsumpy supports AI-powered change summarization using OpenAI, Gemini, and Anthropic. For detailed information about AI analysis features, see our [AI Analysis Guide](features/ai_analysis.md).

Basic usage:
```bash
# Using OpenAI
tfsumpy plan.json --output markdown --ai openai YOUR_API_KEY

# Using Google Gemini
tfsumpy plan.json --output markdown --ai gemini YOUR_API_KEY

# Using Anthropic Claude
tfsumpy plan.json --output markdown --ai anthropic YOUR_API_KEY
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

### Custom Analyzers

Create a Python file in the `plugins/` directory:

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

### Custom Reporters

```python
from tfsumpy.reporter import ReporterInterface

class MyReporter(ReporterInterface):
    @property
    def category(self):
        return "custom"
    
    def print_report(self, data, **kwargs):
        # Your custom reporting logic here
        pass

def register(context):
    context.register_reporter(MyReporter())
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

## API Reference

- [Analyzers API](api/analyzers.md): Extending with custom analyzers
- [Reporters API](api/reporters.md): Creating custom output formats
- [Models API](api/models.md): Data structures and types

## Contributing

We welcome contributions! See our [Contributing Guide](contributing.md) to get started.

## License

tfsumpy is released under the MIT License. See the [LICENSE](https://github.com/rafaelherik/tfsumpy/blob/main/LICENSE) file for details. 