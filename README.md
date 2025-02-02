# TFSumPy - Terraform Plan Analyzer

[![CI](https://github.com/rafaelherik/tfsumpy/actions/workflows/ci.yaml/badge.svg)](https://github.com/rafaelherik/tfsumpy/actions/workflows/ci.yaml)

TFSumPy is a Python-based tool that analyzes Terraform plan files to provide a clear summary of infrastructure changes and identify potential risks. It helps DevOps teams review infrastructure changes more effectively by:

- Summarizing resource changes (create, update, delete)
- Identifying high and medium risk changes
- Automatically redacting sensitive information
- Providing detailed resource-level reporting

## Features

- 🔍 Detailed plan analysis with change breakdown
- 📊 Clear summary statistics for resource changes
- 🔒 Automatic sensitive information redaction
- 🛡️ Risk assessment for infrastructure changes
- 📋 Policy compliance checking
- 🎨 Color-coded output for better readability
- 🔄 Detailed attribute change tracking

## Installation

Install using pip:
```bash
    pip install tfsumpy
```
Or install from source:
```bash
    git clone https://github.com/rafaelherik/tfsumpy.git
    cd tfsumpy
    pip install .
```
## Usage

### Basic Usage

1. Generate a Terraform plan JSON file:
```bash
    terraform plan -out=tfplan
    terraform show -json tfplan > plan.json
```

2. Analyze the plan:

Basic summary:
```bash
    tfsumpy plan.json
```

Show detailed changes:
```bash
    tfsumpy plan.json --changes
```

Show resource details:
```bash
    tfsumpy plan.json --details
```

Enable risk assessment:
```bash
    tfsumpy plan.json --risks
```

Enable policy compliance check:
```bash
    tfsumpy plan.json --policies
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
### Advanced Features

1. Risk Assessment:

```bash
    tfsumpy plan.json --risks
```

This will show:
- High and medium risk changes
- Impact assessment
- Mitigation suggestions

2. Policy Compliance:

```bash
    tfsumpy plan.json --policies
```

Checks resources against:
- Security best practices
- Compliance requirements
- Custom policy rules

3. Detailed Analysis:

```bash
    tfsumpy plan.json --changes --details --risks
```

### Configuration

Create a custom configuration file (config.json):

```json
    {
      "sensitive_patterns": [
        {
          "pattern": "\\b(?:password|secret|key)\\b",
          "replacement": "[REDACTED]"
        }
      ],
      "risk_rules": {
        "high": [
          {
            "pattern": "\\bdelete\\b.*\\b(database|storage)\\b",
            "message": "Critical resource deletion"
          }
        ]
      }
    }
```

Use the configuration:

```bash
    tfsumpy plan.json --config config.json
```

### Debug Mode

For troubleshooting or detailed logging:

```bash
    tfsumpy plan.json --debug
```

This will:
- Enable verbose logging
- Show detailed error messages
- Display analysis process information

## Requirements

- Python 3.10 or higher
- Terraform 1.0 or higher

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please make sure to update tests as appropriate.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
