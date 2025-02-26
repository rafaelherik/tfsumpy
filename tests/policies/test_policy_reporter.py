import pytest
from unittest.mock import Mock, patch
from colorama import Fore, Style, init
from bolwerk.policy.reporter import PolicyReporter
from bolwerk.policy.models import PolicyResult, PolicyReport

@pytest.fixture
def reporter():
    """Create PolicyReporter instance."""
    init()  # Initialize colorama
    return PolicyReporter()

@pytest.fixture
def sample_findings():
    """Create sample policy findings."""
    return [
        PolicyResult(
            policy_id="TEST001",
            resource_id="resource1",
            severity="high",
            message="Encryption not enabled",
            compliant=False,
            remediation="Enable encryption"
        ),
        PolicyResult(
            policy_id="TEST002",
            resource_id="resource2",
            severity="medium",
            message="Tags missing",
            compliant=False,
            remediation="Add required tags"
        ),
        PolicyResult(
            policy_id="TEST003",
            resource_id="resource3",
            severity="low",
            message="Non-compliant configuration",
            compliant=False,
            remediation="Update configuration"
        )
    ]

class TestPolicyReporter:
    def test_category_property(self, reporter):
        """Test category property returns correct value."""
        assert reporter.category == "policy"

    def test_get_report_empty(self, reporter):
        """Test getting report with no findings."""
        data = PolicyReport(findings=[])
        result = reporter.get_report(data)
        assert result == data
        assert isinstance(result, PolicyReport)

    def test_get_report_with_findings(self, reporter, sample_findings):
        """Test getting report with violations."""
        data = PolicyReport(findings=sample_findings)
        result = reporter.get_report(data)
        assert result == data
        assert isinstance(result, PolicyReport)

    def test_invalid_report_type(self, reporter):
        """Test handling of invalid report type."""
        with pytest.raises(TypeError, match="Expected PolicyReport instance"):
            reporter.get_report({"invalid": "data"})

    def test_print_empty_report(self, reporter):
        """Test printing report with no findings."""
        data = PolicyReport(findings=[])
        reporter.print_report(data)

    def test_print_report_with_findings(self, reporter, sample_findings):
        """Test printing report with violations."""
        data = PolicyReport(findings=sample_findings)
        reporter.print_report(data)

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup method to ensure consistent test environment."""
        self.print_patcher = patch('builtins.print')
        self.mock_print = self.print_patcher.start()
        yield
        self.print_patcher.stop() 