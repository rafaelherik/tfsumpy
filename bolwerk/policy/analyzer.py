from typing import Dict, List, Optional
from ..db.manager import DBManager
from dataclasses import dataclass
import logging
from .evaluator import PolicyEvaluator
from ..analyzer import AnalyzerInterface, AnalyzerResult

@dataclass
class PolicyResult:
    """Represents the result of a policy evaluation."""
    policy_id: str
    resource_id: str
    severity: str
    message: str
    compliant: bool
    remediation: Optional[str] = None

@dataclass
class PolicyReport:
    """Container for policy evaluation results."""
    findings: List[PolicyResult]

class PolicyAnalyzer(AnalyzerInterface):
    """Handles policy evaluation and risk assessment by coordinating with PolicyEvaluator."""
    
    def __init__(self, db_manager: DBManager):
        """
        Initialize PolicyAnalyzer.
        
        Args:
            db_manager: Database manager instance for policy retrieval
        """
        self.db_manager = db_manager
        self.evaluator = PolicyEvaluator()
        self.logger = logging.getLogger(__name__)

    @property
    def category(self) -> str:
        """Return the analyzer category."""
        return "policy"

    def analyze(self, context: 'Context', **kwargs) -> AnalyzerResult:
        """
        Analyze resources against policies.
        
        Args:
            context: Analysis context containing plan data
            **kwargs: Additional arguments
            
        Returns:
            AnalyzerResult containing PolicyReport
        """
        plan_data = context.get_plan_data()
        resources = plan_data.get('resources', [])
        all_results = []
        
        for resource in resources:
            results = self._evaluate_resource(resource)
            all_results.extend(results)
            
        return AnalyzerResult(
            category=self.category,
            data=PolicyReport(findings=all_results)
        )

    def _evaluate_resource(self, resource: Dict) -> List[PolicyResult]:
        """
        Evaluate a resource against all applicable policies.
        
        Args:
            resource: Resource configuration dictionary
            
        Returns:
            List of PolicyResult objects containing evaluation results
        """
        results = []
        try:
            provider = self._detect_provider(resource['resource_type'])
            
            # Get applicable policies
            policies = self.db_manager.execute_query(
                """
                SELECT * FROM policies 
                WHERE provider = ? AND resource_type = ?
                """,
                (provider, resource['resource_type'])
            )
            
            for policy in policies:
                try:
                    result = self.evaluator.evaluate(policy, resource)
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Error evaluating policy {policy['id']}: {str(e)}")
                    results.append(PolicyResult(
                        policy_id=policy['id'],
                        resource_id=resource['identifier'],
                        severity=policy['severity'],
                        message=f"Error evaluating policy: {str(e)}",
                        compliant=False
                    ))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in evaluate_resource: {str(e)}")
            return []

    def _detect_provider(self, resource_type: str) -> str:
        """
        Detect cloud provider from resource type.
        
        Args:
            resource_type: Type of the resource
            
        Returns:
            String identifying the cloud provider
        """
        provider_prefixes = {
            'aws_': 'aws',
            'azurerm_': 'azure',
            'google_': 'gcp'
        }
        
        for prefix, provider in provider_prefixes.items():
            if resource_type.startswith(prefix):
                return provider
        return 'unknown' 