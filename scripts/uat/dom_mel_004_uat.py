"""DOM-MEL-004 UAT — Meldewesen Lifecycle (Intrastat/ELSTER simuliert).
Ausführung: python scripts/uat/dom_mel_004_uat.py [--execute]
"""
import argparse

BASE = "http://localhost:8000/api/v1"
HEADERS = {"X-Tenant-ID": "uat-tenant", "Authorization": "Bearer dev-token"}


def run_uat(execute: bool) -> None:
    print("[UAT] DOM-MEL-004 — Meldewesen Lifecycle")
    if not execute:
        print("[DRY-RUN] ENTWURF→IN_PRUEFUNG→FREIGEGEBEN→UEBERMITTELT + ABLEHNUNG-Schleife")
        return

    import requests

    # Hauptflow
    r = requests.post(f"{BASE}/meldewesen/lifecycle", json={
        "meldung_typ": "ELSTER_UMSATZSTEUER",
        "periode": "2026-06",
        "betrag_eur": 48250.00,
        "waehrung": "EUR",
        "referenz_ids": ["rech-001", "rech-002"],
        "operator": "uat_runner",
    }, headers=HEADERS)
    assert r.status_code == 200, r.text
    mel_id = r.json()["id"]
    print(f"  ✓ Meldung angelegt id={mel_id}")

    for step in ["IN_PRUEFUNG", "FREIGEGEBEN"]:
        r = requests.post(f"{BASE}/meldewesen/lifecycle/{mel_id}/transition",
                          json={"new_status": step, "operator": "uat_runner"},
                          headers=HEADERS)
        assert r.status_code == 200
        print(f"  ✓ → {step}")

    # Simulation
    r_sim = requests.post(f"{BASE}/meldewesen/lifecycle/simulate-uebermittlung",
                          params={"meldung_typ": "ELSTER_UMSATZSTEUER",
                                  "periode": "2026-06", "betrag_eur": 48250.00},
                          headers=HEADERS)
    assert r_sim.status_code == 200
    ext_ref = r_sim.json()["externe_referenz"]
    print(f"  ✓ Simulierte Referenz: {ext_ref}")

    r = requests.post(f"{BASE}/meldewesen/lifecycle/{mel_id}/transition", json={
        "new_status": "UEBERMITTELT",
        "externe_referenz": ext_ref,
        "operator": "uat_runner",
    }, headers=HEADERS)
    assert r.status_code == 200
    assert "_hinweis" in r.json()
    print(f"  ✓ UEBERMITTELT (Hinweis: {r.json()['_hinweis']})")

    # Ablehnungs-Schleife testen
    r2 = requests.post(f"{BASE}/meldewesen/lifecycle", json={
        "meldung_typ": "INTRASTAT_EINGANG",
        "periode": "2026-05",
        "betrag_eur": 99000.0,
        "referenz_ids": [],
        "operator": "uat_runner",
    }, headers=HEADERS)
    assert r2.status_code == 200
    mel2_id = r2.json()["id"]
    for step in ["IN_PRUEFUNG", "FREIGEGEBEN", "UEBERMITTELT"]:
        r2 = requests.post(f"{BASE}/meldewesen/lifecycle/{mel2_id}/transition",
                           json={"new_status": step, "operator": "uat_runner"},
                           headers=HEADERS)
        assert r2.status_code == 200
    r2 = requests.post(f"{BASE}/meldewesen/lifecycle/{mel2_id}/transition", json={
        "new_status": "ABGELEHNT", "fehler_grund": "Falsches Format", "operator": "uat_runner"
    }, headers=HEADERS)
    assert r2.status_code == 200 and r2.json()["status"] == "ABGELEHNT"
    r2 = requests.post(f"{BASE}/meldewesen/lifecycle/{mel2_id}/transition",
                       json={"new_status": "IN_PRUEFUNG", "operator": "uat_runner"},
                       headers=HEADERS)
    assert r2.status_code == 200 and r2.json()["status"] == "IN_PRUEFUNG"
    print("  ✓ Ablehnungs-Korrektionsschleife erfolgreich")

    print("[UAT] DOM-MEL-004 erfolgreich. (BESTAETIGT = externes Gate: Behördenbestätigung)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    run_uat(args.execute)
