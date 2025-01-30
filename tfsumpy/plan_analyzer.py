import re
import json
from typing import Dict, List
from .resource import ResourceChange

class LocalPlanAnalyzer:
    def __init__(self):
        self.sensitive_patterns = [
            # AWS credentials
            (r'\bAKIA[0-9A-Z]{16}\b', '[AWS-KEY-REDACTED]'),
            (r'\bASIA[0-9A-Z]{16}\b', '[AWS-TEMP-KEY-REDACTED]'),
            # Azure/GCP credentials
            (r'\b("subscriptionId"|"tenantId"):\s*"[^"]+"', '[CLOUD-ID-REDACTED]'),
            # Generic secrets
            (r'\b(password|secret|token|key)\b["\']?:?[\s"\']+[^\s"\']+', '[SECRET-REDACTED]'),
            # IP addresses
            (r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '[IP-REDACTED]'),
            # Resource names
            (r'\b(name|resourceGroup|clusterName):\s*[\'"][^\'"]+[\'"]', 'name: [REDACTED]')
        ]
        
        self.risk_rules = {
            'high': [
                (r'\bdelete\b.*\b(persistentvolumeclaim|database|storage)\b', 
                 "High risk: Critical storage resource deletion detected"),
                (r'\bmodify\b.*\b(securityGroup|firewall|IAM)\b', 
                 "High risk: Security-related configuration change"),
                (r'\bdelete\b.*\b(customresourcedefinition|CRD)\b',
                 "High risk: CRD deletion could break existing workflows")
            ],
            'medium': [
                (r'\bcreate\b.*\b(bucket|storage)\b.*publicAccessEnabled:\s*true',
                 "Medium risk: Public storage resource being created"),
                (r'\bmodify\b.*\b(image|version)\b',
                 "Medium risk: Version change could cause compatibility issues")
            ]
        }

    def _sanitize_text(self, text: str) -> str:
        """Remove sensitive data using multiple regex patterns"""
        for pattern, replacement in self.sensitive_patterns:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text

    def _parse_plan(self, plan_content: str) -> List[ResourceChange]:
        """Parse Terraform JSON plan output into structured format"""
        try:
            plan = json.loads(plan_content)
            changes = []
            
            # Handle both pre and post Terraform 0.12 plan formats
            resource_changes = plan.get('resource_changes', []) or plan.get('planned_changes', [])
            
            for change in resource_changes:
                action = change.get('change', {}).get('actions', ['no-op'])[0]
                if action != 'no-op':
                    changes.append(ResourceChange(
                        action=action,
                        resource_type=change.get('type', ''),
                        identifier=self._sanitize_text(change.get('address', '')),
                        changes=change.get('change', {}).get('before_sensitive', {})
                    ))
            
            return changes
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON plan format")

    def _analyze_risks(self, changes: List[ResourceChange]) -> Dict[str, List[str]]:
        """Identify risks using predefined rules"""
        findings = {'high': [], 'medium': []}
        text_plan = "\n".join([f"{c.action} {c.resource_type} {c.identifier}" 
                             for c in changes])
        
        for severity in ['high', 'medium']:
            for pattern, message in self.risk_rules[severity]:
                if re.search(pattern, text_plan, re.IGNORECASE):
                    findings[severity].append(message)
        
        return findings

    def generate_report(self, plan_path: str) -> Dict:
        """Process plan file and generate report"""
        with open(plan_path, 'r') as f:
            raw_content = f.read()
            
        sanitized_content = self._sanitize_text(raw_content)
        changes = self._parse_plan(sanitized_content)
        risks = self._analyze_risks(changes)
        
        # Count changes by type
        change_counts = {'create': 0, 'update': 0, 'delete': 0}
        for c in changes:
            change_counts[c.action] += 1
            
        return {
            'summary': {
                'total_changes': len(changes),
                'change_breakdown': change_counts,
                'resources': [c.__dict__ for c in changes]
            },
            'risks': risks
        }

    def print_report(self, report: Dict):
        """Format report for CLI output"""
        print("Infrastructure Change Analysis")
        print("==============================")
        print(f"\nTotal Changes: {report['summary']['total_changes']}")
        print(f"Create: {report['summary']['change_breakdown']['create']}")
        print(f"Update: {report['summary']['change_breakdown']['update']}")
        print(f"Delete: {report['summary']['change_breakdown']['delete']}")
        
        print("\nRisk Assessment:")
        for severity in ['high', 'medium']:
            if report['risks'][severity]:
                print(f"\n{severity.title()} Risks:")
                for risk in report['risks'][severity]:
                    print(f" - {risk}")
                    
        print("\nResource Details:")
        for resource in report['summary']['resources']:
            print(f"{resource['action'].upper()} {resource['resource_type']}: {resource['identifier']}")
