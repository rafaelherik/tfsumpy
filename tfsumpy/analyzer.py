from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .context import Context
from dataclasses import dataclass

@dataclass
class AnalyzerResult:
    """Base class for analyzer results"""
    category: str
    data: Any

class AnalyzerInterface(ABC):
    """Interface for all analyzers"""
    
    @property
    @abstractmethod
    def category(self) -> str:
        """Return the analyzer category"""
        pass
    
    @abstractmethod
    def analyze(self, context: 'Context', **kwargs) -> AnalyzerResult:
        """Perform analysis and return results"""
        pass 