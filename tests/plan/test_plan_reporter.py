import pytest
from unittest.mock import Mock, patch
from bolwerk.plan.reporter import PlanReporter
import re

@pytest.fixture
def reporter():
    """Create PlanReporter instance."""
    return PlanReporter()

@pytest.fixture
def sample_report_data():
    """Create sample report data."""
    return {
        "total_changes": 3,
        "change_breakdown": {
            "create": 1,
            "update": 1,
            "delete": 1
        },
        "resources": [
            {
                "action": "create",
                "resource_type": "aws_s3_bucket",
                "identifier": "data_bucket",
                "before": {},
                "after": {"bucket": "new-bucket"}
            },
            {
                "action": "update",
                "resource_type": "aws_instance",
                "identifier": "web_server",
                "before": {"instance_type": "t2.micro"},
                "after": {"instance_type": "t2.small"}
            },
            {
                "action": "delete",
                "resource_type": "aws_security_group",
                "identifier": "old_sg",
                "before": {"name": "old-sg"},
                "after": {}
            }
        ]
    }

class TestPlanReporter:
    def test_category_property(self, reporter):
        """Test category property returns correct value."""
        assert reporter.category == "plan"

    def test_get_report_valid(self, reporter, sample_report_data):
        """Test getting valid report."""
        result = reporter.get_report(sample_report_data)
        assert result == sample_report_data
        assert isinstance(result, dict)
        assert 'total_changes' in result

    def test_get_report_invalid_format(self, reporter):
        """Test getting report with invalid format."""
        with pytest.raises(ValueError, match="Invalid report format"):
            reporter.get_report({"invalid": "data"})

    def test_get_report_none(self, reporter):
        """Test getting report with None data."""
        with pytest.raises(ValueError, match="Invalid report format"):
            reporter.get_report(None)

    def test_print_report_basic(self, reporter, sample_report_data):
        """Test basic report printing without details."""
        with patch.object(reporter, '_write') as mock_write:
            reporter.print_report(sample_report_data)
            
            # Collect all written strings
            written_text = ''.join(call[0][0] for call in mock_write.call_args_list)
            
            # Verify content - without color/severity expectations
            assert 'Terraform Plan Analysis' in written_text
            assert 'Total Changes: 3' in written_text
            assert 'Create: 1' in written_text
            assert 'Update: 1' in written_text
            assert 'Delete: 1' in written_text

    def test_print_report_with_details(self, reporter, sample_report_data):
        """Test report printing with resource details."""
        def strip_ansi(text):
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            return ansi_escape.sub('', text)

        with patch.object(reporter, '_write') as mock_write:
            reporter.print_report(sample_report_data, show_details=True)
            
            # Collect all written strings and strip ANSI codes
            written_text = strip_ansi(''.join(call[0][0] for call in mock_write.call_args_list))
            
            # Verify resource details without color expectations
            for expected in [
                'CREATE aws_s3_bucket: data_bucket',
                'UPDATE aws_instance: web_server',
                'DELETE aws_security_group: old_sg'
            ]:
                assert expected in written_text

    def test_print_report_with_changes(self, reporter, sample_report_data):
        """Test report printing with attribute changes."""
        with patch.object(reporter, '_write') as mock_write:
            reporter.print_report(sample_report_data, show_changes=True)
            
            # Verify attribute changes
            assert any("instance_type" in call[0][0] 
                      for call in mock_write.call_args_list)
            assert any("t2.micro -> t2.small" in call[0][0] 
                      for call in mock_write.call_args_list)

    def test_invalid_report_format(self, reporter):
        """Test handling of invalid report format."""
        with pytest.raises(ValueError, match="Invalid report format"):
            reporter.print_report({"invalid": "data"})

    def test_missing_resource_details(self, reporter):
        """Test handling of missing resource details."""
        data = {
            "total_changes": 1,
            "change_breakdown": {"create": 1, "update": 0, "delete": 0}
        }
        
        with pytest.raises(ValueError, match="Report missing resource details"):
            reporter.print_report(data, show_details=True)

    def test_attribute_changes_formatting(self, reporter):
        """Test attribute changes formatting."""
        # Helper function to strip ANSI escape codes
        def strip_ansi(text):
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            return ansi_escape.sub('', text)

        resource = {
            "action": "update",
            "before": {"name": "old", "tags": {"env": "dev"}},
            "after": {"name": "new", "tags": {"env": "prod"}},
        }
        
        with patch.object(reporter, '_write') as mock_write:
            reporter._print_attribute_changes(resource)
            
            # Get the written text and strip ANSI codes
            written_text = ''.join(call[0][0] for call in mock_write.call_args_list)
            clean_text = strip_ansi(written_text)
            
            # Now we can assert against the clean text
            assert "  ~ name = old -> new" in clean_text

    def test_color_output(self, reporter, sample_report_data):
        """Test color formatting in output."""
        with patch.object(reporter, '_write') as mock_write:
            reporter.print_report(sample_report_data)
            
            # Verify color codes are included
            assert any("\033[" in call[0][0] for call in mock_write.call_args_list)

    @patch('logging.Logger.error')
    def test_error_handling(self, mock_logger, reporter):
        """Test error handling during report generation."""
        with pytest.raises(Exception):
            reporter.print_report(None)
        mock_logger.assert_called()

    def test_skip_internal_attributes(self, reporter):
        """Test skipping of internal attributes in changes."""
        resource = {
            "action": "update",
            "before": {"id": "123", "tags_all": {}, "name": "old"},
            "after": {"id": "456", "tags_all": {}, "name": "new"},
        }
        
        with patch.object(reporter, '_write') as mock_write:
            reporter._print_attribute_changes(resource)
            
            # Verify internal attributes are skipped
            assert not any("id" in call[0][0] for call in mock_write.call_args_list)
            assert not any("tags_all" in call[0][0] for call in mock_write.call_args_list)
            assert any("name" in call[0][0] for call in mock_write.call_args_list)

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup method to ensure consistent test environment."""
        # Disable actual printing during tests
        self.print_patcher = patch('builtins.print')
        self.mock_print = self.print_patcher.start()
        yield
        self.print_patcher.stop() 