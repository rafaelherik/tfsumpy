import pytest
import json
import tempfile
from pathlib import Path
from tfsumpy.context import Context
from tfsumpy.policy import PolicyDBManager, PolicyLoader

@pytest.fixture
def policy_db():
    # Create a temporary database file
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    # Initialize DB manager with temp file
    db_manager = PolicyDBManager(db_path=db_path)
    
    yield db_manager
    
    # Cleanup after test
    try:
        Path(db_path).unlink()
    except FileNotFoundError:
        pass

@pytest.fixture
def test_context(policy_db):
    context = Context(debug=True)
    context.policy_db = policy_db
    return context

@pytest.fixture
def sample_plan_json():
    """Provide a sample plan with a versioning-enabled S3 bucket."""
    return {
        "resource_changes": [
            {
                "address": "aws_s3_bucket.example",
                "type": "aws_s3_bucket",
                "change": {
                    "actions": ["create"],
                    "before": None,
                    "after": {
                        "bucket": "example-bucket",
                        "versioning": False  # This should trigger the policy violation
                    },
                    "before_sensitive": {},
                    "after_sensitive": {}
                }
            }
        ]
    }

@pytest.fixture
def sample_plan_file(sample_plan_json):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_plan_json, f)
        return f.name

@pytest.fixture
def sample_policy_yaml():
    return """
version: "1.0.0"
policies:
  - id: S3_VERSIONING
    name: "S3 Bucket Versioning"
    description: "Ensure S3 buckets have versioning enabled"
    provider: "aws"
    resource_type: "aws_s3_bucket"
    severity: "high"
    condition:
      type: "attribute_check"
      parameters:
        attribute: "versioning"
        value: true
    remediation: "Enable versioning on the S3 bucket"
"""

@pytest.fixture
def sample_policy_file(sample_policy_yaml):
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
        f.write(sample_policy_yaml)
        return f.name

@pytest.fixture
def policy_loader(policy_db):
    return PolicyLoader(policy_db) 