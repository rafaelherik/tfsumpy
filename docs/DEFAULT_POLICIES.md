# TFSumPy Default Policies

This document lists all default policies included with TFSumPy, organized by cloud provider.

## AWS Policies

### S3 Bucket Policies

#### AWS_S3_VERSIONING
- **Severity**: High
- **Description**: Ensure S3 buckets have versioning enabled
- **Resource Type**: aws_s3_bucket
- **Condition**: Check if versioning is enabled
- **Remediation**: Enable versioning on the S3 bucket using versioning configuration block

#### AWS_S3_ENCRYPTION
- **Severity**: High
- **Description**: Ensure S3 buckets have encryption enabled
- **Resource Type**: aws_s3_bucket
- **Condition**: Check if server-side encryption is configured
- **Remediation**: Configure server-side encryption using server_side_encryption_configuration block

[Note: This file should be expanded with all default policies from the policies/*.yaml files]
