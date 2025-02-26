# Advanced Usage

## Risk Assessment

The risk assessment feature helps identify potentially dangerous changes in your Terraform plans.

### Running Risk Assessment

```bash
bolwerk plan.json --risks
```

This will analyze:
- Resource deletions
- Security group changes
- IAM permission changes
- Public access modifications

### Understanding Risk Levels

Risks are categorized into three levels:

- **High**: Critical changes that could impact system availability or security
- **Medium**: Changes that require careful review but are less critical
- **Low**: Minor changes with minimal impact

## Policy Compliance

Policy compliance checking ensures your infrastructure changes meet organizational standards.

### Running Policy Checks

```bash
bolwerk plan.json --policies
```

### Custom Policy Configuration

Create a custom policy file (`policies.json`):

```json
{
  "policies": [
    {
      "name": "enforce-encryption",
      "description": "Ensure storage resources are encrypted",
      "resource_types": ["aws_s3_bucket", "aws_ebs_volume"],
      "conditions": {
        "encrypted": true
      },
      "severity": "HIGH"
    }
  ]
}
```

### Combining Features

You can combine multiple features for comprehensive analysis:

```bash
bolwerk plan.json --risks --policies --changes --details
```

## Debug Mode

For troubleshooting or detailed analysis:

```bash
bolwerk plan.json --debug
```

This enables:
- Verbose logging
- Detailed error messages
- Analysis process information 