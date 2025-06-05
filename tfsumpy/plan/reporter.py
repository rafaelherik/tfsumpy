import logging
from typing import Dict, Any
from ..reporters.base_reporter import BaseReporter
from ..reporter import ReporterInterface
import json as _json

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
        self._write(f"\n{self._colorize('Resources Changes:', 'bold')}\n")
        
        # Define color mapping for actions
        action_colors = {
            'CREATE': 'green',
            'UPDATE': 'blue',
            'DELETE': 'red'
        }
        
        for resource in resources:
            action_str = resource['action'].upper()
            # Color the action string based on the action type
            colored_action = self._colorize(action_str, action_colors.get(action_str, 'bold'))
            self._write(
                f"\n{colored_action} {resource['resource_type']}: "
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
        
        # Define color mapping for symbols
        symbol_colors = {
            '+': 'green',   # create
            '~': 'blue',    # update
            '-': 'red'      # delete
        }
        
        for attr in sorted(all_attrs - skip_attrs):
            before_val = before.get(attr)
            after_val = after.get(attr)
            
            if before_val != after_val:
                if resource['action'] == 'create':
                    symbol = self._colorize('+', symbol_colors['+'])
                    lines.append(f"  {symbol} {attr} = {after_val}")
                elif resource['action'] == 'delete':
                    symbol = self._colorize('-', symbol_colors['-'])
                    lines.append(f"  {symbol} {attr} = {before_val}")
                else:  # update
                    symbol = self._colorize('~', symbol_colors['~'])
                    lines.append(f"  {symbol} {attr} = {before_val} -> {after_val}")
        
        self._write('\n'.join(lines))

    def print_report_markdown(self, data: Any, **kwargs) -> None:
        """Print the plan analysis report in markdown format.
        Args:
            data: Plan analysis results
            **kwargs: Additional display options
        """
        report = self.get_report(data, **kwargs)
        show_details = kwargs.get('show_details', False)
        show_changes = kwargs.get('show_changes', False)

        # Markdown header
        self._write(f"# Terraform Plan Summary\n\n")
        self._write(f"## Summary\n\n")
        self._write(f"- **Total Changes:** {report['total_changes']}\n")
        for action in ['create', 'update', 'delete']:
            count = report['change_breakdown'][action]
            self._write(f"- **{action.title()}:** {count}\n")

        if show_details or show_changes:
            if 'resources' not in report:
                raise ValueError("Report missing resource details")
            self._write(f"\n## Resource Changes\n\n")
            action_order = [
                ('create', 'Created Resources', '🟩'),
                ('update', 'Updated Resources', '🟦'),
                ('delete', 'Destroyed Resources', '🟥'),
            ]
            resources_by_action = {action: [] for action, _, _ in action_order}
            for resource in report['resources']:
                act = resource['action']
                if act in resources_by_action:
                    resources_by_action[act].append(resource)
                else:
                    resources_by_action.setdefault(act, []).append(resource)
            for action, section_title, badge in action_order:
                if resources_by_action[action]:
                    self._write(f"### {badge} {section_title}\n\n")
                    for resource in resources_by_action[action]:
                        action_str = resource['action'].upper()
                        self._write(f"#### `{resource['resource_type']}`: `{resource['identifier']}`\n")
                        # Show changes as JSON code block
                        before = resource.get('before', {}) or {}
                        after = resource.get('after', {}) or {}
                        if action == 'create':
                            self._write(f"```json\n{_json.dumps(after, indent=2)}\n```")
                            self._write("\n")
                        elif action == 'delete':
                            self._write(f"```json\n{_json.dumps(before, indent=2)}\n```")
                            self._write("\n")
                        else:  # update
                            self._write(f"**Before:**\n")
                            self._write(f"```json\n{_json.dumps(before, indent=2)}\n```")
                            self._write("\n")
                            self._write(f"**After:**\n")
                            self._write(f"```json\n{_json.dumps(after, indent=2)}\n```")
                            self._write("\n")
                        self._write("\n") 