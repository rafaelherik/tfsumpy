import re
from typing import List, Dict, Pattern
from ..models import ProviderRiskAnalyzer, RiskFinding
from ...resource import ResourceChange

class AWSRiskAnalyzer(ProviderRiskAnalyzer):
    """AWS-specific risk analyzer."""
    
    def __init__(self):
        self.high_risk_resources = {
            'aws_vpc', 'aws_subnet', 'aws_security_group',
            'aws_rds_cluster', 'aws_elasticache_cluster'
        }
        
        self.public_access_patterns: Dict[str, Pattern] = {
            'public_access': re.compile(r'public_access.*true', re.I),
            'publicly_accessible': re.compile(r'publicly_accessible.*true', re.I),
            'public_network': re.compile(r'public_network_access_enabled.*true', re.I)
        }
        
        self.ip_attributes = [
            'cidr_block', 'ip_address', 'private_ip', 'public_ip'
        ]
        
        self.sensitive_resources = {
            'aws_iam_role': 'IAM role',
            'aws_iam_policy': 'IAM policy',
            'aws_kms_key': 'KMS key'
        }
    
    @property
    def provider(self) -> str:
        return 'aws'
    
    def analyze(self, change: ResourceChange) -> List[RiskFinding]:
        if not change.resource_type.startswith('aws_'):
            return []
        
        findings = []
        findings.extend(self._check_deletion_risks(change))
        findings.extend(self._check_public_access(change))
        findings.extend(self._check_ip_changes(change))
        findings.extend(self._check_sensitive_resources(change))
        
        return findings
    
    def _check_deletion_risks(self, change: ResourceChange) -> List[RiskFinding]:
        if change.action != 'delete' or change.resource_type not in self.high_risk_resources:
            return []
            
        return [RiskFinding(
            severity='high',
            message=f"Deletion of critical AWS infrastructure: {change.resource_type}",
            resource_id=change.identifier,
            impact="May affect multiple dependent resources",
            mitigation="Verify all resource dependencies before deletion"
        )]
    
