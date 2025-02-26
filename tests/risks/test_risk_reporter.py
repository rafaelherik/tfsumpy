import pytest
from unittest.mock import Mock, patch
from bolwerk.risk.reporter import RiskReporter
from bolwerk.risk.models import RiskFinding, RiskReport

@pytest.fixture
def reporter():
    """Create RiskReporter instance."""
    return RiskReporter()

@pytest.fixture
def sample_findings():
    """Create sample risk findings."""
    return [
        RiskFinding(
            severity="high",
            message="Unencrypted storage",
            resource_id="aws_s3_bucket.data",
            impact="Data exposure",
            mitigation="Enable encryption"
        ),
        RiskFinding(
            severity="medium",
            message="Public access enabled",
            resource_id="aws_security_group.public",
            impact="Unauthorized access",
            mitigation="Restrict access"
        ),
        RiskFinding(
            severity="low",
            message="Missing tags",
            resource_id="aws_instance.server",
            impact="Resource management issues",
            mitigation="Add required tags"
        )
    ]

class TestRiskReporter:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup method to ensure consistent test environment."""
        self.print_patcher = patch('builtins.print')
        self.mock_print = self.print_patcher.start()
        yield
        self.print_patcher.stop()

    def test_category_property(self, reporter):
        """Test category property returns correct value."""
        assert reporter.category == "risk"

    def test_get_report_empty(self, reporter):
        """Test getting report with no findings."""
        data = RiskReport(findings=[])
        result = reporter.get_report(data)
        assert result == data
        assert isinstance(result, RiskReport)

    def test_get_report_with_findings(self, reporter, sample_findings):
        """Test getting report with findings."""
        data = RiskReport(findings=sample_findings)
        result = reporter.get_report(data)
        assert result == data
        assert isinstance(result, RiskReport)

    def test_invalid_report_type(self, reporter):
        """Test handling of invalid report type."""
        with pytest.raises(TypeError, match="Expected RiskReport instance"):
            reporter.get_report({"invalid": "data"})

    def test_print_empty_report(self, reporter):
        """Test printing report with no findings."""
        data = RiskReport(findings=[])
        with patch.object(reporter, '_write') as mock_write:
            reporter.print_report(data)
            assert any("No risks identified" in call[0][0] 
                      for call in mock_write.call_args_list)

    def test_print_report_with_findings(self, reporter, sample_findings):
        """Test printing report with findings."""
        data = RiskReport(findings=sample_findings)
        with patch.object(reporter, '_write') as mock_write:
            reporter.print_report(data)
            assert mock_write.called

    def test_summary_counts(self, reporter, sample_findings):
        """Test risk severity summary counting."""
        data = RiskReport(findings=sample_findings)
        
        with patch.object(reporter, '_write') as mock_write:
            reporter.print_report(data)
            
            # Verify counts for each severity
            assert any("HIGH: 1" in call[0][0] for call in mock_write.call_args_list)
            assert any("MEDIUM: 1" in call[0][0] for call in mock_write.call_args_list)
            assert any("LOW: 1" in call[0][0] for call in mock_write.call_args_list)

    def test_detailed_finding_format(self, reporter, sample_findings):
        """Test detailed finding output format."""
        data = RiskReport(findings=sample_findings)
        
        with patch.object(reporter, '_write') as mock_write:
            reporter.print_report(data)
            
            for finding in sample_findings:
                assert any(finding.message in call[0][0] 
                         for call in mock_write.call_args_list)
                assert any(finding.resource_id in call[0][0] 
                         for call in mock_write.call_args_list)
                assert any(finding.impact in call[0][0] 
                         for call in mock_write.call_args_list)
                assert any(finding.mitigation in call[0][0] 
                         for call in mock_write.call_args_list)

    def test_error_handling(self, reporter):
        """Test error handling during report generation."""
        data = Mock(spec=RiskReport)
        data.findings = None  # Invalid findings
        
        with patch('logging.Logger.error') as mock_error:
            reporter.print_report(data)
            mock_error.assert_called_once()
            
        # Test with findings attribute access error
        data = Mock(spec=RiskReport)
        delattr(data, 'findings')  # Remove findings attribute
        
        with patch('logging.Logger.error') as mock_error:
            reporter.print_report(data)
            mock_error.assert_called_once()

    def test_severity_case_handling(self, reporter):
        """Test handling of different severity case formats."""
        findings = [
            RiskFinding(
                severity="HIGH",
                message="Test high",
                resource_id="test.high",
                impact="High impact"
            ),
            RiskFinding(
                severity="medium",
                message="Test medium",
                resource_id="test.medium",
                impact="Medium impact"
            )
        ]
        data = RiskReport(findings=findings)
        
        with patch.object(reporter, '_write') as mock_write:
            reporter.print_report(data)
            assert any("HIGH: 1" in call[0][0] for call in mock_write.call_args_list)
            assert any("MEDIUM: 1" in call[0][0] for call in mock_write.call_args_list)

    def test_missing_optional_fields(self, reporter):
        """Test handling of findings with missing optional fields."""
        findings = [
            RiskFinding(
                severity="high",
                message="Test finding",
                resource_id="test.resource",
                impact=None,
                mitigation=None
            )
        ]
        data = RiskReport(findings=findings)
        
        with patch.object(reporter, '_write') as mock_write:
            reporter.print_report(data)
            assert mock_write.called
            # Verify optional fields are not printed
            assert not any("Impact:" in call[0][0] 
                         for call in mock_write.call_args_list)
            assert not any("Mitigation:" in call[0][0] 
                         for call in mock_write.call_args_list) 