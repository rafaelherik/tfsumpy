# Reporters API Reference

## Overview

Reporters in bolwerk are responsible for formatting and displaying analysis results. Each reporter corresponds to a specific type of analysis output.

## Base Reporter Interface

```python
from abc import ABC, abstractmethod
from typing import Any

class ReporterInterface(ABC):
    @property
    @abstractmethod
    def category(self) -> str:
        """Return the reporter category"""
        pass
    
    @abstractmethod
    def print_report(self, data: Any, **kwargs) -> None:
        """Format and print the analysis results"""
        pass
```

## Plan Reporter

The `PlanReporter` formats and displays Terraform plan analysis results.

```python
from bolwerk.plan.reporter import PlanReporter

reporter = PlanReporter()
reporter.print_report(plan_results)
```

## Risk Reporter

The `RiskReporter` formats and displays risk assessment results.

```python
from bolwerk.risk.reporter import RiskReporter

reporter = RiskReporter()
reporter.print_report(risk_results)
```

## Policy Reporter

The `PolicyReporter` formats and displays policy compliance results.

```python
from bolwerk.policy.reporter import PolicyReporter

reporter = PolicyReporter()
reporter.print_report(policy_results)
```

## Creating Custom Reporters

To create a custom reporter:

```python
from bolwerk.reporter import ReporterInterface
from bolwerk.reporters.base_reporter import BaseReporter

class CustomReporter(BaseReporter, ReporterInterface):
    @property
    def category(self) -> str:
        return "custom"
    
    def print_report(self, data: Any, **kwargs) -> None:
        # Implement report formatting and display logic
        self._write("Custom Report\n")
        self._write("=============\n")
        # Add custom formatting logic 