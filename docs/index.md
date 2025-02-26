# bolwerk Documentation

bolwerk is a Python-based tool that analyzes Terraform plan files to provide a clear summary of infrastructure changes and identify potential risks. It helps DevOps teams review infrastructure changes more effectively by providing detailed analysis, risk assessment, and policy compliance checking.

## Key Features

- 🔍 **Detailed Plan Analysis**: Comprehensive breakdown of infrastructure changes
- 📊 **Change Statistics**: Clear summary of resource modifications
- 🔒 **Sensitive Information Protection**: Automatic redaction of sensitive data
- 🛡️ **Risk Assessment**: Identification of high and medium risk changes
- 📋 **Policy Compliance**: Verification against security and organizational policies
- 🎨 **Enhanced Readability**: Color-coded output for better understanding
- 🔄 **Attribute Tracking**: Detailed tracking of resource attribute changes

## Quick Start

### Installation

```bash
pip install bolwerk
```

### Basic Usage

1. Generate a Terraform plan JSON file:
```bash
terraform plan -out=tfplan
terraform show -json tfplan > plan.json
```

2. Analyze the plan:
```bash
bolwerk plan.json
```

### Example Output

```bash
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

## Requirements

- Python 3.10 or higher
- Terraform 1.0 or higher

## Getting Started

- [Installation Guide](installation.md): Detailed installation instructions
- [Basic Usage](usage/basic_usage.md): Learn the basic commands
- [Advanced Usage](usage/advanced_usage.md): Explore advanced features
- [Configuration](usage/configuration.md): Configure bolwerk for your needs

## Features in Detail

- [Plan Analysis](features/plan_analysis.md): Understanding infrastructure changes
- [Risk Assessment](features/risk_assessment.md): Identifying potential risks
- [Policy Compliance](features/policy_compliance.md): Ensuring standards compliance

## API Reference

- [Analyzers](api/analyzers.md): Core analysis components
- [Reporters](api/reporters.md): Output formatting components
- [Models](api/models.md): Data structures

## Contributing

We welcome contributions! See our [Contributing Guide](contributing.md) for details on how to get started.

## License

bolwerk is released under the MIT License. See the [LICENSE](https://github.com/rafaelherik/bolwerk/blob/main/LICENSE) file for details. 