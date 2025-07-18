# tfsumpy - Terraform Plan Summary Tool

![image](https://github.com/user-attachments/assets/d6e451e9-21db-487a-b15b-6d245e5a50bf)



[![CI](https://github.com/rafaelherik/tfsumpy/actions/workflows/ci.yaml/badge.svg)](https://github.com/rafaelherik/tfsumpy/actions/workflows/ci.yaml)
[![PyPI](https://img.shields.io/pypi/v/tfsumpy.svg)](https://pypi.org/project/tfsumpy/)

tfsumpy is a Python-based tool that summarizes Terraform plan files to provide a clear overview of infrastructure changes. It helps DevOps teams review infrastructure changes more effectively by providing detailed plan summaries in different formats.

[![Discord](https://img.shields.io/discord/1387715085878820937?color=7289da&label=Discord&logo=discord&logoColor=white)](https://discord.gg/9mw8nXyr)

## Features

- 🔍 Detailed plan analysis with change breakdown
- 📊 Multiple output formats (default, markdown, JSON)
- 🔒 Automatic sensitive information redaction
- 🎨 Color-coded output for better readability
- 🔄 Detailed attribute change tracking
- 📝 Template-based markdown output
- 🔧 Extensible plugin system

## Installation

Install using pip:
```bash
    pip install tfsumpy
```
Or install from source:
```bash
    git clone https://github.com/rafaelherik/tfsumpy.git
    cd tfsumpy
    pip install .
```

## Usage

### Basic Usage

1. Generate a Terraform plan JSON file:
```bash
    terraform plan -out=tfplan
    terraform show -json tfplan > plan.json
```

2. Analyze the plan:

Basic summary:
```bash
    tfsumpy plan.json
```

Show detailed changes:
```bash
    tfsumpy plan.json --hide-changes=false
```

Show resource details:
```bash
    tfsumpy plan.json --detailed
```

### Output Formats

tfsumpy supports three output formats:

1. Default (console output):
```bash
    tfsumpy plan.json
```

2. Markdown:
```bash
    tfsumpy plan.json --output markdown
```

3. JSON:
```bash
    tfsumpy plan.json --output json
```

### Example Outputs

#### Default Output
```
Terraform Plan Analysis
======================
Total Changes: 3
Create: 1
Update: 1
Delete: 1

Resource Changes:
CREATE aws_s3_bucket: data_bucket
  + bucket = "new-bucket"

UPDATE aws_instance: web_server
  ~ instance_type = t2.micro -> t2.small

DELETE aws_security_group: old_sg
  - name = "old-sg"
```

#### Markdown Output
```markdown
# Terraform Plan Analysis Report

## Summary
- **Total Resources**: 3
- **Resources to Add**: 1
- **Resources to Change**: 1
- **Resources to Destroy**: 1

## Resource Changes
### aws_s3_bucket.data_bucket
#### Changes:
- **bucket**: null → "new-bucket"

### aws_instance.web_server
#### Changes:
- **instance_type**: "t2.micro" → "t2.small"

### aws_security_group.old_sg
#### Changes:
- **name**: "old-sg" → null

---
*Generated by tfsumpy on 2024-03-14 15:30:45*
```

#### JSON Output
```json
{
  "metadata": {
    "timestamp": "2024-03-14T15:30:45.123456",
    "version": "1.0",
    "format": "json"
  },
  "summary": {
    "total_resources": 3,
    "resources_to_add": 1,
    "resources_to_change": 1,
    "resources_to_destroy": 1
  },
  "resources": [
    {
      "type": "aws_s3_bucket",
      "name": "data_bucket",
      "action": "create",
      "provider": "aws",
      "module": "root",
      "changes": [
        {
          "attribute": "bucket",
          "before": null,
          "after": "new-bucket"
        }
      ]
    }
  ]
}
```

### Deprecated Arguments

The following arguments are deprecated and will be removed in a future version:

- `--changes` → Use `--hide-changes=false` instead
- `--details` → Use `--detailed` instead
- `--markdown` → Use `--output markdown` instead

### Configuration

Create a custom configuration file (config.json):

```json
{
  "sensitive_patterns": [
    {
      "pattern": "\\b(?:password|secret|key)\\b",
      "replacement": "[REDACTED]"
    }
  ],
  "risk_rules": {
    "high": [
      {
        "pattern": "\\bdelete\\b.*\\b(database|storage)\\b",
        "message": "Critical resource deletion"
      }
    ]
  }
}
```

Use the configuration:

```bash
tfsumpy plan.json --config config.json
```

### Debug Mode

For troubleshooting or detailed logging:

```bash
tfsumpy plan.json --debug
```

This will:
- Enable verbose logging
- Show detailed error messages
- Display analysis process information

## Requirements

- Python 3.10 or higher
- Terraform 1.0 or higher

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please make sure to update tests as appropriate.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Project Status

**Status:** Beta

## Developer Workflow with Taskfile

This project uses [Taskfile](https://taskfile.dev) to simplify common development tasks.

### Install Task

On macOS (with Homebrew):
```bash
brew install go-task/tap/go-task
```
On Linux:
```bash
sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d
```

### Common Commands

- Run all tests:
  ```bash
  task test
  ```
- Build the package:
  ```bash
  task build
  ```
- Run linting:
  ```bash
  task lint
  ```
- Install all dependencies:
  ```bash
  task install
  ```

See all available tasks:
```bash
task --list
```

## 🧩 Extending tfsumpy (Plugins)

tfsumpy supports plug-and-play extensions! You can add your own analyzers or reporters by dropping Python files in a `plugins/` directory (or specify a custom directory with `--plugin-dir`).

- Each plugin should define a `register(context)` function that registers analyzers/reporters.
- tfsumpy will automatically load and register all plugins in the directory at startup.

**Example plugin:**
```python
from tfsumpy.analyzer import AnalyzerInterface, AnalyzerResult
class MyCostAnalyzer(AnalyzerInterface):
    @property
    def category(self): return "cost"
    def analyze(self, context, **kwargs):
        return AnalyzerResult(category="cost", data={"total_cost": 42})
def register(context):
    context.register_analyzer(MyCostAnalyzer())
```

**Usage:**
```bash
tfsumpy plan.json --plugin-dir my_plugins/
```

See [Extending tfsumpy](docs/extending.md) for more details and advanced examples.
