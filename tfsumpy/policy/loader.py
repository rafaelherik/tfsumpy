import yaml
import json
import logging
from pathlib import Path
from typing import List, Dict
from jsonschema import validate, ValidationError
from .db_manager import PolicyDBManager, Policy

class PolicyLoader:
    """Loads and validates policy files."""
    
    def __init__(self, db_manager: PolicyDBManager):
        """Initialize the policy loader.
        
        Args:
            db_manager: Instance of PolicyDBManager for storing policies
        """
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        
        # Load schema
        schema_path = Path(__file__).parent.parent / 'schemas' / 'policy_schema.yaml'
        with open(schema_path) as f:
            self.schema = yaml.safe_load(f)

    def load_policy_file(self, file_path: str) -> None:
        """Load and validate a single policy file.
        
        Args:
            file_path: Path to the policy YAML file
        
        Raises:
            ValidationError: If the policy file doesn't match the schema
            yaml.YAMLError: If the file isn't valid YAML
        """
        try:
            with open(file_path) as f:
                policy_data = yaml.safe_load(f)
            
            # Validate against schema
            validate(instance=policy_data, schema=self.schema)
            
            # Clear existing policies from this file
            self.db_manager.clear_policies(file_path)
            
            # Add new policies
            for policy_dict in policy_data['policies']:
                policy = Policy(
                    id=policy_dict['id'],
                    name=policy_dict['name'],
                    description=policy_dict.get('description', ''),
                    provider=policy_dict['provider'],
                    resource_type=policy_dict['resource_type'],
                    severity=policy_dict['severity'],
                    condition=policy_dict['condition'],
                    remediation=policy_dict.get('remediation')
                )
                self.db_manager.add_policy(policy, file_path)
                
            self.logger.info(f"Successfully loaded {len(policy_data['policies'])} policies from {file_path}")
            
        except ValidationError as e:
            self.logger.error(f"Policy validation failed for {file_path}: {str(e)}")
            raise
        except yaml.YAMLError as e:
            self.logger.error(f"Failed to parse YAML file {file_path}: {str(e)}")
            raise

    def load_policy_directory(self, directory: str) -> None:
        """Load all policy files from a directory.
        
        Args:
            directory: Path to directory containing policy YAML files
        """
        policy_dir = Path(directory)
        if not policy_dir.is_dir():
            raise ValueError(f"Directory not found: {directory}")
            
        for policy_file in policy_dir.glob("*.yaml"):
            try:
                self.load_policy_file(str(policy_file))
            except Exception as e:
                self.logger.error(f"Failed to load policy file {policy_file}: {str(e)}") 