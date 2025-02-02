import json
import logging
import os
from typing import Dict, List
from .policy import PolicyDBManager

class Context:
    def __init__(self, config_path: str = None, debug: bool = False):
        self.config_path = config_path
        self.debug = debug
        
        # Configure logging
        self.logger = logging.getLogger(__name__)
        log_level = logging.DEBUG if debug else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Initialize configuration attributes
        self.sensitive_patterns = []
        self.risk_rules = {}
        self.config = {}
        
        # Initialize policy database
        self.policy_db = PolicyDBManager()

    def load_config(self) -> None:
        """Load and merge configuration files"""
        # Load default config
        default_config_path = os.path.join(os.path.dirname(__file__), 'rules_config.json')
        self.logger.debug(f"Loading default config file: {default_config_path}")
        
        try:
            with open(default_config_path, 'r') as f:
                self.config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.logger.error(f"Error loading default config: {str(e)}")
            raise

        # Merge external config if provided
        if self.config_path:
            self._merge_external_config()

        # Process configuration
        self._process_config()

    def _merge_external_config(self) -> None:
        """Merge external configuration with default configuration"""
        self.logger.debug(f"Merging external config file: {self.config_path}")
        try:
            with open(self.config_path, 'r') as f:
                external_config = json.load(f)
                
            # Merge sensitive patterns
            self.config['sensitive_patterns'].extend(
                external_config.get('sensitive_patterns', [])
            )
            
            # Merge risk rules
            for severity in ['high', 'medium']:
                if severity in external_config.get('risk_rules', {}):
                    self.config['risk_rules'][severity].extend(
                        external_config['risk_rules'][severity]
                    )
            
            self.logger.debug("Successfully merged external config")
        except FileNotFoundError:
            self.logger.error(f"External config file not found: {self.config_path}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing external JSON config file: {str(e)}")
            raise

    def _process_config(self) -> None:
        """Process loaded configuration into usable formats"""
        self.sensitive_patterns = [
            (rule['pattern'], rule['replacement']) 
            for rule in self.config['sensitive_patterns']
        ]
        self.risk_rules = {
            severity: [(rule['pattern'], rule['message']) 
                      for rule in rules]
            for severity, rules in self.config['risk_rules'].items()
        }
        
        self.logger.debug(f"Loaded {len(self.sensitive_patterns)} sensitive patterns")
        self.logger.debug(f"Loaded risk rules: {self.risk_rules.keys()}")
