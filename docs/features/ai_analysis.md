# AI Analysis in tfsumpy

tfsumpy supports AI-powered analysis of Terraform plans using OpenAI, Google Gemini, and Anthropic Claude. This feature helps you get natural language summaries of your infrastructure changes.

## Prerequisites

The required AI provider packages are included in tfsumpy's dependencies and will be installed automatically when you install tfsumpy:

- OpenAI (`openai`)
- Google Gemini (`google-generativeai`)
- Anthropic (`anthropic`)

If you're installing tfsumpy using Poetry:
```bash
poetry install
```

Or if you're installing from PyPI:
```bash
pip install tfsumpy
```

## Supported AI Providers

- **OpenAI**: Uses GPT models (default: gpt-3.5-turbo)
- **Google Gemini**: Uses Gemini Pro model
- **Anthropic**: Uses Claude models (default: claude-3-sonnet-20240229)

## Basic Usage

Enable AI analysis by providing your API key:

```bash
# Using OpenAI
tfsumpy plan.json --output markdown --ai openai YOUR_API_KEY

# Using Google Gemini
tfsumpy plan.json --output markdown --ai gemini YOUR_API_KEY

# Using Anthropic Claude
tfsumpy plan.json --output markdown --ai anthropic YOUR_API_KEY
```

## Environment Variables

You can store your API keys as environment variables:

```bash
# OpenAI
export TFSUMPY_OPENAI_API_KEY="your-key-here"

# Google Gemini
export TFSUMPY_GEMINI_API_KEY="your-key-here"

# Anthropic
export TFSUMPY_ANTHROPIC_API_KEY="your-key-here"
```

When using environment variables, you only need to specify the provider:

```bash
tfsumpy plan.json --output markdown --ai openai
```

## Advanced Configuration

### Model Selection

Choose a specific model for your provider:

```bash
# OpenAI
tfsumpy plan.json --output markdown --ai openai YOUR_KEY --ai-model gpt-4

# Google Gemini
tfsumpy plan.json --output markdown --ai gemini YOUR_KEY --ai-model gemini-pro

# Anthropic
tfsumpy plan.json --output markdown --ai anthropic YOUR_KEY --ai-model claude-3-opus-20240229
```

### Response Control

Adjust the AI response characteristics:

```bash
# Control response length (tokens)
tfsumpy plan.json --output markdown --ai openai YOUR_KEY --ai-max-tokens 2000

# Control creativity (0.0-1.0)
tfsumpy plan.json --output markdown --ai openai YOUR_KEY --ai-temperature 0.7
```

### Custom System Prompt

Provide a custom system prompt to guide the AI analysis:

```bash
tfsumpy plan.json --output markdown --ai openai YOUR_KEY --ai-system-prompt "Focus on security implications of the changes"
```

## Output Format

> **Important**: AI analysis is currently only supported with markdown output format. Using other output formats will result in a warning and the AI analysis will be skipped.

```bash
tfsumpy plan.json --output markdown --ai openai YOUR_KEY > plan_analysis.md
```

Example output:
```markdown
# Terraform Plan Analysis

## Summary
- Total Changes: 3
- Resources to Add: 1
- Resources to Change: 1
- Resources to Destroy: 1

## AI Analysis
The changes primarily affect the application's infrastructure:
1. A new S3 bucket is being created for data storage
2. The web server instance type is being upgraded from t2.micro to t2.small
3. An old security group is being removed

These changes appear to be part of a planned infrastructure upgrade. The instance type upgrade will provide better performance, while the new S3 bucket suggests additional storage requirements. The security group removal should be verified to ensure no dependencies are affected.

## Resource Changes
...
```

## Best Practices

1. **API Key Security**
   - Use environment variables for API keys
   - Never commit API keys to version control
   - Rotate API keys regularly

2. **Cost Management**
   - Monitor your AI provider usage
   - Use appropriate model sizes for your needs
   - Set reasonable token limits

3. **Output Quality**
   - Use markdown output for best results
   - Adjust temperature for desired detail level
   - Use custom prompts for specific analysis needs

4. **Error Handling**
   - Check API key validity
   - Verify model availability
   - Monitor rate limits

## Troubleshooting

Common issues and solutions:

1. **Missing Dependencies**
   ```bash
   # Install required packages
   pip install openai google-generativeai anthropic
   ```

2. **API Key Issues**
   ```bash
   # Verify API key is set
   echo $TFSUMPY_OPENAI_API_KEY
   
   # Try with explicit key
   tfsumpy plan.json --output markdown --ai openai YOUR_KEY
   ```

3. **Model Availability**
   ```bash
   # Try a different model
   tfsumpy plan.json --output markdown --ai openai YOUR_KEY --ai-model gpt-3.5-turbo
   ```

4. **Rate Limiting**
   ```bash
   # Reduce token usage
   tfsumpy plan.json --output markdown --ai openai YOUR_KEY --ai-max-tokens 1000
   ```

## Current Limitations

1. AI analysis is only available with markdown output
2. Large plans may require higher token limits
3. API costs may apply based on your provider
4. Response quality depends on the model used
5. Configuration is only available via command-line arguments
6. No built-in cost estimation
7. No compliance analysis features

## Planned Features

The following features are planned for future releases:
- Support for more AI providers
- Custom analysis templates
- Batch processing capabilities
- Cost estimation integration
- Compliance analysis
- Configuration file support
- JSON output support for AI analysis 