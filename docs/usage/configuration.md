# Configuration

## Configuration File

bolwerk can be customized using a JSON configuration file. Create a file named `config.json`:

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

## Configuration Options

### Sensitive Pattern Configuration

The `sensitive_patterns` section defines patterns for redacting sensitive information:

```json
{
  "sensitive_patterns": [
    {
      "pattern": "pattern_regex",
      "replacement": "replacement_text",
      "description": "Optional description"
    }
  ]
}
```

### Risk Rules Configuration

The `risk_rules` section defines patterns for identifying risky changes:

```json
{
  "risk_rules": {
    "high": [
      {
        "pattern": "pattern_regex",
        "message": "Risk message",
        "description": "Optional description"
      }
    ],
    "medium": [],
    "low": []
  }
}
```

## Using Custom Configuration

Apply your configuration using the `--config` flag:

```bash
bolwerk plan.json --config path/to/config.json
```

## Environment Variables

bolwerk supports the following environment variables:

- `bolwerk_CONFIG`: Path to configuration file
- `bolwerk_DEBUG`: Enable debug mode (set to "1" or "true") 