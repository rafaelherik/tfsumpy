# TFSumPy - Terraform Plan Analyzer

[![CI](https://github.com/rafaelherik/tfsumpy/actions/workflows/ci.yaml/badge.svg)](https://github.com/rafaelherik/tfsumpy/actions/workflows/ci.yaml)

TFSumPy is a Python-based tool that analyzes Terraform plan files to provide a clear summary of infrastructure changes and identify potential risks. It helps DevOps teams review infrastructure changes more effectively by:

- Summarizing resource changes (create, update, delete)
- Identifying high and medium risk changes
- Automatically redacting sensitive information
- Providing detailed resource-level reporting

## Features

- 🔍 Analyzes Terraform plan JSON output
- ⚠️ Identifies high-risk changes (deletions of critical resources, security group modifications)
- 🔒 Automatically redacts sensitive information (credentials, IPs, resource names)
- 📊 Provides clear summary statistics
- 🛡️ Supports Terraform 1.0+ plan formats
- 📂 Module-aware resource grouping
- 🔄 Detailed attribute change tracking

## Installation

Currently, TFSumPy can only be installed from source:

```bash
git clone https://github.com/rafaelherik/tfsumpy.git
cd tfsumpy
pip install .
```

## Usage

First, generate a Terraform plan JSON file:

```bash
terraform plan -out=tfplan
terraform show -json tfplan > plan.json
```

Then analyze the plan using TFSumPy:

```bash
# Basic usage
tfsumpy plan.json

# Show resources grouped by module
tfsumpy plan.json --show-module

# Show detailed attribute changes
tfsumpy plan.json --show-changes

# Using custom rules configuration
tfsumpy plan.json --config rules_config.json

# Enable debug logging
tfsumpy plan.json --debug

# Show only specific sections
tfsumpy plan.json --risks --details
```

### Command Line Options

- `--show-module`: Group resources by their Terraform module
- `--show-changes`: Display detailed attribute changes for resources
- `--risks`: Show only the risk assessment section
- `--details`: Show only the resource details section
- `--debug`: Enable debug logging
- `--config`: Specify a custom rules configuration file

### Custom Rules Configuration

You can customize the analysis rules by creating a JSON configuration file. Here's an example structure:

```json
{
  "sensitive_patterns": [
    {
      "pattern": "\\bAKIA[0-9A-Z]{16}\\b",
      "replacement": "[AWS-KEY-REDACTED]"
    },
    {
      "pattern": "\\b(password|secret|token)\\b[\"']?:?[\\s\"']+[^\\s\"']+",
      "replacement": "[SECRET-REDACTED]"
    }
  ],
  "risk_rules": {
    "high": [
      {
        "pattern": "\\bdelete\\b.*\\b(database|storage)\\b",
        "message": "High risk: Critical storage resource deletion detected"
      }
    ],
    "medium": [
      {
        "pattern": "\\bcreate\\b.*\\b(bucket|storage)\\b.*public:\\s*true",
        "message": "Medium risk: Public storage resource being created"
      }
    ]
  }
}
```

The configuration file allows you to define:
- `sensitive_patterns`: Regular expressions to identify and redact sensitive information
- `risk_rules`: Patterns to identify high and medium risk changes

## Example Output

### Default Output (without --show-module)
```
Infrastructure Change Analysis
==============================
Total Changes: 5
Create: 2
Update: 2
Delete: 1

Risk Assessment:
High Risks:
- High risk: Security-related configuration change
Medium Risks:
- Medium risk: Version change could cause compatibility issues

Resource Details:
CREATE aws_s3_bucket: project-storage-[REDACTED]
UPDATE aws_security_group: app-sg-[REDACTED]
  ~ ingress = [] -> [{port = 443}]
UPDATE aws_ecs_service: api-service
DELETE aws_iam_role: legacy-role
CREATE aws_lambda_function: processor-function
```

### With Module Grouping (--show-module)
```
Infrastructure Change Analysis
==============================
Total Changes: 5
Create: 2
Update: 2
Delete: 1

Changes by Module:
root:
  Create: 1
  Update: 1
module.storage:
  Create: 1
  Update: 1
  Delete: 1

Risk Assessment:
High Risks:
- High risk: Security-related configuration change
Medium Risks:
- Medium risk: Version change could cause compatibility issues

Resource Details:
Module: root
  CREATE aws_s3_bucket: project-storage-[REDACTED]
  UPDATE aws_security_group: app-sg-[REDACTED]
    ~ ingress = [] -> [{port = 443}]

Module: module.storage
  UPDATE aws_ecs_service: api-service
  DELETE aws_iam_role: legacy-role
  CREATE aws_lambda_function: processor-function
```

## Requirements

- Python 3.10 or higher
- Terraform 1.0 or higher (for plan generation)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. Visit our [GitHub repository](https://github.com/rafaelherik/tfsumpy) for more information.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
