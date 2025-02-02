import logging
from typing import Dict, Any
from ..reporters.base_reporter import BaseReporter
from ..reporter import ReporterInterface

class PlanReporter(BaseReporter, ReporterInterface):
    """Handles formatting and display of Terraform plan results."""
    
    def __init__(self):
        """Initialize the plan reporter."""
        super().__init__()
        self.logger = logging.getLogger(__name__)

    @property
    def category(self) -> str:
        return "plan"

    def get_report(self, data: Any, **kwargs) -> Dict:
        """Return the plan report object.
        
        Args:
            data: Plan analysis results
            **kwargs: Additional options
            
        Returns:
            Dict: The validated plan report
            
        Raises:
            ValueError: If report format is invalid
        """
        try:
            if not isinstance(data, dict) or 'total_changes' not in data:
                self.logger.error("Invalid report format")
                raise ValueError("Invalid report format")
            return data
        except Exception as e:
            self.logger.error(f"Error processing report: {str(e)}")
            raise

    def print_report(self, data: Any, **kwargs) -> None:
        """Print the plan analysis report.
        
        Args:
            data: Plan analysis results
            **kwargs: Additional display options
            
        Raises:
            ValueError: If report format is invalid
        """
        report = self.get_report(data, **kwargs)
        show_details = kwargs.get('show_details', False)
        show_changes = kwargs.get('show_changes', False)

        self._print_header("Terraform Plan Analysis")
        self._print_summary(report)
        
        if show_details or show_changes:
            if 'resources' not in report:
                raise ValueError("Report missing resource details")
            self._print_resource_details(report['resources'], show_changes)

    def _print_header(self, title: str) -> None:
        """Print a formatted header."""
        self._write(f"\n{self._colorize(title, 'bold')}\n")
        self._write("=" * 50 + "\n")

    def _print_summary(self, report: Dict) -> None:
        """Format the change summary section."""
        self._write(f"\n{self._colorize('Total Changes: ' + str(report['total_changes']), 'bold')}\n")
        
        # Add change counts by type
        for action in ['create', 'update', 'delete']:
            count = report['change_breakdown'][action]
            self._write(f"{action.title()}: {count}\n")

    def _print_resource_details(self, resources: list, show_changes: bool = False) -> None:
        """Format the resource details section."""
        self._write(f"\n{self._colorize('Resource Changes:', 'bold')}\n")
        
        for resource in resources:
            action_str = resource['action'].upper()
            self._write(
                f"\n{action_str} {resource['resource_type']}: "
                f"{resource['identifier']}\n"
            )
            
            if show_changes:
                self._print_attribute_changes(resource)

    def _print_attribute_changes(self, resource: Dict) -> None:
        """Format attribute changes for a resource."""
        lines = []
        before = resource.get('before', {}) or {}
        after = resource.get('after', {}) or {}
        
        # Get all changed attributes
        all_attrs = set(before.keys()) | set(after.keys())
        skip_attrs = {'id', 'tags_all'}  # Skip internal attributes
        
        for attr in sorted(all_attrs - skip_attrs):
            before_val = before.get(attr)
            after_val = after.get(attr)
            
            if before_val != after_val:
                if resource['action'] == 'create':
                    lines.append(f"  + {attr} = {after_val}")
                elif resource['action'] == 'delete':
                    lines.append(f"  - {attr} = {before_val}")
                else:  # update
                    lines.append(f"  ~ {attr} = {before_val} -> {after_val}")
        
        self._write('\n'.join(lines)) 