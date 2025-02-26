import pkg_resources
import yaml
import logging
from pathlib import Path
from typing import List
from ..db.manager import DBManager

class DefaultPolicyLoader:
    """Loads default policies from package data."""
    
    def __init__(self, db_manager: DBManager):
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)

    def load_default_policies(self) -> None:
        """Load all default policies from package data."""
        try:
            # Get all policy files from package data
            policy_files = pkg_resources.resource_listdir('bolwerk', 'policies')
            
            for filename in policy_files:
                if filename.endswith('.yaml'):
                    policy_content = pkg_resources.resource_string(
                        'bolwerk', f'policies/{filename}'
                    ).decode('utf-8')
                    
                    try:
                        policy_data = yaml.safe_load(policy_content)
                        provider = policy_data.get('provider')
                        
                        for policy in policy_data.get('policies', []):
                            self.db_manager.add_policy(
                                policy,
                                is_default=True,
                                source_file=f'default/{filename}'
                            )
                            
                        self.logger.info(f"Loaded default policies for provider: {provider}")
                    except yaml.YAMLError as e:
                        self.logger.error(f"Error parsing default policy file {filename}: {e}")
                        
        except Exception as e:
            self.logger.error(f"Error loading default policies: {e}") 