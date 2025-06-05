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

#### Basic Summary
```bash
Terraform Plan Analysis
======================
Total Changes: 3
Create: 1
Update: 1
Delete: 1
```

#### Detailed Changes
```bash
Resource Changes:
CREATE aws_s3_bucket.data_bucket
  + bucket = "new-bucket"
  + versioning_enabled = true

UPDATE aws_instance.web_server
  ~ instance_type = "t2.micro" -> "t2.small"
  ~ tags = {
      ~ environment = "dev" -> "staging"
    }
```

## Usage Examples

### Basic Summary
```bash
tfsumpy plan.json
```

### Detailed Changes
```bash
tfsumpy plan.json --changes
```

### Resource Details
```bash
tfsumpy plan.json --details
``` 