from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class ResourceChange:
    """Represents a single Terraform resource change."""

    action: str
    resource_type: str
    identifier: str
    changes: Dict[str, Any] = field(default_factory=dict)
    module: str = "root"
    before: Dict[str, Any] = field(default_factory=dict)
    after: Dict[str, Any] = field(default_factory=dict)
    replacement: bool = False
    replacement_triggers: list = field(default_factory=list)