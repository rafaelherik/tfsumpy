# Plan Analysis

## Overview

Plan analysis is the core feature of tfsumpy, providing detailed insights into Terraform infrastructure changes.

## Features

### Change Detection

tfsumpy identifies three types of changes:

- **Create**: New resources being added
- **Update**: Modifications to existing resources
- **Delete**: Resources being removed

### Attribute Tracking

For each resource change, tfsumpy tracks:

- Resource type and name
- Changed attributes
- Old and new values
- Dependencies

### Output Formats

tfsumpy supports three output formats:

#### Console Output (Default)
```bash
Terraform Plan Analysis
======================
Total Changes: 3
Create: 1
Update: 1
Delete: 1
```

#### Markdown Output
```markdown
# Terraform Plan Analysis
Generated: 2024-03-21 10:00:00

## Summary
- Total Changes: 3
- Create: 1
- Update: 1
- Delete: 1

## Resource Changes
### Create
- aws_s3_bucket.data_bucket
  - bucket: "new-bucket"
  - versioning_enabled: true

### Update
- aws_instance.web_server
  - instance_type: "t2.micro" → "t2.small"
  - tags.environment: "dev" → "staging"
```

#### JSON Output
```json
{
  "metadata": {
    "timestamp": "2024-03-21T10:00:00Z",
    "version": "1.0.0"
  },
  "summary": {
    "total_changes": 3,
    "create": 1,
    "update": 1,
    "delete": 1
  },
  "changes": {
    "create": [
      {
        "type": "aws_s3_bucket",
        "name": "data_bucket",
        "attributes": {
          "bucket": "new-bucket",
          "versioning_enabled": true
        }
      }
    ]
  }
}
```

## Usage Examples

### Basic Summary
```bash
tfsumpy plan.json
```

### Detailed Changes
```bash
tfsumpy plan.json --hide-changes=false
```

### Resource Details
```bash
tfsumpy plan.json --detailed
```

### Output Formats
```bash
# Console output (default)
tfsumpy plan.json

# Markdown output
tfsumpy plan.json --output markdown > plan_summary.md

# JSON output
tfsumpy plan.json --output json > plan_summary.json
```

> **Note:** The following options are deprecated and will be removed in a future version:
> - `--changes` → Use `--hide-changes=false` instead
> - `--details` → Use `--detailed` instead
> - `--markdown` → Use `--output markdown` instead 