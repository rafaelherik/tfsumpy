# Troubleshooting Guide

This guide helps you resolve common issues with tfsumpy.

## Installation Issues

### Python Version

**Error**: `Python version X.Y.Z is not supported`

**Solution**: Ensure you have Python 3.9 or higher installed:
```bash
python --version
```

### Missing Dependencies

**Error**: `ModuleNotFoundError: No module named 'X'`

**Solution**: Install missing dependencies:
```bash
# Using Poetry
poetry install

# Using pip
pip install tfsumpy
```

### Permission Issues

**Error**: `Permission denied`

**Solution**: Use virtual environments or install with `--user`:
```bash
# Using virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install tfsumpy

# Using --user
pip install --user tfsumpy
```

## Plan File Issues

### Invalid Plan File

**Error**: `Invalid plan file: X`

**Solution**: Ensure the plan file is in JSON format:
```bash
# Generate correct JSON plan
terraform plan -out=tfplan
terraform show -json tfplan > plan.json
```

### Missing Plan File

**Error**: `Plan file not found: X`

**Solution**: Check the file path and permissions:
```bash
# Verify file exists
ls -l plan.json

# Check file permissions
chmod 644 plan.json
```

## Configuration Issues

### Invalid Configuration

**Error**: `Invalid configuration: X`

**Solution**: Check your configuration file format:
```json
{
  "sensitive_patterns": [
    {
      "pattern": "\\b(?:password|secret|key)\\b",
      "replacement": "[REDACTED]"
    }
  ]
}
```

### Environment Variables

**Error**: `Configuration error: X`

**Solution**: Check environment variables:
```bash
# List all TFSUMPY variables
env | grep TFSUMPY

# Unset problematic variables
unset TFSUMPY_DEBUG
```

## AI Analysis Issues

### API Key Issues

**Error**: `Invalid API key for provider X`

**Solution**: Verify your API key:
```bash
# Check environment variable
echo $TFSUMPY_OPENAI_API_KEY

# Try with explicit key
tfsumpy plan.json --output markdown --ai openai YOUR_KEY
```

### Model Availability

**Error**: `Model X is not available`

**Solution**: Use a supported model:
```bash
# List available models
tfsumpy --help

# Use default model
tfsumpy plan.json --output markdown --ai openai YOUR_KEY
```

### Rate Limiting

**Error**: `Rate limit exceeded`

**Solution**: Reduce request frequency or increase limits:
```bash
# Reduce token usage
tfsumpy plan.json --output markdown --ai openai YOUR_KEY --ai-max-tokens 1000

# Use a different provider
tfsumpy plan.json --output markdown --ai gemini YOUR_KEY
```

## Plugin Issues

### Plugin Loading

**Error**: `Failed to load plugin: X`

**Solution**: Check plugin structure:
```bash
# Verify plugin directory
ls -l plugins/

# Check plugin permissions
chmod 644 plugins/*.py
```

### Plugin Dependencies

**Error**: `Missing dependency for plugin X`

**Solution**: Install required dependencies:
```bash
# Using Poetry
poetry add dependency-name

# Using pip
pip install dependency-name
```

## Output Issues

### Markdown Output

**Error**: `Failed to generate markdown`

**Solution**: Check output directory permissions:
```bash
# Create output directory
mkdir -p output
chmod 755 output

# Write to file
tfsumpy plan.json --output markdown > output/plan.md
```

### JSON Output

**Error**: `Invalid JSON output`

**Solution**: Use proper JSON parsing:
```bash
# Validate JSON
tfsumpy plan.json --output json | jq '.'

# Save to file
tfsumpy plan.json --output json > plan.json
```

## Debugging

Enable debug mode for more information:
```bash
# Using command line
tfsumpy plan.json --debug

# Using environment variable
export TFSUMPY_DEBUG=true
tfsumpy plan.json
```

## Getting Help

If you're still having issues:

1. Check the [documentation](https://tfsumpy.readthedocs.io/)
2. Search [existing issues](https://github.com/rafaelherik/tfsumpy/issues)
3. Create a new issue with:
   - Error message
   - Steps to reproduce
   - Environment details
   - Debug output 