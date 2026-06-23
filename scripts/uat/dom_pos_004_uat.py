"""DOM-POS-004 UAT — POS Tagesabschluss inkl. simulierter TSE.
Ausführung: python scripts/uat/dom_pos_004_uat.py [--execute]
"""
import argparse
import uuid

BASE = "http://localhost:8000/api/v1"
HEADERS = {"X-Tenant-ID": "uat-tenant", "Authorization": "Bearer dev-token"}


def run_uat(execute: bool) -> None:
    print("[UAT] DOM-POS-004 — Kassen-Tagesabschluss Lifecycle")
    if not execute:
        print("[DRY-RUN] OFFEN→IN_ABSCHLUSS→Z_BON→TSE_SIGNIERT→DSFINVK→ABGESCHLOSSEN")
        return

    import requests
    kasse_id = "KASSE-UAT-001"
    datum = "2026-06-23"

    r = requests.post(f"{BASE}/pos/tagesabschluss", json={
        "kasse_id": kasse_id, "datum": datum, "operator": "uat_runner"
    }, headers=HEADERS)
    assert r.status_code == 200, r.text
    ta_id = r.json()["id"]
    print(f"  ✓ Tagesabschluss angelegt id={ta_id}")

    r = requests.post(f"{BASE}/pos/tagesabschluss/{ta_id}/transition",
                      json={"new_status": "IN_ABSCHLUSS", "operator": "uat_runner"},
                      headers=HEADERS)
    assert r.status_code == 200
    print("  ✓ IN_ABSCHLUSS")

    r = requests.post(f"{BASE}/pos/tagesabschluss/{ta_id}/transition", json={
        "new_status": "Z_BON_ERSTELLT",
        "z_bon_nr": "Z-2026-0623-001",
        "umsatz_brutto_eur": 12450.80,
        "operator": "uat_runner",
    }, headers=HEADERS)
    assert r.status_code == 200
    print("  ✓ Z_BON_ERSTELLT")

    # TSE simulieren
    r_tse = requests.post(
        f"{BASE}/pos/tagesabschluss/tse/simulate",
        params={"kasse_id": kasse_id, "z_bon_nr": "Z-2026-0623-001", "umsatz_brutto_eur": 12450.80},
        headers=HEADERS
    )
    assert r_tse.status_code == 200
    tse_sig = r_tse.json()["tse_signatur"]
    print(f"  ✓ TSE simuliert: {tse_sig}")

    r = requests.post(f"{BASE}/pos/tagesabschluss/{ta_id}/transition", json={
        "new_status": "TSE_SIGNIERT",
        "tse_signatur": tse_sig,
        "operator": "uat_runner",
    }, headers=HEADERS)
    assert r.status_code == 200
    print("  ✓ TSE_SIGNIERT")

    r = requests.post(f"{BASE}/pos/tagesabschluss/{ta_id}/transition", json={
        "new_status": "DSFINVK_EXPORTIERT",
        "dsfinvk_export_pfad": "/exports/dsfinvk/2026-06-23.zip",
        "operator": "uat_runner",
    }, headers=HEADERS)
    assert r.status_code == 200
    print("  ✓ DSFINVK_EXPORTIERT (simuliert)")

    r = requests.post(f"{BASE}/pos/tagesabschluss/{ta_id}/transition",
                      json={"new_status": "ABGESCHLOSSEN", "operator": "uat_runner"},
                      headers=HEADERS)
    assert r.status_code == 200
    print("  ✓ ABGESCHLOSSEN")
    print("[UAT] DOM-POS-004 erfolgreich.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    run_uat(args.execute)
