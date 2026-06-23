"""DOM-DOC-004 UAT — Nachweisraum Dokument + GoBD-Export Lifecycle.
Ausführung: python scripts/uat/dom_doc_004_uat.py [--execute]
"""
import argparse

BASE = "http://localhost:8000/api/v1"
HEADERS = {"X-Tenant-ID": "uat-tenant", "Authorization": "Bearer dev-token"}


def run_uat(execute: bool) -> None:
    print("[UAT] DOM-DOC-004 — Nachweisraum + GoBD")
    if not execute:
        print("[DRY-RUN] EINGEGANGEN→IN_PRUEFUNG→WIEDERVORLAGE→FREIGEGEBEN→ARCHIVIERT + GoBD")
        return

    import requests
    # Dokument anlegen
    r = requests.post(f"{BASE}/nachweisraum/dokumente", json={
        "dokument_typ": "LIEFERSCHEIN",
        "bezeichnung": "LS-2026-001",
        "referenz_id": "ls-001",
        "referenz_typ": "sales_lieferschein",
        "datei_pfad": "/dms/LS-2026-001.pdf",
        "operator": "uat_runner",
    }, headers=HEADERS)
    assert r.status_code == 200, r.text
    dok_id = r.json()["id"]
    print(f"  ✓ Dokument angelegt id={dok_id}")

    for step, extra in [
        ("IN_PRUEFUNG", {}),
        ("WIEDERVORLAGE", {"kommentar": "Unterschrift fehlt", "wiedervorlage_datum": "2026-07-01"}),
        ("IN_PRUEFUNG", {"kommentar": "Nachtrag erhalten"}),
        ("FREIGEGEBEN", {}),
        ("ARCHIVIERT", {}),
    ]:
        r = requests.post(f"{BASE}/nachweisraum/dokumente/{dok_id}/transition",
                          json={"new_status": step, "operator": "uat_runner", **extra},
                          headers=HEADERS)
        assert r.status_code == 200, f"{step}: {r.text}"
        print(f"  ✓ Dokument → {step}")

    # GoBD Export
    r = requests.post(f"{BASE}/nachweisraum/gobd-exporte", json={
        "periode": "2026-06",
        "referenz_ids": ["ls-001", "rech-001"],
        "operator": "uat_runner",
    }, headers=HEADERS)
    assert r.status_code == 200
    export_id = r.json()["id"]
    print(f"  ✓ GoBD-Export angelegt id={export_id}")

    for step, extra in [
        ("IN_ERSTELLUNG", {}),
        ("EXPORTIERT", {"export_pfad": "/gobd/2026-06.zip"}),
        ("PRUEFBAR", {}),
    ]:
        r = requests.post(f"{BASE}/nachweisraum/gobd-exporte/{export_id}/transition",
                          json={"new_status": step, "operator": "uat_runner", **extra},
                          headers=HEADERS)
        assert r.status_code == 200, f"{step}: {r.text}"
        print(f"  ✓ GoBD → {step}")

    print("[UAT] DOM-DOC-004 erfolgreich. (ABGENOMMEN = externes Gate: Prüfer-Unterschrift)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    run_uat(args.execute)
