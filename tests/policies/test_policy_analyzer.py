import pytest
from unittest.mock import Mock, patch
from bolwerk.policy.analyzer import PolicyAnalyzer, PolicyReport, PolicyResult
from bolwerk.analyzer import AnalyzerResult

@pytest.fixture
def mock_db_manager():
    """Create a mock database manager."""
    return Mock()

@pytest.fixture
def analyzer(mock_db_manager):
    """Create PolicyAnalyzer instance with mock dependencies."""
    return PolicyAnalyzer(mock_db_manager)

@pytest.fixture
def sample_context():
    """Create a mock context with plan data."""
    context = Mock()
    context.get_plan_data.return_value = {
        "resources": [
            {
                "identifier": "test_resource_1",
                "resource_type": "aws_s3_bucket",
                "provider": "aws"
            },
            {
                "identifier": "test_resource_2",
                "resource_type": "aws_instance",
                "provider": "aws"
            }
        ]
    }
    return context

class TestPolicyAnalyzer:
    def test_category_property(self, analyzer):
        """Test category property returns correct value."""
        assert analyzer.category == "policy"

    def test_analyze_empty_plan(self, analyzer):
        """Test analyzing empty plan data."""
        context = Mock()
        context.get_plan_data.return_value = {"resources": []}
        
        result = analyzer.analyze(context)
        assert isinstance(result, AnalyzerResult)
        assert isinstance(result.data, PolicyReport)
        assert len(result.data.findings) == 0

    def test_analyze_with_resources(self, analyzer, sample_context, mock_db_manager):
        """Test analyzing plan with resources."""
        # Mock database query results
        mock_db_manager.execute_query.return_value = [{
            "id": "TEST001",
            "severity": "high",
            "condition": {
                "type": "attribute_check",
                "parameters": {"attribute": "encryption", "value": "AES256"}
            }
        }]

        result = analyzer.analyze(sample_context)
        assert isinstance(result, AnalyzerResult)
        assert isinstance(result.data, PolicyReport)
        
        # Verify DB was queried for each resource
        assert mock_db_manager.execute_query.call_count == 2

    def test_provider_detection(self, analyzer):
        """Test cloud provider detection from resource type."""
        assert analyzer._detect_provider("aws_s3_bucket") == "aws"
        assert analyzer._detect_provider("azurerm_resource_group") == "azure"
        assert analyzer._detect_provider("google_storage_bucket") == "gcp"
        assert analyzer._detect_provider("unknown_type") == "unknown"

    def test_evaluate_resource_error_handling(self, analyzer, mock_db_manager):
        """Test error handling during resource evaluation."""
        # Mock database error
        mock_db_manager.execute_query.side_effect = Exception("Database error")
        
        resource = {
            "identifier": "test_resource",
            "resource_type": "aws_s3_bucket"
        }
        
        results = analyzer._evaluate_resource(resource)
        assert len(results) == 0  # Should handle error gracefully

    @patch('logging.Logger.error')
    def test_logging_on_error(self, mock_logger, analyzer, mock_db_manager):
        """Test error logging during analysis."""
        mock_db_manager.execute_query.side_effect = Exception("Test error")
        
        resource = {
            "identifier": "test_resource",
            "resource_type": "aws_s3_bucket"
        }
        
        analyzer._evaluate_resource(resource)
        mock_logger.assert_called() 