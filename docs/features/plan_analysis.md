# Plan Analysis

## Overview
The plan analysis feature provides detailed insights into Terraform plan changes, including resource modifications, attribute changes, and potential risks. It supports multiple output formats and AI-powered summarization.

## Features
- Change detection and tracking
- Attribute change analysis
- Multiple output formats (console, markdown, JSON)
- AI-powered change summarization
- Risk assessment
- Customizable analysis rules

## Output Formats

### Console Output
The default output format provides a clear, colorized view of plan changes in the terminal.

### Markdown Output
Generate detailed markdown reports suitable for documentation or pull requests.

### JSON Output
Get structured JSON output for integration with other tools or custom processing.

### AI Summarization
Get AI-powered analysis of your Terraform changes using various providers:

```bash
# Using OpenAI
tfsumpy plan.json --output markdown --ai openai YOUR_API_KEY

# Using Google Gemini
tfsumpy plan.json --output markdown --ai gemini YOUR_API_KEY

# Using Anthropic Claude
tfsumpy plan.json --output markdown --ai anthropic YOUR_API_KEY
```

#### AI Configuration Options
- `--ai PROVIDER API_KEY`: Enable AI summarization with provider and API key
- `--ai-model MODEL`: Specify the model to use
- `--ai-max-tokens N`: Maximum tokens for the AI response
- `--ai-temperature N`: Control response creativity (0.0 to 1.0)
- `--ai-system-prompt PROMPT`: Custom system prompt for the AI

#### Example AI Summary
The AI summary provides:
- Overall impact assessment
- Key resource changes
- Potential risks
- Recommendations

## Usage Examples

### Basic Analysis
```bash
tfsumpy plan.json
```

### Detailed Analysis with AI
```bash
tfsumpy plan.json --output markdown --detailed --ai openai YOUR_API_KEY --ai-model gpt-4
```

### JSON Output with AI
```bash
tfsumpy plan.json --output json --ai anthropic YOUR_API_KEY --ai-model claude-3-opus-20240229
```

## Notes
- AI summarization requires an API key for the chosen provider
- The AI feature is optional and can be installed with: `pip install tfsumpy[ai]`
- Default models are provider-specific:
  - OpenAI: gpt-3.5-turbo
  - Gemini: gemini-pro
  - Anthropic: claude-3-sonnet-20240229 