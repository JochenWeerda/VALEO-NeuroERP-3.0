"""FEED-CORE-020 / FEED-T051, FEED-T054: Bewertungssysteme, Bedarfsprofile, Solverlaeufe.

TDD-Red-Welle 1 (Domain/Service): Diese Tests wurden vor der Implementierung
geschrieben und schlugen zunaechst fehl (ImportError bzw. fehlende Tabellen).
"""
from __future__ import annotations

from uuid import uuid4

from app.core.database import SessionLocal

TENANT = "00000000-0000-0000-0000-000000000001"


def _service(db):
    from app.services.feeding_requirements_service import FeedingRequirementsService
    return FeedingRequirementsService(db, TENANT, "req-test")


def test_seeded_evaluation_systems_are_versioned_and_idempotent() -> None:
    """FEED-T051a: gfe2023 und dlg2025 sind als versionierte Referenzdaten geseedet;
    erneutes Seeding erzeugt keine Duplikate (append-only Registry)."""
    db = SessionLocal()
    try:
        service = _service(db)
        first = service.seed_systems()
        second = service.seed_systems()
        systems = service.list_systems()
        slugs = {s["id"]: s for s in systems}
        assert "gfe2023" in slugs and "dlg2025" in slugs
        for system in systems:
            assert system["versions"], system
            current = [v for v in system["versions"] if v["is_current"]]
            assert len(current) == 1
            assert current[0]["module_ref"].startswith("app.agrar.rations.")
        assert second["created_versions"] == 0, "Seeding muss idempotent sein"
        assert first["created_versions"] >= 0
    finally:
        db.close()


def test_requirement_profile_is_reproducible_versioned_and_marks_estimates() -> None:
    """FEED-T051b: Ein Bedarfsprofil persistiert Eingangsgroessen, Systemversion und
    Ergebnis reproduzierbar; fehlende Eingaben werden als Schaetzwerte gekennzeichnet,
    nie still ergaenzt. Profile sind append-only (kein Update-Pfad)."""
    db = SessionLocal()
    try:
        service = _service(db)
        service.seed_systems()
        group_id = _make_group(db, f"ReqProfil {uuid4().hex[:6]}")

        # milk_fat_pct fehlt bewusst -> muss als estimated gekennzeichnet werden
        inputs = {"body_weight_kg": 650, "milk_kg_day": 32, "milk_protein_pct": 3.4,
                  "lactation_stage_days": 120, "parity": 2}
        profile_a = service.create_requirement_profile(group_id, inputs)
        profile_b = service.create_requirement_profile(group_id, inputs)

        assert profile_a["system_version_id"] == profile_b["system_version_id"]
        assert profile_a["requirements"] == profile_b["requirements"], "nicht reproduzierbar"
        assert profile_a["requirements"]["me_mj"] > 0
        assert "milk_fat_pct" in profile_a["estimated_inputs"]
        assert "body_weight_kg" not in profile_a["estimated_inputs"]
        assert profile_a["id"] != profile_b["id"], "append-only: jeder Lauf ein neues Profil"

        listed = service.list_requirement_profiles(group_id)
        assert len(listed) >= 2
        assert listed[0]["created_at"] >= listed[-1]["created_at"]
    finally:
        db.close()


def test_optimization_run_documents_solver_metadata_reproducibly() -> None:
    """FEED-T054a: Ein Solverlauf wird mit Version, Ziel, Parametern und Status
    dokumentiert und ist ueber die Rationsversion abrufbar; Parameter kommen
    unveraendert zurueck (Reproduzierbarkeit, FEED-OPT-005)."""
    db = SessionLocal()
    try:
        service = _service(db)
        group_id = _make_group(db, f"RunGruppe {uuid4().hex[:6]}")
        ration_id, version_id = _make_ration_version(db, group_id)

        params = {"objective": "min_cost", "fan_mode": "005", "seed": 42,
                  "bounds": {"mais": [0, 12]}}
        run = service.record_optimization_run(version_id, {
            "solver_version": "lp_stage2-2026.07", "objective": "min_cost",
            "status": "optimal", "duration_ms": 812, "parameters": params,
        })
        assert run["ration_version_id"] == version_id
        assert run["parameters"] == params
        assert run["status"] == "optimal"

        runs = service.list_optimization_runs(ration_id=ration_id)
        assert any(r["id"] == run["id"] for r in runs)

        # Unbekannte Version wird abgelehnt (kein stiller Waisen-Run)
        try:
            service.record_optimization_run(str(uuid4()), {
                "solver_version": "x", "objective": "min_cost", "status": "optimal",
                "parameters": {}})
            raise AssertionError("Run ohne existierende Version darf nicht persistieren")
        except LookupError:
            pass
    finally:
        db.close()


# ── Helpers: Anlage ueber die echte Lifecycle-API (Endpoint fuellt die
#    vollstaendige Gruppen-Payload; kein Mock in Produktivpfaden) ────────────

def _lifecycle_client():
    from fastapi.testclient import TestClient
    from app.main import app
    return TestClient(app, raise_server_exceptions=False)


_HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-Id": TENANT}
_LIFECYCLE = "/api/v1/agrar/rations-optimization/lifecycle"


def _make_group(db, name: str) -> str:
    response = _lifecycle_client().post(f"{_LIFECYCLE}/groups", headers=_HEADERS, json={
        "name": name, "animal_count": 10, "feeding_system": "TMR",
        "profile_code": "fresh_cow", "pregnancy_status": "unknown"})
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _make_ration_version(db, group_id: str) -> tuple[str, str]:
    response = _lifecycle_client().post(f"{_LIFECYCLE}/rations", headers=_HEADERS, json={
        "group_id": group_id, "name": "Testration", "snapshot": {"components": []}})
    assert response.status_code == 201, response.text
    payload = response.json()
    return payload["id"], payload["latest_version_id"]
