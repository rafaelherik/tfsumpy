from dataclasses import dataclass
from typing import List, Dict

@dataclass
class ResourceChange:
    action: str
    resource_type: str
    identifier: str
    changes: List[str]
    module: str = 'root'
    before: dict = None
    after: dict = None

    def __init__(self, action: str, resource_type: str, identifier: str, 
                 changes: dict, module: str = 'root', before: dict = None, 
                 after: dict = None):
        self.action = action
        self.resource_type = resource_type
        self.identifier = identifier
        self.changes = changes
        self.module = module
        self.before = before or {}
        self.after = after or {}