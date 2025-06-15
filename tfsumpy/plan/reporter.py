import logging
from typing import Dict, Any, List
from ..reporters.base_reporter import BaseReporter
from ..reporter import ReporterInterface
import json as _json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

class PlanReporter(BaseReporter, ReporterInterface):
    """Handles formatting and display of Terraform plan results."""
    
    def __init__(self):
        """Initialize the plan reporter."""
        super().__init__()
        self.logger = logging.getLogger(__name__)
        # Initialize Jinja2 environment
        template_dir = Path(__file__).parent.parent / 'templates'
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )

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

    def _process_resources(self, resources: List[Dict], show_changes: bool = False, show_details: bool = False) -> List[Dict]:
        """Process resources and their changes.
        
        Args:
            resources: List of resources to process
            show_changes: Whether to include attribute changes
            show_details: Whether to include additional details
            
        Returns:
            List[Dict]: Processed resources with changes and details
        """
        processed_resources = []
        for resource in resources:
            resource_data = {
                'resource_type': resource['resource_type'],
                'identifier': resource['identifier'],
                'action': resource['action'],
                'provider': resource.get('provider', 'unknown'),
                'module': resource.get('module', 'root')
            }

            # Process changes if requested
            if show_changes:
                before = resource.get('before', {}) or {}
                after = resource.get('after', {}) or {}
                changes = []
                
                # Get all changed attributes
                all_attrs = set(before.keys()) | set(after.keys())
                skip_attrs = {'id', 'tags_all'}  # Skip internal attributes
                
                for attr in sorted(all_attrs - skip_attrs):
                    before_val = before.get(attr)
                    after_val = after.get(attr)
                    
                    if before_val != after_val:
                        changes.append({
                            'attribute': attr,
                            'before': before_val,
                            'after': after_val
                        })
                
                if changes:
                    resource_data['changes'] = changes

            # Add additional details if requested
            if show_details:
                resource_data['details'] = {
                    'dependencies': resource.get('dependencies', []),
                    'tags': resource.get('tags', {}),
                    'raw': {
                        'before': resource.get('before', {}),
                        'after': resource.get('after', {})
                    }
                }

            processed_resources.append(resource_data)
        
        return processed_resources

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

        # Process resources
        processed_resources = self._process_resources(
            report.get('resources', []),
            show_changes=show_changes,
            show_details=show_details
        )

        # Prepare template data
        template_data = {
            'total_resources': report['total_changes'],
            'resources_to_add': report['change_breakdown']['create'],
            'resources_to_change': report['change_breakdown']['update'],
            'resources_to_destroy': report['change_breakdown']['delete'],
            'resources': processed_resources,
            'show_changes': show_changes,
            'show_details': show_details,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'analysis': []  # Placeholder for future analysis results
        }

        # Load and render template
        template = self.env.get_template('plan_report.md')
        output = template.render(**template_data)
        
        # Write the output
        self._write(output)

    def print_report_json(self, data: Any, **kwargs) -> None:
        """Print the plan analysis report in JSON format.
        
        Args:
            data: Plan analysis results
            **kwargs: Additional display options
        """
        report = self.get_report(data, **kwargs)
        show_details = kwargs.get('show_details', False)
        show_changes = kwargs.get('show_changes', False)

        # Process resources
        processed_resources = self._process_resources(
            report.get('resources', []),
            show_changes=show_changes,
            show_details=show_details
        )

        # Prepare JSON output structure
        json_output = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'version': '1.0',
                'format': 'json'
            },
            'summary': {
                'total_resources': report['total_changes'],
                'resources_to_add': report['change_breakdown']['create'],
                'resources_to_change': report['change_breakdown']['update'],
                'resources_to_destroy': report['change_breakdown']['delete']
            },
            'resources': processed_resources
        }

        # Add analysis section if available
        if 'analysis' in report:
            json_output['analysis'] = report['analysis']

        # Write the JSON output with proper formatting
        self._write(_json.dumps(json_output, indent=2)) 