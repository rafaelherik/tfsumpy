from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod
from ..resource import ResourceChange

@dataclass
class RiskFinding:
    severity: str
    message: str
    resource_id: str
    impact: Optional[str] = None
    mitigation: Optional[str] = None

@dataclass
class RiskReport:
    findings: List[RiskFinding]
    summary: Dict[str, int]  # Count by severity
    
    def __init__(self, findings: List[RiskFinding]):
        self.findings = findings
        self.summary = self._generate_summary()
    
    def _generate_summary(self) -> Dict[str, int]:
        summary = {'high': 0, 'medium': 0, 'low': 0}
        for finding in self.findings:
            summary[finding.severity.lower()] += 1
        return summary
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'findings': [vars(f) for f in self.findings],
            'summary': self.summary
        }

class ProviderRiskAnalyzer(ABC):
    """Interface for provider-specific risk analyzers."""
    
    @property
    @abstractmethod
    def provider(self) -> str:
        """Return the provider name (e.g., 'aws', 'azure', 'google')."""
        pass
    
    @abstractmethod
    def analyze(self, change: ResourceChange) -> List[RiskFinding]:
        """Analyze risks for a specific resource change."""
        pass

class RiskAnalyzerInterface(ABC):
    """Interface for provider-specific risk analyzers."""
    
    @abstractmethod
    def analyze(self, change: 'ResourceChange') -> List[RiskFinding]:
        """Analyze a single resource change for risks."""
        pass
    
    @property
    @abstractmethod
    def provider(self) -> str:
        """Return the provider name this analyzer handles."""
        pass 