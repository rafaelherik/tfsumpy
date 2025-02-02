import pytest
from tfsumpy.policy import Policy
import tempfile

@pytest.mark.skip(reason="Policy feature currently disabled")
def test_policy_loader_valid_file(policy_loader, sample_policy_file):
    policy_loader.db_manager.clear_policies()  # Clear existing policies
    policy_loader.load_policy_file(sample_policy_file)
    policies = policy_loader.db_manager.get_policies(provider="aws")
    assert len(policies) == 1
    assert policies[0].id == "S3_VERSIONING"

@pytest.mark.skip(reason="Policy feature currently disabled")
def test_policy_loader_invalid_yaml(policy_loader):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as f:
        f.write("invalid: yaml: content")
        f.flush()
        with pytest.raises(Exception):
            policy_loader.load_policy_file(f.name)

@pytest.mark.skip(reason="Policy feature currently disabled")
def test_policy_db_operations(policy_db):
    policy_db.clear_policies()  # Clear existing policies
    policy = Policy(
        id="TEST_POLICY",
        name="Test Policy",
        description="Test Description",
        provider="aws",
        resource_type="aws_instance",
        severity="high",
        condition={"type": "attribute_check", "parameters": {}}
    )
    
    policy_db.add_policy(policy)
    policies = policy_db.get_policies(provider="aws")
    assert len(policies) == 1
    assert policies[0].id == "TEST_POLICY" 