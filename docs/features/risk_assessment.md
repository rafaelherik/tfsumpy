# Risk Assessment

## Overview

bolwerk's risk assessment feature analyzes Terraform plans to identify potentially dangerous changes to your infrastructure.

## Risk Categories

### High Risk Changes

- Deletion of critical resources
- Security group modifications
- IAM permission changes
- Public access modifications

### Medium Risk Changes

- Instance type modifications
- Storage configuration changes
- Network configuration updates

### Low Risk Changes

- Tag modifications
- Non-critical resource updates
- Documentation changes

## Risk Analysis Output

Example risk assessment output:

```bash
Risk Assessment Results
======================
High Risk Changes: 1
Medium Risk Changes: 2
Low Risk Changes: 3

HIGH RISK:
- aws_security_group.main: Security group rule modification
  Impact: Could affect application accessibility
  Mitigation: Review security group changes carefully

MEDIUM RISK:
- aws_instance.web: Instance type change
  Impact: Potential performance impact
  Mitigation: Schedule change during low-traffic period
```

## Provider-Specific Risk Analysis

### AWS Risks

- IAM role/policy modifications
- Security group changes
- Public subnet creation
- S3 bucket policy changes

### Azure Risks

- Network security group modifications
- Role assignments
- Public IP assignments
- Storage account access changes

### GCP Risks

- IAM policy modifications
- Firewall rule changes
- Public IP configurations
- Service account modifications 