import pytest
from tfsumpy.report import PlanReporter
import sys
from io import StringIO

@pytest.fixture
def capture_stdout(monkeypatch):
    """Fixture to capture stdout for testing."""
    class StdoutCapture:
        def __init__(self):
            self.data = []
        
        def write(self, text):
            self.data.append(text)
        
        def flush(self):
            pass
        
        def getvalue(self):
            return ''.join(self.data)
    
    capture = StdoutCapture()
    monkeypatch.setattr(sys, 'stdout', capture)
    return capture

def test_report_generation(capture_stdout):
    """Test basic report generation with risks."""
    reporter = PlanReporter()
    sample_report = {
        'summary': {
            'total_changes': 1,
            'change_breakdown': {'create': 1, 'update': 0, 'delete': 0},
            'resources': [{
                'action': 'create',
                'resource_type': 'aws_s3_bucket',
                'identifier': 'example',
                'module': 'root',
                'before': {},
                'after': {'versioning': False}
            }]
        },
        'risks': {
            'high': ['S3 bucket versioning is not enabled'],
            'medium': []
        }
    }
    
    result = reporter.print_report(sample_report)
    
    # Test the returned structured data
    assert result['header'] == 'Infrastructure Change Analysis'
    assert result['change_summary']['total_changes'] == 1
    assert result['change_summary']['changes']['create'] == 1
    assert len(result['resource_details']) == 1
    assert result['resource_details'][0]['action'] == 'create'
    assert result['resource_details'][0]['type'] == 'aws_s3_bucket'
    assert result['risk_assessment']['high'] == ['S3 bucket versioning is not enabled']

def test_report_with_modules(capture_stdout):
    reporter = PlanReporter()
    sample_report = {
        'summary': {
            'total_changes': 2,
            'change_breakdown': {'create': 2, 'update': 0, 'delete': 0},
            'resources': [{
                'action': 'create',
                'resource_type': 'aws_s3_bucket',
                'identifier': 'example1',
                'module': 'module1',
                'before': {},
                'after': {}
            }, {
                'action': 'create',
                'resource_type': 'aws_s3_bucket',
                'identifier': 'example2',
                'module': 'module2',
                'before': {},
                'after': {}
            }]
        },
        'risks': {'high': [], 'medium': []}
    }
    
    result = reporter.print_report(sample_report, show_module=True)
    
    # Test the returned structured data
    assert result['header'] == 'Infrastructure Change Analysis'
    assert len(result['resource_details']) == 2
    assert result['resource_details'][0]['module'] == 'module1'
    assert result['resource_details'][1]['module'] == 'module2'
    assert result['change_summary']['total_changes'] == 2 