# Advanced Usage

## Using tfsumpy in CI/CD

Integrate tfsumpy into your CI pipeline to automatically summarize Terraform changes in pull requests or deployments:

```yaml
# Example GitHub Actions step
- name: Summarize Terraform Plan
  run: |
    terraform plan -out=tfplan
    terraform show -json tfplan > plan.json
    tfsumpy plan.json --markdown > plan_summary.md
```

Attach `plan_summary.md` to your PR or publish as a build artifact for easy review.

## For Code Review

Generate a Markdown summary and paste it directly into your pull request description:

```bash
tfsumpy plan.json --markdown > plan_summary.md
cat plan_summary.md
```

## For Compliance Snapshots

Keep a record of planned infrastructure changes for audit or compliance:

```bash
tfsumpy plan.json --markdown > compliance/plan_$(date +%Y%m%d).md
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