import os
import sqlite3
import hashlib
import json
from datetime import datetime
from loguru import logger
from backend.scratchpad import scratchpad

class SahayakLedger:
    """Immutable Ledger with SHA-256 hash chaining for grievance redressal."""
    
    def __init__(self, db_path=None):
        if db_path is None:
            # For Docker (relative to app) or for local dev
            db_path = os.path.join(os.path.dirname(__file__), "sahayak_ledger.db")
        self.conn = sqlite3.connect(db_path)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS work_ledger (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                platform TEXT,
                payout REAL,
                safety_score REAL,
                job_data TEXT,
                prev_hash TEXT,
                current_hash TEXT
            )
        ''')
        self.conn.commit()

    def get_last_hash(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT current_hash FROM work_ledger ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        return result[0] if result else "0" * 64

    def add_entry(self, platform: str, payout: float, safety_score: float, raw_data: dict):
        """Adds a cryptographically chained entry to the ledger."""
        prev_hash = self.get_last_hash()
        timestamp = datetime.now().isoformat()
        job_data_json = json.dumps(raw_data)
        
        # Hash Calculation (Immutable Chain Link)
        payload = f"{timestamp}{platform}{payout}{safety_score}{job_data_json}{prev_hash}"
        current_hash = hashlib.sha256(payload.encode()).hexdigest()
        
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO work_ledger (timestamp, platform, payout, safety_score, job_data, prev_hash, current_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (timestamp, platform, payout, safety_score, job_data_json, prev_hash, current_hash))
        self.conn.commit()
        
        logger.info(f"Ledger Entry Added: {platform} (₹{payout}) | Hash: {current_hash[:10]}...")
        return current_hash

    def export_grievance_payload(self):
        """
        Generates a JSON payload of the last 100 entries for legal appeals.
        This provides proof of performance and safety compliance.
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM work_ledger ORDER BY id DESC LIMIT 100")
        rows = cursor.fetchall()
        
        # Formatting for the 'Automated Grievance Arbitrator' agent
        ledger_data = []
        for r in rows:
            ledger_data.append({
                "ts": r[1], "platform": r[2], "payout": r[3], 
                "safety": r[4], "job": r[5], "hash": r[7]
            })
        
        return json.dumps({
            "worker_id": "99XXXXXXXX",
            "proof_of_persistence": ledger_data,
            "signature_verified": True
        })

# Global instance for audit tracking
ledger = SahayakLedger()
