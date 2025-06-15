# AI Analysis

TFSumpy provides AI-powered analysis of Terraform plan changes using various AI providers. This feature helps you understand the impact of your infrastructure changes in natural language.

## Usage

To use AI analysis, you can use the `--ai` flag followed by your API key:

```bash
tfsumpy plan.json --output markdown --ai openai 'your-api-key'
```

### Available Providers

- OpenAI (default)
- Anthropic
- Google AI

### Output Options

By default, when using AI analysis, the output will only show the AI summary. If you want to see both the AI summary and the detailed resource changes, use the `--show-changes` flag:

```bash
tfsumpy plan.json --output markdown --ai openai 'your-api-key' --show-changes
```

### Example Output

```markdown
# Terraform Plan Analysis Report

## Summary
- **Total Resources**: 32
- **Resources to Add**: 11
- **Resources to Change**: 7
- **Resources to Destroy**: 14

## AI Analysis
### Summary of Terraform Plan Changes

#### Overall Impact:
- Several resources are being modified, created, or deleted across different resource groups and regions.
- Changes include updates to network configurations, Azure services configurations, SKU upgrades, and location migrations.

[... AI analysis continues ...]
```

## Configuration

You can configure the AI analysis behavior in your `tfsumpy.yaml` file:

```yaml
ai:
  provider: openai  # or anthropic, google
  model: gpt-4     # model name for the selected provider
  temperature: 0.7 # optional: controls response creativity
  max_tokens: 1000 # optional: maximum response length
```

## Best Practices

1. Use AI analysis for high-level understanding of changes
2. Use `--show-changes` when you need detailed resource information
3. Consider the cost implications of using AI providers
4. Keep your API keys secure and never commit them to version control 