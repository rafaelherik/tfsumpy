from dataclasses import dataclass
from typing import List, Optional

@dataclass
class PolicyResult:
    """Represents a single policy check result."""
    policy_id: str
    resource_id: str
    severity: str
    message: str
    compliant: bool
    remediation: Optional[str] = None

@dataclass
class PolicyReport:
    """Container for policy check results."""
    findings: List[PolicyResult] 