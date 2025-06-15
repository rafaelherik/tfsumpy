# Advanced Usage

## Output Formats

tfsumpy supports three output formats, each designed for different use cases:

### Console Output (Default)
```bash
tfsumpy plan.json
```
Color-coded, human-readable output in your terminal. Perfect for quick reviews and local development.

### Markdown Output
```bash
tfsumpy plan.json --output markdown > plan_summary.md
```
Template-based Markdown output with:
- Summary statistics
- Resource changes
- Detailed attribute changes (if enabled)
- Timestamp and metadata

### JSON Output
```bash
tfsumpy plan.json --output json > plan_summary.json
```
Structured JSON output with:
- Metadata (timestamp, version)
- Summary statistics
- Resource changes
- Detailed information (if enabled)
- Analysis results (if available)

## Using tfsumpy in CI/CD

Integrate tfsumpy into your CI pipeline to automatically summarize Terraform changes in pull requests or deployments:

```yaml
# Example GitHub Actions step
- name: Summarize Terraform Plan
  run: |
    terraform plan -out=tfplan
    terraform show -json tfplan > plan.json
    tfsumpy plan.json --output markdown > plan_summary.md
```

Attach `plan_summary.md` to your PR or publish as a build artifact for easy review.

## For Code Review

Generate a Markdown summary and paste it directly into your pull request description:

```bash
tfsumpy plan.json --output markdown > plan_summary.md
cat plan_summary.md
```

## For Compliance Snapshots

Keep a record of planned infrastructure changes for audit or compliance:

```bash
# Markdown format
tfsumpy plan.json --output markdown > compliance/plan_$(date +%Y%m%d).md

# JSON format
tfsumpy plan.json --output json > compliance/plan_$(date +%Y%m%d).json
```

## Debug Mode

For troubleshooting or detailed analysis:

```bash
tfsumpy plan.json --debug
```

This enables:
- Verbose logging
- Detailed error messages
- Analysis process information

## Command Line Options

### Output Control
- `--output` or `-o`: Choose output format (`default`, `markdown`, `json`)
- `--detailed`: Show detailed resource information
- `--hide-changes`: Hide detailed attribute changes

### Deprecated Options
The following options are deprecated and will be removed in a future version:
- `--changes` → Use `--hide-changes=false` instead
- `--details` → Use `--detailed` instead
- `--markdown` → Use `--output markdown` instead

### Configuration
- `--config`: Path to configuration file
- `--plugin-dir`: Directory to load plugins from
- `--debug`: Enable debug logging

## Markdown Output (Beta)

You can generate a Markdown summary of your Terraform plan with:

```bash
tfsumpy plan.json --markdown > plan_summary.md
```

This will create a Markdown file with:
- A summary section
- Sections for created, updated, and destroyed resources
- JSON code blocks for each resource change

For updates, both before and after states are shown. For creates and deletes, only the relevant state is shown.

> **Note:** Markdown output is a beta feature. Please report any issues or suggestions! 