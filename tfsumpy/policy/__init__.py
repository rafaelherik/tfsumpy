"""Policy module for TFSumPy.

This module provides policy management functionality including policy loading,
database management, and policy evaluation.
"""

from .db_manager import Policy, PolicyDBManager
from .loader import PolicyLoader

# Feature flag for policy functionality
POLICY_FEATURE_ENABLED = False

__all__ = [
    'Policy',
    'PolicyDBManager',
    'PolicyLoader',
    'POLICY_FEATURE_ENABLED',
]
