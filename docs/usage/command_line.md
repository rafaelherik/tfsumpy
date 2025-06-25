# Command-Line Reference

This guide provides a complete reference for tfsumpy's command-line interface.

## Basic Syntax

```bash
tfsumpy [OPTIONS] PLAN_FILE
```

## Arguments

- `PLAN_FILE`: Path to the Terraform plan JSON file (required)

## Options

### Output Format

- `-o, --output [default|markdown|json]`: Output format (default: default)
- `--detailed`: Show detailed resource information
- `--hide-changes`: Hide detailed attribute changes

### Configuration

- `--config FILE`: Path to configuration JSON file
- `--debug`: Enable debug logging
- `--plugin-dir DIR`: Directory containing custom plugins

### AI Analysis

- `--ai PROVIDER API_KEY`: Enable AI summarization
- `--ai-model MODEL`: Specify AI model to use
- `--ai-max-tokens N`: Maximum tokens for AI response
- `--ai-temperature N`: Control response creativity (0.0-1.0)
- `--ai-system-prompt PROMPT`: Custom system prompt

### Azure Integration Options

- `--azure`: Enable Azure integration for AI analysis (requires Azure credentials)
- `--azure-subscription-id`: Azure Subscription ID for resource queries (default from AZURE_SUBSCRIPTION_ID env var)
- `--azure-resource-groups`: List of Azure resource group names to filter (default: all)
- `--azure-include-resources`: Include Azure resources information for analysis

### Deprecated Options

> **Warning**: These options are deprecated and will be removed in a future version.

- `--changes`: (deprecated; attribute changes are shown by default)
- `--details`: Use `--detailed` instead
- `--markdown`: Use `--output markdown` instead

## Examples

### Basic Usage

```bash
# Default output
tfsumpy plan.json

# Markdown output with detailed changes
tfsumpy plan.json --output markdown --detailed

# JSON output with custom config
tfsumpy plan.json --output json --config config.json
```

### AI Analysis

```bash
# OpenAI with custom model
tfsumpy plan.json --output markdown --ai openai YOUR_KEY --ai-model gpt-4

# Gemini with custom temperature
tfsumpy plan.json --output markdown --ai gemini YOUR_KEY --ai-temperature 0.5

# Anthropic with custom prompt
tfsumpy plan.json --output markdown --ai anthropic YOUR_KEY --ai-system-prompt "Focus on security"
```

### Plugin Usage

```bash
# Load plugins from custom directory
tfsumpy plan.json --plugin-dir ./plugins

# Debug mode with plugins
tfsumpy plan.json --plugin-dir ./plugins --debug
```

## Exit Codes

- `0`: Success
- `1`: Error (validation, configuration, or unexpected error)
- `2`: Invalid command-line arguments

## Environment Variables

All command-line options can be set using environment variables:

```bash
# Output format
export TFSUMPY_OUTPUT=markdown

# Debug mode
export TFSUMPY_DEBUG=true

# AI configuration
export TFSUMPY_AI_PROVIDER=openai
export TFSUMPY_AI_MODEL=gpt-4
export TFSUMPY_AI_MAX_TOKENS=2000
export TFSUMPY_AI_TEMPERATURE=0.7
```

## Configuration Precedence

1. Command-line arguments
2. Environment variables
3. Configuration file
4. Default values 