"""
Database cache for enhanced extraction results
Stores and retrieves enhanced company data to avoid redundant processing
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict
import hashlib


class EnhancedDataCache:
    """SQLite cache for enhanced extraction results"""
    
    def __init__(self, db_path: str = "data/enhanced_cache.db"):
        """Initialize database connection and create tables if needed"""
        self.db_path = db_path
        
        # Ensure directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Create tables
        self._init_db()
    
    def _init_db(self):
        """Create tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS enhanced_data (
                    company_name TEXT PRIMARY KEY,
                    data_json TEXT NOT NULL,
                    sources_hash TEXT NOT NULL,
                    status TEXT DEFAULT 'ready',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Create index for faster lookups
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_company_name 
                ON enhanced_data(company_name)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_status
                ON enhanced_data(status)
            """)
            
            conn.commit()
    
    def _compute_sources_hash(self, company_folder: str) -> str:
        """
        Compute hash of all source files to detect changes.
        Returns different hash if sources have been added/modified.
        """
        sources_path = Path(company_folder) / "sources"
        
        if not sources_path.exists():
            return ""
        
        # Collect all file paths and their modification times
        file_data = []
        for json_file in sorted(sources_path.glob("*.json")):
            file_data.append(f"{json_file.name}:{json_file.stat().st_mtime}")
        
        # Create hash from concatenated string
        combined = "|".join(file_data)
        return hashlib.md5(combined.encode()).hexdigest()
    
    def get(self, company_name: str, company_folder: str) -> Optional[Dict]:
        """
        Get cached enhanced data for a company.
        Returns None if not cached or if sources have changed.
        
        Args:
            company_name: Name of the company
            company_folder: Path to company data folder (to check for changes)
            
        Returns:
            Cached enhanced data dict or None if cache miss/stale
        """
        # Compute current sources hash
        current_hash = self._compute_sources_hash(company_folder)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT data_json, sources_hash FROM enhanced_data WHERE company_name = ?",
                (company_name,)
            )
            row = cursor.fetchone()
            
            if not row:
                return None  # Cache miss
            
            data_json, cached_hash = row
            
            # Check if sources have changed
            if cached_hash != current_hash:
                return None  # Sources changed, cache is stale
            
            # Return cached data
            return json.loads(data_json)
    
    def set(self, company_name: str, company_folder: str, data: Dict, status: str = 'ready'):
        """
        Store enhanced data in cache.
        
        Args:
            company_name: Name of the company
            company_folder: Path to company data folder
            data: Enhanced data dictionary to cache
            status: Status of the data ('preparing', 'ready', 'error')
        """
        sources_hash = self._compute_sources_hash(company_folder)
        data_json = json.dumps(data, ensure_ascii=False)
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            # Use INSERT OR REPLACE to handle updates
            conn.execute("""
                INSERT OR REPLACE INTO enhanced_data 
                (company_name, data_json, sources_hash, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, 
                    COALESCE((SELECT created_at FROM enhanced_data WHERE company_name = ?), ?),
                    ?)
            """, (company_name, data_json, sources_hash, status, company_name, now, now))
            
            conn.commit()
    
    def set_status(self, company_name: str, status: str):
        """Update status for a company"""
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE enhanced_data 
                SET status = ?, updated_at = ?
                WHERE company_name = ?
            """, (status, now, company_name))
            conn.commit()
    
    def get_status(self, company_name: str) -> Optional[str]:
        """Get preparation status for a company"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT status FROM enhanced_data WHERE company_name = ?",
                (company_name,)
            )
            row = cursor.fetchone()
            return row[0] if row else None
    
    def list_all(self) -> list:
        """List all cached companies with their metadata"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT company_name, status, created_at, updated_at
                FROM enhanced_data
                ORDER BY updated_at DESC
            """)
            rows = cursor.fetchall()
            
            return [
                {
                    'company_name': row[0],
                    'status': row[1],
                    'created_at': row[2],
                    'updated_at': row[3]
                }
                for row in rows
            ]
    
    def delete(self, company_name: str):
        """Delete cached data for a company"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM enhanced_data WHERE company_name = ?", (company_name,))
            conn.commit()
    
    def clear_all(self):
        """Clear all cached data"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM enhanced_data")
            conn.commit()
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM enhanced_data WHERE status = 'ready'")
            ready_count = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM enhanced_data WHERE status = 'preparing'")
            preparing_count = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM enhanced_data")
            total_count = cursor.fetchone()[0]
            
            cursor = conn.execute("""
                SELECT 
                    MIN(created_at) as oldest,
                    MAX(updated_at) as newest
                FROM enhanced_data
            """)
            row = cursor.fetchone()
            oldest, newest = row if row else (None, None)
            
            return {
                'total_cached': total_count,
                'ready': ready_count,
                'preparing': preparing_count,
                'oldest_entry': oldest,
                'newest_entry': newest,
                'db_path': self.db_path
            }


# Global cache instance
_cache = None

def get_cache() -> EnhancedDataCache:
    """Get or create global cache instance"""
    global _cache
    if _cache is None:
        _cache = EnhancedDataCache()
    return _cache
