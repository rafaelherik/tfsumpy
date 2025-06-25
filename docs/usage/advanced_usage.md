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
+ Timestamp and metadata
  
## AI Analysis with Azure
When Azure integration is enabled via the `--azure` flag, tfsumpy will retrieve Azure resource details before performing AI summarization.
Ensure your Azure credentials (e.g., via Azure CLI login or environment variables) and subscription ID are configured.

Example:
```bash
tfsumpy plan.json \
  --output markdown \
  --ai openai YOUR_API_KEY \
  --azure
```

For JSON output with AI and Azure:
```bash
tfsumpy plan.json \
  --output json \
  --ai openai YOUR_API_KEY \
  --azure
```

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
- `--changes`: (deprecated; attribute changes are shown by default)
- `--details` → Use `--detailed` instead
- `--markdown` → Use `--output markdown` instead

### Configuration
- `--config`: Path to configuration file
- `--plugin-dir`: Directory to load plugins from
- `--debug`: Enable debug logging

## Markdown Output

Generate a Markdown summary of your Terraform plan with:

```bash
tfsumpy plan.json --output markdown > plan_summary.md
```

You can further control the content with:
- `--detailed`: Show detailed resource information and attribute changes
- `--hide-changes`: Hide detailed attribute changes

The generated Markdown includes:
- Summary statistics
- Resource changes formatted as HCL code blocks
- Replacement enforcement attributes (for recreate operations)
- Timestamp and metadata