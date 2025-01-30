import re
import json
import logging
import os
from typing import Dict, List
from .resource import ResourceChange

class LocalPlanAnalyzer:
    def __init__(self, config_path: str = None, debug: bool = False):
        # Configure logging
        self.logger = logging.getLogger(__name__)
        log_level = logging.DEBUG if debug else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Load default config first
        default_config_path = os.path.join(os.path.dirname(__file__), 'rules_config.json')
        self.logger.debug(f"Loading default config file: {default_config_path}")
        
        try:
            with open(default_config_path, 'r') as f:
                config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.logger.error(f"Error loading default config: {str(e)}")
            raise

        # If external config provided, merge it with default config
        if config_path:
            self.logger.debug(f"Merging external config file: {config_path}")
            try:
                with open(config_path, 'r') as f:
                    external_config = json.load(f)
                    
                # Merge sensitive patterns
                config['sensitive_patterns'].extend(external_config.get('sensitive_patterns', []))
                
                # Merge risk rules for each severity level
                for severity in ['high', 'medium']:
                    if severity in external_config.get('risk_rules', {}):
                        config['risk_rules'][severity].extend(
                            external_config['risk_rules'][severity]
                        )
                
                self.logger.debug("Successfully merged external config")
            except FileNotFoundError:
                self.logger.error(f"External config file not found: {config_path}")
                raise
            except json.JSONDecodeError as e:
                self.logger.error(f"Error parsing external JSON config file: {str(e)}")
                raise
        
        # Set the configuration
        self.sensitive_patterns = [(rule['pattern'], rule['replacement']) 
                                 for rule in config['sensitive_patterns']]
        self.risk_rules = {
            severity: [(rule['pattern'], rule['message']) 
                      for rule in rules]
            for severity, rules in config['risk_rules'].items()
        }
        
        self.logger.debug(f"Loaded {len(self.sensitive_patterns)} sensitive patterns")
        self.logger.debug(f"Loaded risk rules: {self.risk_rules.keys()}")

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
                    changes.append(ResourceChange(
                        action=action,
                        resource_type=change.get('type', ''),
                        identifier=self._sanitize_text(change.get('address', '')),
                        changes=change.get('change', {}).get('before_sensitive', {})
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

    def print_report(self, report: Dict):
        """Format report for CLI output"""
        print("Infrastructure Change Analysis")
        print("==============================")
        print(f"\nTotal Changes: {report['summary']['total_changes']}")
        print(f"Create: {report['summary']['change_breakdown']['create']}")
        print(f"Update: {report['summary']['change_breakdown']['update']}")
        print(f"Delete: {report['summary']['change_breakdown']['delete']}")
        
        print("\nRisk Assessment:")
        for severity in ['high', 'medium']:
            if report['risks'][severity]:
                print(f"\n{severity.title()} Risks:")
                for risk in report['risks'][severity]:
                    print(f" - {risk}")
                    
        print("\nResource Details:")
        for resource in report['summary']['resources']:
            print(f"{resource['action'].upper()} {resource['resource_type']}: {resource['identifier']}")
