import importlib
import pkgutil
from typing import Dict, List, Optional
from pathlib import Path
import logging
from ..resource import ResourceChange
from .models import ProviderRiskAnalyzer, RiskFinding, RiskReport
from ..analyzer import AnalyzerInterface, AnalyzerResult
from colorama import Fore

class RiskAnalyzer(AnalyzerInterface):
    """Main risk analyzer that coordinates provider-specific analyzers."""
    
    def __init__(self):
        """Initialize the risk analyzer."""
        self.logger = logging.getLogger(__name__)
        self.provider_analyzers: Dict[str, ProviderRiskAnalyzer] = {}
        self._load_provider_analyzers()
    
    @property
    def category(self) -> str:
        """Return the analyzer category."""
        return "risk"
    
    def _load_provider_analyzers(self) -> None:
        """Dynamically load all provider analyzers from the providers package."""
        providers_path = Path(__file__).parent / "providers"
        
        if not providers_path.exists():
            self.logger.error(f"Providers directory not found: {providers_path}")
            return

        for module_info in pkgutil.iter_modules([str(providers_path)]):
            try:
                module = importlib.import_module(f".providers.{module_info.name}", package="tfsumpy.risk")
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, ProviderRiskAnalyzer) and 
                        attr != ProviderRiskAnalyzer):
                        analyzer = attr()
                        self.provider_analyzers[analyzer.provider] = analyzer
                        self.logger.debug(f"Loaded provider analyzer: {analyzer.provider}")
            except Exception as e:
                self.logger.error(f"Error loading provider module {module_info.name}: {str(e)}")
    
    def analyze(self, context) -> AnalyzerResult:
        """Analyze risks using provider-specific analyzers.
        
        Args:
            context: Analysis context containing plan data
            
        Returns:
            AnalyzerResult containing risk findings
        """
        findings: List[RiskFinding] = []
        processed_resources = set()
        
        try:
            plan_data = context.get_plan_data()
            if not isinstance(plan_data, dict) or 'resources' not in plan_data:
                self.logger.error("Invalid plan data format")
                return AnalyzerResult(category=self.category, data=RiskReport(findings=[]))
            
            changes = plan_data['resources']
            
            for change in changes:
                try:
                    # Validate resource is a dictionary
                    if not isinstance(change, dict):
                        self.logger.error("Invalid resource change format")
                        continue
                        
                    resource_id = change.get('identifier')
                    resource_type = change.get('resource_type')
                    
                    # Skip already processed resources
                    if resource_id in processed_resources:
                        continue

                    # Handle malformed resource types
                    if not resource_type:
                        self.logger.warning(f"Empty or missing resource type for resource: {resource_id}")
                        continue

                    provider = self._get_provider_from_resource(resource_type)
                    if not provider:
                        self.logger.warning(f"Could not determine provider from resource type: {resource_type}")
                        continue
                    
                    if provider in self.provider_analyzers:
                        try:
                            provider_findings = self.provider_analyzers[provider].analyze(change)
                            if provider_findings:
                                findings.extend(provider_findings)
                            processed_resources.add(resource_id)
                        except Exception as e:
                            self.logger.error(f"Provider analyzer error for {resource_id}: {str(e)}")
                    else:
                        self.logger.warning(f"No analyzer found for provider: {provider}")
                    
                except Exception as e:
                    self.logger.error(f"Error processing resource change: {str(e)}")
                    continue
                
        except Exception as e:
            self.logger.error(f"Error during analysis: {str(e)}")
            
        return AnalyzerResult(
            category=self.category,
            data=RiskReport(findings=findings)
        )
    
    def _get_provider_from_resource(self, resource_type: str) -> str:
        """Extract provider from resource type.
        
        Args:
            resource_type: Resource type string (e.g., 'aws_s3_bucket')
            
        Returns:
            Provider name or empty string if not found
        """
        if not resource_type or not isinstance(resource_type, str):
            return ''
        parts = resource_type.split('_')
        return parts[0] if len(parts) > 1 else '' 