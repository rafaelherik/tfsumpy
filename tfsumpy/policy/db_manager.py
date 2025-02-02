import sqlite3
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class Policy:
    id: str
    name: str
    description: str
    provider: str
    resource_type: str
    severity: str
    condition: Dict
    remediation: Optional[str] = None

class PolicyDBManager:
    """Manages the local SQLite database for storing policies."""
    
    def __init__(self, db_path: str = None):
        """Initialize the database manager.
        
        Args:
            db_path: Optional path to the database file. If None, uses default location.
        """
        if not db_path:
            db_path = str(Path.home() / '.tfsumpy' / 'policies.db')
        
        # Ensure directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS policies (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    provider TEXT NOT NULL,
                    resource_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    condition JSON NOT NULL,
                    remediation TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    source_file TEXT
                )
            """)
            conn.commit()

    def add_policy(self, policy: Policy, source_file: str = None) -> None:
        """Add a new policy to the database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO policies 
                (id, name, description, provider, resource_type, severity, condition, remediation, source_file)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                policy.id,
                policy.name,
                policy.description,
                policy.provider,
                policy.resource_type,
                policy.severity,
                json.dumps(policy.condition),
                policy.remediation,
                source_file
            ))
            conn.commit()

    def get_policies(self, provider: str = None, resource_type: str = None) -> List[Policy]:
        """Retrieve policies with optional filtering."""
        query = "SELECT * FROM policies"
        params = []
        
        if provider or resource_type:
            conditions = []
            if provider:
                conditions.append("provider IN (?, 'any')")
                params.append(provider)
            if resource_type:
                conditions.append("resource_type = ?")
                params.append(resource_type)
            query += " WHERE " + " AND ".join(conditions)

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            
            return [Policy(
                id=row['id'],
                name=row['name'],
                description=row['description'],
                provider=row['provider'],
                resource_type=row['resource_type'],
                severity=row['severity'],
                condition=json.loads(row['condition']),
                remediation=row['remediation']
            ) for row in rows]

    def clear_policies(self, source_file: str = None) -> None:
        """Clear policies, optionally only from a specific source file."""
        with sqlite3.connect(self.db_path) as conn:
            if source_file:
                conn.execute("DELETE FROM policies WHERE source_file = ?", (source_file,))
            else:
                conn.execute("DELETE FROM policies")
            conn.commit() 