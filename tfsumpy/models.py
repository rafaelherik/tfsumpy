from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class ResourceChange:
    """Represents a change to a Terraform resource."""
    action: str  # 'create', 'update', or 'delete'
    resource_type: str
    identifier: str
    data: Optional[Dict[str, Any]] = None 