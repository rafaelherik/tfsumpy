from typing import Dict, List

class PlanReporter:
    """Handles the formatting and display of Terraform plan analysis reports."""
    
    # Class constants for ANSI colors
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

    SEVERITY_COLORS = {
        'high': RED,
        'medium': YELLOW
    }

    ACTION_COLORS = {
        'create': GREEN,
        'update': YELLOW,
        'delete': RED
    }

    def print_report(self, report: Dict, show_module: bool = False, show_changes: bool = False, show_risks: bool = False, show_details: bool = False) -> Dict:
        """
        Format and print the infrastructure change analysis report.
        
        Args:
            report (Dict): Analysis report containing summary and risks
            show_module (bool): Whether to show resources grouped by module
            show_changes (bool): Whether to show detailed attribute changes
            show_risks (bool): Whether to show risk assessment
            show_details (bool): Whether to show detailed resource changes. 
                               Note: This is automatically set to True if show_changes is True.
            
        Returns:
            Dict: Structured data report for testing and programmatic use
        """
        # Print formatted report
        print(self._format_header())
        print(self._format_change_summary(report['summary'], show_module))
        
        if show_risks:
            print(self._format_risk_assessment(report['risks']))
        
        # Show details if explicitly requested or if showing changes
        if show_details or show_changes:
            print(self._format_resource_details(report['summary']['resources'], show_module, show_changes))
        
        # Return structured data for testing
        return {
            'header': 'Infrastructure Change Analysis',
            'change_summary': {
                'total_changes': report['summary']['total_changes'],
                'changes': report['summary']['change_breakdown']
            },
            'risk_assessment': {
                'high': report['risks']['high'],
                'medium': report['risks']['medium']
            },
            'resource_details': [
                {
                    'action': resource['action'],
                    'type': resource['resource_type'],
                    'identifier': resource['identifier'],
                    'module': resource.get('module', 'root')
                }
                for resource in report['summary']['resources']
            ]
        }

    def _format_header(self) -> str:
        """Format the report header."""
        return "\n".join([
            "=" * 30,
            f"{self.BOLD}Infrastructure Change Analysis{self.RESET}",
            "=" * 30
        ])

    def _format_change_summary(self, summary: Dict, show_module: bool) -> str:
        """Format the summary of changes with color coding and module grouping."""
        lines = []
        lines.append(f"\n{self.BOLD}Total Changes: {summary['total_changes']}{self.RESET}")
        
        # Group changes by module
        module_changes = {}
        for resource in summary['resources']:
            module = resource.get('module', 'root')
            if module not in module_changes:
                module_changes[module] = {'create': 0, 'update': 0, 'delete': 0}
            module_changes[module][resource['action'].lower()] += 1
        
        # Format overall summary
        for action, color in [
            ('create', self.GREEN),
            ('update', self.YELLOW),
            ('delete', self.RED)
        ]:
            count = summary['change_breakdown'][action]
            lines.append(f"{color}{action.title()}: {self.RESET}{count}")
        
        if show_module and len(module_changes) > 1:
            lines.append(f"\n{self.BOLD}Changes by Module:{self.RESET}")
            for module, changes in module_changes.items():
                lines.append(f"\n{self.BOLD}{module}:{self.RESET}")
                for action, color in [
                    ('create', self.GREEN),
                    ('update', self.YELLOW),
                    ('delete', self.RED)
                ]:
                    count = changes[action]
                    if count > 0:
                        lines.append(f"  {color}{action.title()}: {self.RESET}{count}")
        
        return '\n'.join(lines)

    def _format_risk_assessment(self, risks: Dict[str, List[str]]) -> str:
        """Format risk assessment section with proper formatting."""
        lines = []
        lines.append(f"\n{self.BOLD}Risk Assessment:{self.RESET}")
        
        for severity in ('high', 'medium'):
            if risks[severity]:
                color = self.SEVERITY_COLORS[severity]
                lines.append(f"{color}{severity.title()} Risks:{self.RESET}")
                for risk in risks[severity]:
                    lines.append(f" - {risk}\n")
        
        return '\n'.join(lines)

    def _format_resource_details(self, resources: List[Dict], show_module: bool, show_changes: bool) -> str:
        """
        Format detailed resource changes with color coding and module grouping.
        
        Args:
            resources (List[Dict]): List of resource changes
            show_module (bool): Whether to group by module
            show_changes (bool): Whether to show detailed attribute changes
        """
        lines = []
        lines.append(f"\n{self.BOLD}Resource Details:{self.RESET}")
        
        # Group resources by module
        module_resources = {}
        for resource in resources:
            module = resource.get('module', 'root')
            if module not in module_resources:
                module_resources[module] = []
            module_resources[module].append(resource)
        
        def format_resource(resource, indent=""):
            resource_lines = []
            action = resource['action'].lower()
            color = self.ACTION_COLORS.get(action, '')
            resource_lines.append(
                f"{indent}{color}{resource['action'].upper()} {self.RESET}"
                f"{resource['resource_type']}: {resource['identifier']}"
                f"{self.RESET}"
            )
            
            if show_changes and 'before' in resource and 'after' in resource:
                before = resource['before'] or {}
                after = resource['after'] or {}
                
                # Get all unique keys from both before and after
                all_keys = set(before.keys()) | set(after.keys())
                
                # Skip internal keys
                skip_keys = {'id', 'tags_all'}
                
                for key in sorted(all_keys - skip_keys):
                    before_val = before.get(key)
                    after_val = after.get(key)
                    
                    if before_val != after_val:
                        if action == 'create':
                            resource_lines.append(f"{indent}  + {key} = {after_val}")
                        elif action == 'delete':
                            resource_lines.append(f"{indent}  - {key} = {before_val}")
                        else:  # update
                            resource_lines.append(f"{indent}  ~ {key} = {before_val} -> {after_val}")
            return '\n'.join(resource_lines)
        
        if show_module:
            for module, module_resources_list in module_resources.items():
                lines.append(f"\n{self.BOLD}Module: {module}{self.RESET}")
                for resource in module_resources_list:
                    lines.append(format_resource(resource, "  "))
        else:
            for resource in resources:
                lines.append(format_resource(resource))
        
        return '\n'.join(lines) 