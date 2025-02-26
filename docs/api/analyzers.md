# Analyzers API Reference

## Overview

Analyzers in bolwerk are responsible for analyzing different aspects of Terraform plans. Each analyzer focuses on a specific type of analysis (plan, risk, or policy).

## Base Analyzer Interface

```python
from abc import ABC, abstractmethod
from typing import Any

class AnalyzerInterface(ABC):
    @property
    @abstractmethod
    def category(self) -> str:
        """Return the analyzer category"""
        pass
    
    @abstractmethod
    def analyze(self, context: 'Context', **kwargs) -> 'AnalyzerResult':
        """Perform analysis and return results"""
        pass
```

## Plan Analyzer

The `PlanAnalyzer` processes Terraform plan files and extracts change information.

```python
from bolwerk.plan.analyzer import PlanAnalyzer

analyzer = PlanAnalyzer(context)
result = analyzer.analyze(context, plan_path="plan.json")
```

## Risk Analyzer

The `RiskAnalyzer` evaluates potential risks in infrastructure changes.

```python
from bolwerk.risk.analyzer import RiskAnalyzer

analyzer = RiskAnalyzer()
result = analyzer.analyze(context)
```

## Policy Analyzer

The `PolicyAnalyzer` checks resources against defined policies.

```python
from bolwerk.policy.analyzer import PolicyAnalyzer

analyzer = PolicyAnalyzer(db_manager)
result = analyzer.analyze(context)
```

## Creating Custom Analyzers

To create a custom analyzer:

```python
from bolwerk.analyzer import AnalyzerInterface, AnalyzerResult

class CustomAnalyzer(AnalyzerInterface):
    @property
    def category(self) -> str:
        return "custom"
    
    def analyze(self, context: 'Context', **kwargs) -> AnalyzerResult:
        # Implement analysis logic
        return AnalyzerResult(category="custom", data={}) 