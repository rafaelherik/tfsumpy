import yaml
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional
from jsonschema import validate, ValidationError
from ..db.manager import DBManager

class PolicyLoader:
    """Loads and validates both default and custom policy files."""
    
    def __init__(self, db_manager: DBManager):
        """Initialize the policy loader.
        
        Args:
            db_manager: Instance of DBManager for storing policies
        """
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        
        # Load schema
        schema_path = Path(__file__).parent.parent / 'schemas' / 'policy_schema.yaml'
        with open(schema_path) as f:
            self.schema = yaml.safe_load(f)

    def initialize_policies(self, custom_policy_path: Optional[str] = None) -> None:
        """Initialize policies by loading both default and custom policies.
        
        Args:
            custom_policy_path: Optional path to directory containing custom policy files
        """
        try:
            # Load default policies first
            self._load_default_policies()
            
            # Load custom policies if specified
            if custom_policy_path:
                self.load_policy_directory(custom_policy_path)
                
        except Exception as e:
            self.logger.error(f"Failed to initialize policies: {str(e)}")
            raise

    def _load_default_policies(self) -> None:
        """Load default policies from package data."""
        try:
            default_policy_dir = Path(__file__).parent.parent / 'policies'
            if not default_policy_dir.exists():
                self.logger.warning("No default policies directory found")
                return
                
            for policy_file in default_policy_dir.glob("*.yaml"):
                try:
                    self._load_single_policy(str(policy_file), is_default=True)
                except Exception as e:
                    self.logger.error(f"Failed to load default policy file {policy_file}: {str(e)}")
                    
        except Exception as e:
            self.logger.error(f"Error loading default policies: {str(e)}")
            raise

    def _load_single_policy(self, file_path: str, is_default: bool = False) -> None:
        """Load and validate a single policy file.
        
        Args:
            file_path: Path to the policy YAML file
            is_default: Whether this is a default policy file
        
        Raises:
            ValidationError: If the policy file doesn't match the schema
            yaml.YAMLError: If the file isn't valid YAML
        """
        try:
            with open(file_path) as f:
                policy_data = yaml.safe_load(f)
            
            if not policy_data:
                self.logger.warning(f"Empty policy file: {file_path}")
                return
            
            # Validate against schema
            validate(instance=policy_data, schema=self.schema)
            
            # Add policies to database
            for policy_dict in policy_data['policies']:
                try:
                    self.db_manager.add_policy(
                        policy=policy_dict,
                        is_default=is_default,
                        source_file=file_path
                    )
                    self.logger.debug(f"Added policy {policy_dict.get('id')} from {file_path}")
                except Exception as e:
                    self.logger.error(f"Failed to add policy from {file_path}: {str(e)}")
                    raise
                
            self.logger.info(
                f"Successfully loaded {len(policy_data['policies'])} "
                f"{'default' if is_default else 'custom'} policies from {file_path}"
            )
            
        except ValidationError as e:
            self.logger.error(f"Policy validation failed for {file_path}: {str(e)}")
            raise
        except yaml.YAMLError as e:
            self.logger.error(f"Failed to parse YAML file {file_path}: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error loading policy file {file_path}: {str(e)}")
            raise

    def load_policy_directory(self, directory: str) -> None:
        """Load all policy files from a directory.
        
        Args:
            directory: Path to directory containing policy YAML files
            
        Raises:
            ValueError: If directory doesn't exist
        """
        policy_dir = Path(directory)
        if not policy_dir.is_dir():
            raise ValueError(f"Policy directory not found: {directory}")
        
        loaded_count = 0
        error_count = 0
        
        for policy_file in policy_dir.glob("*.yaml"):
            try:
                self._load_single_policy(str(policy_file), is_default=False)
                loaded_count += 1
            except Exception as e:
                self.logger.error(f"Failed to load policy file {policy_file}: {str(e)}")
                error_count += 1
            
        self.logger.info(
            f"Loaded {loaded_count} policies from directory {directory} "
            f"({error_count} errors)"
        ) 