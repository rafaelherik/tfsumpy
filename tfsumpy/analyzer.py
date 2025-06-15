from abc import ABC, abstractmethod
from typing import Dict, List, Any, Protocol, runtime_checkable
from dataclasses import dataclass
from enum import Enum, auto

class AnalyzerCategory(Enum):
    """Enumeration of supported analyzer categories"""
    PLAN = auto()
    SECURITY = auto()
    COST = auto()
    COMPLIANCE = auto()

@dataclass(frozen=True)
class AnalyzerResult:
    """Result of an analyzer execution.
    
    Attributes:
        category: Category of the analyzer
        data: Analysis results
        success: Whether the analysis was successful
        error: Error message if analysis failed
    """
    category: AnalyzerCategory
    data: Any
    success: bool = True
    error: str = ""

@runtime_checkable
class AnalyzerInterface(Protocol):
    """Interface for all analyzers
    
    This interface defines the contract that all analyzers must implement.
    Analyzers are responsible for analyzing specific aspects of Terraform plans
    and producing structured results.
    """
    
    @property
    def category(self) -> AnalyzerCategory:
        """Return the analyzer category
        
        Returns:
            AnalyzerCategory: The category this analyzer belongs to
        """
        ...
    
    def analyze(self, context: 'Context', **kwargs) -> AnalyzerResult:
        """Perform analysis and return results
        
        Args:
            context: The application context containing configuration and state
            **kwargs: Additional arguments specific to the analyzer
            
        Returns:
            AnalyzerResult: The analysis results
            
        Raises:
            ValueError: If required arguments are missing or invalid
            RuntimeError: If analysis fails due to runtime issues
        """
        ... 