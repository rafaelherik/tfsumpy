# Models API Reference

## Overview

**tfsumpy** uses several data models to represent the results of plan analysis and reporting. Understanding these models is essential for extending tfsumpy or integrating it into other tools.

---

## ResourceChange

Represents a single resource change in a Terraform plan.

```python
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class ResourceChange:
    action: str           # 'create', 'update', or 'delete'
    resource_type: str    # e.g., 'aws_s3_bucket'
    identifier: str       # Resource address (e.g., 'aws_s3_bucket.my_bucket')
    changes: List[str]    # List of changed attributes (optional/legacy)
    module: str = 'root'  # Module path (e.g., 'root', 'network.vpc')
    before: Dict = None   # State before the change
    after: Dict = None    # State after the change
```

**Fields:**
- `action`: The type of change ('create', 'update', 'delete')
- `resource_type`: The Terraform resource type
- `identifier`: The resource address in the plan
- `changes`: List of changed attributes (may be empty)
- `module`: Module path (default 'root')
- `before`: Dictionary of the resource's state before the change
- `after`: Dictionary of the resource's state after the change

---

## AnalyzerResult

Represents the result of an analyzer (e.g., PlanAnalyzer).

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class AnalyzerResult:
    category: str   # e.g., 'plan'
    data: Any      # Typically a dict with summary and resource changes
```

**Fields:**
- `category`: The analyzer category (e.g., 'plan')
- `data`: The analysis result (usually a dict with summary and resource changes)

---

## Example: Using Models

### ResourceChange Example

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

### AnalyzerResult Example

```python
result = AnalyzerResult(
    category="plan",
    data={
        "total_changes": 1,
        "change_breakdown": {"create": 1, "update": 0, "delete": 0},
        "resources": [change]
    }
)
```

---

## Notes
- The `data` field in `AnalyzerResult` is typically a dictionary with keys like `total_changes`, `change_breakdown`, and `resources` (a list of `ResourceChange` objects or dicts).
- See the [Analyzers API](analyzers.md) and [Reporters API](reporters.md) for how these models are used in practice. 