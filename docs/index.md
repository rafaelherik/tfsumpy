# tfsumpy: Effortless Terraform Plan Summaries

Welcome to **tfsumpy** — the modern, Python-based CLI tool for summarizing and reviewing Terraform plan files. Instantly understand what will change in your infrastructure, catch surprises, and share clear, readable summaries with your team.

---

## 🚀 Why tfsumpy?

- **Instant Plan Summaries:** See what will be created, updated, or destroyed at a glance.
- **Human-Friendly Output:** Color-coded, Markdown, and JSON output for easy review and sharing.
- **Sensitive Data Protection:** Automatically redact secrets and sensitive values.
- **Customizable:** Configure redaction and output to fit your workflow.
- **No Cloud Required:** Runs locally, works with any Terraform JSON plan.

---

## 🔥 Quick Start

### 1. Install
```bash
pip install tfsumpy
```

### 2. Generate a Terraform plan JSON
```bash
terraform plan -out=tfplan
terraform show -json tfplan > plan.json
```

### 3. Summarize your plan
```bash
tfsumpy plan.json
```

---

## 💡 Usage Scenarios

### Basic Summary
```bash
tfsumpy plan.json
```
Shows a concise summary of all resource changes.

### Detailed Attribute Changes
```bash
tfsumpy plan.json --changes
```
See exactly which attributes will change for each resource.

### Full Resource Details
```bash
tfsumpy plan.json --details
```
Get a deep dive into every resource and its planned state.

### Markdown Output (for PRs, docs, or sharing)
```bash
tfsumpy plan.json --markdown > plan_summary.md
```
Generates a beautiful Markdown summary, perfect for code reviews or documentation.

### Custom Redaction & Config
```bash
tfsumpy plan.json --config myconfig.json
```
Redact custom patterns or tweak output using a JSON config file.

### Debugging
```bash
tfsumpy plan.json --debug
```
Enables verbose logging for troubleshooting.

---

## ⚙️ Configuration Example

Create a `config.json` to redact custom sensitive patterns:
```json
{
  "sensitive_patterns": [
    { "pattern": "password|secret|key", "replacement": "[REDACTED]" }
  ]
}
```

---

## 📚 Documentation & API

- [Plan Analysis](features/plan_analysis.md): How tfsumpy analyzes your plans
- [Configuration](usage/configuration.md): Customizing output and redaction
- [Advanced Usage](usage/advanced_usage.md): Markdown, debug, and more
- [Analyzers API](api/analyzers.md): Extend or integrate tfsumpy
- [Reporters API](api/reporters.md): Custom output formats
- [Models API](api/models.md): Data structures

---

## 🤝 Contributing

We welcome contributions! See our [Contributing Guide](contributing.md) to get started.

---

## 📝 License

tfsumpy is released under the MIT License. See the [LICENSE](https://github.com/rafaelherik/tfsumpy/blob/main/LICENSE) file for details.

---

## 🚦 Project Status

**Status:** Beta — Feedback and contributions are welcome! 