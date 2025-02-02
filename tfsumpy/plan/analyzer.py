import json
import logging
from typing import Dict, List
from ..resource import ResourceChange
from ..analyzer import AnalyzerInterface, AnalyzerResult

class PlanAnalyzer(AnalyzerInterface):
    """Analyzes Terraform plan files and generates structured reports."""
    
    def __init__(self, context):
        """Initialize the plan analyzer.
        
        Args:
            context: Application context containing configuration
        """
        self.context = context
        self.logger = logging.getLogger(__name__)

    @property
    def category(self) -> str:
        """Return the analyzer category."""
        return "plan"

    def analyze(self, context: 'Context', **kwargs) -> AnalyzerResult:
        """Analyze a Terraform plan file and generate a report.
        
        Args:
            context: Analysis context
            **kwargs: Must include plan_path
            
        Returns:
            AnalyzerResult containing the analysis results
        """
        plan_path = kwargs.get('plan_path')
        if not plan_path:
            raise ValueError("plan_path is required")
            
        self.logger.debug(f"Starting plan analysis for {plan_path}")
        
        try:
            # Read and parse plan file
            with open(plan_path, 'r') as f:
                self.logger.debug("Reading plan file")
                plan_content = f.read()
            
            # Parse the plan content
            self.logger.debug("Parsing plan content")
            changes = self._parse_plan(plan_content)
            
            # Generate summary statistics
            change_counts = {'create': 0, 'update': 0, 'delete': 0}
            for change in changes:
                change_counts[change.action] += 1
            
            self.logger.info(f"Found {len(changes)} resource changes")
            self.logger.debug(f"Change breakdown: {change_counts}")
            
            result_data = {
                'total_changes': len(changes),
                'change_breakdown': change_counts,
                'resources': [c.__dict__ for c in changes]
            }
            
            return AnalyzerResult(
                category=self.category,
                data=result_data
            )
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse plan JSON: {str(e)}")
            raise ValueError("Invalid plan file format")
        except Exception as e:
            self.logger.error(f"Error analyzing plan: {str(e)}")
            raise

    def _parse_plan(self, plan_content: str) -> List[ResourceChange]:
        """Parse Terraform plan JSON into structured format.
        
        Args:
            plan_content: Raw plan JSON content
            
        Returns:
            List of ResourceChange objects
        """
        self.logger.debug("Parsing plan JSON")
        plan = json.loads(plan_content)
        changes = []
        
        # Get resource changes from plan
        resource_changes = plan.get('resource_changes', [])
        self.logger.debug(f"Found {len(resource_changes)} resource changes in plan")
        
        for change in resource_changes:
            # Extract change action
            action = change.get('change', {}).get('actions', ['no-op'])[0]
            if action != 'no-op':
                self.logger.debug(f"Processing {action} change for {change.get('address', '')}")
                
                # Extract module information
                address = change.get('address', '')
                module_name = self._extract_module_name(address)
                
                # Get change details
                change_details = change.get('change', {})
                
                changes.append(ResourceChange(
                    action=action,
                    resource_type=change.get('type', ''),
                    identifier=self._sanitize_text(address),
                    changes=change_details.get('before_sensitive', {}),
                    module=module_name,
                    before=change_details.get('before', {}),
                    after=change_details.get('after', {})
                ))
        
        return changes

    def _extract_module_name(self, address: str) -> str:
        """Extract module name from resource address.
        
        Args:
            address: Resource address from plan
            
        Returns:
            Module name or 'root' if not in a module
        """
        if 'module.' in address:
            module_parts = address.split('.')
            module_path = []
            for i, part in enumerate(module_parts):
                if part == 'module' and i + 1 < len(module_parts):
                    module_path.append(module_parts[i + 1])
            return '.'.join(module_path)
        return 'root'

    def _sanitize_text(self, text: str) -> str:
        """Remove sensitive information from text.
        
        Args:
            text: Text to sanitize
            
        Returns:
            Sanitized text
        """
        self.logger.debug("Sanitizing text")
        sanitized = text
        for pattern, replacement in self.context.sensitive_patterns:
            sanitized = pattern.sub(replacement, sanitized)
        return sanitized 