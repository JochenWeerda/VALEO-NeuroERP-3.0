"""
Policy Store - SQLite-basierte Persistenz
"""

from __future__ import annotations
import json
import os
import sqlite3
from pathlib import Path
from typing import List, Optional
from .models import Rule

DEFAULT_DB = os.environ.get("POLICY_DB", "data/policies.db")


class PolicyStore:
    """SQLite-Store für Policy-Regeln"""

    def __init__(self, db_path: str = DEFAULT_DB) -> None:
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _conn(self) -> sqlite3.Connection:
        """Erstellt Connection mit Row-Factory"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Initialisiert Datenbank-Schema"""
        with self._conn() as c:
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS policies (
                  id TEXT PRIMARY KEY,
                  when_kpiId TEXT NOT NULL,
                  when_severity TEXT NOT NULL, -- JSON array
                  action TEXT NOT NULL,
                  params TEXT,    -- JSON
                  limits TEXT,    -- JSON
                  window TEXT,    -- JSON
                  approval TEXT,  -- JSON
                  autoExecute INTEGER,
                  autoSuggest INTEGER
                )
                """
            )

    def list(self) -> List[Rule]:
        """Listet alle Policies auf"""
        with self._conn() as c:
            rows = c.execute("SELECT * FROM policies ORDER BY id").fetchall()
        out: List[Rule] = []
        for r in rows:
            out.append(
                Rule(
                    id=r["id"],
                    when={
                        "kpiId": r["when_kpiId"],
                        "severity": json.loads(r["when_severity"]),
                    },
                    action=r["action"],
                    params=json.loads(r["params"]) if r["params"] else None,
                    limits=json.loads(r["limits"]) if r["limits"] else None,
                    window=json.loads(r["window"]) if r["window"] else None,
                    approval=json.loads(r["approval"]) if r["approval"] else None,
                    autoExecute=bool(r["autoExecute"]),
                    autoSuggest=bool(r["autoSuggest"]),
                )
            )
        return out

    def get(self, id_: str) -> Optional[Rule]:
        """Holt einzelne Policy"""
        with self._conn() as c:
            r = c.execute("SELECT * FROM policies WHERE id=?", (id_,)).fetchone()
        if not r:
            return None
        return Rule(
            id=r["id"],
            when={
                "kpiId": r["when_kpiId"],
                "severity": json.loads(r["when_severity"]),
            },
            action=r["action"],
            params=json.loads(r["params"]) if r["params"] else None,
            limits=json.loads(r["limits"]) if r["limits"] else None,
            window=json.loads(r["window"]) if r["window"] else None,
            approval=json.loads(r["approval"]) if r["approval"] else None,
            autoExecute=bool(r["autoExecute"]),
            autoSuggest=bool(r["autoSuggest"]),
        )

    def upsert(self, rule: Rule) -> None:
        """Erstellt oder aktualisiert Policy"""
        with self._conn() as c:
            c.execute(
                """
                INSERT INTO policies (id, when_kpiId, when_severity, action, params, limits, window, approval, autoExecute, autoSuggest)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                  when_kpiId=excluded.when_kpiId,
                  when_severity=excluded.when_severity,
                  action=excluded.action,
                  params=excluded.params,
                  limits=excluded.limits,
                  window=excluded.window,
                  approval=excluded.approval,
                  autoExecute=excluded.autoExecute,
                  autoSuggest=excluded.autoSuggest
                """,
                (
                    rule.id,
                    rule.when.kpiId,
                    json.dumps(rule.when.severity),
                    rule.action,
                    json.dumps(rule.params or {}),
                    json.dumps(rule.limits or {}),
                    json.dumps(rule.window.model_dump() if rule.window else {}),
                    json.dumps(rule.approval.model_dump() if rule.approval else {}),
                    1 if rule.autoExecute else 0,
                    1 if rule.autoSuggest else 0,
                ),
            )

    def delete(self, id_: str) -> None:
        """Löscht Policy"""
        with self._conn() as c:
            c.execute("DELETE FROM policies WHERE id=?", (id_,))

    def bulk_upsert(self, rules: List[Rule]) -> None:
        """Bulk-Upsert (transaktional)"""
        for r in rules:
            self.upsert(r)

