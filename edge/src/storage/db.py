import sqlite3
import sqlcipher3
import os
import json
import uuid
import hashlib
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class Employee:
    id: str
    name_ar: str
    name_en: str
    status: str = "active"


@dataclass
class BiometricTemplate:
    id: int
    employee_id: str
    vector_blob: bytes
    pose: str


@dataclass
class AttendanceLog:
    id: str
    employee_id: str
    timestamp: datetime
    confidence: float
    sync_status: str = "pending"
    zone: str = "green"
    requires_review: bool = False


class EncryptedDB:
    def __init__(self, db_path: str, key: str):
        self.db_path = db_path
        self.key = key
        self._conn: Optional[sqlcipher3.Connection] = None
        self._init_database()

    def _get_connection(self):
        if self._conn is None:
            self._conn = sqlcipher3.connect(self.db_path)
            hex_key = self.key.encode("utf-8").hex()
            self._conn.execute(f"PRAGMA key = x'{hex_key}'")
            self._conn.execute("PRAGMA cipher_page_size = 4096")
            self._conn.execute("PRAGMA foreign_keys = ON")
        return self._conn

    def _init_database(self) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id TEXT PRIMARY KEY,
                name_ar TEXT NOT NULL,
                name_en TEXT NOT NULL,
                status TEXT DEFAULT 'active'
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS biometric_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id TEXT NOT NULL,
                vector_blob BLOB NOT NULL,
                pose TEXT NOT NULL,
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance_logs (
                id TEXT PRIMARY KEY,
                employee_id TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                confidence REAL NOT NULL,
                zone TEXT DEFAULT 'green',
                requires_review INTEGER DEFAULT 0,
                sync_status TEXT DEFAULT 'pending',
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS device_config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_attendance_sync_status 
            ON attendance_logs(sync_status)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_biometric_employee 
            ON biometric_templates(employee_id)
        """)

        conn.commit()
        logger.info("Database initialized successfully")

    def add_employee(self, name_ar: str, name_en: str) -> Employee:
        emp_id = str(uuid.uuid4())
        conn = self._get_connection()
        conn.execute(
            "INSERT INTO employees (id, name_ar, name_en) VALUES (?, ?, ?)",
            (emp_id, name_ar, name_en),
        )
        conn.commit()
        return Employee(id=emp_id, name_ar=name_ar, name_en=name_en)

    def get_employee(self, employee_id: str) -> Optional[Employee]:
        conn = self._get_connection()
        cursor = conn.execute(
            "SELECT id, name_ar, name_en, status FROM employees WHERE id = ?",
            (employee_id,),
        )
        row = cursor.fetchone()
        if row:
            return Employee(id=row[0], name_ar=row[1], name_en=row[2], status=row[3])
        return None

    def add_biometric_template(
        self, employee_id: str, vector_blob: bytes, pose: str
    ) -> BiometricTemplate:
        conn = self._get_connection()
        cursor = conn.execute(
            "INSERT INTO biometric_templates (employee_id, vector_blob, pose) VALUES (?, ?, ?)",
            (employee_id, vector_blob, pose),
        )
        conn.commit()
        return BiometricTemplate(
            id=cursor.lastrowid,
            employee_id=employee_id,
            vector_blob=vector_blob,
            pose=pose,
        )

    def get_biometric_templates(self, employee_id: str) -> List[BiometricTemplate]:
        conn = self._get_connection()
        cursor = conn.execute(
            "SELECT id, employee_id, vector_blob, pose FROM biometric_templates WHERE employee_id = ?",
            (employee_id,),
        )
        return [
            BiometricTemplate(
                id=row[0], employee_id=row[1], vector_blob=row[2], pose=row[3]
            )
            for row in cursor.fetchall()
        ]

    def get_all_biometric_templates(self) -> List[BiometricTemplate]:
        conn = self._get_connection()
        cursor = conn.execute(
            "SELECT id, employee_id, vector_blob, pose FROM biometric_templates"
        )
        return [
            BiometricTemplate(
                id=row[0], employee_id=row[1], vector_blob=row[2], pose=row[3]
            )
            for row in cursor.fetchall()
        ]

    def add_attendance_log(
        self,
        employee_id: str,
        confidence: float,
        zone: str = "green",
        requires_review: bool = False,
    ) -> AttendanceLog:
        log_id = str(uuid.uuid4())
        conn = self._get_connection()
        conn.execute(
            "INSERT INTO attendance_logs (id, employee_id, confidence, zone, requires_review, sync_status) VALUES (?, ?, ?, ?, ?, 'pending')",
            (log_id, employee_id, confidence, zone, 1 if requires_review else 0),
        )
        conn.commit()
        return AttendanceLog(
            id=log_id,
            employee_id=employee_id,
            timestamp=datetime.utcnow(),
            confidence=confidence,
            zone=zone,
            requires_review=requires_review,
            sync_status="pending",
        )

    def get_pending_logs(self, limit: int = 500) -> List[AttendanceLog]:
        conn = self._get_connection()
        cursor = conn.execute(
            """SELECT id, employee_id, timestamp, confidence, zone, requires_review, sync_status 
               FROM attendance_logs 
               WHERE sync_status = 'pending' 
               ORDER BY timestamp 
               LIMIT ?""",
            (limit,),
        )
        return [
            AttendanceLog(
                id=row[0],
                employee_id=row[1],
                timestamp=datetime.fromisoformat(row[2])
                if isinstance(row[2], str)
                else row[2],
                confidence=row[3],
                zone=row[4] if row[4] else "green",
                requires_review=bool(row[5]) if row[5] else False,
                sync_status=row[6],
            )
            for row in cursor.fetchall()
        ]

    def mark_logs_synced(self, log_ids: List[str]) -> None:
        conn = self._get_connection()
        placeholders = ",".join("?" * len(log_ids))
        conn.execute(
            f"UPDATE attendance_logs SET sync_status = 'synced' WHERE id IN ({placeholders})",
            log_ids,
        )
        conn.commit()

    def mark_log_failed(self, log_id: str) -> None:
        conn = self._get_connection()
        conn.execute(
            "UPDATE attendance_logs SET sync_status = 'failed' WHERE id = ?", (log_id,)
        )
        conn.commit()

    def get_config(self, key: str) -> Optional[str]:
        conn = self._get_connection()
        cursor = conn.execute("SELECT value FROM device_config WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row[0] if row else None

    def set_config(self, key: str, value: str) -> None:
        conn = self._get_connection()
        conn.execute(
            "INSERT OR REPLACE INTO device_config (key, value) VALUES (?, ?)",
            (key, value),
        )
        conn.commit()

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None


def create_db(db_path: str, key: str) -> EncryptedDB:
    os.makedirs(
        os.path.dirname(db_path) if os.path.dirname(db_path) else ".", exist_ok=True
    )
    return EncryptedDB(db_path, key)
