# TFSumPy Policy System

The TFSumPy policy system provides a robust framework for defining and enforcing infrastructure compliance rules. This document explains how to use and configure policies.

## Policy Structure

Policies are defined in YAML format with the following structure:

```yaml
provider: aws  # Cloud provider (aws, azure, gcp)
policies:
  - id: POLICY_ID
    name: "Human Readable Name"
    description: "Detailed policy description"
    provider: aws
    resource_type: aws_s3_bucket
    severity: high
    disabled: false
    condition:
      type: attribute_check
      parameters:
        attribute: versioning
        value: true
    remediation: "How to fix this issue"
```

### Required Fields

- `id`: Unique identifier for the policy
- `name`: Human-readable policy name
- `description`: Detailed description of what the policy checks
- `provider`: Cloud provider (aws, azure, gcp)
- `resource_type`: Terraform resource type to check
- `severity`: Impact level (high, medium, low)
- `condition`: Rule definition
- `remediation`: Instructions for fixing violations

### Optional Fields

- `disabled`: Boolean to disable the policy (default: false)

## Condition Types

TFSumPy supports three types of policy conditions:

### 1. Attribute Check
Verifies resource attribute values:

```yaml
condition:
  type: attribute_check
  parameters:
    attribute: encryption_enabled
    value: true
```

### 2. Attribute Change
Detects specific attribute changes:

```yaml
condition:
  type: attribute_change
  parameters:
    attribute: public_access
    from: false
    to: true
```

### 3. Resource Count
Enforces resource count limits:

```yaml
condition:
  type: resource_count
  parameters:
    max: 5
```

## Using Policies

### Command Line Options

1. Enable policy checking:

```bash
tfsumpy plan.json --policies
```

2. Load custom policy file:

```bash
tfsumpy plan.json --policies --policy-file custom-policy.yaml
```

3. Load policies from directory:

```bash
tfsumpy plan.json --policies --policy-dir ./policies
```

### Policy Output

The policy check output includes:
- Total number of violations by severity
- Detailed violation information
- Remediation steps for each violation

Example output:

```
Policy Compliance Report
=======================
Violations Summary:
HIGH: 2
MEDIUM: 1

Detailed Violations:
[HIGH] Policy AWS_S3_ENCRYPTION
Resource: aws_s3_bucket.data
Message: S3 bucket encryption not enabled
Remediation: Configure server-side encryption using server_side_encryption_configuration block
```

## Built-in Policies

### AWS Policies

1. S3 Bucket Versioning (AWS_S3_VERSIONING)
   - Severity: High
   - Checks: S3 bucket versioning enabled
   - Resource: aws_s3_bucket

2. S3 Bucket Encryption (AWS_S3_ENCRYPTION)
   - Severity: High
   - Checks: S3 bucket encryption enabled
   - Resource: aws_s3_bucket

### Azure Policies
[Coming soon]

### GCP Policies
[Coming soon]

## Creating Custom Policies

1. Create a YAML file following the policy schema:

```yaml
provider: aws
policies:
  - id: CUSTOM_S3_POLICY
    name: "Custom S3 Policy"
    description: "Ensures S3 buckets follow custom rules"
    provider: aws
    resource_type: aws_s3_bucket
    severity: high
    condition:
      type: attribute_check
      parameters:
        attribute: custom_setting
        value: expected_value
    remediation: "Instructions to fix"
```

2. Load your custom policies using the CLI:

```bash
tfsumpy plan.json --policy-file my-policy.yaml
```

## Best Practices

1. Use meaningful policy IDs
2. Provide clear remediation steps
3. Set appropriate severity levels
4. Keep policies focused and specific
5. Document custom policies
6. Regular policy review and updates

## Policy Precedence

1. Custom policies override built-in policies with the same ID
2. Latest loaded policy takes precedence
3. Built-in policies are loaded first

For more examples and detailed information, visit our [GitHub repository](https://github.com/rafaelherik/tfsumpy). 