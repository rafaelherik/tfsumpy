# Getting Started with tfsumpy

This guide will help you get started with tfsumpy, from installation to basic usage.

## Prerequisites

- Python 3.9 or higher
- Terraform installed and configured
- Basic understanding of Terraform plans

## Installation

### Using Poetry (Recommended for Development)

1. Clone the repository:
```bash
git clone https://github.com/rafaelherik/tfsumpy.git
cd tfsumpy
```

2. Install dependencies:
```bash
poetry install
```

3. Activate the virtual environment:
```bash
poetry shell
```

### Using pip (For Production)

```bash
pip install tfsumpy
```

## Basic Usage

### 1. Generate a Terraform Plan

First, generate a Terraform plan in JSON format:

```bash
# Create a plan file
terraform plan -out=tfplan

# Convert to JSON
terraform show -json tfplan > plan.json
```

### 2. Analyze the Plan

Basic analysis:
```bash
tfsumpy plan.json
```

This will show:
- Total number of changes
- Resources to be created, modified, or destroyed
- Color-coded output for better readability

### 3. Output Formats

tfsumpy supports multiple output formats:

```bash
# Console output (default)
tfsumpy plan.json

# Markdown output
tfsumpy plan.json --output markdown

# JSON output
tfsumpy plan.json --output json
```

### 4. Detailed Analysis

Get more detailed information about changes:

```bash
# Show detailed changes
tfsumpy plan.json --detailed

# Show attribute changes
tfsumpy plan.json --hide-changes=false
```

## Configuration

### Configuration File

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

### Environment Variables

tfsumpy supports environment variables for configuration:

```bash
# Debug mode
export TFSUMPY_DEBUG=true

# AI provider keys
export TFSUMPY_OPENAI_API_KEY="your-key-here"
export TFSUMPY_GEMINI_API_KEY="your-key-here"
export TFSUMPY_ANTHROPIC_API_KEY="your-key-here"
```

### Configuration Precedence

1. Command-line arguments
2. Environment variables
3. Configuration file
4. Default values

## Understanding the Output

### Console Output

The console output uses color coding:
- 🟢 Green: Resources to be created
- 🟡 Yellow: Resources to be modified
- 🔴 Red: Resources to be destroyed

Example:
```
Terraform Plan Analysis
======================

Total Changes: 3
Resources to Add: 1 🟢
Resources to Change: 1 🟡
Resources to Destroy: 1 🔴

Resource Changes:
----------------
+ aws_s3_bucket.example (new)
  - bucket: "my-new-bucket"
  - region: "us-west-2"

~ aws_instance.web (modify)
  - instance_type: "t2.micro" → "t2.small"

- aws_security_group.old (destroy)
  - name: "old-sg"
```

### Markdown Output

The markdown output is suitable for documentation or pull requests:

```markdown
# Terraform Plan Analysis

## Summary
- Total Changes: 3
- Resources to Add: 1
- Resources to Change: 1
- Resources to Destroy: 1

## Resource Changes
...
```

### JSON Output

The JSON output is useful for integration with other tools:

```json
{
  "summary": {
    "total_changes": 3,
    "create": 1,
    "update": 1,
    "delete": 1
  },
  "resources": [...]
}
```

## Common Use Cases

### 1. Review Pull Requests

```bash
# Generate markdown report
tfsumpy plan.json --output markdown > plan_analysis.md

# Include in PR description
cat plan_analysis.md
```

### 2. Integration with CI/CD

```bash
# Check for destructive changes
tfsumpy plan.json --output json | jq '.summary.delete > 0'
```

### 3. Security Review

```bash
# Show detailed changes
tfsumpy plan.json --detailed --hide-changes=false
```

## Next Steps

- Learn about [AI Analysis](features/ai_analysis.md)
- Explore [Custom Analyzers](extending.md)
- Check out [Advanced Features](features/advanced.md) 