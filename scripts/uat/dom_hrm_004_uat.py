"""DOM-HRM-004 UAT — Zeiterfassung + Abwesenheit Lifecycle.
Ausführung: python scripts/uat/dom_hrm_004_uat.py [--execute]
"""
import argparse

BASE = "http://localhost:8000/api/v1"
HEADERS = {"X-Tenant-ID": "uat-tenant", "Authorization": "Bearer dev-token"}


def run_uat(execute: bool) -> None:
    print("[UAT] DOM-HRM-004 — Zeiterfassung + Abwesenheit")
    if not execute:
        print("[DRY-RUN] Zeitbuchung OFFEN→GEBUCHT + Abwesenheit BEANTRAGT→GENEHMIGT")
        return

    import requests

    # Zeitbuchung
    r = requests.post(f"{BASE}/hrm/lifecycle/zeitbuchungen", json={
        "mitarbeiter_id": "ma-uat-001",
        "datum": "2026-06-23",
        "von_zeit": "08:00",
        "bis_zeit": "17:00",
        "taetigkeit": "Lagerarbeit",
        "kostenstelle_id": "kst-lager",
        "operator": "uat_runner",
    }, headers=HEADERS)
    assert r.status_code == 200, r.text
    buchung_id = r.json()["id"]
    stunden = r.json()["stunden"]
    assert stunden == 9.0, f"Erwarte 9h, bekam {stunden}"
    print(f"  ✓ Zeitbuchung angelegt {stunden}h id={buchung_id}")

    r = requests.post(f"{BASE}/hrm/lifecycle/zeitbuchungen/{buchung_id}/transition",
                      json={"new_status": "GEBUCHT", "operator": "uat_runner"},
                      headers=HEADERS)
    assert r.status_code == 200 and r.json()["status"] == "GEBUCHT"
    print("  ✓ GEBUCHT")

    # Arbeitszeitkonto
    r = requests.get(f"{BASE}/hrm/lifecycle/arbeitszeitkonto/ma-uat-001",
                     params={"monat": "2026-06"}, headers=HEADERS)
    assert r.status_code == 200
    konto = r.json()
    print(f"  ✓ Konto: ist={konto['ist_stunden']}h soll={konto['soll_stunden']}h diff={konto['differenz']}h ampel={konto['ampel']}")

    # Abwesenheit
    r = requests.post(f"{BASE}/hrm/lifecycle/abwesenheiten", json={
        "mitarbeiter_id": "ma-uat-001",
        "abwesenheit_typ": "URLAUB",
        "von_datum": "2026-07-07",
        "bis_datum": "2026-07-18",
        "arbeitstage": 10,
        "kommentar": "Sommerurlaub 2026",
        "operator": "uat_runner",
    }, headers=HEADERS)
    assert r.status_code == 200
    abw_id = r.json()["id"]
    print(f"  ✓ Urlaubsantrag angelegt id={abw_id}")

    r = requests.post(f"{BASE}/hrm/lifecycle/abwesenheiten/{abw_id}/transition",
                      json={"new_status": "GENEHMIGT", "operator": "hr_manager"},
                      headers=HEADERS)
    assert r.status_code == 200 and r.json()["status"] == "GENEHMIGT"
    print("  ✓ Urlaub GENEHMIGT")
    print("[UAT] DOM-HRM-004 erfolgreich.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    run_uat(args.execute)
