from typing import Any, Dict, Optional
import logging
from .models import PolicyResult

class PolicyEvaluator:
    """Evaluates resources against policy conditions."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def evaluate(self, policy: Dict[str, Any], resource: Dict[str, Any]) -> PolicyResult:
        """
        Evaluate if a resource complies with a policy.

        Args:
            policy: Policy definition dictionary
            resource: Resource configuration dictionary

        Returns:
            PolicyResult: Result of policy evaluation
        """
        if policy.get('disabled', False):
            return PolicyResult(
                policy_id=policy['id'],
                resource_id=resource.get('id', 'unknown'),
                compliant=True,
                severity=policy['severity'],
                message="Policy is disabled",
                remediation=None
            )

        try:
            condition = policy['condition']
            condition_type = condition['type']
            parameters = condition['parameters']

            compliant = False
            message = ""

            if condition_type == 'attribute_check':
                compliant, message = self._evaluate_attribute_check(resource, parameters)
            elif condition_type == 'attribute_change':
                compliant, message = self._evaluate_attribute_change(resource, parameters)
            elif condition_type == 'resource_count':
                compliant, message = self._evaluate_resource_count(resource, parameters)
            else:
                message = f"Unsupported condition type: {condition_type}"

            return PolicyResult(
                policy_id=policy['id'],
                resource_id=resource.get('id', 'unknown'),
                compliant=compliant,
                severity=policy['severity'],
                message=message,
                remediation=policy.get('remediation') if not compliant else None
            )

        except KeyError as e:
            self.logger.error(f"Missing required field in policy or resource: {e}")
            return PolicyResult(
                policy_id=policy['id'],
                resource_id=resource.get('id', 'unknown'),
                compliant=False,
                severity=policy['severity'],
                message=f"Error evaluating policy: Missing field {e}",
                remediation=None
            )
        except Exception as e:
            self.logger.error(f"Error evaluating policy {policy['id']}: {e}")
            return PolicyResult(
                policy_id=policy['id'],
                resource_id=resource.get('id', 'unknown'),
                compliant=False,
                severity=policy['severity'],
                message=f"Error evaluating policy: {str(e)}",
                remediation=None
            )

    def _evaluate_attribute_check(
        self, resource: Dict[str, Any], parameters: Dict[str, Any]
    ) -> tuple[bool, str]:
        """Evaluate attribute check condition."""
        attribute = parameters['attribute']
        
        # Check if attribute exists
        if 'exists' in parameters:
            exists = attribute in resource
            return exists, f"Attribute '{attribute}' {'exists' if exists else 'does not exist'}"

        # Check attribute value
        if attribute not in resource:
            return False, f"Required attribute '{attribute}' not found"

        expected_value = parameters['value']
        actual_value = resource[attribute]
        
        compliant = actual_value == expected_value
        return compliant, (
            f"Attribute '{attribute}' matches expected value" if compliant
            else f"Attribute '{attribute}' value '{actual_value}' does not match expected '{expected_value}'"
        )

    def _evaluate_attribute_change(
        self, resource: Dict[str, Any], parameters: Dict[str, Any]
    ) -> tuple[bool, str]:
        """Evaluate attribute change condition."""
        attribute = parameters['attribute']
        if 'planned_change' not in resource:
            return True, "No planned changes"

        changes = resource['planned_change']
        if attribute not in changes:
            return True, f"No changes planned for attribute '{attribute}'"

        allowed_changes = parameters.get('allowed_changes', [])
        actual_change = changes[attribute]
        
        compliant = actual_change in allowed_changes
        return compliant, (
            f"Planned change '{actual_change}' is allowed" if compliant
            else f"Planned change '{actual_change}' is not allowed"
        )

    def _evaluate_resource_count(
        self, resource: Dict[str, Any], parameters: Dict[str, Any]
    ) -> tuple[bool, str]:
        """Evaluate resource count condition."""
        count = resource.get('count', 1)
        max_count = parameters.get('max_count')
        min_count = parameters.get('min_count')

        if max_count and count > max_count:
            return False, f"Resource count {count} exceeds maximum {max_count}"
        if min_count and count < min_count:
            return False, f"Resource count {count} is below minimum {min_count}"
        
        return True, f"Resource count {count} is within allowed range" 