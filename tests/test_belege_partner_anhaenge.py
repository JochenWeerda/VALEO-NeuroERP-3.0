"""Partnername und Anhaenge im Beleg (BELEG-014).

Geprueft gegen die echte Datenbank, an den Referenzbelegen.
"""

from __future__ import annotations

import importlib.util
import pathlib
import uuid

import pytest
from sqlalchemy import text

from app.core import belegvertrag as bv
from app.core.database import SessionLocal
from app.services import docflow_service
from app.services.docflow_belegadapter import lies_beleg
from app.services.docflow_service import DocflowService

WURZEL = pathlib.Path(__file__).resolve().parent.parent


def _modul(name: str):
    spec = importlib.util.spec_from_file_location(name, WURZEL / f"scripts/{name}.py")
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


AUFRAEUMEN = (
    "DELETE FROM domain_docflow.document_artifacts WHERE tenant_id = :t",
    "DELETE FROM domain_einkauf.lieferanten WHERE tenant_id = :t",
    "DELETE FROM domain_crm.customers WHERE tenant_id = :t",
    "DELETE FROM domain_erp.journal_entry_lines WHERE journal_entry_id IN "
    "(SELECT id FROM domain_erp.journal_entries WHERE tenant_id = :t)",
    "DELETE FROM domain_erp.journal_entries WHERE tenant_id = :t",
    "DELETE FROM domain_erp.offene_posten WHERE tenant_id = :t",
    "DELETE FROM domain_docflow.approvals WHERE tenant_id = :t",
    "DELETE FROM domain_docflow.document_status_history WHERE tenant_id = :t",
    "DELETE FROM domain_docflow.document_command_log WHERE tenant_id = :t",
    "DELETE FROM domain_docflow.command_idempotency_keys WHERE tenant_id = :t",
    "DELETE FROM domain_docflow.create_request_idempotency WHERE tenant_id = :t",
    "DELETE FROM domain_docflow.document_links WHERE tenant_id = :t",
    "DELETE FROM domain_docflow.document_header_links WHERE tenant_id = :t",
    "DELETE FROM domain_docflow.document_postings WHERE tenant_id = :t",
    "DELETE FROM domain_docflow.document_items WHERE tenant_id = :t",
    "DELETE FROM domain_docflow.document_headers WHERE tenant_id = :t",
    "DELETE FROM domain_erp.tax_keys WHERE tenant_id = :t",
    "DELETE FROM domain_erp.chart_of_accounts WHERE tenant_id = :t",
    "DELETE FROM domain_shared.system_properties WHERE tenant_id = :t",
    "DELETE FROM domain_shared.tenants WHERE id = :t",
)


@pytest.fixture(scope="module")
def satz():
    mandant = f"pa-{uuid.uuid4().hex[:8]}"
    patch = pytest.MonkeyPatch()
    patch.setattr(docflow_service, "assert_customer_allowed_for_invoice", lambda *_a, **_k: None)
    with SessionLocal() as db:
        _modul("sichtpruefung_mandant_einrichten").richte_ein(db, mandant, "Partner und Anhaenge Test")
        db.commit()
        angelegt = _modul("referenzbelege_anlegen").lege_an(db, mandant)
    yield {"mandant": mandant, **{b["rolle"]: b for b in angelegt}}
    patch.undo()
    with SessionLocal() as db:
        db.execute(text("SELECT set_config('valeo.docflow_wartung', 'loeschen', true)"))
        for sql in AUFRAEUMEN:
            db.execute(text(sql), {"t": mandant})
        db.commit()


def _lies(satz, rolle: str) -> bv.Beleg:
    with SessionLocal() as db:
        beleg = lies_beleg(DocflowService(db, satz["mandant"]), satz[rolle]["id"])
        db.rollback()
    assert beleg is not None and bv.pruefe(beleg) == []
    return beleg


def test_ohne_stammsatz_bleibt_die_kennung_des_belegs_ohne_namen(satz):
    assert _lies(satz, "vk-rechnung-1").partner == bv.Partner(rolle="kunde", nummer="REF-KUNDE")
    assert _lies(satz, "ek-rechnung-1").partner == bv.Partner(rolle="lieferant", nummer="REF-LIEFERANT")


def test_name_und_nummer_kommen_aus_den_stammdaten_des_eigenen_mandanten(satz):
    lieferant_id = str(uuid.uuid4())
    fremd = f"{satz['mandant']}-x"
    with SessionLocal() as db:
        db.execute(text(
            "INSERT INTO domain_crm.customers (id, tenant_id, customer_number, company_name) "
            "VALUES (:id, :t, 'REF-KUNDE', 'Hof Referenz GbR')"), {"id": f"k-{uuid.uuid4().hex[:8]}", "t": satz["mandant"]})
        # Ein Kunde eines anderen Mandanten stoert die Suche nicht.
        db.execute(text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, :id, true)"),
                   {"id": fremd})
        db.execute(text(
            "INSERT INTO domain_crm.customers (id, tenant_id, customer_number, company_name) "
            "VALUES (:id, :t, :nr, 'Fremder Hof')"),
            {"id": f"k-{uuid.uuid4().hex[:8]}", "t": fremd, "nr": f"REF-KUNDE-{uuid.uuid4().hex[:6]}"})
        db.execute(text(
            "INSERT INTO domain_einkauf.lieferanten (id, tenant_id, lieferantennummer, firmenname) "
            "VALUES (CAST(:id AS uuid), :t, 'REF-LIEFERANT', 'Agrarhandel Referenz GmbH')"),
            {"id": lieferant_id, "t": satz["mandant"]})
        db.commit()
    try:
        assert _lies(satz, "vk-rechnung-1").partner == bv.Partner(
            rolle="kunde", nummer="REF-KUNDE", name="Hof Referenz GbR")
        assert _lies(satz, "vk-lieferschein-1").partner.name == "Hof Referenz GbR"
        assert _lies(satz, "ek-bestellung").partner == bv.Partner(
            rolle="lieferant", nummer="REF-LIEFERANT", name="Agrarhandel Referenz GmbH")
        # Traegt der Beleg die Kennung statt der Nummer, zeigt der Vertrag trotzdem die Nummer.
        with SessionLocal() as db:
            db.execute(text("SELECT set_config('valeo.docflow_wartung', 'loeschen', true)"))
            db.execute(text("UPDATE domain_docflow.document_headers SET supplier_id = :neu WHERE id = :id"),
                       {"neu": lieferant_id, "id": satz["ek-rechnung-2"]["id"]})
            db.commit()
        assert _lies(satz, "ek-rechnung-2").partner == bv.Partner(
            rolle="lieferant", nummer="REF-LIEFERANT", name="Agrarhandel Referenz GmbH")
    finally:
        with SessionLocal() as db:
            db.execute(text("DELETE FROM domain_crm.customers WHERE tenant_id = :t"), {"t": fremd})
            db.execute(text("DELETE FROM domain_shared.tenants WHERE id = :t"), {"t": fremd})
            db.commit()


def test_anhaenge_kommen_mit_version_und_stand_und_nur_die_des_belegs(satz):
    rechnung, andere = satz["ek-rechnung-1"]["id"], satz["ek-rechnung-2"]["id"]
    assert _lies(satz, "ek-rechnung-1").dokumente == []
    with SessionLocal() as db:
        for header, art, datei, version, stand in (
            (rechnung, "pdf", "rechnung-lieferant.pdf", 1, "entwurf"),
            (rechnung, "pdf", "rechnung-lieferant-korrigiert.pdf", 2, "freigegeben"),
            (rechnung, "xml", None, 1, "entwurf"),
            (andere, "pdf", "andere.pdf", 1, "entwurf"),
        ):
            db.execute(text(
                "INSERT INTO domain_docflow.document_artifacts "
                "(id, tenant_id, header_id, artifact_type, content_hash_sha256, storage_key, file_name, version, freigabe_status) "
                "VALUES (:id, :t, :h, :art, :hash, :sk, :datei, :v, :stand)"),
                {"id": str(uuid.uuid4()), "t": satz["mandant"], "h": header, "art": art, "hash": "0" * 64,
                 "sk": f"test/{uuid.uuid4().hex}", "datei": datei, "v": version, "stand": stand})
        db.commit()
    dokumente = _lies(satz, "ek-rechnung-1").dokumente
    assert [(d.art, d.bezeichnung, d.version, d.stand, d.aktuell) for d in dokumente] == [
        ("pdf", "rechnung-lieferant.pdf", 1, "entwurf", False),
        ("pdf", "rechnung-lieferant-korrigiert.pdf", 2, "freigegeben", True),
        ("xml", "xml", 1, "entwurf", True),
    ]
    assert all(d.datum is not None for d in dokumente)
    assert [d.bezeichnung for d in _lies(satz, "ek-rechnung-2").dokumente] == ["andere.pdf"]
