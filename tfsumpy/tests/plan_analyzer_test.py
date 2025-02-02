import pytest
from pathlib import Path
from tfsumpy.plan_analyzer import LocalPlanAnalyzer
from tfsumpy.context import Context
import json

@pytest.fixture
def sample_plan_path():
    return str(Path(__file__).parent / 'sample1.json')

@pytest.fixture
def context():
    """Create a test context with default configuration"""
    return Context(debug=True)

@pytest.fixture
def plan_analyzer(context):
    """Create a plan analyzer with test context"""
    return LocalPlanAnalyzer(context=context)

def test_generate_report(plan_analyzer, sample_plan_path):
    """Test report generation with sample plan"""
    report = plan_analyzer.generate_report(sample_plan_path)
    
    # Test summary statistics
    assert report['summary']['total_changes'] == 3
    assert report['summary']['change_breakdown'] == {
        'create': 1,  # aws_s3_bucket.example
        'update': 1,  # aws_instance.web_server
        'delete': 1   # aws_security_group.obsolete
    }
    
    # Test resource details
    resources = report['summary']['resources']
    assert len(resources) == 3
    
    # Verify S3 bucket creation
    s3_resource = next(r for r in resources if r['resource_type'] == 'aws_s3_bucket')
    assert s3_resource['action'] == 'create'
    assert 'example' in s3_resource['identifier']
    assert s3_resource['module'] == 'root'  # Test module information
    
    # Verify EC2 instance update
    ec2_resource = next(r for r in resources if r['resource_type'] == 'aws_instance')
    assert ec2_resource['action'] == 'update'
    assert 'web_server' in ec2_resource['identifier']
    assert ec2_resource['module'] == 'root'
    
    # Verify security group deletion
    sg_resource = next(r for r in resources if r['resource_type'] == 'aws_security_group')
    assert sg_resource['action'] == 'delete'
    assert 'obsolete' in sg_resource['identifier']
    assert sg_resource['module'] == 'root'

def test_sanitization(plan_analyzer):
    """Test text sanitization with sensitive data"""
    sensitive_text = """
    {
        "access_key": "AKIAXXXXXXXXXXXXXXXX",
        "secret": "super_secret_value",
        "ip": "192.168.1.1"
    }
    """
    sanitized = plan_analyzer._sanitize_text(sensitive_text)
    
    assert 'AKIAXXXXXXXXXXXXXXXX' not in sanitized
    assert '[AWS-KEY-REDACTED]' in sanitized
    assert 'super_secret_value' not in sanitized
    assert '[SECRET-REDACTED]' in sanitized
    assert '192.168.1.1' not in sanitized
    assert '[IP-REDACTED]' in sanitized

def test_module_handling(plan_analyzer, tmp_path):
    """Test handling of module-based resources"""
    # Create a sample plan with module resources
    module_plan = {
        "resource_changes": [
            {
                "address": "module.network.aws_vpc.main",
                "type": "aws_vpc",
                "change": {"actions": ["create"]},
                "module": "network"
            }
        ]
    }
    
    plan_path = tmp_path / "module_plan.json"
    with open(plan_path, "w") as f:
        json.dump(module_plan, f)
    
    report = plan_analyzer.generate_report(str(plan_path))
    resources = report['summary']['resources']
    
    assert len(resources) == 1
    vpc_resource = resources[0]
    assert vpc_resource['module'] == 'network'
    assert vpc_resource['resource_type'] == 'aws_vpc'
    assert vpc_resource['action'] == 'create'
