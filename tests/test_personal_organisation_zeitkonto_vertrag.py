"""Organigramm und Arbeitszeitkonto — zwei fehlende Tabellen und eine falsche Formel.

Vier Dinge, die vorher fehlten:

1. **`domain_hr.org_units`** existierte in keiner Datenbank: Alle vier Wege des
   Organigramms antworteten 503.
2. **`domain_hr.time_account_adjustments`** ebenso: Jede Saldokorrektur
   antwortete 503.
3. **`domain_hr.schichten`** gibt es nicht — aber `domain_hr.shifts`. Der Weg las
   zusätzlich `planned_hours` und `employee_ref`, die die vorhandene Tabelle
   nicht hat (sie führt `starts_at`/`ends_at` als Uhrzeiten und
   `assigned_employee_refs` als JSONB-Liste). Weil alle drei Abfragen in **einem**
   `try` standen, antwortete `/time-accounts/{ref}` ausnahmslos 503.
4. **Die Saldoformel zählte die Korrektur zweimal** — in `saldo_hours` und in
   `transferred_from_prev_period`, das außerdem die Ist-Stunden aller Vorjahre
   summierte: keine Übertragung, sondern eine Lebenssumme.

Geprüft wird gegen die gemeinsame, vorhandene Prüfstand-Datenbank.
"""

from __future__ import annotations

import json
import os
import uuid

import pytest

pytestmark = pytest.mark.integration

DB_URL = os.environ.get(
    "TEST_DATABASE_URL",
    os.environ.get(
        "DATABASE_URL",
        "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe",
    ),
)
os.environ.setdefault("DATABASE_URL", DB_URL)
os.environ.setdefault("API_DEV_TOKEN", "dev-token")

HAUS_A = f"pers-a-{uuid.uuid4().hex[:6]}"
HAUS_B = f"pers-b-{uuid.uuid4().hex[:6]}"

WEG = "/api/v1/personal"
EINHEITEN = "domain_hr.org_units"
KORREKTUREN = "domain_hr.time_account_adjustments"
ZEITEINTRAEGE = "domain_hr.time_entries"
SCHICHTEN = "domain_hr.shifts"
KOSTENSTELLEN = "domain_finance.kostenstellen"

MITARBEITER = f"EMP-{uuid.uuid4().hex[:6]}"
KOSTENSTELLE_A = str(uuid.uuid4())
KOSTENSTELLE_B = str(uuid.uuid4())


@pytest.fixture(scope="module")
def engine():
    from sqlalchemy import create_engine, text

    try:
        motor = create_engine(DB_URL)
        with motor.connect() as conn:
            vorhanden = conn.execute(
                text(
                    "SELECT 1 FROM information_schema.tables "
                    "WHERE table_schema='domain_hr' AND table_name='org_units'"
                )
            ).scalar()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    if not vorhanden:
        pytest.skip("Migration personal_organisation_zeitkonto_20261006 nicht angewandt")
    return motor


@pytest.fixture(scope="module", autouse=True)
def bestand(engine):
    from sqlalchemy import text

    with engine.begin() as v:
        for haus in (HAUS_A, HAUS_B):
            v.execute(
                text(
                    "INSERT INTO domain_shared.tenants (id, name) VALUES (:id, :name) "
                    "ON CONFLICT (id) DO NOTHING"
                ),
                {"id": haus, "name": f"Pruefpersonal {haus}"},
            )
        for kid, haus in ((KOSTENSTELLE_A, HAUS_A), (KOSTENSTELLE_B, HAUS_B)):
            v.execute(
                text(
                    f"INSERT INTO {KOSTENSTELLEN} (id, tenant_id, nummer, bezeichnung, aktiv) "
                    "VALUES (:id, :tid, :nr, 'Pruefkostenstelle', TRUE)"
                ),
                {"id": kid, "tid": haus, "nr": f"KS-{kid[:8]}"},
            )
    yield
    _aufraeumen(engine)


def _aufraeumen(engine) -> None:
    from sqlalchemy import text

    haeuser = [HAUS_A, HAUS_B]
    with engine.begin() as v:
        # Von den Blaettern nach oben, weil der Elternverweis RESTRICT traegt.
        for _ in range(6):
            v.execute(
                text(
                    f"DELETE FROM {EINHEITEN} WHERE tenant_id = ANY(:h) AND id NOT IN "
                    f"(SELECT parent_id FROM {EINHEITEN} WHERE parent_id IS NOT NULL)"
                ),
                {"h": haeuser},
            )
        for tabelle in (KORREKTUREN, ZEITEINTRAEGE, SCHICHTEN, KOSTENSTELLEN):
            v.execute(
                text(f"DELETE FROM {tabelle} WHERE tenant_id = ANY(:h)"), {"h": haeuser}
            )
        v.execute(text("DELETE FROM domain_shared.tenants WHERE id = ANY(:h)"), {"h": haeuser})


@pytest.fixture(autouse=True)
def leer(engine):
    """Jeder Test beginnt ohne Einheiten, Zeiten, Schichten und Korrekturen."""
    from sqlalchemy import text

    with engine.begin() as v:
        for _ in range(6):
            v.execute(
                text(
                    f"DELETE FROM {EINHEITEN} WHERE tenant_id = ANY(:h) AND id NOT IN "
                    f"(SELECT parent_id FROM {EINHEITEN} WHERE parent_id IS NOT NULL)"
                ),
                {"h": [HAUS_A, HAUS_B]},
            )
        for tabelle in (KORREKTUREN, ZEITEINTRAEGE, SCHICHTEN):
            v.execute(
                text(f"DELETE FROM {tabelle} WHERE tenant_id = ANY(:h)"),
                {"h": [HAUS_A, HAUS_B]},
            )
    yield


@pytest.fixture(scope="module")
def client(engine):
    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app, raise_server_exceptions=False)


def kopf(haus: str) -> dict[str, str]:
    return {"X-Tenant-ID": haus, "Authorization": "Bearer dev-token"}


def einheit(client, haus: str, code: str, **felder):
    nutzlast = {"unit_code": code, "name": felder.pop("name", f"Einheit {code}")}
    nutzlast.update(felder)
    return client.post(f"{WEG}/org-units", json=nutzlast, headers=kopf(haus))


def zeit_eintragen(engine, haus: str, datum: str, stunden: float) -> None:
    from sqlalchemy import text

    with engine.begin() as v:
        v.execute(
            text(
                f"INSERT INTO {ZEITEINTRAEGE} (id, tenant_id, employee_ref, entry_date, hours) "
                "VALUES (:id, :tid, :ref, :datum, :std)"
            ),
            {
                "id": str(uuid.uuid4()),
                "tid": haus,
                "ref": MITARBEITER,
                "datum": datum,
                "std": stunden,
            },
        )


def schicht_planen(
    engine, haus: str, datum: str, von: str, bis: str, refs=None, status: str = "planned"
) -> None:
    from sqlalchemy import text

    with engine.begin() as v:
        v.execute(
            text(
                f"INSERT INTO {SCHICHTEN} (id, tenant_id, shift_date, name, starts_at, "
                " ends_at, assigned_employee_refs, status) "
                "VALUES (:id, :tid, :datum, 'Pruefschicht', :von, :bis, "
                "        CAST(:refs AS jsonb), :status)"
            ),
            {
                "id": str(uuid.uuid4()),
                "tid": haus,
                "datum": datum,
                "von": von,
                "bis": bis,
                "refs": json.dumps(refs if refs is not None else [MITARBEITER]),
                "status": status,
            },
        )


def korrigieren(client, haus: str, **felder):
    nutzlast = {
        "delta_hours": felder.pop("delta_hours", 1.5),
        "reason": felder.pop("reason", "Urlaubsabgeltung"),
    }
    nutzlast.update(felder)
    return client.post(
        f"{WEG}/time-accounts/{MITARBEITER}/adjust", json=nutzlast, headers=kopf(haus)
    )


# ── 1. Das Schema ───────────────────────────────────────────────────────────


class TestSchema:
    def test_beide_tabellen_sind_angelegt(self, engine):
        from sqlalchemy import text

        with engine.connect() as c:
            for tabelle in ("org_units", "time_account_adjustments"):
                assert c.execute(
                    text(
                        "SELECT 1 FROM information_schema.tables "
                        "WHERE table_schema='domain_hr' AND table_name=:t"
                    ),
                    {"t": tabelle},
                ).scalar() == 1, tabelle

    def test_schichten_existiert_nicht_und_wird_nicht_angelegt(self, engine):
        """Die Dublette wird abgeloest, nicht nachgebaut."""
        from sqlalchemy import text

        with engine.connect() as c:
            assert c.execute(
                text(
                    "SELECT 1 FROM information_schema.tables "
                    "WHERE table_schema='domain_hr' AND table_name='schichten'"
                )
            ).scalar() is None

    def test_code_verweist_nicht_mehr_auf_schichten(self):
        from pathlib import Path

        for pfad in (
            "app/api/v1/endpoints/personal.py",
            "app/services/personal_organisation_service.py",
        ):
            quelle = Path(pfad).read_text(encoding="utf-8")
            # Nur der SQL-Zugriff darf fehlen; Kommentar und Docstring duerfen den
            # alten Namen nennen, damit der Befund nachlesbar bleibt.
            sql_stellen = [
                z for z in quelle.splitlines()
                if "domain_hr.schichten" in z and "FROM" in z.upper()
                and not z.lstrip().startswith("#") and "``" not in z
            ]
            assert not sql_stellen, pfad

    @pytest.mark.parametrize(
        "bedingung",
        [
            "ck_orgeinheit_art",
            "ck_orgeinheit_nicht_sich",
            "ck_orgeinheit_name_gefuellt",
            "fk_orgeinheit_eltern",
            "fk_orgeinheit_kostenstelle",
            "ck_zeitkorrektur_wirksam",
            "ck_zeitkorrektur_begruendet",
        ],
    )
    def test_bedingung_vorhanden(self, engine, bedingung):
        from sqlalchemy import text

        with engine.connect() as c:
            assert c.execute(
                text("SELECT 1 FROM pg_constraint WHERE conname = :n"), {"n": bedingung}
            ).scalar() == 1

    def test_einheit_mit_untereinheit_ist_nicht_loeschbar(self, engine, client):
        from sqlalchemy import text
        from sqlalchemy.exc import IntegrityError

        oben = einheit(client, HAUS_A, "OBEN").json()
        einheit(client, HAUS_A, "UNTEN", parent_id=oben["id"])
        with pytest.raises(IntegrityError):
            with engine.begin() as v:
                v.execute(text(f"DELETE FROM {EINHEITEN} WHERE id = :id"), {"id": oben["id"]})

    def test_korrektur_um_null_wird_von_der_datenbank_abgewiesen(self, engine):
        from sqlalchemy import text
        from sqlalchemy.exc import IntegrityError

        with pytest.raises(IntegrityError):
            with engine.begin() as v:
                v.execute(
                    text(
                        f"INSERT INTO {KORREKTUREN} (id, tenant_id, employee_ref, "
                        " delta_hours, reason, adjustment_date) "
                        "VALUES (:id, :tid, :ref, 0, 'Grund', CURRENT_DATE)"
                    ),
                    {"id": str(uuid.uuid4()), "tid": HAUS_A, "ref": MITARBEITER},
                )

    def test_korrektur_ohne_grund_wird_von_der_datenbank_abgewiesen(self, engine):
        from sqlalchemy import text
        from sqlalchemy.exc import IntegrityError

        with pytest.raises(IntegrityError):
            with engine.begin() as v:
                v.execute(
                    text(
                        f"INSERT INTO {KORREKTUREN} (id, tenant_id, employee_ref, "
                        " delta_hours, reason, adjustment_date) "
                        "VALUES (:id, :tid, :ref, 2, '   ', CURRENT_DATE)"
                    ),
                    {"id": str(uuid.uuid4()), "tid": HAUS_A, "ref": MITARBEITER},
                )


# ── 2. Das Organigramm ──────────────────────────────────────────────────────


class TestOrganigramm:
    def test_baum_statt_503(self, client):
        """Vorher: "org_units table not available"."""
        oben = einheit(client, HAUS_A, "GL", name="Geschaeftsleitung").json()
        einheit(client, HAUS_A, "VK", name="Verkauf", parent_id=oben["id"])
        antwort = client.get(f"{WEG}/org-chart", headers=kopf(HAUS_A))
        assert antwort.status_code == 200, antwort.text
        baum = antwort.json()["org_chart"]
        assert len(baum) == 1
        assert baum[0]["unit_code"] == "GL"
        assert [k["unit_code"] for k in baum[0]["children"]] == ["VK"]

    def test_teilbaum(self, client):
        oben = einheit(client, HAUS_A, "GL2").json()
        mitte = einheit(client, HAUS_A, "VK2", parent_id=oben["id"]).json()
        einheit(client, HAUS_A, "ID2", parent_id=mitte["id"])
        antwort = client.get(f"{WEG}/org-chart/{mitte['id']}", headers=kopf(HAUS_A))
        assert antwort.status_code == 200, antwort.text
        teil = antwort.json()["org_chart"]
        assert teil["unit_code"] == "VK2"
        assert [k["unit_code"] for k in teil["children"]] == ["ID2"]

    def test_unbekannter_teilbaum_ist_ein_404(self, client):
        antwort = client.get(f"{WEG}/org-chart/{uuid.uuid4()}", headers=kopf(HAUS_A))
        assert antwort.status_code == 404

    def test_einheitenschluessel_ist_je_mandant_eindeutig(self, client):
        assert einheit(client, HAUS_A, "DOPPEL").status_code == 201
        assert einheit(client, HAUS_A, "DOPPEL").status_code == 409
        assert einheit(client, HAUS_B, "DOPPEL").status_code == 201

    def test_fremdes_organigramm_ist_nicht_sichtbar(self, client):
        einheit(client, HAUS_B, "NUR-B")
        antwort = client.get(f"{WEG}/org-chart", headers=kopf(HAUS_A))
        assert antwort.status_code == 200
        assert antwort.json()["org_chart"] == []

    def test_fremde_elterneinheit_wird_abgewiesen(self, client):
        fremd = einheit(client, HAUS_B, "B-OBEN").json()
        antwort = einheit(client, HAUS_A, "A-UNTEN", parent_id=fremd["id"])
        assert antwort.status_code == 422

    def test_unbekannte_art_wird_abgewiesen(self, client):
        antwort = client.post(
            f"{WEG}/org-units",
            json={"unit_code": "X", "name": "X", "unit_type": "FILIALE"},
            headers=kopf(HAUS_A),
        )
        assert antwort.status_code == 422

    def test_leerer_name_wird_abgewiesen(self, client):
        antwort = client.post(
            f"{WEG}/org-units", json={"unit_code": "Y", "name": ""}, headers=kopf(HAUS_A)
        )
        assert antwort.status_code == 422


class TestKostenstelle:
    def test_eigene_kostenstelle_wird_angenommen(self, client):
        antwort = einheit(client, HAUS_A, "KS1", cost_center_id=KOSTENSTELLE_A)
        assert antwort.status_code == 201, antwort.text

    def test_fremde_kostenstelle_wird_abgewiesen(self, client):
        """Eine fremde Kostenstelle im Organigramm waere ein Auswertungsfehler."""
        antwort = einheit(client, HAUS_A, "KS2", cost_center_id=KOSTENSTELLE_B)
        assert antwort.status_code == 422
        assert "Mandanten" in antwort.text

    def test_unbekannte_kostenstelle_wird_abgewiesen(self, client):
        assert einheit(client, HAUS_A, "KS3", cost_center_id=str(uuid.uuid4())).status_code == 422


class TestZyklus:
    def test_einheit_ist_nicht_ihr_eigener_elternteil(self, client):
        eins = einheit(client, HAUS_A, "SELF").json()
        antwort = client.patch(
            f"{WEG}/org-units/{eins['id']}",
            json={"parent_id": eins["id"]},
            headers=kopf(HAUS_A),
        )
        assert antwort.status_code == 422

    def test_umhaengen_in_den_eigenen_teilbaum_wird_abgewiesen(self, client):
        """Der Zyklus entsteht beim Schreiben — abweisen, nicht spaeter bemerken."""
        oben = einheit(client, HAUS_A, "Z-OBEN").json()
        unten = einheit(client, HAUS_A, "Z-UNTEN", parent_id=oben["id"]).json()
        antwort = client.patch(
            f"{WEG}/org-units/{oben['id']}",
            json={"parent_id": unten["id"]},
            headers=kopf(HAUS_A),
        )
        assert antwort.status_code == 409
        assert "Zyklus" in antwort.text

    def test_datenbank_verhindert_den_trivialen_zyklus(self, engine, client):
        from sqlalchemy import text
        from sqlalchemy.exc import IntegrityError

        eins = einheit(client, HAUS_A, "DB-SELF").json()
        with pytest.raises(IntegrityError):
            with engine.begin() as v:
                v.execute(
                    text(f"UPDATE {EINHEITEN} SET parent_id = id WHERE id = :id"),
                    {"id": eins["id"]},
                )

    def test_tiefengrenze_ist_ein_fehler_und_kein_gekuerzter_baum(self):
        from fastapi import HTTPException

        from app.services import personal_organisation_service as dienst

        tief = [{"id": "x", "parent_id": None, "depth": dienst.MAX_TIEFE}]
        with pytest.raises(HTTPException) as fehler:
            dienst.zyklus_pruefen(tief)
        assert fehler.value.status_code == 409
        assert "Zyklus" in str(fehler.value.detail)
        dienst.zyklus_pruefen([{"id": "x", "parent_id": None, "depth": 3}])


# ── 3. Das Arbeitszeitkonto ─────────────────────────────────────────────────


class TestZeitkonto:
    def test_saldo_statt_503(self, engine, client):
        """Vorher antwortete dieser Weg ausnahmslos 503."""
        zeit_eintragen(engine, HAUS_A, "2026-05-04", 8.0)
        zeit_eintragen(engine, HAUS_A, "2026-05-05", 8.0)
        antwort = client.get(f"{WEG}/time-accounts/{MITARBEITER}", headers=kopf(HAUS_A))
        assert antwort.status_code == 200, antwort.text
        assert antwort.json()["saldo_hours"] == pytest.approx(16.0)

    def test_planstunden_kommen_aus_den_schichten(self, engine, client):
        """Gerechnet aus `starts_at`/`ends_at` — nicht aus `planned_hours`."""
        zeit_eintragen(engine, HAUS_A, "2026-05-04", 9.0)
        schicht_planen(engine, HAUS_A, "2026-05-04", "07:00", "15:00")
        daten = client.get(f"{WEG}/time-accounts/{MITARBEITER}", headers=kopf(HAUS_A)).json()
        monat = next(m for m in daten["monate"] if m["monat"] == "2026-05")
        assert monat["planned_hours"] == pytest.approx(8.0)
        assert monat["actual_hours"] == pytest.approx(9.0)
        assert monat["saldo_hours"] == pytest.approx(1.0)

    def test_nachtschicht_zaehlt_bis_zum_naechsten_tag(self, engine, client):
        schicht_planen(engine, HAUS_A, "2026-05-04", "22:00", "06:00")
        daten = client.get(f"{WEG}/time-accounts/{MITARBEITER}", headers=kopf(HAUS_A)).json()
        monat = next(m for m in daten["monate"] if m["monat"] == "2026-05")
        assert monat["planned_hours"] == pytest.approx(8.0)

    def test_fremde_schicht_zaehlt_nicht(self, engine, client):
        """Nur Schichten, in deren Zuordnungsliste der Mitarbeiter steht."""
        schicht_planen(engine, HAUS_A, "2026-05-04", "07:00", "15:00", refs=["EMP-ANDERS"])
        daten = client.get(f"{WEG}/time-accounts/{MITARBEITER}", headers=kopf(HAUS_A)).json()
        assert daten["monate"] == []

    def test_abgesagte_schicht_zaehlt_nicht(self, engine, client):
        schicht_planen(engine, HAUS_A, "2026-05-04", "07:00", "15:00", status="cancelled")
        daten = client.get(f"{WEG}/time-accounts/{MITARBEITER}", headers=kopf(HAUS_A)).json()
        assert daten["monate"] == []

    def test_schicht_eines_anderen_hauses_zaehlt_nicht(self, engine, client):
        schicht_planen(engine, HAUS_B, "2026-05-04", "07:00", "15:00")
        daten = client.get(f"{WEG}/time-accounts/{MITARBEITER}", headers=kopf(HAUS_A)).json()
        assert daten["monate"] == []


class TestSaldoformel:
    def test_korrektur_zaehlt_genau_einmal(self, engine, client):
        """Vorher ging sie in `saldo_hours` **und** in den "Uebertrag" ein."""
        zeit_eintragen(engine, HAUS_A, "2026-05-04", 8.0)
        assert korrigieren(client, HAUS_A, delta_hours=1.5,
                           adjustment_date="2026-05-31").status_code == 201
        daten = client.get(
            f"{WEG}/time-accounts/{MITARBEITER}", params={"jahr": 2026}, headers=kopf(HAUS_A)
        ).json()
        assert daten["saldo_hours"] == pytest.approx(9.5)
        assert daten["saldo_laufende_periode"] == pytest.approx(9.5)
        assert daten["uebertrag_vorperioden"] == pytest.approx(0.0)

    def test_saldo_ist_die_summe_der_ausgewiesenen_zahlen(self, engine, client):
        zeit_eintragen(engine, HAUS_A, "2025-11-03", 10.0)
        zeit_eintragen(engine, HAUS_A, "2026-05-04", 8.0)
        korrigieren(client, HAUS_A, delta_hours=-2.0, reason="Abbau",
                    adjustment_date="2026-05-31")
        daten = client.get(
            f"{WEG}/time-accounts/{MITARBEITER}", params={"jahr": 2026}, headers=kopf(HAUS_A)
        ).json()
        assert daten["uebertrag_vorperioden"] == pytest.approx(10.0)
        assert daten["saldo_laufende_periode"] == pytest.approx(6.0)
        assert daten["saldo_hours"] == pytest.approx(
            daten["uebertrag_vorperioden"]
            + daten["saldo_laufende_periode"]
            + daten["saldo_folgeperioden"]
        )

    def test_uebertrag_ist_kein_lebenssummenwert(self, engine, client):
        """Vorher summierte der "Uebertrag" die Ist-Stunden aller Vorjahre."""
        zeit_eintragen(engine, HAUS_A, "2025-11-03", 10.0)
        schicht_planen(engine, HAUS_B, "2025-11-03", "08:00", "16:00")  # anderes Haus
        schicht_planen(engine, HAUS_A, "2025-11-03", "08:00", "16:00")
        daten = client.get(
            f"{WEG}/time-accounts/{MITARBEITER}", params={"jahr": 2026}, headers=kopf(HAUS_A)
        ).json()
        # 10 Ist − 8 Plan = 2, nicht 10.
        assert daten["uebertrag_vorperioden"] == pytest.approx(2.0)

    def test_fremde_zeiten_zaehlen_nicht(self, engine, client):
        # 9,0 Stunden: `time_entries` hat eine Bereichspruefung
        # (`ck_hr_time_entries_hours_range`) und weist einen 40-Stunden-Tag
        # zu Recht ab.
        zeit_eintragen(engine, HAUS_B, "2026-05-04", 9.0)
        daten = client.get(f"{WEG}/time-accounts/{MITARBEITER}", headers=kopf(HAUS_A)).json()
        assert daten["saldo_hours"] == pytest.approx(0.0)
        assert daten["monate"] == []


class TestKorrektur:
    def test_korrektur_wird_gebucht(self, client):
        antwort = korrigieren(client, HAUS_A, delta_hours=2.5, reason="Uebertrag 2025")
        assert antwort.status_code == 201, antwort.text
        assert antwort.json()["delta_hours"] == pytest.approx(2.5)
        assert antwort.json()["reason"] == "Uebertrag 2025"

    @pytest.mark.parametrize("grund", ["", "   "])
    def test_korrektur_ohne_grund_wird_abgewiesen(self, client, grund):
        """§ 16 Abs. 2 ArbZG: Eine Aenderung ohne Grund ist nicht nachvollziehbar."""
        antwort = korrigieren(client, HAUS_A, reason=grund)
        assert antwort.status_code == 422

    def test_korrektur_um_null_wird_abgewiesen(self, client):
        antwort = korrigieren(client, HAUS_A, delta_hours=0)
        assert antwort.status_code == 422

    def test_korrektur_tragt_den_mandanten(self, engine, client):
        from sqlalchemy import text

        daten = korrigieren(client, HAUS_A).json()
        with engine.connect() as c:
            assert c.execute(
                text(f"SELECT tenant_id FROM {KORREKTUREN} WHERE id = :id"), {"id": daten["id"]}
            ).scalar() == HAUS_A

    def test_unbekanntes_feld_wird_abgewiesen(self, client):
        antwort = client.post(
            f"{WEG}/time-accounts/{MITARBEITER}/adjust",
            json={"delta_hours": 1, "reason": "x", "saldo_hours": 99},
            headers=kopf(HAUS_A),
        )
        assert antwort.status_code == 422
