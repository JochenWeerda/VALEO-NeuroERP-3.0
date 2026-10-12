"""Kontenplan: Der Mandant kommt aus dem Mandantenkontext, nicht aus der Anfrage.

Bis zum 12.10.2026 nahm ``chart_of_accounts.py`` den Mandanten aus dem Query-Parameter
``tenant_id`` (Liste, Pruefung, DATEV-Ausgabe) oder aus dem Rumpf (anlegen); lesen, aendern
und loeschen eines einzelnen Kontos filterten gar nicht. Wer lesen durfte, bekam mit
``?tenant_id=`` Kontenplan und DATEV-Buchungen eines anderen Mandanten.

Geprueft gegen die echte Datenbank — ein Mandantenfilter, der nur im Mock greift, greift nicht.
"""

from __future__ import annotations

import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.api.v1.endpoints import chart_of_accounts
from app.auth.deps import get_current_user
from app.core.database import SessionLocal, get_db
from testgrenze import ersetze_mandant

HAUS_A = "kp-mandant-a"
HAUS_B = "kp-mandant-b"
PREFIX = "/api/v1/finance/chart-of-accounts"


def _kopf(mandant: str) -> dict[str, str]:
    return {"X-Tenant-ID": mandant}


def _konto(nummer: str, mandant_im_rumpf: str) -> dict:
    return {"tenant_id": mandant_im_rumpf, "account_number": nummer, "account_name": f"Konto {nummer}",
            "account_type": "asset", "category": "current_assets", "currency": "EUR"}


@pytest.fixture
def haus():
    """Zwei Mandanten, je ein eigenes Konto, dazu eines im gemeinsamen Rahmen."""
    lauf = uuid.uuid4().hex[:6]
    gemeinsam_id = f"kp-{lauf}-sys"
    with SessionLocal() as db:
        for mandant in (HAUS_A, HAUS_B, "system"):
            db.execute(text(
                "INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, :id, true) "
                "ON CONFLICT (id) DO NOTHING"), {"id": mandant})
        db.execute(text(
            "INSERT INTO domain_erp.chart_of_accounts "
            "(id, account_number, account_name, account_type, category, tenant_id, is_active) "
            "VALUES (:id, :nr, 'Gemeinsam', 'asset', 'current_assets', 'system', true)"),
            {"id": gemeinsam_id, "nr": f"S{lauf}"})
        db.commit()

    app = FastAPI()
    app.include_router(chart_of_accounts.router, prefix="/api/v1/finance")
    # Der Mandant kommt im Betrieb aus dem geprueften Token. Hier nennt ihn der Kopf der Testanfrage:
    # Geprueft wird, dass der Weg nur diesen Mandanten nimmt — nicht Query und nicht Rumpf.
    ersetze_mandant(app)
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "5f0c2a9e", "name": "t.de-vries", "roles": ["FINANCE_ADMIN"]}
    with TestClient(app) as client:
        a = client.post(PREFIX + "/", json=_konto(f"A{lauf}", HAUS_A), headers=_kopf(HAUS_A))
        b = client.post(PREFIX + "/", json=_konto(f"B{lauf}", HAUS_B), headers=_kopf(HAUS_B))
        assert a.status_code == 200 and b.status_code == 200, (a.text, b.text)
        try:
            yield {"client": client, "app": app, "lauf": lauf, "a": a.json()["id"], "b": b.json()["id"],
                   "gemeinsam": gemeinsam_id}
        finally:
            with SessionLocal() as db:
                db.execute(text("DELETE FROM domain_erp.chart_of_accounts WHERE account_number LIKE :m"),
                           {"m": f"_{lauf}%"})
                db.commit()


def _nummern(antwort) -> set[str]:
    return {k["account_number"] for k in antwort.json()["items"]}


def test_liste_zeigt_eigene_und_gemeinsame_konten(haus):
    lauf = haus["lauf"]
    antwort = haus["client"].get(PREFIX + "/", params={"search": lauf, "limit": 200}, headers=_kopf(HAUS_A))
    assert antwort.status_code == 200, antwort.text
    assert _nummern(antwort) == {f"A{lauf}", f"S{lauf}"}


def test_query_parameter_waehlt_keinen_fremden_mandanten(haus):
    """Der alte Weg: ``?tenant_id=`` nannte den Mandanten, dessen Konten man sehen wollte."""
    lauf = haus["lauf"]
    antwort = haus["client"].get(
        PREFIX + "/", params={"search": lauf, "limit": 200, "tenant_id": HAUS_B}, headers=_kopf(HAUS_A))
    assert antwort.status_code == 200, antwort.text
    assert f"B{lauf}" not in _nummern(antwort)
    assert f"A{lauf}" in _nummern(antwort)


@pytest.mark.parametrize("methode,rumpf", [("GET", None), ("PUT", {"account_name": "gekapert"}), ("DELETE", None)])
def test_fremdes_konto_gibt_es_nicht(haus, methode, rumpf):
    antwort = haus["client"].request(methode, f"{PREFIX}/{haus['b']}", json=rumpf, headers=_kopf(HAUS_A))
    assert antwort.status_code == 404, antwort.text
    eigentuemer = haus["client"].get(f"{PREFIX}/{haus['b']}", headers=_kopf(HAUS_B))
    assert eigentuemer.status_code == 200, eigentuemer.text
    assert eigentuemer.json()["account_name"] == f"Konto B{haus['lauf']}"
    assert eigentuemer.json()["is_active"] is True


def test_eigenes_und_gemeinsames_konto_sind_lesbar(haus):
    for konto in (haus["a"], haus["gemeinsam"]):
        antwort = haus["client"].get(f"{PREFIX}/{konto}", headers=_kopf(HAUS_A))
        assert antwort.status_code == 200, antwort.text


def test_anlegen_folgt_der_anmeldung_nicht_dem_rumpf(haus):
    """Im Rumpf steht Haus B — das Konto gehoert trotzdem dem angemeldeten Haus A."""
    nummer = f"X{haus['lauf']}"
    antwort = haus["client"].post(PREFIX + "/", json=_konto(nummer, HAUS_B), headers=_kopf(HAUS_A))
    assert antwort.status_code == 200, antwort.text
    assert antwort.json()["tenant_id"] == HAUS_A
    bei_b = haus["client"].get(PREFIX + "/", params={"search": nummer}, headers=_kopf(HAUS_B))
    assert _nummern(bei_b) == set()


def test_aendern_wirkt_auch_ohne_namen_im_rumpf(haus):
    """Der Weg aenderte nur, wenn der Name im Rumpf stand — und meldete sonst Erfolg ohne Wirkung."""
    antwort = haus["client"].put(f"{PREFIX}/{haus['a']}", json={"category": "fixed_assets"}, headers=_kopf(HAUS_A))
    assert antwort.status_code == 200, antwort.text
    gelesen = haus["client"].get(f"{PREFIX}/{haus['a']}", headers=_kopf(HAUS_A))
    assert gelesen.json()["category"] == "fixed_assets"


def _als(haus, *rollen):
    haus["app"].dependency_overrides[get_current_user] = lambda: {
        "sub": "5f0c2a9e", "name": "t.de-vries", "roles": list(rollen)}


@pytest.mark.parametrize("methode,rumpf", [("PUT", {"account_name": "umbenannt"}), ("DELETE", None)])
@pytest.mark.parametrize("rollen", [("FINANCE_ADMIN",), ("FINANCE_ADMIN", "manager")])
def test_gemeinsamer_rahmen_ist_fuer_die_hausrolle_nur_lesbar(haus, methode, rumpf, rollen):
    """Die Finanzleitung eines Hauses sieht den gemeinsamen Rahmen — aendern wuerde alle Haeuser treffen."""
    _als(haus, *rollen)
    antwort = haus["client"].request(methode, f"{PREFIX}/{haus['gemeinsam']}", json=rumpf, headers=_kopf(HAUS_A))
    assert antwort.status_code == 403, antwort.text
    assert "KONTENRAHMEN_PFLEGE" in antwort.json()["detail"]
    gelesen = haus["client"].get(f"{PREFIX}/{haus['gemeinsam']}", headers=_kopf(HAUS_B))
    assert gelesen.status_code == 200, gelesen.text
    assert gelesen.json()["account_name"] == "Gemeinsam"
    assert gelesen.json()["is_active"] is True


@pytest.mark.parametrize("pflegerecht", ["KONTENRAHMEN_PFLEGE", "admin"])
def test_gemeinsamen_rahmen_pflegt_wer_das_recht_hat(haus, pflegerecht):
    _als(haus, "FINANCE_ADMIN", pflegerecht)
    geaendert = haus["client"].put(
        f"{PREFIX}/{haus['gemeinsam']}", json={"account_name": "Gepflegt"}, headers=_kopf(HAUS_A))
    assert geaendert.status_code == 200, geaendert.text
    assert haus["client"].get(f"{PREFIX}/{haus['gemeinsam']}", headers=_kopf(HAUS_B)).json()["account_name"] == "Gepflegt"
    assert haus["client"].delete(f"{PREFIX}/{haus['gemeinsam']}", headers=_kopf(HAUS_A)).status_code == 200


def test_pflegerecht_allein_ist_keine_schreibrolle(haus):
    """Das Recht am gemeinsamen Rahmen ersetzt die Finanzrolle nicht."""
    _als(haus, "KONTENRAHMEN_PFLEGE")
    antwort = haus["client"].put(
        f"{PREFIX}/{haus['gemeinsam']}", json={"account_name": "ohne Finanzrolle"}, headers=_kopf(HAUS_A))
    assert antwort.status_code == 403, antwort.text


def test_eigenes_konto_braucht_kein_pflegerecht(haus):
    _als(haus, "FINANCE_ADMIN")
    assert haus["client"].put(
        f"{PREFIX}/{haus['a']}", json={"account_name": "eigenes"}, headers=_kopf(HAUS_A)).status_code == 200
    assert haus["client"].delete(f"{PREFIX}/{haus['a']}", headers=_kopf(HAUS_A)).status_code == 200


@pytest.fixture
def bebucht(haus):
    """Eine Buchungszeile gegen das Konto von Haus A."""
    lauf = haus["lauf"]
    with SessionLocal() as db:
        db.execute(text(
            "INSERT INTO domain_erp.journal_entries (id, tenant_id, entry_number, entry_date, posting_date) "
            "VALUES (:id, :t, :nr, DATE '2026-10-01', DATE '2026-10-01')"),
            {"id": f"kp-{lauf}-je", "t": HAUS_A, "nr": f"KP-{lauf}"})
        db.execute(text(
            "INSERT INTO domain_erp.journal_entry_lines (id, journal_entry_id, account_id, line_number) "
            "VALUES (:id, :je, :konto, 1)"),
            {"id": f"kp-{lauf}-jel", "je": f"kp-{lauf}-je", "konto": haus["a"]})
        db.commit()
    try:
        yield haus
    finally:
        with SessionLocal() as db:
            db.execute(text("DELETE FROM domain_erp.journal_entry_lines WHERE id = :id"), {"id": f"kp-{lauf}-jel"})
            db.execute(text("DELETE FROM domain_erp.journal_entries WHERE id = :id"), {"id": f"kp-{lauf}-je"})
            db.commit()


def test_bebuchtes_konto_wird_nicht_deaktiviert(bebucht):
    """Die alte Pruefung fragte eine Beziehung ab, die das Modell nicht hat — sie griff nie."""
    antwort = bebucht["client"].delete(f"{PREFIX}/{bebucht['a']}", headers=_kopf(HAUS_A))
    assert antwort.status_code == 409, antwort.text
    assert "bebucht" in antwort.json()["detail"]
    assert bebucht["client"].get(f"{PREFIX}/{bebucht['a']}", headers=_kopf(HAUS_A)).json()["is_active"] is True


def test_bebuchtes_konto_behaelt_die_kontenart(bebucht):
    kopf = _kopf(HAUS_A)
    wechsel = bebucht["client"].put(f"{PREFIX}/{bebucht['a']}", json={"account_type": "expense"}, headers=kopf)
    assert wechsel.status_code == 409, wechsel.text
    assert "Kontenart" in wechsel.json()["detail"]
    # Die Maske schickt die unveraenderte Kontenart immer mit — das ist kein Wechsel.
    umbenannt = bebucht["client"].put(
        f"{PREFIX}/{bebucht['a']}", json={"account_name": "Neuer Name", "account_type": "asset"}, headers=kopf)
    assert umbenannt.status_code == 200, umbenannt.text
    gelesen = bebucht["client"].get(f"{PREFIX}/{bebucht['a']}", headers=kopf).json()
    assert (gelesen["account_name"], gelesen["account_type"]) == ("Neuer Name", "asset")


def test_unbebuchtes_konto_wechselt_die_kontenart(haus):
    antwort = haus["client"].put(f"{PREFIX}/{haus['a']}", json={"account_type": "expense"}, headers=_kopf(HAUS_A))
    assert antwort.status_code == 200, antwort.text


@pytest.mark.parametrize("methode,weg,rumpf", [
    ("POST", "/", "neu"), ("PUT", "/{a}", {"account_name": "x"}), ("DELETE", "/{a}", None)])
def test_kontenpflege_ist_sache_der_leitung(haus, methode, weg, rumpf):
    """Die Buchhaltung bucht — den Kontenplan pflegt, wer das Recht dazu hat."""
    if rumpf == "neu":
        rumpf = _konto(f"Y{haus['lauf']}", HAUS_A)
    _als(haus, "FINANCE_BEARBEITEN", "manager")
    antwort = haus["client"].request(methode, PREFIX + weg.format(a=haus["a"]), json=rumpf, headers=_kopf(HAUS_A))
    assert antwort.status_code == 403, antwort.text
    # Das Pflegerecht ist delegierbar und haengt nicht an Adminrechten.
    _als(haus, "KONTENPLAN_PFLEGE")
    antwort = haus["client"].request(methode, PREFIX + weg.format(a=haus["a"]), json=rumpf, headers=_kopf(HAUS_A))
    assert antwort.status_code == 200, antwort.text


def test_kontenpflege_des_hauses_reicht_nicht_fuer_den_gemeinsamen_rahmen(haus):
    _als(haus, "KONTENPLAN_PFLEGE")
    antwort = haus["client"].put(
        f"{PREFIX}/{haus['gemeinsam']}", json={"account_name": "x"}, headers=_kopf(HAUS_A))
    assert antwort.status_code == 403, antwort.text
    assert "KONTENRAHMEN_PFLEGE" in antwort.json()["detail"]


# --- Kontosperre (KONTO-SPERRE-20261012) -------------------------------------------------------


def _zeile(lauf: str, konto: str, nr: int) -> None:
    """Schreibt eine Buchungszeile so, wie es die rohen SQL-Wege tun — an der Maske und am Weg vorbei."""
    with SessionLocal() as db:
        db.execute(text(
            "INSERT INTO domain_erp.journal_entry_lines (id, journal_entry_id, account_id, line_number) "
            "VALUES (:id, :je, :konto, :nr)"),
            {"id": f"kp-{lauf}-jel{nr}", "je": f"kp-{lauf}-je", "konto": konto, "nr": nr})
        db.commit()


@pytest.fixture
def gesperrt(bebucht):
    antwort = bebucht["client"].put(
        f"{PREFIX}/{bebucht['a']}", json={"posting_blocked": True}, headers=_kopf(HAUS_A))
    assert antwort.status_code == 200, antwort.text
    assert antwort.json()["posting_blocked"] is True
    try:
        yield bebucht
    finally:
        with SessionLocal() as db:
            db.execute(text("DELETE FROM domain_erp.journal_entry_lines WHERE id LIKE :m"),
                       {"m": f"kp-{bebucht['lauf']}-jel_"})
            db.commit()


def test_bebuchtes_konto_laesst_sich_sperren_und_bleibt_sichtbar(gesperrt):
    """Deaktivieren geht bei einem bebuchten Konto nicht — sperren schon, und es bleibt im Kontenplan."""
    liste = gesperrt["client"].get(PREFIX + "/", params={"search": gesperrt["lauf"]}, headers=_kopf(HAUS_A))
    eigene = [k for k in liste.json()["items"] if k["id"] == gesperrt["a"]]
    assert [(k["posting_blocked"], k["is_active"]) for k in eigene] == [(True, True)]


def test_gesperrtes_konto_nimmt_keine_buchungszeile_an(gesperrt):
    """Die Sperre gilt an der Tabelle, nicht an einem einzelnen Weg: Auch rohes SQL kommt nicht vorbei."""
    from sqlalchemy.exc import IntegrityError

    with pytest.raises(IntegrityError) as fehler:
        _zeile(gesperrt["lauf"], gesperrt["a"], 2)
    assert "fuer Buchungen gesperrt" in str(fehler.value)
    assert f"A{gesperrt['lauf']}" in str(fehler.value)


def test_sperre_laesst_bestehende_zeilen_in_ruhe(gesperrt):
    with SessionLocal() as db:
        zeilen = db.execute(text(
            "SELECT count(*) FROM domain_erp.journal_entry_lines WHERE account_id = :k"), {"k": gesperrt["a"]}).scalar()
        # Eine bestehende Zeile laesst sich weiter aendern, solange sie auf ihrem Konto bleibt.
        db.execute(text("UPDATE domain_erp.journal_entry_lines SET line_number = 1 WHERE account_id = :k"),
                   {"k": gesperrt["a"]})
        db.commit()
    assert zeilen == 1


def test_umhaengen_auf_ein_gesperrtes_konto_wird_abgelehnt(gesperrt):
    from sqlalchemy.exc import IntegrityError

    _zeile(gesperrt["lauf"], gesperrt["b"], 3)  # Konto von Haus B ist offen
    with SessionLocal() as db, pytest.raises(IntegrityError):
        db.execute(text("UPDATE domain_erp.journal_entry_lines SET account_id = :k WHERE id = :id"),
                   {"k": gesperrt["a"], "id": f"kp-{gesperrt['lauf']}-jel3"})
        db.commit()


def test_entsperrtes_konto_wird_wieder_bebucht(gesperrt):
    antwort = gesperrt["client"].put(
        f"{PREFIX}/{gesperrt['a']}", json={"posting_blocked": False}, headers=_kopf(HAUS_A))
    assert antwort.status_code == 200, antwort.text
    _zeile(gesperrt["lauf"], gesperrt["a"], 4)


def test_sperren_ist_kontenpflege(bebucht):
    """Die Buchhaltung sperrt kein Konto; wer die Kontenpflege hat, schon."""
    _als(bebucht, "FINANCE_BEARBEITEN", "manager")
    assert bebucht["client"].put(
        f"{PREFIX}/{bebucht['a']}", json={"posting_blocked": True}, headers=_kopf(HAUS_A)).status_code == 403
    _als(bebucht, "KONTENPLAN_PFLEGE")
    assert bebucht["client"].put(
        f"{PREFIX}/{bebucht['a']}", json={"posting_blocked": True}, headers=_kopf(HAUS_A)).status_code == 200
    bebucht["client"].put(f"{PREFIX}/{bebucht['a']}", json={"posting_blocked": False}, headers=_kopf(HAUS_A))


def test_gemeinsamen_rahmen_sperrt_nur_das_rahmenrecht(haus):
    _als(haus, "FINANCE_ADMIN")
    assert haus["client"].put(
        f"{PREFIX}/{haus['gemeinsam']}", json={"posting_blocked": True}, headers=_kopf(HAUS_A)).status_code == 403


def test_manuelle_buchung_auf_gesperrtes_konto_nennt_den_grund(gesperrt, monkeypatch):
    """Die Buchhaltung liest „Konto … ist gesperrt“ — nicht den Datenbankfehler des Triggers."""
    from app.api.v1.endpoints import journal_entries

    def kein_schreiben(_klasse):
        raise AssertionError("Die Buchung darf vor der Ablehnung nicht angelegt werden")

    monkeypatch.setattr(journal_entries.container, "resolve", kein_schreiben)
    app = FastAPI()
    app.include_router(journal_entries.router, prefix="/journal-entries")
    ersetze_mandant(app)
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "5f0c2a9e", "name": "t.de-vries", "roles": ["FINANCE_BEARBEITEN"]}
    rumpf = {
        "entry_number": f"KP-{gesperrt['lauf']}-M", "entry_date": "2026-10-12T00:00:00",
        "posting_date": "2026-10-12T00:00:00", "description": "Test", "reference": "BELEG-1",
        "lines": [
            {"account_id": gesperrt["a"], "debit_amount": "10.00", "line_number": 1},
            {"account_id": gesperrt["gemeinsam"], "credit_amount": "10.00", "line_number": 2},
        ],
    }
    with TestClient(app) as client:
        antwort = client.post("/journal-entries/", json=rumpf, headers=_kopf(HAUS_A))
    assert antwort.status_code == 409, antwort.text
    assert antwort.json()["detail"] == f"Konto A{gesperrt['lauf']} ist fuer Buchungen gesperrt."


class _Mitschnitt:
    """Nimmt die Parameter der DATEV-Abfrage auf und liefert keine Buchungen."""

    def __init__(self):
        self.parameter: list[dict] = []

    def execute(self, _sql, parameter=None):
        self.parameter.append(dict(parameter or {}))
        return self

    def fetchall(self):
        return []


def test_datev_ausgabe_nimmt_den_mandanten_der_anmeldung(haus):
    mitschnitt = _Mitschnitt()
    haus["app"].dependency_overrides[get_db] = lambda: mitschnitt
    try:
        haus["client"].post(
            PREFIX + "/datev-export", params={"von_datum": "2026-01-01", "tenant_id": HAUS_B}, headers=_kopf(HAUS_A))
    finally:
        haus["app"].dependency_overrides.pop(get_db, None)
    assert [p["tenant_id"] for p in mitschnitt.parameter] == [HAUS_A]


def test_kein_weg_nimmt_den_mandanten_aus_der_anfrage():
    """Ratsche: Kein Weg des Kontenplans hat einen Query-Parameter ``tenant_id``."""
    for route in chart_of_accounts.router.routes:
        assert "tenant_id" not in {p.name for p in route.dependant.query_params}, route.path
