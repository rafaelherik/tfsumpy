from dataclasses import dataclass
from typing import List

@dataclass
class ResourceChange:
    action: str
    resource_type: str
    identifier: str
    changes: List[str]