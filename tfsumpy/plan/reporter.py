import logging
from typing import Dict, Any, List, Optional
from ..reporters.base_reporter import BaseReporter
from ..reporter import ReporterInterface
import json as _json
from pathlib import Path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os
from ..ai.base import AIBase
import asyncio

class PlanReporter(BaseReporter, ReporterInterface, AIBase):
    """Handles formatting and display of Terraform plan results."""
    
    def __init__(self):
        """Initialize the plan reporter."""
        # Initialize all parent classes
        BaseReporter.__init__(self)
        ReporterInterface.__init__(self)
        AIBase.__init__(self)
        
        self.logger = logging.getLogger(__name__)
        # Initialize Jinja2 environment
        template_dir = Path(__file__).parent.parent / 'templates'
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=select_autoescape(['html', 'xml'])
        )
        # Add custom filters
        self.env.filters['to_json'] = self._to_json_filter

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
            # derive provider from resource type (e.g., 'aws' from 'aws_s3_bucket')
            rtype = resource.get('resource_type', '') or ''
            provider = rtype.split('_', 1)[0] if rtype else ''
            resource_data = {
                'resource_type': rtype,
                'identifier': resource.get('identifier'),
                'action': resource.get('action'),
                'actions': resource.get('action'),
                'provider': provider,
                'module': resource.get('module', 'root')
            }
            resource_data['replace'] = resource.get('replace', [])

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
                    
                    # Handle different operation types
                    actions = resource['action'] if isinstance(resource['action'], list) else [resource['action']]
                    if 'create' in actions and 'delete' in actions:
                        # For delete+create, show both before and after values
                        changes.append({
                            'attribute': attr,
                            'before': before_val,
                            'after': after_val
                        })
                    elif 'create' in actions:
                        if after_val is not None:
                            changes.append({
                                'attribute': attr,
                                'before': None,
                                'after': after_val
                            })
                    elif 'delete' in actions:
                        if before_val is not None:
                            changes.append({
                                'attribute': attr,
                                'before': before_val,
                                'after': None
                            })
                    elif 'update' in actions:
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
                        'before': before,
                        'after': after
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
        # Always print header and summary
        self._print_header("Terraform Plan Analysis")
        self._print_summary(report)
        # If user requested detailed or change output, ensure resources exist and print
        if show_changes or show_details:
            if 'resources' not in report:
                self.logger.error("Report missing resource details")
                raise ValueError("Report missing resource details")
            # pass both flags for printing changes and details
            self._print_resource_details(report['resources'], show_changes, show_details)
        # AI analysis if configured
        ai_config = kwargs.get('ai_config')
        azure_config = kwargs.get('azure_config')
        if ai_config:
            try:
                if azure_config:
                    from ..ai.agent_workflow import PlanAnalysisAgent
                    changes = report.get('resources', [])
                    ai_summary = asyncio.run(
                        PlanAnalysisAgent(ai_config, azure_config).run(changes)
                    )
                else:
                    ai_summary = self.get_ai_summary(report, ai_config)
            except Exception as e:
                self.logger.error(f"AI analysis failed: {e}")
                ai_summary = None
            if ai_summary:
                self._write(f"\n{self._colorize('AI Analysis:', 'bold')}\n")
                self._write(f"{ai_summary}\n")

    def _print_header(self, title: str) -> None:
        """Print a formatted header."""
        self._write(f"\n{self._colorize(title, 'bold')}\n")
        self._write("=" * 50 + "\n")

    def _print_summary(self, report: Dict) -> None:
        """Format the change summary section."""
        self._write(f"\n{self._colorize('Total Changes: ' + str(report['total_changes']), 'bold')}\n")
        
        # Add change counts by type
        for action in ['create', 'update', 'delete']:
            count = report['change_breakdown'].get(action, 0)
            if count > 0:  # Only show non-zero counts
                self._write(f"{action.title()}: {count}\n")

    def _print_resource_details(self, resources: list, show_changes: bool = False, show_details: bool = False) -> None:
        """Format the resource details section."""
        self._write(f"\n{self._colorize('Resources Changes:', 'bold')}\n")
        
        # Define color mapping for actions
        action_colors = {
            'CREATE': 'green',
            'UPDATE': 'blue',
            'DELETE': 'red',
            'DELETE/CREATE': 'yellow'  # Special color for replace operations
        }
        
        for resource in resources:
            # Handle both single action and list of actions
            actions = resource.get('actions', resource.get('action', []))
            if not isinstance(actions, list):
                actions = [actions]
            
            # Determine the display action and color
            if isinstance(actions, list) and 'delete' in actions and 'create' in actions:
                action_str = 'DELETE/CREATE'
            else:
                action_str = actions[0].upper()
            
            # Color the action string based on the action type
            colored_action = self._colorize(action_str, action_colors.get(action_str, 'bold'))
            self._write(
                f"\n{colored_action} {resource['resource_type']}: "
                f"{resource['identifier']}\n"
            )
            if action_str == 'DELETE/CREATE' and resource.get('replace'):
                attrs = resource['replace']
                self._write(f"  [REPLACE enforced by attribute(s): {', '.join(attrs)}]\n")
            
            if show_changes:
                self._print_attribute_changes(resource)

    def _print_attribute_changes(self, resource: Dict) -> None:
        """Format attribute changes for a resource."""
        lines = []
        before = resource.get('before', {}) or {}
        after = resource.get('after', {}) or {}
        
        # Get all attributes
        all_attrs = set(before.keys()) | set(after.keys())
        skip_attrs = {'id', 'tags_all'}  # Skip internal attributes
        
        # Define color mapping for symbols
        symbol_colors = {
            '+': 'green',   # create
            '~': 'blue',    # update
            '-': 'red',     # delete
            '-/+': 'yellow' # replace
        }
        
        # Get actions
        actions = resource.get('actions', resource.get('action', []))
        if not isinstance(actions, list):
            actions = [actions]
        
        # Count unchanged attributes
        unchanged_count = 0
        
        for attr in sorted(all_attrs - skip_attrs):
            before_val = before.get(attr)
            after_val = after.get(attr)
            
            if before_val != after_val:
                if isinstance(actions, list) and 'delete' in actions and 'create' in actions:
                    symbol = self._colorize('-/+', symbol_colors['-/+'])
                    lines.append(f"  {symbol} {attr} = {before_val} -> {after_val}")
                elif 'create' in actions:
                    symbol = self._colorize('+', symbol_colors['+'])
                    lines.append(f"  {symbol} {attr} = {after_val}")
                elif 'delete' in actions:
                    symbol = self._colorize('-', symbol_colors['-'])
                    lines.append(f"  {symbol} {attr} = {before_val}")
                else:  # update
                    symbol = self._colorize('~', symbol_colors['~'])
                    lines.append(f"  {symbol} {attr} = {before_val} -> {after_val}")
            else:
                unchanged_count += 1
        
        # Add unchanged count if there are any
        if unchanged_count > 0:
            lines.append(f"  {unchanged_count} attributes unchanged")
        
        self._write('\n'.join(lines))

    def _colorize(self, text: str, color: str) -> str:
        """Colorize text for terminal output.
        
        Args:
            text: Text to colorize
            color: Color to use
            
        Returns:
            Colorized text
        """
        colors = {
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'bold': '\033[1m',
            'reset': '\033[0m'
        }
        
        return f"{colors.get(color, '')}{text}{colors['reset']}"

    def _prepare_report_data(self, data: Dict[str, Any], show_changes: bool = True, show_details: bool = False) -> Dict[str, Any]:
        """Prepare data for report generation."""
        report = self.get_report(data, **{'show_changes': show_changes, 'show_details': show_details})
        processed_resources = self._process_resources(
            report.get('resources', []),
            show_changes=show_changes,
            show_details=show_details
        )
        
        # Calculate summary statistics
        total_resources = len(processed_resources)
        resources_to_add = 0
        resources_to_change = 0
        resources_to_destroy = 0
        
        for r in processed_resources:
            actions = r.get('actions', r.get('action', []))
            if not isinstance(actions, list):
                actions = [actions]
            
            # Count replace operations as both delete and create
            if isinstance(actions, list) and 'delete' in actions and 'create' in actions:
                resources_to_add += 1
                resources_to_destroy += 1
            elif 'create' in actions:
                resources_to_add += 1
            elif 'update' in actions:
                resources_to_change += 1
            elif 'delete' in actions:
                resources_to_destroy += 1
        
        # Create summary section
        summary = {
            'total_resources': total_resources,
            'resources_to_add': resources_to_add,
            'resources_to_change': resources_to_change,
            'resources_to_destroy': resources_to_destroy
        }
        
        # Update change_breakdown in the report
        report['change_breakdown'] = {
            'create': resources_to_add,
            'update': resources_to_change,
            'delete': resources_to_destroy
        }
        
        # Update total_changes to include all operations
        report['total_changes'] = (
            resources_to_add + 
            resources_to_change + 
            resources_to_destroy
        )
        
        return {
            'summary': summary,
            'resources': processed_resources,
            'show_changes': show_changes,
            'show_details': show_details,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'analysis': []  # Placeholder for future analysis results
        }

    def _to_json_filter(self, value: Any) -> str:
        """Convert a value to JSON string."""
        try:
            return _json.dumps(value, default=str)
        except Exception as e:
            self.logger.error(f"Failed to convert value to JSON: {str(e)}")
            return str(value)

    def print_report_markdown(
        self,
        data: Dict[str, Any],
        show_changes: bool = True,
        show_details: bool = False,
        ai_config: Optional[Dict[str, Any]] = None,
        azure_config: Optional[Dict[str, Any]] = None
    ) -> None:
        """Print the report in markdown format to a file."""
        template = self.env.get_template('plan_report.md')
        report_data = self._prepare_report_data(data, show_changes, show_details)
        
        # Add AI summary if configured
        if ai_config:
            # Use agentic workflow if Azure configuration is provided
            if azure_config:
                try:
                    from ..ai.agent_workflow import PlanAnalysisAgent
                    # Prepare changes list for agent
                    changes = report_data.get('resources', [])
                    # Run agent workflow to get analysis
                    ai_summary = asyncio.run(
                        PlanAnalysisAgent(ai_config, azure_config).run(changes)
                    )
                except Exception as e:
                    self.logger.error(f"Agent workflow failed: {e}")
                    ai_summary = None
            else:
                ai_summary = self.get_ai_summary(data, ai_config)
            if ai_summary:
                report_data['ai_summary'] = ai_summary
        
        # Add flags to template context
        report_data['show_changes'] = show_changes
        report_data['show_details'] = show_details
        
        # Format timestamp for markdown
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Generate output filename
        output_file = f"tfsumpy_output_{timestamp}.md"
        
        # Render markdown content
        rendered = template.render(**report_data)
        # If changes not requested, strip resource changes section
        if not show_changes:
            rendered = rendered.replace('## Resource Changes\n', '')
        # Output rendered markdown
        self._write(rendered)
        # If AI summary provided (fallback template), output it
        if report_data.get('ai_summary'):
            self._write("## AI Analysis\n\n")
            self._write(f"{report_data['ai_summary']}\n")
        # Write to file
        with open(output_file, 'w') as f:
            f.write(rendered)
        # Show success message (printed directly)
        print(f"Markdown report written to: {output_file}")

    def print_report_json(
        self,
        data: Dict[str, Any],
        show_changes: bool = True,
        show_details: bool = False,
        ai_config: Optional[Dict[str, Any]] = None,
        azure_config: Optional[Dict[str, Any]] = None
    ) -> None:
        """Print the report in JSON format to a file."""
        report_data = self._prepare_report_data(data, show_changes, show_details)
        
        # Add AI summary if configured
        if ai_config:
            try:
                if azure_config:
                    from ..ai.agent_workflow import PlanAnalysisAgent
                    changes = report_data.get('resources', [])
                    ai_summary = asyncio.run(
                        PlanAnalysisAgent(ai_config, azure_config).run(changes)
                    )
                else:
                    ai_summary = self.get_ai_summary(data, ai_config)
            except Exception as e:
                self.logger.error(f"AI analysis failed: {e}")
                ai_summary = None
            if ai_summary:
                report_data['ai_summary'] = ai_summary
        
        # Add metadata
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_data['metadata'] = {
            'timestamp': datetime.now().isoformat(),
            'version': '0.2.0',
            'format': 'json',
            'summary': {
                'total_resources': report_data['summary']['total_resources'],
                'resources_to_add': report_data['summary']['resources_to_add'],
                'resources_to_change': report_data['summary']['resources_to_change'],
                'resources_to_destroy': report_data['summary']['resources_to_destroy']
            }
        }
        
        # Generate output filename
        output_file = f"tfsumpy_output_{timestamp}.json"
        
        # Render JSON content
        rendered = _json.dumps(report_data, indent=2)
        # Output rendered JSON
        self._write(rendered)
        # Write to file
        with open(output_file, 'w') as f:
            f.write(rendered)
        # Show success message (printed directly)
        print(f"JSON report written to: {output_file}")

    def _write(self, text: str) -> None:
        """Write text to output.
        
        Args:
            text: Text to write
        """
        if text.endswith('\n'):
            print(text, end='')
        else:
            print(text) 