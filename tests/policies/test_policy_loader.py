import pytest
import yaml
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch
from bolwerk.policy.loader import PolicyLoader
from jsonschema import ValidationError

@pytest.fixture
def mock_db_manager():
    """Create a mock database manager."""
    return Mock()

@pytest.fixture
def loader(mock_db_manager):
    """Create PolicyLoader instance with mock dependencies."""
    return PolicyLoader(mock_db_manager)

@pytest.fixture
def valid_policy_yaml():
    """Create a valid policy YAML content."""
    return """
    provider: aws
    policies:
      - id: TEST001
        name: S3 Bucket Encryption
        description: Ensure S3 buckets have encryption enabled
        severity: high
        provider: aws
        resource_type: aws_s3_bucket
        condition:
          type: attribute_check
          parameters:
            attribute: encryption
            value: AES256
        remediation: Enable encryption using AES256
    """

@pytest.fixture
def invalid_policy_yaml():
    """Create an invalid policy YAML content."""
    return """
    provider: invalid_provider
    policies:
      - id: TEST001
        severity: invalid_severity
        provider: aws
    """

@pytest.fixture
def invalid_yaml():
    """Create an invalid YAML syntax."""
    return """
    provider: aws
    policies: [
      invalid yaml
      syntax error
    """

class TestPolicyLoader:
    def test_initialization(self, loader):
        """Test PolicyLoader initialization."""
        assert loader.db_manager is not None
        assert loader.schema is not None

    def test_load_valid_policy(self, loader, valid_policy_yaml, tmp_path):
        """Test loading valid policy file."""
        policy_file = tmp_path / "test_policy.yaml"
        policy_file.write_text(valid_policy_yaml)
        
        loader._load_single_policy(str(policy_file))
        loader.db_manager.add_policy.assert_called_once()

    def test_load_invalid_policy_schema(self, loader, invalid_policy_yaml, tmp_path):
        """Test loading policy with invalid schema."""
        policy_file = tmp_path / "invalid_policy.yaml"
        policy_file.write_text(invalid_policy_yaml)
        
        with pytest.raises(ValidationError, match="is not one of"):
            loader._load_single_policy(str(policy_file))

    def test_load_invalid_yaml_syntax(self, loader, invalid_yaml, tmp_path):
        """Test loading file with invalid YAML syntax."""
        policy_file = tmp_path / "invalid.yaml"
        policy_file.write_text(invalid_yaml)
        
        with pytest.raises(yaml.YAMLError):
            loader._load_single_policy(str(policy_file))

    def test_load_policy_directory(self, loader, valid_policy_yaml, tmp_path):
        """Test loading policies from directory."""
        # Create multiple policy files
        for i in range(3):
            policy_file = tmp_path / f"policy_{i}.yaml"
            policy_file.write_text(valid_policy_yaml)
        
        loader.load_policy_directory(str(tmp_path))
        assert loader.db_manager.add_policy.call_count == 3

    def test_load_nonexistent_directory(self, loader):
        """Test loading from non-existent directory."""
        with pytest.raises(ValueError, match="Policy directory not found"):
            loader.load_policy_directory("/nonexistent/path")

    def test_load_empty_directory(self, loader, tmp_path):
        """Test loading from empty directory."""
        loader.load_policy_directory(str(tmp_path))
        assert not loader.db_manager.add_policy.called

    def test_load_mixed_valid_invalid_policies(self, loader, valid_policy_yaml, invalid_policy_yaml, tmp_path):
        """Test loading directory with mix of valid and invalid policies."""
        # Create valid policy
        (tmp_path / "valid.yaml").write_text(valid_policy_yaml)
        # Create invalid policy
        (tmp_path / "invalid.yaml").write_text(invalid_policy_yaml)
        
        loader.load_policy_directory(str(tmp_path))
        assert loader.db_manager.add_policy.call_count == 1

    @patch('logging.Logger.error')
    def test_error_logging(self, mock_logger, loader, invalid_yaml, tmp_path):
        """Test error logging during policy loading."""
        policy_file = tmp_path / "error_policy.yaml"
        policy_file.write_text(invalid_yaml)
        
        with pytest.raises(yaml.YAMLError):
            loader._load_single_policy(str(policy_file))
        mock_logger.assert_called() 