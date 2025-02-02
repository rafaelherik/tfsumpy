import pytest
import json
import tempfile
from tfsumpy.context import Context

def test_context_initialization():
    context = Context(debug=True)
    assert context.debug is True
    assert context.config_path is None
    assert isinstance(context.sensitive_patterns, list)
    assert isinstance(context.risk_rules, dict)

def test_context_load_config():
    context = Context()
    context.load_config()
    assert context.sensitive_patterns
    assert context.risk_rules
    assert 'high' in context.risk_rules
    assert 'medium' in context.risk_rules

def test_context_merge_external_config():
    external_config = {
        "sensitive_patterns": [
            {"pattern": "test_pattern", "replacement": "***"}
        ],
        "risk_rules": {
            "high": [
                {"pattern": "test_rule", "message": "test message"}
            ]
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(external_config, f)
        config_path = f.name
    
    context = Context(config_path=config_path)
    context.load_config()
    
    assert any(pattern[0] == "test_pattern" for pattern in context.sensitive_patterns)
    assert any(rule[0] == "test_rule" for rule in context.risk_rules["high"]) 