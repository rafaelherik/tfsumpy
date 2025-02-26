# Models API Reference

## Overview

bolwerk uses several data models to represent different aspects of infrastructure analysis.

## Resource Change Model

```python
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class ResourceChange:
    action: str
    resource_type: str
    identifier: str
    changes: List[str]
    module: str = 'root'
    before: Dict = None
    after: Dict = None
```

## Risk Models

```python
@dataclass
class RiskFinding:
    severity: str
    message: str
    resource_id: str
    impact: str
    mitigation: str = None

@dataclass
class RiskReport:
    findings: List[RiskFinding]
    summary: Dict[str, int]
```

## Policy Models

```python
@dataclass
class PolicyResult:
    policy_id: str
    resource_id: str
    compliant: bool
    severity: str
    message: str
    remediation: str = None

@dataclass
class PolicyReport:
    findings: List[PolicyResult]
```

## Analysis Result Model

```python
@dataclass
class AnalyzerResult:
    category: str
    data: Any
```

## Using Models

### Resource Change Example

```python
change = ResourceChange(
    action="create",
    resource_type="aws_s3_bucket",
    identifier="my_bucket",
    changes=["bucket_name", "versioning"],
    before={},
    after={"bucket_name": "new-bucket", "versioning": True}
)
```

### Risk Finding Example

```python
finding = RiskFinding(
    severity="HIGH",
    message="Security group allows all inbound traffic",
    resource_id="aws_security_group.main",
    impact="Potential security vulnerability",
    mitigation="Restrict inbound rules to specific ports/sources"
)
``` 