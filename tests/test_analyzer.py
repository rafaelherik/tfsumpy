import pytest
from tfsumpy.plan_analyzer import LocalPlanAnalyzer
from tfsumpy.policy import Policy

def test_plan_analysis(test_context, sample_plan_file):
    analyzer = LocalPlanAnalyzer(context=test_context)
    report = analyzer.generate_report(sample_plan_file)
    
    assert 'summary' in report
    assert 'risks' in report
    assert report['summary']['total_changes'] == 1
    assert report['summary']['change_breakdown']['create'] == 1

def test_risk_analysis(test_context, sample_plan_file, policy_db):
    """Test that policy violations are correctly identified."""
    # Setup
    test_context.policy_db = policy_db
    policy_db.clear_policies()
    
    analyzer = LocalPlanAnalyzer(context=test_context)
    
    # Add test policy for S3 bucket versioning
    policy = Policy(
        id="TEST_POLICY",
        name="S3 Bucket Versioning",
        description="Ensure S3 buckets have versioning enabled",
        provider="aws",
        resource_type="aws_s3_bucket",
        severity="high",
        condition={
            "type": "attribute_check",
            "parameters": {
                "attribute": "versioning",
                "value": True  # We expect versioning to be enabled
            }
        }
    )
    policy_db.add_policy(policy)
    
    # Generate report
    report = analyzer.generate_report(sample_plan_file)
    
    # Verify policy violation was detected
    assert 'risks' in report
    assert 'high' in report['risks']
    assert len(report['risks']['high']) > 0
    assert any('versioning' in risk.lower() for risk in report['risks']['high']) 