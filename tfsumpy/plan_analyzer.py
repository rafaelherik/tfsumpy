import re
import json
import logging
import os
from typing import Dict, List
from .resource import ResourceChange
from .context import Context
from .policy import Policy

class LocalPlanAnalyzer:
    def __init__(self, context: Context):
        self.context = context
        self.logger = context.logger
        
        # Load configuration through context
        self.context.load_config()
        
        # Get configuration from context
        self.sensitive_patterns = self.context.sensitive_patterns
        self.risk_rules = self.context.risk_rules

    def _sanitize_text(self, text: str) -> str:
        """Remove sensitive data using multiple regex patterns"""
        self.logger.debug("Starting text sanitization")
        sanitized = text
        for pattern, replacement in self.sensitive_patterns:
            matches = re.findall(pattern, sanitized, flags=re.IGNORECASE)
            if matches:
                self.logger.debug(f"Found {len(matches)} matches for pattern: {pattern}")
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
        return sanitized

    def _parse_plan(self, plan_content: str) -> List[ResourceChange]:
        """Parse Terraform JSON plan output into structured format"""
        self.logger.debug("Starting plan parsing")
        try:
            plan = json.loads(plan_content)
            changes = []
            
            resource_changes = plan.get('resource_changes', []) or plan.get('planned_changes', [])
            self.logger.debug(f"Found {len(resource_changes)} resource changes in plan")
            
            for change in resource_changes:
                action = change.get('change', {}).get('actions', ['no-op'])[0]
                if action != 'no-op':
                    self.logger.debug(f"Processing change: {action} on {change.get('type', '')} - {change.get('address', '')}")
                    # Extract module information from address
                    address = change.get('address', '')
                    module_name = 'root'
                    
                    # Only try to extract module info if it's a module resource
                    if 'module.' in address:
                        module_parts = address.split('.')
                        # Handle both single and nested modules
                        module_path = []
                        for i, part in enumerate(module_parts):
                            if part == 'module' and i + 1 < len(module_parts):
                                module_path.append(module_parts[i + 1])
                        module_name = '.'.join(module_path) if module_path else 'root'
                    
                    # Extract before and after states for attribute changes
                    change_details = change.get('change', {})
                    before = change_details.get('before', {})
                    after = change_details.get('after', {})
                    
                    changes.append(ResourceChange(
                        action=action,
                        resource_type=change.get('type', ''),
                        identifier=self._sanitize_text(address),
                        changes=change.get('change', {}).get('before_sensitive', {}),
                        module=module_name,
                        before=before,
                        after=after
                    ))
            
            return changes
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON plan: {str(e)}")
            raise ValueError("Invalid JSON plan format")

    def _analyze_risks(self, changes: List[ResourceChange]) -> Dict[str, List[str]]:
        """Identify risks using predefined rules and cloud-specific policies"""
        self.logger.debug("Starting risk analysis")
        findings = {'high': [], 'medium': [], 'low': []}
        
        # Get policies for the changes
        for change in changes:
            # Determine provider from resource type
            provider = self._detect_provider(change.resource_type)
            
            # Get relevant policies
            policies = self.context.policy_db.get_policies(
                provider=provider,
                resource_type=change.resource_type
            )
            
            # Evaluate each policy
            for policy in policies:
                if self._evaluate_policy(change, policy):
                    message = f"{policy.name}: {policy.description}"
                    if policy.remediation:
                        message += f"\nRemediation: {policy.remediation}"
                    findings[policy.severity].append(message)
        
        return findings

    def _detect_provider(self, resource_type: str) -> str:
        """Detect the cloud provider from resource type."""
        provider_prefixes = {
            'aws_': 'aws',
            'azurerm_': 'azure',
            'google_': 'gcp'
        }
        
        for prefix, provider in provider_prefixes.items():
            if resource_type.startswith(prefix):
                return provider
        return 'unknown'

    def _evaluate_policy(self, change: ResourceChange, policy: Policy) -> bool:
        """Evaluate if a change violates a policy."""
        condition = policy.condition
        
        if condition['type'] == 'attribute_check':
            return self._evaluate_attribute_check(change, condition['parameters'])
        elif condition['type'] == 'attribute_change':
            return self._evaluate_attribute_change(change, condition['parameters'])
        elif condition['type'] == 'resource_count':
            return self._evaluate_resource_count(change, condition['parameters'])
        
        return False

    def _evaluate_attribute_check(self, change: ResourceChange, parameters: Dict) -> bool:
        """Evaluate if a resource change violates an attribute check policy.
        
        Args:
            change: The resource change to evaluate
            parameters: Policy condition parameters
        
        Returns:
            bool: True if policy is violated, False otherwise
        """
        try:
            attribute = parameters.get('attribute')
            expected_value = parameters.get('value')
            
            if not attribute or expected_value is None:
                self.logger.warning("Invalid policy parameters: missing attribute or value")
                return False
            
            # For create/update actions, check the 'after' state
            if change.action in ['create', 'update']:
                actual_value = change.after.get(attribute)
                # Policy is violated if the actual value doesn't match expected
                return actual_value != expected_value
                
            # For delete actions, check the 'before' state
            elif change.action == 'delete':
                actual_value = change.before.get(attribute)
                # For deletions, policy is violated if the value matched (we're removing a compliant resource)
                return actual_value == expected_value
                
            return False
            
        except Exception as e:
            self.logger.error(f"Error evaluating attribute check: {str(e)}")
            return False

    def _evaluate_attribute_change(self, change: ResourceChange, parameters: Dict) -> bool:
        """Evaluate an attribute change condition."""
        # Implementation for attribute change evaluation
        return False

    def _evaluate_resource_count(self, change: ResourceChange, parameters: Dict) -> bool:
        """Evaluate a resource count condition."""
        # Implementation for resource count evaluation
        return False

    def generate_report(self, plan_path: str) -> Dict:
        """Process plan file and generate report"""
        self.logger.info(f"Generating report for plan: {plan_path}")
        with open(plan_path, 'r') as f:
            raw_content = f.read()
            
        sanitized_content = self._sanitize_text(raw_content)
        changes = self._parse_plan(sanitized_content)
        risks = self._analyze_risks(changes)
        
        change_counts = {'create': 0, 'update': 0, 'delete': 0}
        for c in changes:
            change_counts[c.action] += 1
            
        self.logger.info(f"Analysis complete. Found {len(changes)} changes and risks: {risks}")
        return {
            'summary': {
                'total_changes': len(changes),
                'change_breakdown': change_counts,
                'resources': [c.__dict__ for c in changes]
            },
            'risks': risks
        }
