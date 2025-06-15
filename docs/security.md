# Security Guide

This guide covers security best practices for using tfsumpy.

## Sensitive Data Handling

### Automatic Redaction

tfsumpy automatically redacts sensitive data using pattern matching:

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

### Custom Patterns

Add custom patterns to redact specific data:

```json
{
  "sensitive_patterns": [
    {
      "pattern": "\\b(?:password|secret|key)\\b",
      "replacement": "[REDACTED]"
    },
    {
      "pattern": "\\b(?:api_key|token)\\b",
      "replacement": "[REDACTED]"
    },
    {
      "pattern": "\\b(?:credit_card|ssn)\\b",
      "replacement": "[REDACTED]"
    }
  ]
}
```

### Output Security

1. **Console Output**
   - Sensitive data is redacted before display
   - Use `--debug` with caution in shared environments

2. **Markdown Output**
   - Check for sensitive data before committing
   - Use `.gitignore` to prevent accidental commits

3. **JSON Output**
   - Validate redaction before sharing
   - Use secure channels for transmission

## API Key Management

### Environment Variables

Store API keys in environment variables:

```bash
# OpenAI
export TFSUMPY_OPENAI_API_KEY="your-key-here"

# Google Gemini
export TFSUMPY_GEMINI_API_KEY="your-key-here"

# Anthropic
export TFSUMPY_ANTHROPIC_API_KEY="your-key-here"
```

### Key Rotation

1. **Regular Rotation**
   - Rotate keys every 90 days
   - Update all environments simultaneously

2. **Emergency Rotation**
   - Revoke compromised keys immediately
   - Update environment variables
   - Check for unauthorized usage

### Key Storage

1. **Development**
   - Use `.env` files (gitignored)
   - Use secret management tools

2. **Production**
   - Use cloud secret management
   - Use container secrets
   - Use CI/CD secret storage

## Plugin Security

### Plugin Validation

1. **Source Verification**
   - Verify plugin source
   - Check plugin signatures
   - Review plugin code

2. **Permission Management**
   - Use least privilege
   - Restrict file access
   - Monitor plugin activity

### Plugin Dependencies

1. **Dependency Verification**
   - Use trusted sources
   - Check package signatures
   - Monitor for vulnerabilities

2. **Version Pinning**
   - Pin dependency versions
   - Regular security updates
   - Automated vulnerability scanning

## Best Practices

1. **Data Protection**
   - Never commit sensitive data
   - Use secure channels
   - Regular security audits

2. **Access Control**
   - Principle of least privilege
   - Regular access reviews
   - Audit logging

3. **Monitoring**
   - Monitor API usage
   - Track sensitive data
   - Log security events

4. **Incident Response**
   - Document procedures
   - Regular testing
   - Quick response plan

## Compliance

### Data Privacy

1. **GDPR**
   - Data minimization
   - Right to be forgotten
   - Data portability

2. **HIPAA**
   - PHI protection
   - Access controls
   - Audit trails

3. **PCI DSS**
   - Card data protection
   - Access monitoring
   - Regular testing

### Security Standards

1. **ISO 27001**
   - Risk management
   - Security controls
   - Regular audits

2. **SOC 2**
   - Security controls
   - Availability
   - Processing integrity

## Reporting Issues

Report security issues to:
1. Create a security advisory
2. Contact maintainers directly
3. Follow responsible disclosure

## Additional Resources

- [Security Policy](SECURITY.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Contributing Guidelines](CONTRIBUTING.md) 