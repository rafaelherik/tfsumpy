import logging
from pathlib import Path
import sqlite3
import json
from typing import List, Dict


 
class DBManager:
    """Global database manager for bulwerk."""
    
    def __init__(self, db_path: str = None):
        if not db_path:
            db_path = str(Path.home() / '.bulwerk' / 'bulwerk.db')
        
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            # Policies table with override support
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
                    disabled BOOLEAN DEFAULT FALSE,
                    is_default BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    source_file TEXT
                )
            """)
            conn.commit()

    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """Execute a query and return results as dictionaries."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def execute_update(self, query: str, params: tuple = ()) -> None:
        """Execute an update query."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(query, params)
            conn.commit()

    def add_policy(self, policy: Dict, is_default: bool = False, source_file: str = None) -> None:
        """Add or update a policy."""
        with sqlite3.connect(self.db_path) as conn:
            # If policy exists and is default, only update if new policy is custom
            if is_default:
                conn.execute("""
                    INSERT OR IGNORE INTO policies 
                    (id, name, description, provider, resource_type, severity, 
                     condition, remediation, disabled, is_default, source_file)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    policy['id'], policy['name'], policy['description'],
                    policy['provider'], policy['resource_type'], policy['severity'],
                    json.dumps(policy['condition']), policy.get('remediation'),
                    policy.get('disabled', False), True, source_file
                ))
            else:
                # Custom policies override default ones
                conn.execute("""
                    INSERT OR REPLACE INTO policies 
                    (id, name, description, provider, resource_type, severity, 
                     condition, remediation, disabled, is_default, source_file)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    policy['id'], policy['name'], policy['description'],
                    policy['provider'], policy['resource_type'], policy['severity'],
                    json.dumps(policy['condition']), policy.get('remediation'),
                    policy.get('disabled', False), False, source_file
                ))
            conn.commit() 