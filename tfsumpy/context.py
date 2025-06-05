import json
import logging
import os
from typing import Dict, List, Type, Any
from .analyzer import AnalyzerInterface, AnalyzerResult
from .reporter import ReporterInterface

class Context:
    """Application context that manages analyzers and configuration."""
    
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
        
        # Initialize components
        self.sensitive_patterns = []
        self.config = {}
        
        # Initialize analyzer registry
        self._analyzers: Dict[str, List[AnalyzerInterface]] = {}
        self._reporters: Dict[str, List[ReporterInterface]] = {}
        self.plan_data = None

    def register_analyzer(self, analyzer: AnalyzerInterface) -> None:
        """Register an analyzer in its category.
        
        Args:
            analyzer: Analyzer instance implementing AnalyzerInterface
        """
        if not isinstance(analyzer, AnalyzerInterface):
            raise ValueError("Analyzer must implement AnalyzerInterface")
            
        category = analyzer.category
        if category not in self._analyzers:
            self._analyzers[category] = []
            
        if analyzer not in self._analyzers[category]:
            self.logger.debug(f"Registering analyzer {analyzer.__class__.__name__} for category {category}")
            self._analyzers[category].append(analyzer)
    
    def get_analyzers(self, category: str) -> List[AnalyzerInterface]:
        """Get all registered analyzers for a category.
        
        Args:
            category: Analyzer category to retrieve
            
        Returns:
            List of registered analyzers for the category
        """
        return self._analyzers.get(category, [])
    
    def run_analyzers(self, category: str, **kwargs) -> List[AnalyzerResult]:
        """Run all analyzers for a specific category.
        
        Args:
            category: Category of analyzers to run
            **kwargs: Additional arguments to pass to analyzers
            
        Returns:
            List of analyzer results
        """
        results = []
        analyzers = self.get_analyzers(category)
        
        for analyzer in analyzers:
            try:
                self.logger.debug(f"Running analyzer {analyzer.__class__.__name__}")
                result = analyzer.analyze(self, **kwargs)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Error running analyzer {analyzer.__class__.__name__}: {str(e)}")
                if self.debug:
                    self.logger.exception("Detailed error:")
        
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
        
        self.logger.debug(f"Loaded {len(self.sensitive_patterns)} sensitive patterns")

    def register_reporter(self, reporter: ReporterInterface) -> None:
        """Register a reporter in its category.
        
        Args:
            reporter: Reporter instance implementing ReporterInterface
        """
        if not isinstance(reporter, ReporterInterface):
            raise ValueError("Reporter must implement ReporterInterface")
            
        category = reporter.category
        if category not in self._reporters:
            self._reporters[category] = []
            
        if reporter not in self._reporters[category]:
            self.logger.debug(f"Registering reporter {reporter.__class__.__name__} for category {category}")
            self._reporters[category].append(reporter)

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
