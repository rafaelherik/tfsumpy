import pytest
from bolwerk.policy.evaluator import PolicyEvaluator
from bolwerk.policy.models import PolicyResult

@pytest.fixture
def evaluator():
    """Create PolicyEvaluator instance."""
    return PolicyEvaluator()

@pytest.fixture
def sample_resource():
    """Create a sample resource for testing."""
    return {
        "id": "test_resource",
        "resource_type": "aws_s3_bucket",
        "tags": {"environment": "production"},
        "encryption": "AES256",
        "versioning": True,
        "count": 2,
        "planned_change": {
            "tags": "modify",
            "encryption": "no_change"
        }
    }

class TestPolicyEvaluator:
    def test_evaluate_disabled_policy(self, evaluator, sample_resource):
        """Test evaluation of disabled policy."""
        policy = {
            "id": "TEST001",
            "disabled": True,
            "severity": "high"
        }
        
        result = evaluator.evaluate(policy, sample_resource)
        assert isinstance(result, PolicyResult)
        assert result.compliant
        assert result.message == "Policy is disabled"

    def test_attribute_check_exists(self, evaluator, sample_resource):
        """Test attribute existence check."""
        policy = {
            "id": "TEST002",
            "severity": "high",
            "condition": {
                "type": "attribute_check",
                "parameters": {
                    "attribute": "encryption",
                    "exists": True
                }
            }
        }
        
        result = evaluator.evaluate(policy, sample_resource)
        assert result.compliant
        assert "exists" in result.message.lower()

    def test_attribute_check_value(self, evaluator, sample_resource):
        """Test attribute value check."""
        policy = {
            "id": "TEST003",
            "severity": "high",
            "condition": {
                "type": "attribute_check",
                "parameters": {
                    "attribute": "encryption",
                    "value": "AES256"
                }
            }
        }
        
        result = evaluator.evaluate(policy, sample_resource)
        assert result.compliant
        assert "matches expected value" in result.message

    def test_attribute_change_check(self, evaluator, sample_resource):
        """Test attribute change check."""
        policy = {
            "id": "TEST004",
            "severity": "medium",
            "condition": {
                "type": "attribute_change",
                "parameters": {
                    "attribute": "tags",
                    "allowed_changes": ["modify", "no_change"]
                }
            }
        }
        
        result = evaluator.evaluate(policy, sample_resource)
        assert result.compliant
        assert "is allowed" in result.message

    def test_resource_count_check(self, evaluator, sample_resource):
        """Test resource count check."""
        policy = {
            "id": "TEST005",
            "severity": "low",
            "condition": {
                "type": "resource_count",
                "parameters": {
                    "max_count": 3,
                    "min_count": 1
                }
            }
        }
        
        result = evaluator.evaluate(policy, sample_resource)
        assert result.compliant
        assert "within allowed range" in result.message

    def test_invalid_condition_type(self, evaluator, sample_resource):
        """Test handling of invalid condition type."""
        policy = {
            "id": "TEST006",
            "severity": "high",
            "condition": {
                "type": "invalid_type",
                "parameters": {}
            }
        }
        
        result = evaluator.evaluate(policy, sample_resource)
        assert not result.compliant
        assert "Unsupported condition type" in result.message

    def test_missing_required_fields(self, evaluator, sample_resource):
        """Test handling of missing required fields."""
        policy = {
            "id": "TEST007",
            "severity": "high",
            "condition": {}  # Missing type and parameters
        }
        
        result = evaluator.evaluate(policy, sample_resource)
        assert not result.compliant
        assert "Missing field" in result.message

    def test_attribute_not_found(self, evaluator, sample_resource):
        """Test handling of non-existent attribute."""
        policy = {
            "id": "TEST008",
            "severity": "high",
            "condition": {
                "type": "attribute_check",
                "parameters": {
                    "attribute": "nonexistent_attr",
                    "value": "some_value"
                }
            }
        }
        
        result = evaluator.evaluate(policy, sample_resource)
        assert not result.compliant
        assert "not found" in result.message

    @pytest.mark.parametrize("count,max_count,min_count,expected_compliant", [
        (1, 2, None, True),    # Only max_count
        (3, 2, None, False),   # Exceeds max_count
        (2, None, 1, True),    # Only min_count
        (0, None, 1, False),   # Below min_count
        (2, 3, 1, True),       # Within range
        (4, 3, 1, False),      # Above range
        (0, 3, 1, False),      # Below range
    ])
    def test_resource_count_variations(self, evaluator, sample_resource, 
                                     count, max_count, min_count, expected_compliant):
        """Test various resource count scenarios."""
        sample_resource["count"] = count
        policy = {
            "id": "TEST009",
            "severity": "medium",
            "condition": {
                "type": "resource_count",
                "parameters": {
                    **({"max_count": max_count} if max_count is not None else {}),
                    **({"min_count": min_count} if min_count is not None else {})
                }
            }
        }
        
        result = evaluator.evaluate(policy, sample_resource)
        assert result.compliant == expected_compliant 