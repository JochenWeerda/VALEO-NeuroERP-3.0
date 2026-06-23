"""DOM-FEED-PROD-004 UAT — Rezeptur Freigabe + Produktionsauftrag QS-Lifecycle.
Ausführung: python scripts/uat/dom_feed_prod_004_uat.py [--execute]
"""
import argparse
import uuid

BASE = "http://localhost:8000/api/v1"
HEADERS = {"X-Tenant-ID": "uat-tenant", "Authorization": "Bearer dev-token"}


def run_uat(execute: bool) -> None:
    print("[UAT] DOM-FEED-PROD-004 — Mischfutter-Produktionskette")
    if not execute:
        print("[DRY-RUN] Würde ausführen: Rezeptur anlegen→freigeben, Auftrag GEPLANT→QS_FREIGEGEBEN")
        return

    import requests
    rezeptur_nr = f"REZ-UAT-{uuid.uuid4().hex[:6].upper()}"

    # Rezeptur mit 3 Positionen (100%)
    r = requests.post(f"{BASE}/futtermittel/produktion/rezepturen", json={
        "rezeptur_nr": rezeptur_nr,
        "artikel_id": "art-mischfutter-001",
        "bezeichnung": "UAT-Standardmischung",
        "positionen": [
            {"rohware_id": "gerste", "anteil_pct": 40.0},
            {"rohware_id": "weizen", "anteil_pct": 35.0},
            {"rohware_id": "soja", "anteil_pct": 25.0},
        ],
        "operator": "uat_runner",
    }, headers=HEADERS)
    assert r.status_code == 200, r.text
    rezeptur_id = r.json()["id"]
    print(f"  ✓ Rezeptur {rezeptur_nr} angelegt (id={rezeptur_id})")

    r = requests.post(f"{BASE}/futtermittel/produktion/rezepturen/{rezeptur_id}/transition",
                      json={"new_status": "FREIGEGEBEN", "operator": "uat_runner"},
                      headers=HEADERS)
    assert r.status_code == 200 and r.json()["status"] == "FREIGEGEBEN"
    print("  ✓ Rezeptur FREIGEGEBEN")

    charge_nr = f"CH-UAT-{uuid.uuid4().hex[:8].upper()}"
    r = requests.post(f"{BASE}/futtermittel/produktion/auftraege", json={
        "rezeptur_id": rezeptur_id,
        "soll_menge_kg": 5000.0,
        "geplant_datum": "2026-07-01",
        "charge_nr": charge_nr,
        "operator": "uat_runner",
    }, headers=HEADERS)
    assert r.status_code == 200
    auftrag_id = r.json()["id"]
    print(f"  ✓ Produktionsauftrag {charge_nr} angelegt")

    for step, extra in [
        ("IN_PRODUKTION", {}),
        ("FERTIG", {"ist_menge_kg": 4950.0}),
        ("QS_FREIGEGEBEN", {"qs_befund": "Analyse OK, Feuchte 14%"}),
        ("AUSGELAGERT", {}),
    ]:
        r = requests.post(f"{BASE}/futtermittel/produktion/auftraege/{auftrag_id}/transition",
                          json={"new_status": step, "operator": "uat_runner", **extra},
                          headers=HEADERS)
        assert r.status_code == 200, f"{step}: {r.text}"
        print(f"  ✓ Auftrag → {step}")

    print("[UAT] DOM-FEED-PROD-004 erfolgreich.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    run_uat(args.execute)
