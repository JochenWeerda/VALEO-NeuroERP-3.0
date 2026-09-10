"""
Vertragstests fuer die Policy-Endpunkte unter /api/mcp/policy
(Slice L3-JOURNAL-SOURCE-20260910, Besitzerweiterung 2026-09-10).

Zwei belegte Regressionen werden hier festgenagelt:

1. ``/api/mcp/policy/backup`` kopierte eine SQLite-Datei ueber ``DEFAULT_DB``.
   Der Policy-Store liegt laengst in PostgreSQL, ``DEFAULT_DB`` ist ``None`` —
   der Endpunkt scheiterte mit
   ``stat: path should be string, bytes, os.PathLike or integer, not NoneType``.
   Gesichert wird jetzt der JSON-Export.

2. ``policies.py`` deklarierte ``response_model=StatusResponse`` (Feld
   ``success``), die Handler gaben aber ``{"ok": True}`` zurueck. FastAPI
   validiert die Antwort *nach* der Ausfuehrung: ``/policy/restore`` ersetzte
   alle Regeln und meldete danach HTTP 500. ``/policy/list`` verlor durch
   dasselbe Modell still sein ``data``.

Die Tests kommen ohne Datenbank und ohne Netzwerk aus.
"""

import pytest
from pydantic import ValidationError

from app.api.v1.endpoints.policies import (
    PolicyListResponse,
    PolicyUpsertResponse,
)
from app.api.v1.schemas.base import StatusResponse


# ═══════════════════════════════════════════════════════════════════════════
# Antwortmodelle passen zu dem, was die Handler zurueckgeben
# ═══════════════════════════════════════════════════════════════════════════

class TestAntwortvertrag:
    def test_list_behaelt_die_nutzlast(self):
        """StatusResponse haette ``data`` still verworfen."""
        body = PolicyListResponse.model_validate(
            {"success": True, "data": [{"id": "r1", "action": "notify"}]}
        )
        assert body.data == [{"id": "r1", "action": "notify"}]

    def test_upsert_meldet_die_anzahl(self):
        body = PolicyUpsertResponse.model_validate({"success": True, "count": 3})
        assert body.count == 3

    @pytest.mark.parametrize(
        "payload",
        [
            {"success": True, "message": "Policy r1 angelegt"},
            {"success": True, "message": "Policy r1 aktualisiert"},
            {"success": True, "message": "Policy r1 geloescht"},
            {"success": True, "message": "Alle Policies ersetzt"},
        ],
    )
    def test_mutationen_erfuellen_statusresponse(self, payload):
        assert StatusResponse.model_validate(payload).success is True

    def test_altes_ok_schema_erfuellt_statusresponse_nicht(self):
        """Regressionsgrund: genau diese Rueckgabe erzeugte HTTP 500, nachdem
        die Mutation bereits ausgefuehrt war."""
        with pytest.raises(ValidationError):
            StatusResponse.model_validate({"ok": True})


# ═══════════════════════════════════════════════════════════════════════════
# Backup-Dateiname: nur JSON, kein Ausbruch aus dem Backup-Verzeichnis
# ═══════════════════════════════════════════════════════════════════════════

class TestBackupPfad:
    def test_gueltiger_name_wird_aufgeloest(self):
        from app.policy.router import _resolve_backup_file, BACKUP_DIR
        from pathlib import Path

        resolved = _resolve_backup_file("policies-2026-09-10T05-00-00.json")
        assert resolved.parent == Path(BACKUP_DIR).resolve()
        assert resolved.suffix == ".json"

    @pytest.mark.parametrize(
        "name",
        [
            "../etc/passwd",
            "../../secrets.json",
            "policies.db",
            "policies.json.exe",
            "",
        ],
    )
    def test_ungueltige_namen_werden_abgewiesen(self, name):
        from fastapi import HTTPException
        from app.policy.router import _resolve_backup_file

        with pytest.raises(HTTPException) as exc:
            _resolve_backup_file(name)
        assert exc.value.status_code == 400

    def test_absoluter_pfad_wird_abgewiesen(self):
        from fastapi import HTTPException
        from app.policy.router import _resolve_backup_file

        with pytest.raises(HTTPException) as exc:
            _resolve_backup_file("/etc/policies.json")
        assert exc.value.status_code == 400

    def test_kein_sqlite_pfad_mehr_im_backup_pfad(self):
        """``DEFAULT_DB`` ist None; der Backup-Weg darf ihn nicht mehr nutzen."""
        import importlib
        import inspect

        # ``from app.policy import router`` liefert das APIRouter-Objekt,
        # nicht das Modul — deshalb explizit importieren.
        policy_router = importlib.import_module("app.policy.router")
        quelle = inspect.getsource(policy_router.backup_db)
        assert "DEFAULT_DB" not in quelle.split('"""')[-1]
        assert "export_json" in quelle
