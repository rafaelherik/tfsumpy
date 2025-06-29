import pytest
from unittest.mock import patch
from tfsumpy.plan.reporter import PlanReporter
import re
import json

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

def strip_ansi(text):
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
    return ansi_escape.sub('', text)

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
        with patch.object(reporter, '_write') as mock_write:
            reporter.print_report(sample_report_data, show_details=True)
            written_text = ''.join(call[0][0] for call in mock_write.call_args_list)
            plain_text = strip_ansi(written_text)
            for expected in [
                'CREATE aws_s3_bucket: data_bucket',
                'UPDATE aws_instance: web_server',
                'DELETE aws_security_group: old_sg'
            ]:
                assert expected in plain_text

    def test_print_report_with_changes(self, reporter, sample_report_data):
        """Test report printing with attribute changes."""
        with patch.object(reporter, '_write') as mock_write:
            reporter.print_report(sample_report_data, show_changes=True)
            
            # Verify attribute changes
            assert any("instance_type" in call[0][0] 
                      for call in mock_write.call_args_list)
            assert any("t2.micro -> t2.small" in call[0][0] 
                      for call in mock_write.call_args_list)

    def test_print_report_markdown(self, reporter, sample_report_data):
        """Test markdown report generation."""
        with patch.object(reporter, '_write') as mock_write:
            reporter.print_report_markdown(sample_report_data)
            written_text = ''.join(call[0][0] for call in mock_write.call_args_list)
            
            # Verify markdown structure
            assert '# Terraform Plan Analysis Report' in written_text
            assert '## Summary' in written_text
            assert '## Resource Changes' in written_text
            
            # Verify summary content
            assert '**Total Resources**: 3' in written_text
            assert '**Resources to Add**: 1' in written_text
            assert '**Resources to Change**: 1' in written_text
            assert '**Resources to Destroy**: 1' in written_text

    def test_print_report_markdown_with_details(self, reporter, sample_report_data):
        """Test markdown report with detailed information."""
        with patch.object(reporter, '_write') as mock_write:
            reporter.print_report_markdown(sample_report_data, show_details=True, show_changes=True)
            written_text = ''.join(call[0][0] for call in mock_write.call_args_list)
            
            # Verify detailed information
            assert '## Resource Changes' in written_text
            assert '#### Details for aws_s3_bucket.data_bucket' in written_text
            assert '#### Details for aws_instance.web_server' in written_text
            assert '#### Details for aws_security_group.old_sg' in written_text
            assert '**Provider**:' in written_text
            assert '**Module**:' in written_text
            # Dependencies is optional and only shown if they exist

    def test_print_report_json(self, reporter, sample_report_data):
        """Test JSON report generation."""
        with patch.object(reporter, '_write') as mock_write:
            reporter.print_report_json(sample_report_data)
            written_text = ''.join(call[0][0] for call in mock_write.call_args_list)
            
            # Parse JSON output
            json_data = json.loads(written_text)
            
            # Verify JSON structure
            assert 'metadata' in json_data
            assert 'summary' in json_data
            assert 'resources' in json_data
            
            # Verify metadata
            assert 'timestamp' in json_data['metadata']
            assert 'version' in json_data['metadata']
            
            # Verify summary
            assert json_data['summary']['total_resources'] == 3
            assert json_data['summary']['resources_to_add'] == 1
            assert json_data['summary']['resources_to_change'] == 1
            assert json_data['summary']['resources_to_destroy'] == 1
            
            # Verify resources
            assert len(json_data['resources']) == 3
            assert any(r['action'] == 'create' for r in json_data['resources'])
            assert any(r['action'] == 'update' for r in json_data['resources'])
            assert any(r['action'] == 'delete' for r in json_data['resources'])

    def test_print_report_json_with_details(self, reporter, sample_report_data):
        """Test JSON report with detailed information."""
        with patch.object(reporter, '_write') as mock_write:
            reporter.print_report_json(sample_report_data, show_details=True, show_changes=True)
            written_text = ''.join(call[0][0] for call in mock_write.call_args_list)
            json_data = json.loads(written_text)
            
            # Verify detailed information in JSON
            for resource in json_data['resources']:
                assert 'action' in resource
                assert 'module' in resource
                assert 'resource_type' in resource
                assert 'identifier' in resource
                assert 'provider' in resource
                
                if resource['action'] == 'update':
                    assert 'changes' in resource
                    assert 'details' in resource
                    assert 'raw' in resource['details']
                    assert 'before' in resource['details']['raw']
                    assert 'after' in resource['details']['raw']
                    
                    # Verify changes array
                    assert len(resource['changes']) > 0
                    for change in resource['changes']:
                        assert 'attribute' in change
                        assert 'before' in change
                        assert 'after' in change

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
        resource = {
            "action": "update",
            "before": {"name": "old", "tags": {"env": "dev"}},
            "after": {"name": "new", "tags": {"env": "prod"}},
        }
        with patch.object(reporter, '_write') as mock_write:
            reporter._print_attribute_changes(resource)
            written_text = ''.join(call[0][0] for call in mock_write.call_args_list)
            plain_text = strip_ansi(written_text)
            assert "~ name = old -> new" in plain_text

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