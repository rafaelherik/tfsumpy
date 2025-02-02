from abc import ABC, abstractmethod
from typing import Any

class ReporterInterface(ABC):
    """Interface for all reporters"""
    
    @property
    @abstractmethod
    def category(self) -> str:
        """Return the reporter category"""
        pass
    
    @abstractmethod
    def get_report(self, data: Any, **kwargs) -> Any:
        """Return the analysis results object"""
        pass
        
    @abstractmethod
    def print_report(self, data: Any, **kwargs) -> None:
        """Format and print the analysis results"""
        pass 