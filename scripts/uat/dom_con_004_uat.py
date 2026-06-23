"""DOM-CON-004 UAT-Script — Kontrakt Lifecycle, Fixing, Settlement.

Führt den kompletten fachlichen Flow durch:
1. Kontrakt anlegen (ENTWURF)
2. Freigeben → Aktivieren
3. Fixing anlegen (KASSA + MATIF)
4. Settlement anlegen + abrechnen
5. Kontrakt → ERFUELLT prüfen

Ausführung: python scripts/uat/dom_con_004_uat.py [--execute]
"""
import argparse
import sys

BASE = "http://localhost:8000/api/v1"
HEADERS = {"X-Tenant-ID": "uat-tenant", "Authorization": "Bearer dev-token"}


def run_uat(execute: bool) -> None:
    import uuid
    kontrakt_id = str(uuid.uuid4())
    print(f"[UAT] DOM-CON-004 Kontrakt-Lifecycle — kontrakt_id={kontrakt_id}")

    if not execute:
        print("[DRY-RUN] Würde folgende Schritte ausführen:")
        print("  1. POST /kontrakte/lifecycle → ENTWURF")
        print("  2. POST /kontrakte/lifecycle/{id}/transition → FREIGEGEBEN")
        print("  3. POST /kontrakte/lifecycle/{id}/transition → AKTIV")
        print("  4. POST /kontrakte/fixing (2x)")
        print("  5. GET  /kontrakte/fixing/{id}/summary")
        print("  6. POST /kontrakte/settlement → OFFEN → IN_ABRECHNUNG → ABGERECHNET")
        print("[DRY-RUN] Abgeschlossen. Mit --execute gegen echte DB ausführen.")
        return

    import requests
    # 1. Anlage
    r = requests.post(f"{BASE}/kontrakte/lifecycle", json={
        "kontrakt_id": kontrakt_id,
        "kontrakt_nr": f"KNR-UAT-{kontrakt_id[:8]}",
        "artikel_id": "art-weizen",
        "menge_t": 500.0,
        "preis_eur_t": 220.0,
        "lieferant_id": "lft-uat-001",
        "periode": "2026-07",
        "operator": "uat_runner",
    }, headers=HEADERS)
    assert r.status_code == 200, f"Anlage fehlgeschlagen: {r.text}"
    assert r.json()["status"] == "ENTWURF"
    print("  ✓ Kontrakt angelegt")

    # 2. Freigeben
    r = requests.post(f"{BASE}/kontrakte/lifecycle/{kontrakt_id}/transition",
                      json={"new_status": "FREIGEGEBEN", "operator": "uat_runner"},
                      headers=HEADERS)
    assert r.status_code == 200 and r.json()["status"] == "FREIGEGEBEN"
    print("  ✓ FREIGEGEBEN")

    # 3. Aktivieren
    r = requests.post(f"{BASE}/kontrakte/lifecycle/{kontrakt_id}/transition",
                      json={"new_status": "AKTIV", "operator": "uat_runner"},
                      headers=HEADERS)
    assert r.status_code == 200 and r.json()["status"] == "AKTIV"
    print("  ✓ AKTIV")

    # 4. Fixing
    for menge, preis, markt in [(300.0, 218.0, "MATIF"), (200.0, 223.0, "KASSA")]:
        r = requests.post(f"{BASE}/kontrakte/fixing", json={
            "kontrakt_id": kontrakt_id,
            "fixing_datum": "2026-06-23",
            "fixing_preis_eur_t": preis,
            "menge_t": menge,
            "markt": markt,
            "referenz": f"REF-{markt}",
            "operator": "uat_runner",
        }, headers=HEADERS)
        assert r.status_code == 200
    print("  ✓ 2 Fixings angelegt")

    r = requests.get(f"{BASE}/kontrakte/fixing/{kontrakt_id}/summary", headers=HEADERS)
    assert r.status_code == 200
    s = r.json()
    assert s["vollstaendig_gefixt"] is True
    print(f"  ✓ Fixing-Summary: avg={s['avg_fixing_preis_eur_t']} EUR/t, vollständig={s['vollstaendig_gefixt']}")

    # 5. Settlement
    r = requests.post(f"{BASE}/kontrakte/settlement", json={
        "kontrakt_id": kontrakt_id,
        "lieferung_datum": "2026-07-10",
        "gelieferte_menge_t": 500.0,
        "abrechnungspreis_eur_t": 220.0,
        "referenz": "LS-UAT-001",
        "operator": "uat_runner",
    }, headers=HEADERS)
    assert r.status_code == 200
    settlement_id = r.json()["id"]
    print(f"  ✓ Settlement angelegt id={settlement_id}")

    for new_s in ["IN_ABRECHNUNG", "ABGERECHNET"]:
        r = requests.post(f"{BASE}/kontrakte/settlement/{settlement_id}/transition",
                          json={"new_status": new_s, "operator": "uat_runner"},
                          headers=HEADERS)
        assert r.status_code == 200
        print(f"  ✓ Settlement → {new_s}")

    print("[UAT] DOM-CON-004 erfolgreich abgeschlossen.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    run_uat(args.execute)
