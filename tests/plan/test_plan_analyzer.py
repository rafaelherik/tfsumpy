import pytest
import json
from unittest.mock import Mock, patch, mock_open
from bolwerk.plan.analyzer import PlanAnalyzer
from bolwerk.analyzer import AnalyzerResult
from bolwerk.resource import ResourceChange

@pytest.fixture
def mock_context():
    """Create a mock context with sensitive patterns."""
    context = Mock()
    # Create a mock regex that only replaces sensitive patterns
    mock_pattern = Mock()
    mock_pattern.sub = lambda pattern, text: text  # Don't modify text by default
    context.sensitive_patterns = [(mock_pattern, "***")]
    return context

@pytest.fixture
def analyzer(mock_context):
    """Create PlanAnalyzer instance."""
    return PlanAnalyzer(mock_context)

@pytest.fixture
def sample_plan_json():
    """Create sample Terraform plan JSON."""
    return {
        "resource_changes": [
            {
                "address": "aws_s3_bucket.data",
                "type": "aws_s3_bucket",
                "change": {
                    "actions": ["create"],
                    "before": None,
                    "after": {"bucket": "test-bucket"},
                    "before_sensitive": {}
                }
            },
            {
                "address": "module.storage.aws_s3_bucket.logs",
                "type": "aws_s3_bucket",
                "change": {
                    "actions": ["update"],
                    "before": {"bucket": "old-name"},
                    "after": {"bucket": "new-name"},
                    "before_sensitive": {"secret": True}
                }
            },
            {
                "address": "aws_instance.server",
                "type": "aws_instance",
                "change": {
                    "actions": ["delete"],
                    "before": {"instance_type": "t2.micro"},
                    "after": None,
                    "before_sensitive": {}
                }
            }
        ]
    }

class TestPlanAnalyzer:
    def test_category_property(self, analyzer):
        """Test category property returns correct value."""
        assert analyzer.category == "plan"

    def test_analyze_missing_plan_path(self, analyzer):
        """Test analysis with missing plan path."""
        with pytest.raises(ValueError, match="plan_path is required"):
            analyzer.analyze(Mock())

    def test_analyze_valid_plan(self, analyzer, sample_plan_json):
        """Test analysis of valid plan file."""
        plan_content = json.dumps(sample_plan_json)
        
        with patch("builtins.open", mock_open(read_data=plan_content)):
            result = analyzer.analyze(Mock(), plan_path="test.tfplan")
            
            assert isinstance(result, AnalyzerResult)
            assert result.category == "plan"
            assert result.data["total_changes"] == 3
            assert result.data["change_breakdown"] == {
                "create": 1,
                "update": 1,
                "delete": 1
            }

    def test_analyze_invalid_json(self, analyzer):
        """Test analysis with invalid JSON plan."""
        with patch("builtins.open", mock_open(read_data="invalid json")):
            with pytest.raises(ValueError, match="Invalid plan file format"):
                analyzer.analyze(Mock(), plan_path="test.tfplan")

    def test_parse_plan(self, analyzer, sample_plan_json):
        """Test plan parsing functionality."""
        changes = analyzer._parse_plan(json.dumps(sample_plan_json))
        
        assert len(changes) == 3
        assert all(isinstance(change, ResourceChange) for change in changes)
        
        # Verify specific changes
        create_change = next(c for c in changes if c.action == "create")
        assert create_change.resource_type == "aws_s3_bucket"
        
        update_change = next(c for c in changes if c.action == "update")
        assert update_change.module == "storage"
        
        delete_change = next(c for c in changes if c.action == "delete")
        assert delete_change.identifier == "aws_instance.server"

    def test_extract_module_name(self, analyzer):
        """Test module name extraction."""
        assert analyzer._extract_module_name("module.storage.aws_s3_bucket.logs") == "storage"
        assert analyzer._extract_module_name("module.a.module.b.resource") == "a.b"
        assert analyzer._extract_module_name("aws_s3_bucket.data") == "root"

    def test_sanitize_text(self, analyzer):
        """Test text sanitization."""
        text = "sensitive_text"
        sanitized = analyzer._sanitize_text(text)
        assert sanitized == text  # Mock pattern doesn't modify text

    def test_sanitize_sensitive_text(self, analyzer):
        """Test text sanitization with sensitive content."""
        context = Mock()
        # Create a mock regex that replaces 'secret' with '***'
        mock_pattern = Mock()
        mock_pattern.sub = lambda pattern, text: text.replace('secret', '***')
        context.sensitive_patterns = [(mock_pattern, "***")]
        analyzer.context = context
        
        assert analyzer._sanitize_text("my-secret-value") == "my-***-value"
        assert analyzer._sanitize_text("normal-text") == "normal-text"

    @patch('logging.Logger.error')
    def test_error_handling(self, mock_logger, analyzer):
        """Test error handling during analysis."""
        with patch("builtins.open", side_effect=Exception("Test error")):
            with pytest.raises(Exception):
                analyzer.analyze(Mock(), plan_path="test.tfplan")
            mock_logger.assert_called()

    def test_no_op_changes(self, analyzer):
        """Test handling of no-op changes."""
        plan_json = {
            "resource_changes": [
                {
                    "address": "aws_s3_bucket.data",
                    "type": "aws_s3_bucket",
                    "change": {
                        "actions": ["no-op"],
                        "before": {"bucket": "test"},
                        "after": {"bucket": "test"}
                    }
                }
            ]
        }
        
        changes = analyzer._parse_plan(json.dumps(plan_json))
        assert len(changes) == 0

    def test_complex_module_structure(self, analyzer):
        """Test handling of complex module structures."""
        address = "module.network.module.vpc.module.subnets.aws_subnet.private"
        module_name = analyzer._extract_module_name(address)
        assert module_name == "network.vpc.subnets"

    @patch('logging.Logger.debug')
    def test_debug_logging(self, mock_debug, analyzer, sample_plan_json):
        """Test debug logging during analysis."""
        plan_content = json.dumps(sample_plan_json)
        
        with patch("builtins.open", mock_open(read_data=plan_content)):
            analyzer.analyze(Mock(), plan_path="test.tfplan")
            assert mock_debug.called 