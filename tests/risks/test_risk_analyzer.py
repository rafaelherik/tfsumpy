import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from tfsumpy.risk.analyzer import RiskAnalyzer
from tfsumpy.risk.models import ProviderRiskAnalyzer, RiskFinding, RiskReport
from tfsumpy.analyzer import AnalyzerResult

@pytest.fixture
def mock_provider_analyzer():
    """Create a mock provider-specific analyzer."""
    analyzer = Mock(spec=ProviderRiskAnalyzer)
    analyzer.provider = "aws"
    finding = RiskFinding(
        severity="high",
        message="Security group too permissive",
        resource_id="aws_security_group.test",
        impact="Potential unauthorized access",
        mitigation="Restrict access to specific IPs"
    )
    analyzer.analyze.return_value = [finding]
    return analyzer

@pytest.fixture
def risk_analyzer():
    """Create RiskAnalyzer instance with mocked provider loading."""
    with patch('tfsumpy.risk.analyzer.RiskAnalyzer._load_provider_analyzers'):
        return RiskAnalyzer()

@pytest.fixture
def sample_context():
    """Create a mock context with plan data."""
    context = Mock()
    context.get_plan_data.return_value = {
        "resources": [
            {
                "resource_type": "aws_security_group",
                "identifier": "test_sg",
                "changes": {"ingress": "modified"}
            }
        ]
    }
    return context

class TestRiskAnalyzer:
    def test_category_property(self, risk_analyzer):
        """Test category property returns correct value."""
        assert risk_analyzer.category == "risk"

    def test_provider_loading(self):
        """Test dynamic provider analyzer loading."""
        with patch('pkgutil.iter_modules') as mock_iter_modules:
            mock_module_info = MagicMock()
            mock_module_info.name = 'aws'
            mock_iter_modules.return_value = [mock_module_info]

            class MockAWSAnalyzer(ProviderRiskAnalyzer):
                @property
                def provider(self):
                    return 'aws'
                
                def analyze(self, resource):
                    return []

            mock_module = MagicMock()
            mock_module.AWSAnalyzer = MockAWSAnalyzer
            
            with patch('importlib.import_module') as mock_import:
                mock_import.return_value = mock_module
                with patch('pathlib.Path.exists', return_value=True):
                    analyzer = RiskAnalyzer()
                    assert len(analyzer.provider_analyzers) == 1
                    assert 'aws' in analyzer.provider_analyzers

    def test_analyze_with_provider(self, risk_analyzer, mock_provider_analyzer, sample_context):
        """Test analysis with available provider analyzer."""
        risk_analyzer.provider_analyzers['aws'] = mock_provider_analyzer
        result = risk_analyzer.analyze(sample_context)

        assert isinstance(result, AnalyzerResult)
        assert isinstance(result.data, RiskReport)
        assert len(result.data.findings) == 1
        finding = result.data.findings[0]
        assert finding.severity == "high"
        assert finding.resource_id == "aws_security_group.test"

        mock_provider_analyzer.analyze.assert_called_once()

    def test_analyze_without_provider(self, risk_analyzer, sample_context):
        """Test analysis when provider analyzer is not available."""
        with patch('logging.Logger.warning') as mock_warning:
            result = risk_analyzer.analyze(sample_context)
            assert isinstance(result, AnalyzerResult)
            assert isinstance(result.data, RiskReport)
            assert len(result.data.findings) == 0
            mock_warning.assert_called_once()

    def test_provider_detection(self, risk_analyzer):
        """Test provider detection from resource type."""
        assert risk_analyzer._get_provider_from_resource('aws_vpc') == 'aws'
        assert risk_analyzer._get_provider_from_resource('azurerm_resource_group') == 'azurerm'
        assert risk_analyzer._get_provider_from_resource('invalid') == ''

    def test_error_handling(self, risk_analyzer, sample_context):
        """Test error handling during analysis."""
        mock_provider_analyzer = Mock(spec=ProviderRiskAnalyzer)
        mock_provider_analyzer.analyze.side_effect = Exception("Test error")
        risk_analyzer.provider_analyzers['aws'] = mock_provider_analyzer
        
        with patch('logging.Logger.error') as mock_error:
            result = risk_analyzer.analyze(sample_context)
            assert isinstance(result, AnalyzerResult)
            assert len(result.data.findings) == 0
            mock_error.assert_called()

    def test_multiple_providers(self, risk_analyzer, sample_context):
        """Test analysis with multiple provider analyzers."""
        sample_context.get_plan_data.return_value = {
            'resources': [
                {
                    'resource_type': 'aws_resource',
                    'identifier': 'aws_1',
                    'changes': {}
                },
                {
                    'resource_type': 'azure_resource',
                    'identifier': 'azure_1',
                    'changes': {}
                }
            ]
        }

        aws_analyzer = Mock(spec=ProviderRiskAnalyzer)
        aws_analyzer.provider = 'aws'
        aws_analyzer.analyze.return_value = [
            RiskFinding(
                severity="high",
                message="AWS finding",
                resource_id="aws_1",
                impact="High impact",
                mitigation="Fix it"
            )
        ]

        azure_analyzer = Mock(spec=ProviderRiskAnalyzer)
        azure_analyzer.provider = 'azure'
        azure_analyzer.analyze.return_value = [
            RiskFinding(
                severity="medium",
                message="Azure finding",
                resource_id="azure_1",
                impact="Medium impact",
                mitigation="Fix it"
            )
        ]

        risk_analyzer.provider_analyzers = {
            'aws': aws_analyzer,
            'azure': azure_analyzer
        }

        result = risk_analyzer.analyze(sample_context)
        assert isinstance(result.data, RiskReport)
        assert len(result.data.findings) == 2
        
        findings_by_severity = {f.severity: f for f in result.data.findings}
        assert "high" in findings_by_severity
        assert "medium" in findings_by_severity

    def test_invalid_resource_data(self, risk_analyzer):
        """Test handling of invalid resource data scenarios."""
        # Test completely invalid resource
        context = Mock()
        context.get_plan_data.return_value = {
            'resources': [
                None,  # Invalid resource
                {},    # Empty resource
                {'invalid_key': 'value'},  # Missing required fields
                {      # Valid resource for comparison
                    'resource_type': 'aws_s3_bucket',
                    'identifier': 'test_bucket',
                    'changes': {}
                }
            ]
        }
        
        with patch('logging.Logger.warning') as mock_error:
            result = risk_analyzer.analyze(context)
            assert isinstance(result, AnalyzerResult)
            assert isinstance(result.data, RiskReport)
            assert len(result.data.findings) == 0  # No findings for invalid resources
            # Should log errors for the three invalid resources
            assert mock_error.call_count >= 3

    def test_invalid_plan_data(self, risk_analyzer):
        """Test handling of invalid plan data format."""
        test_cases = [
            (None, "Invalid plan data"),
            ({}, "Missing resources key"),
            ({'resources': None}, "Invalid resources data"),
            ({'resources': "not_a_list"}, "Invalid resources format"),
        ]
        
        for plan_data, case_desc in test_cases:
            context = Mock()
            context.get_plan_data.return_value = plan_data
            
            with patch('logging.Logger.error') as mock_error:
                result = risk_analyzer.analyze(context)
                assert isinstance(result, AnalyzerResult)
                assert len(result.data.findings) == 0
                mock_error.assert_called()
            
    def test_malformed_resource_type(self, risk_analyzer):
        """Test handling of malformed resource types."""
        context = Mock()
        context.get_plan_data.return_value = {
            'resources': [
                {
                    'resource_type': '',  # Empty resource type
                    'identifier': 'test_1'
                },
                {
                    'resource_type': 'invalid',  # No provider prefix
                    'identifier': 'test_2'
                },
                {
                    'resource_type': None,  # None resource type
                    'identifier': 'test_3'
                }
            ]
        }
        
        with patch('logging.Logger.warning') as mock_warning:
            result = risk_analyzer.analyze(context)
            assert isinstance(result, AnalyzerResult)
            assert len(result.data.findings) == 0
            assert mock_warning.call_count >= 3

    def test_provider_analyzer_error(self, risk_analyzer):
        """Test handling of provider analyzer errors."""
        context = Mock()
        context.get_plan_data.return_value = {
            'resources': [
                {
                    'resource_type': 'aws_s3_bucket',
                    'identifier': 'test_bucket',
                    'changes': {}
                }
            ]
        }
        
        mock_analyzer = Mock(spec=ProviderRiskAnalyzer)
        mock_analyzer.analyze.side_effect = Exception("Provider analyzer error")
        risk_analyzer.provider_analyzers['aws'] = mock_analyzer
        
        with patch('logging.Logger.error') as mock_error:
            result = risk_analyzer.analyze(context)
            assert isinstance(result, AnalyzerResult)
            assert len(result.data.findings) == 0
            mock_error.assert_called_with(
                "Provider analyzer error for test_bucket: Provider analyzer error"
            )

    def test_empty_plan_data(self, risk_analyzer):
        """Test handling of empty plan data."""
        context = Mock()
        context.get_plan_data.return_value = {'resources': []}
        
        result = risk_analyzer.analyze(context)
        assert isinstance(result, AnalyzerResult)
        assert len(result.data.findings) == 0

    def test_provider_loading_error(self, risk_analyzer):
        """Test handling of provider loading errors."""
        with patch('pathlib.Path.exists', return_value=False):
            with patch('logging.Logger.error') as mock_error:
                risk_analyzer._load_provider_analyzers()
                mock_error.assert_called_once() 