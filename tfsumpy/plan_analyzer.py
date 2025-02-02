import re
import json
import logging
import os
from typing import Dict, List
from .resource import ResourceChange
from .context import Context

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
        """Identify risks using predefined rules"""
        self.logger.debug("Starting risk analysis")
        findings = {'high': [], 'medium': []}
        
        text_plan = ""
        for c in changes:
            action = c.action.lower()
            line = f"{action} {c.resource_type} {c.identifier}\n"
            text_plan += line
            self.logger.debug(f"Added plan line: {line.strip()}")
        
        self.logger.debug(f"Complete plan text for analysis:\n{text_plan}")
        
        for severity in ['high', 'medium']:
            self.logger.debug(f"Checking {severity} risk patterns")
            for pattern, message in self.risk_rules[severity]:
                if re.search(pattern, text_plan, re.IGNORECASE):
                    self.logger.debug(f"Found match for pattern: {pattern}")
                    self.logger.debug(f"Adding risk: {message}")
                    findings[severity].append(message)
        
        return findings

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

    def print_report(self, report: Dict, show_module: bool = False, show_changes: bool = False) -> None:
        """
        Format and print the infrastructure change analysis report.
        
        Args:
            report (Dict): Analysis report containing summary and risks
            show_module (bool): Whether to show resources grouped by module
            show_changes (bool): Whether to show detailed attribute changes
        """
        self._print_header()
        self._print_change_summary(report['summary'], show_module)
        self._print_risk_assessment(report['risks'])
        self._print_resource_details(report['summary']['resources'], show_module, show_changes)

    def _print_header(self) -> None:
        """Print the report header with formatting."""
        print("=" * 30)
        print(f"{self.BOLD}Infrastructure Change Analysis{self.RESET}")
        print("=" * 30)

    def _print_change_summary(self, summary: Dict, show_module: bool) -> None:
        """Print the summary of changes with color coding and module grouping."""
        print(f"\n{self.BOLD}Total Changes: {summary['total_changes']}{self.RESET}")
        
        # Group changes by module
        module_changes = {}
        for resource in summary['resources']:
            module = resource.get('module', 'root')
            if module not in module_changes:
                module_changes[module] = {'create': 0, 'update': 0, 'delete': 0}
            module_changes[module][resource['action'].lower()] += 1
        
        # Print overall summary
        for action, color in [
            ('create', self.GREEN),
            ('update', self.YELLOW),
            ('delete', self.RED)
        ]:
            count = summary['change_breakdown'][action]
            print(f"{color}{action.title()}: {self.RESET}{count}")
        
        # Print per-module breakdown only if show_module is True and there are multiple modules
        if show_module and len(module_changes) > 1:
            print(f"\n{self.BOLD}Changes by Module:{self.RESET}")
            for module, changes in module_changes.items():
                print(f"\n{self.BOLD}{module}:{self.RESET}")
                for action, color in [
                    ('create', self.GREEN),
                    ('update', self.YELLOW),
                    ('delete', self.RED)
                ]:
                    count = changes[action]
                    if count > 0:
                        print(f"  {color}{action.title()}: {self.RESET}{count}")

    def _print_risk_assessment(self, risks: Dict[str, List[str]]) -> None:
        """Print risk assessment section with proper formatting."""
        print(f"\n{self.BOLD}Risk Assessment:{self.RESET}")
        
        for severity in ('high', 'medium'):
            if risks[severity]:
                color = self.SEVERITY_COLORS[severity]
                print(f"{color}{severity.title()} Risks:{self.RESET}")
                for risk in risks[severity]:
                    print(f" - {risk}\n")

    def _print_resource_details(self, resources: List[Dict], show_module: bool, show_changes: bool) -> None:
        """Print detailed resource changes with color coding and module grouping."""
        print(f"\n{self.BOLD}Resource Details:{self.RESET}")
        
        # Group resources by module
        module_resources = {}
        for resource in resources:
            module = resource.get('module', 'root')
            if module not in module_resources:
                module_resources[module] = []
            module_resources[module].append(resource)
        
        def print_resource(resource, indent=""):
            action = resource['action'].lower()
            color = self.ACTION_COLORS.get(action, '')
            print(
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
                            print(f"{indent}  + {key} = {after_val}")
                        elif action == 'delete':
                            print(f"{indent}  - {key} = {before_val}")
                        else:  # update
                            print(f"{indent}  ~ {key} = {before_val} -> {after_val}")
        
        if show_module:
            for module, module_resources_list in module_resources.items():
                print(f"\n{self.BOLD}Module: {module}{self.RESET}")
                for resource in module_resources_list:
                    print_resource(resource, "  ")
        else:
            for resource in resources:
                print_resource(resource)
