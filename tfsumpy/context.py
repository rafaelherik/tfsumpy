import json
import logging
import os
from typing import Dict, List, Type, Any, Optional
from pathlib import Path
from .analyzer import AnalyzerInterface, AnalyzerResult, AnalyzerCategory
from .reporter import ReporterInterface

class ConfigurationError(Exception):
    """Raised when there is an error in configuration loading or validation"""
    pass

class Context:
    """Application context that manages analyzers and configuration.
    
    This class serves as the central hub for managing analyzers, reporters,
    and configuration. It provides a consistent interface for accessing
    application state and configuration.
    
    Attributes:
        config_path: Path to the external configuration file
        debug: Whether debug mode is enabled
        logger: Logger instance for this context
        sensitive_patterns: List of patterns for sensitive data
        config: Loaded configuration dictionary
        _analyzers: Registry of analyzers by category
        _reporters: Registry of reporters by category
        plan_data: Cached Terraform plan data
    """
    
    def __init__(self, config_path: Optional[str] = None, debug: bool = False):
        self.config_path = config_path
        self.debug = debug
        
        # Configure logging
        self.logger = logging.getLogger(__name__)
        log_level = logging.DEBUG if debug else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Initialize components
        self.sensitive_patterns: List[tuple] = []
        self.config: Dict[str, Any] = {}
        
        # Initialize analyzer registry
        self._analyzers: Dict[AnalyzerCategory, List[AnalyzerInterface]] = {}
        self._reporters: Dict[str, List[ReporterInterface]] = {}
        self.plan_data: Optional[Dict] = None

    def register_analyzer(self, analyzer: AnalyzerInterface) -> None:
        """Register an analyzer in its category.
        
        Args:
            analyzer: Analyzer instance implementing AnalyzerInterface
            
        Raises:
            ValueError: If analyzer is invalid or already registered
        """
        # Validate analyzer has a valid category attribute (enum or string)
        from .analyzer import AnalyzerCategory
        cat = getattr(analyzer, 'category', None)
        if not isinstance(cat, (AnalyzerCategory, str)):
            raise ValueError("Analyzer must implement AnalyzerInterface with valid category")
        category = cat
        if category not in self._analyzers:
            self._analyzers[category] = []
            
        if analyzer not in self._analyzers[category]:
            self.logger.debug(f"Registering analyzer {analyzer.__class__.__name__} for category {category}")
            self._analyzers[category].append(analyzer)
        else:
            raise ValueError(f"Analyzer {analyzer.__class__.__name__} already registered for category {category}")
    
    def get_analyzers(self, category: AnalyzerCategory) -> List[AnalyzerInterface]:
        """Get all registered analyzers for a category.
        
        Args:
            category: Analyzer category to retrieve
            
        Returns:
            List of registered analyzers for the category
        """
        return self._analyzers.get(category, [])
    
    def run_analyzers(self, category: AnalyzerCategory, **kwargs) -> List[AnalyzerResult]:
        """Run all analyzers for a specific category.
        
        Args:
            category: Category of analyzers to run
            **kwargs: Additional arguments to pass to analyzers
            
        Returns:
            List of analyzer results
            
        Raises:
            RuntimeError: If no analyzers are registered for the category
        """
        results = []
        analyzers = self.get_analyzers(category)
        
        if not analyzers:
            raise RuntimeError(f"No analyzers registered for category {category}")
        
        for analyzer in analyzers:
            try:
                self.logger.debug(f"Running analyzer {analyzer.__class__.__name__}")
                result = analyzer.analyze(self, **kwargs)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Error running analyzer {analyzer.__class__.__name__}: {str(e)}")
                if self.debug:
                    self.logger.exception("Detailed error:")
                results.append(AnalyzerResult(
                    category=category,
                    data=None,
                    success=False,
                    error=str(e)
                ))
        
        return results
    
    def set_plan_data(self, plan_data: Dict) -> None:
        """Store plan data in context.
        
        Args:
            plan_data: Terraform plan data
        """
        self.plan_data = plan_data
    
    def get_plan_data(self) -> Dict:
        """Retrieve stored plan data.
        
        Returns:
            Stored Terraform plan data
        """
        return self.plan_data

    def load_config(self) -> None:
        """Load and merge configuration files
        
        Raises:
            ConfigurationError: If configuration loading or validation fails
        """
        try:
            # Load default config
            default_config_path = Path(__file__).parent / 'rules_config.json'
            self.logger.debug(f"Loading default config file: {default_config_path}")
            
            with open(default_config_path, 'r') as f:
                self.config = json.load(f)
                
            # Validate default config
            self._validate_config(self.config)
            
            # Merge external config if provided
            if self.config_path:
                self._merge_external_config()
            
            # Process configuration
            self._process_config()
            
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {str(e)}")

    def _validate_config(self, config: Dict[str, Any]) -> None:
        """Validate configuration structure and values
        
        Args:
            config: Configuration dictionary to validate
            
        Raises:
            ConfigurationError: If validation fails
        """
        required_keys = {'sensitive_patterns'}
        missing_keys = required_keys - set(config.keys())
        if missing_keys:
            raise ConfigurationError(f"Missing required configuration keys: {missing_keys}")
            
        if not isinstance(config['sensitive_patterns'], list):
            raise ConfigurationError("sensitive_patterns must be a list")
            
        for pattern in config['sensitive_patterns']:
            if not isinstance(pattern, dict) or 'pattern' not in pattern or 'replacement' not in pattern:
                raise ConfigurationError("Each sensitive pattern must have 'pattern' and 'replacement' keys")

    def _merge_external_config(self) -> None:
        """Merge external configuration with default configuration
        
        Raises:
            ConfigurationError: If external config loading or merging fails
        """
        self.logger.debug(f"Merging external config file: {self.config_path}")
        try:
            with open(self.config_path, 'r') as f:
                external_config = json.load(f)
                
            # Validate external config
            self._validate_config(external_config)
                
            # Merge sensitive patterns
            self.config['sensitive_patterns'].extend(
                external_config.get('sensitive_patterns', [])
            )
            
            self.logger.debug("Successfully merged external config")
        except FileNotFoundError:
            raise ConfigurationError(f"External config file not found: {self.config_path}")
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Error parsing external JSON config file: {str(e)}")
        except Exception as e:
            raise ConfigurationError(f"Error merging external config: {str(e)}")

    def _process_config(self) -> None:
        """Process loaded configuration into usable formats
        
        Raises:
            ConfigurationError: If processing fails
        """
        try:
            self.sensitive_patterns = [
                (rule['pattern'], rule['replacement']) 
                for rule in self.config['sensitive_patterns']
            ]
            
            self.logger.debug(f"Loaded {len(self.sensitive_patterns)} sensitive patterns")
        except Exception as e:
            raise ConfigurationError(f"Error processing configuration: {str(e)}")

    def register_reporter(self, reporter: ReporterInterface) -> None:
        """Register a reporter.

        Args:
            reporter: The reporter to register

        Raises:
            ValueError: If the reporter is invalid or already registered
        """
        if not isinstance(reporter, ReporterInterface):
            raise ValueError("Invalid reporter")
        
        category = reporter.category
        if category not in self._reporters:
            self._reporters[category] = []
        
        if reporter in self._reporters[category]:
            raise ValueError("Reporter already registered")
        
        self._reporters[category].append(reporter)
        self.logger.debug(f"Registered reporter {reporter.__class__.__name__} for category {category}")

    def get_reporters(self, category: str) -> List[ReporterInterface]:
        """Get all registered reporters for a category."""
        return self._reporters.get(category, [])

    def run_reports(self, category: str, data: Any, **kwargs) -> None:
        """Run all reporters for a specific category.
        
        Args:
            category: Category of reporters to run
            data: Data to report
            **kwargs: Additional arguments to pass to reporters
        """
        reporters = self.get_reporters(category)
        
        for reporter in reporters:
            try:
                self.logger.debug(f"Running reporter {reporter.__class__.__name__}")
                reporter.print_report(data, **kwargs)
            except Exception as e:
                self.logger.error(f"Error running reporter {reporter.__class__.__name__}: {str(e)}")
                if self.debug:
                    self.logger.exception("Detailed error:")
