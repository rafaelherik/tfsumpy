# Policy Compliance

## Overview

The policy compliance feature ensures that infrastructure changes adhere to organizational standards and security best practices.

## Policy Types

### Security Policies

- Encryption requirements
- Network access restrictions
- Authentication requirements
- Logging configurations

### Compliance Policies

- Resource naming conventions
- Tag requirements
- Region restrictions
- Resource size limitations

### Cost Control Policies

- Instance type restrictions
- Resource count limits
- Storage tier requirements
- Backup retention policies

## Policy Configuration

### Basic Policy Structure

```json
{
  "policies": [
    {
      "name": "require-encryption",
      "description": "Ensure all storage resources are encrypted",
      "resource_types": ["aws_s3_bucket", "aws_ebs_volume"],
      "conditions": {
        "encrypted": true
      },
      "severity": "HIGH"
    }
  ]
}
```

### Policy Evaluation

Policies are evaluated against each resource in the Terraform plan:

```bash
Policy Compliance Check
======================
Violations Found: 2

HIGH: require-encryption
- aws_s3_bucket.data: Encryption not enabled
  Required: encryption = true
  Found: encryption = false
  Remediation: Add server_side_encryption_configuration block

MEDIUM: require-tags
- aws_instance.web: Missing required tags
  Required: environment, owner
  Found: environment
  Remediation: Add missing tags to resource
```

## Custom Policy Development

### Creating Custom Policies

1. Create a policy file:
```json
{
  "policies": [
    {
      "name": "custom-policy",
      "description": "Custom policy description",
      "resource_types": ["resource_type"],
      "conditions": {
        "attribute": "value"
      },
      "severity": "MEDIUM"
    }
  ]
}
```

2. Apply the policy:
```bash
bolwerk plan.json --policies --config custom_policies.json 