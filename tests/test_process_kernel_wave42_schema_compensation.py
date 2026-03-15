"""
Wave 42 — Schema Registry & Process Compensation Contracts
Exactly 60 deterministic pytest tests (no mocking, no DB, no server).

Modules under test:
  app/core/domain_event_schema_registry.py      (tests 1-30)
  app/core/process_compensation_contracts.py    (tests 31-60)
"""

from __future__ import annotations

import datetime

from app.core.domain_event_schema_registry import (
    EventSchemaEintrag,
    EventSchemaStatus,
    KompatibilitaetsPruefung,
    KompatibilitaetsTyp,
    finde_aktives_schema,
    get_default_event_schemas,
    pruefe_schema_kompatibilitaet,
)
from app.core.process_compensation_contracts import (
    KompensationsKette,
    KompensationsSchritt,
    KompensationsStatus,
    KompensationsTyp,
    SagaDefinition,
    SagaStatus,
    erstelle_kompensations_kette,
    get_default_saga_definitionen,
)


# ===========================================================================
# Helpers (not test_ prefixed — not collected by pytest)
# ===========================================================================

_SENTINEL = object()


def _schema(
    schema_id="ES-T01",
    event_typ="test.event",
    version="1.0.0",
    status=EventSchemaStatus.AKTIV,
    payload_felder=_SENTINEL,
    pflicht_felder=_SENTINEL,
    tenant_id="",
) -> EventSchemaEintrag:
    return EventSchemaEintrag(
        schema_id=schema_id,
        event_typ=event_typ,
        version=version,
        status=status,
        payload_felder=["feld_a", "feld_b"] if payload_felder is _SENTINEL else payload_felder,
        pflicht_felder=["feld_a"] if pflicht_felder is _SENTINEL else pflicht_felder,
        tenant_id=tenant_id,
    )


def _schritt(
    schritt_id="WF-001-KS-001",
    workflow_instanz_id="WF-001",
    reihenfolge=1,
    status=KompensationsStatus.AUSSTEHEND,
    kompensations_typ=KompensationsTyp.RUECKGAENGIG,
) -> KompensationsSchritt:
    return KompensationsSchritt(
        schritt_id=schritt_id,
        workflow_instanz_id=workflow_instanz_id,
        aktion_id="AKTION-1",
        kompensations_aktion="Storno",
        kompensations_typ=kompensations_typ,
        reihenfolge=reihenfolge,
        status=status,
    )


def _kette(schritte=None) -> KompensationsKette:
    return KompensationsKette(
        kette_id="KK-WF-001",
        workflow_instanz_id="WF-001",
        tenant_id="T1",
        ausgeloest_am=datetime.datetime(2026, 3, 1),
        schritte=schritte or [],
    )


# ===========================================================================
# MODULE 1: domain_event_schema_registry  (30 tests)
# ===========================================================================

# 1 — EventSchemaStatus enum values
def test_schema_status_enum_values():
    assert EventSchemaStatus.ENTWURF.value == "ENTWURF"
    assert EventSchemaStatus.AKTIV.value == "AKTIV"
    assert EventSchemaStatus.VERALTET.value == "VERALTET"
    assert EventSchemaStatus.ARCHIVIERT.value == "ARCHIVIERT"


# 2 — EventSchemaStatus has exactly 4 members
def test_schema_status_enum_count():
    assert len(EventSchemaStatus) == 4


# 3 — KompatibilitaetsTyp enum values
def test_kompatibilitaets_typ_enum_values():
    assert KompatibilitaetsTyp.VOLL.value == "VOLL"
    assert KompatibilitaetsTyp.ERWEITERUNG.value == "ERWEITERUNG"
    assert KompatibilitaetsTyp.BREAKING.value == "BREAKING"
    assert KompatibilitaetsTyp.UNBEKANNT.value == "UNBEKANNT"


# 4 — KompatibilitaetsTyp has exactly 4 members
def test_kompatibilitaets_typ_enum_count():
    assert len(KompatibilitaetsTyp) == 4


# 5 — EventSchemaEintrag field defaults
def test_schema_eintrag_field_defaults():
    s = EventSchemaEintrag(schema_id="X", event_typ="e", version="1.0.0", status=EventSchemaStatus.AKTIV)
    assert s.payload_felder == []
    assert s.pflicht_felder == []
    assert s.tenant_id == ""
    assert s.beschreibung == ""


# 6 — erstellt_am default is a datetime
def test_schema_eintrag_erstellt_am_is_datetime():
    s = _schema()
    assert isinstance(s.erstellt_am, datetime.datetime)


# 7 — ist_aktiv True for AKTIV
def test_schema_ist_aktiv_true():
    assert _schema(status=EventSchemaStatus.AKTIV).ist_aktiv is True


# 8 — ist_aktiv False for VERALTET
def test_schema_ist_aktiv_false_veraltet():
    assert _schema(status=EventSchemaStatus.VERALTET).ist_aktiv is False


# 9 — ist_aktiv False for ENTWURF
def test_schema_ist_aktiv_false_entwurf():
    assert _schema(status=EventSchemaStatus.ENTWURF).ist_aktiv is False


# 10 — ist_aktiv False for ARCHIVIERT
def test_schema_ist_aktiv_false_archiviert():
    assert _schema(status=EventSchemaStatus.ARCHIVIERT).ist_aktiv is False


# 11 — versions_hash is 12 hex characters
def test_versions_hash_length_and_hex():
    h = _schema().versions_hash
    assert len(h) == 12
    int(h, 16)  # raises ValueError if not valid hex


# 12 — versions_hash is deterministic
def test_versions_hash_deterministic():
    assert _schema(payload_felder=["x", "y"]).versions_hash == _schema(payload_felder=["x", "y"]).versions_hash


# 13 — versions_hash is field-order-independent
def test_versions_hash_field_order_independent():
    assert _schema(payload_felder=["x", "y"]).versions_hash == _schema(payload_felder=["y", "x"]).versions_hash


# 14 — versions_hash changes with different version string
def test_versions_hash_changes_with_version():
    assert _schema(version="1.0.0").versions_hash != _schema(version="2.0.0").versions_hash


# 15 — validiere_payload: all pflicht_felder present → (True, [])
def test_validiere_payload_all_present():
    s = _schema(pflicht_felder=["a", "b"])
    ok, missing = s.validiere_payload({"a": 1, "b": 2, "extra": 3})
    assert ok is True and missing == []


# 16 — validiere_payload: one missing → (False, ["b"])
def test_validiere_payload_one_missing():
    s = _schema(pflicht_felder=["a", "b"])
    ok, missing = s.validiere_payload({"a": 1})
    assert ok is False and "b" in missing


# 17 — validiere_payload: empty payload, empty pflicht_felder → (True, [])
def test_validiere_payload_empty_pflicht_felder():
    s = _schema(pflicht_felder=[])
    ok, missing = s.validiere_payload({})
    assert ok is True and missing == []


# 18 — as_dict contains feld_anzahl
def test_as_dict_feld_anzahl():
    d = _schema(payload_felder=["a", "b", "c"]).as_dict()
    assert d["feld_anzahl"] == 3


# 19 — as_dict contains pflicht_anzahl
def test_as_dict_pflicht_anzahl():
    d = _schema(pflicht_felder=["a"]).as_dict()
    assert d["pflicht_anzahl"] == 1


# 20 — as_dict contains versions_hash (12 chars)
def test_as_dict_versions_hash_present():
    d = _schema().as_dict()
    assert "versions_hash" in d and len(d["versions_hash"]) == 12


# 21 — as_dict contains ist_aktiv
def test_as_dict_ist_aktiv_present():
    assert _schema(status=EventSchemaStatus.AKTIV).as_dict()["ist_aktiv"] is True


# 22 — KompatibilitaetsPruefung ist_kompatibel for VOLL
def test_pruefung_ist_kompatibel_voll():
    assert KompatibilitaetsPruefung("A", "B", KompatibilitaetsTyp.VOLL).ist_kompatibel is True


# 23 — KompatibilitaetsPruefung ist_kompatibel for ERWEITERUNG
def test_pruefung_ist_kompatibel_erweiterung():
    assert KompatibilitaetsPruefung("A", "B", KompatibilitaetsTyp.ERWEITERUNG).ist_kompatibel is True


# 24 — KompatibilitaetsPruefung not kompatibel for BREAKING
def test_pruefung_nicht_kompatibel_breaking():
    assert KompatibilitaetsPruefung("A", "B", KompatibilitaetsTyp.BREAKING).ist_kompatibel is False


# 25 — pruefe_schema_kompatibilitaet: identical fields → VOLL with 1 message
def test_pruefe_kompatibilitaet_voll():
    von = _schema(schema_id="V", payload_felder=["a", "b"])
    zu = _schema(schema_id="Z", payload_felder=["a", "b"])
    r = pruefe_schema_kompatibilitaet(von, zu)
    assert r.kompatibilitaets_typ == KompatibilitaetsTyp.VOLL
    assert r.fehlende_felder == [] and r.neue_felder == []
    assert len(r.nachrichten) == 1


# 26 — pruefe_schema_kompatibilitaet: superset → ERWEITERUNG, no fehlende
def test_pruefe_kompatibilitaet_erweiterung():
    von = _schema(schema_id="V", payload_felder=["a", "b"])
    zu = _schema(schema_id="Z", payload_felder=["a", "b", "c"])
    r = pruefe_schema_kompatibilitaet(von, zu)
    assert r.kompatibilitaets_typ == KompatibilitaetsTyp.ERWEITERUNG
    assert r.fehlende_felder == [] and "c" in r.neue_felder


# 27 — pruefe_schema_kompatibilitaet: removed fields → BREAKING
def test_pruefe_kompatibilitaet_breaking_removed():
    von = _schema(schema_id="V", payload_felder=["a", "b", "c"])
    zu = _schema(schema_id="Z", payload_felder=["a", "b"])
    r = pruefe_schema_kompatibilitaet(von, zu)
    assert r.kompatibilitaets_typ == KompatibilitaetsTyp.BREAKING
    assert "c" in r.fehlende_felder


# 28 — pruefe_schema_kompatibilitaet: removed + added → BREAKING, 2 messages
def test_pruefe_kompatibilitaet_breaking_with_additions():
    von = _schema(schema_id="V", payload_felder=["a", "b"])
    zu = _schema(schema_id="Z", payload_felder=["a", "d"])
    r = pruefe_schema_kompatibilitaet(von, zu)
    assert r.kompatibilitaets_typ == KompatibilitaetsTyp.BREAKING
    assert len(r.nachrichten) == 2


# 29 — finde_aktives_schema: picks AKTIV schema, tenant preferred over global
def test_finde_aktives_schema_tenant_over_global():
    schemata = [
        _schema(schema_id="GLOBAL", tenant_id=""),
        _schema(schema_id="TENANT", tenant_id="T1"),
    ]
    r = finde_aktives_schema("test.event", schemata, tenant_id="T1")
    assert r.schema_id == "TENANT"


# 30 — get_default_event_schemas: 6 schemas, ES-001 VERALTET, ES-002 AKTIV v2, ES-006 ENTWURF
def test_default_event_schemas_structure():
    schemas = {s.schema_id: s for s in get_default_event_schemas()}
    assert len(schemas) == 6
    assert schemas["ES-001"].status == EventSchemaStatus.VERALTET
    assert schemas["ES-002"].status == EventSchemaStatus.AKTIV
    assert schemas["ES-002"].version == "2.0.0"
    assert schemas["ES-006"].status == EventSchemaStatus.ENTWURF
    # payload_felder counts per spec
    assert len(schemas["ES-001"].payload_felder) == 4
    assert len(schemas["ES-002"].payload_felder) == 6
    assert len(schemas["ES-003"].payload_felder) == 6
    assert len(schemas["ES-004"].payload_felder) == 5
    assert len(schemas["ES-005"].payload_felder) == 5
    assert len(schemas["ES-006"].payload_felder) == 7
    # pflicht_felder counts per spec
    assert len(schemas["ES-001"].pflicht_felder) == 3
    assert len(schemas["ES-002"].pflicht_felder) == 4
    assert len(schemas["ES-003"].pflicht_felder) == 4
    assert len(schemas["ES-004"].pflicht_felder) == 4
    assert len(schemas["ES-005"].pflicht_felder) == 3
    assert len(schemas["ES-006"].pflicht_felder) == 4


# ===========================================================================
# MODULE 2: process_compensation_contracts  (30 tests)
# ===========================================================================

# 31 — KompensationsStatus enum values
def test_kompensations_status_enum_values():
    assert KompensationsStatus.AUSSTEHEND.value == "AUSSTEHEND"
    assert KompensationsStatus.LAUFEND.value == "LAUFEND"
    assert KompensationsStatus.ABGESCHLOSSEN.value == "ABGESCHLOSSEN"
    assert KompensationsStatus.FEHLGESCHLAGEN.value == "FEHLGESCHLAGEN"
    assert KompensationsStatus.NICHT_ERFORDERLICH.value == "NICHT_ERFORDERLICH"


# 32 — KompensationsStatus has exactly 5 members
def test_kompensations_status_count():
    assert len(KompensationsStatus) == 5


# 33 — KompensationsTyp enum values
def test_kompensations_typ_enum_values():
    assert KompensationsTyp.RUECKGAENGIG.value == "RUECKGAENGIG"
    assert KompensationsTyp.AUSGLEICH.value == "AUSGLEICH"
    assert KompensationsTyp.BENACHRICHTIGUNG.value == "BENACHRICHTIGUNG"
    assert KompensationsTyp.MANUELL.value == "MANUELL"


# 34 — KompensationsTyp has exactly 4 members
def test_kompensations_typ_count():
    assert len(KompensationsTyp) == 4


# 35 — SagaStatus enum values
def test_saga_status_enum_values():
    assert SagaStatus.AKTIV.value == "AKTIV"
    assert SagaStatus.KOMPENSIEREND.value == "KOMPENSIEREND"
    assert SagaStatus.ABGESCHLOSSEN.value == "ABGESCHLOSSEN"
    assert SagaStatus.FEHLGESCHLAGEN.value == "FEHLGESCHLAGEN"


# 36 — SagaStatus has exactly 4 members
def test_saga_status_count():
    assert len(SagaStatus) == 4


# 37 — KompensationsSchritt ist_abgeschlossen True for ABGESCHLOSSEN
def test_schritt_ist_abgeschlossen_abgeschlossen():
    assert _schritt(status=KompensationsStatus.ABGESCHLOSSEN).ist_abgeschlossen is True


# 38 — KompensationsSchritt ist_abgeschlossen True for NICHT_ERFORDERLICH
def test_schritt_ist_abgeschlossen_nicht_erforderlich():
    assert _schritt(status=KompensationsStatus.NICHT_ERFORDERLICH).ist_abgeschlossen is True


# 39 — KompensationsSchritt ist_abgeschlossen False for AUSSTEHEND
def test_schritt_ist_abgeschlossen_false_ausstehend():
    assert _schritt(status=KompensationsStatus.AUSSTEHEND).ist_abgeschlossen is False


# 40 — KompensationsSchritt ist_abgeschlossen False for LAUFEND
def test_schritt_ist_abgeschlossen_false_laufend():
    assert _schritt(status=KompensationsStatus.LAUFEND).ist_abgeschlossen is False


# 41 — KompensationsSchritt ist_abgeschlossen False for FEHLGESCHLAGEN
def test_schritt_ist_abgeschlossen_false_fehlgeschlagen():
    assert _schritt(status=KompensationsStatus.FEHLGESCHLAGEN).ist_abgeschlossen is False


# 42 — KompensationsSchritt as_dict includes ist_abgeschlossen
def test_schritt_as_dict_ist_abgeschlossen():
    d = _schritt(status=KompensationsStatus.ABGESCHLOSSEN).as_dict()
    assert d["ist_abgeschlossen"] is True


# 43 — KompensationsSchritt as_dict ausgefuehrt_am is None when not set
def test_schritt_as_dict_ausgefuehrt_am_none():
    assert _schritt().as_dict()["ausgefuehrt_am"] is None


# 44 — KompensationsSchritt as_dict ausgefuehrt_am is ISO string when set
def test_schritt_as_dict_ausgefuehrt_am_iso():
    ts = datetime.datetime(2026, 3, 10, 12, 0, 0)
    s = _schritt()
    s.ausgefuehrt_am = ts
    assert s.as_dict()["ausgefuehrt_am"] == ts.isoformat()


# 45 — KompensationsKette ist_vollstaendig True for empty schritte
def test_kette_ist_vollstaendig_empty():
    assert _kette().ist_vollstaendig is True


# 46 — KompensationsKette ist_vollstaendig True when all ABGESCHLOSSEN
def test_kette_ist_vollstaendig_all_done():
    schritte = [_schritt(schritt_id=f"S{i}", reihenfolge=i, status=KompensationsStatus.ABGESCHLOSSEN) for i in (1, 2)]
    assert _kette(schritte).ist_vollstaendig is True


# 47 — KompensationsKette ist_vollstaendig False when any AUSSTEHEND
def test_kette_ist_nicht_vollstaendig_with_ausstehend():
    schritte = [
        _schritt(schritt_id="S1", reihenfolge=1, status=KompensationsStatus.ABGESCHLOSSEN),
        _schritt(schritt_id="S2", reihenfolge=2, status=KompensationsStatus.AUSSTEHEND),
    ]
    assert _kette(schritte).ist_vollstaendig is False


# 48 — KompensationsKette naechster_schritt picks max reihenfolge among AUSSTEHEND
def test_kette_naechster_schritt_max_reihenfolge():
    schritte = [
        _schritt(schritt_id="S1", reihenfolge=1, status=KompensationsStatus.AUSSTEHEND),
        _schritt(schritt_id="S2", reihenfolge=2, status=KompensationsStatus.AUSSTEHEND),
        _schritt(schritt_id="S3", reihenfolge=3, status=KompensationsStatus.ABGESCHLOSSEN),
    ]
    assert _kette(schritte).naechster_schritt.schritt_id == "S2"


# 49 — KompensationsKette naechster_schritt None when all done
def test_kette_naechster_schritt_none_when_done():
    assert _kette([_schritt(status=KompensationsStatus.ABGESCHLOSSEN)]).naechster_schritt is None


# 50 — KompensationsKette fehlgeschlagene_schritte is empty when none failed
def test_kette_fehlgeschlagene_empty():
    assert _kette([_schritt(status=KompensationsStatus.AUSSTEHEND)]).fehlgeschlagene_schritte == []


# 51 — KompensationsKette fehlgeschlagene_schritte detects FEHLGESCHLAGEN
def test_kette_fehlgeschlagene_detected():
    schritte = [
        _schritt(schritt_id="S1", status=KompensationsStatus.ABGESCHLOSSEN),
        _schritt(schritt_id="S2", status=KompensationsStatus.FEHLGESCHLAGEN),
    ]
    assert len(_kette(schritte).fehlgeschlagene_schritte) == 1


# 52 — KompensationsKette saga_status ABGESCHLOSSEN when all done, no failures
def test_kette_saga_status_abgeschlossen():
    schritte = [_schritt(schritt_id=f"S{i}", reihenfolge=i, status=KompensationsStatus.ABGESCHLOSSEN) for i in (1, 2)]
    assert _kette(schritte).saga_status == SagaStatus.ABGESCHLOSSEN


# 53 — KompensationsKette saga_status FEHLGESCHLAGEN when any failed
def test_kette_saga_status_fehlgeschlagen():
    assert _kette([_schritt(status=KompensationsStatus.FEHLGESCHLAGEN)]).saga_status == SagaStatus.FEHLGESCHLAGEN


# 54 — KompensationsKette saga_status KOMPENSIEREND when any LAUFEND
def test_kette_saga_status_kompensierend():
    assert _kette([_schritt(status=KompensationsStatus.LAUFEND)]).saga_status == SagaStatus.KOMPENSIEREND


# 55 — KompensationsKette saga_status AKTIV when all AUSSTEHEND
def test_kette_saga_status_aktiv():
    assert _kette([_schritt(status=KompensationsStatus.AUSSTEHEND)]).saga_status == SagaStatus.AKTIV


# 56 — KompensationsKette as_dict contains schritte_anzahl, ist_vollstaendig, fehlgeschlagene_anzahl, saga_status
def test_kette_as_dict_structure():
    d = _kette().as_dict()
    assert d["schritte_anzahl"] == 0
    assert d["ist_vollstaendig"] is True
    assert d["fehlgeschlagene_anzahl"] == 0
    assert "saga_status" in d


# 57 — SagaDefinition as_dict contains schritte_anzahl
def test_saga_definition_as_dict_schritte_anzahl():
    saga = SagaDefinition(
        saga_id="S1", saga_name="Test", workflow_typ="test",
        schritte_vorlage=[{"aktion_id": "A", "kompensations_aktion": "B", "typ": "RUECKGAENGIG"}],
    )
    assert saga.as_dict()["schritte_anzahl"] == 1


# 58 — erstelle_kompensations_kette: kette_id, schritt_ids, reihenfolge, status, tenant
def test_erstelle_kette_basic_structure():
    saga = get_default_saga_definitionen()[0]
    kette = erstelle_kompensations_kette("WF-42", saga, "T1")
    assert kette.kette_id == "KK-WF-42"
    assert kette.tenant_id == "T1"
    assert kette.schritte[0].schritt_id == "WF-42-KS-001"
    assert kette.schritte[0].reihenfolge == 1
    for s in kette.schritte:
        assert s.status == KompensationsStatus.AUSSTEHEND


# 59 — get_default_saga_definitionen: 3 sagas with correct IDs and workflow_typ
def test_default_saga_definitionen_ids_and_workflow_typen():
    sagas = {s.saga_id: s for s in get_default_saga_definitionen()}
    assert len(sagas) == 3
    assert sagas["SAGA-001"].workflow_typ == "kontrakt_annahme"
    assert sagas["SAGA-002"].workflow_typ == "settlement_freigabe"
    assert sagas["SAGA-003"].workflow_typ == "ap_approval"
    assert len(sagas["SAGA-001"].schritte_vorlage) == 4
    assert len(sagas["SAGA-002"].schritte_vorlage) == 3
    assert len(sagas["SAGA-003"].schritte_vorlage) == 3


# 60 — default sagas: Typ-Sequenzen korrekt
def test_default_saga_typ_sequenzen():
    sagas = {s.saga_id: s for s in get_default_saga_definitionen()}

    s001_typen = [v["typ"] for v in sagas["SAGA-001"].schritte_vorlage]
    assert s001_typen == [
        KompensationsTyp.RUECKGAENGIG.value,
        KompensationsTyp.AUSGLEICH.value,
        KompensationsTyp.RUECKGAENGIG.value,
        KompensationsTyp.BENACHRICHTIGUNG.value,
    ]

    s002_typen = [v["typ"] for v in sagas["SAGA-002"].schritte_vorlage]
    assert s002_typen == [
        KompensationsTyp.AUSGLEICH.value,
        KompensationsTyp.AUSGLEICH.value,
        KompensationsTyp.MANUELL.value,
    ]

    s003_typen = [v["typ"] for v in sagas["SAGA-003"].schritte_vorlage]
    assert s003_typen == [
        KompensationsTyp.RUECKGAENGIG.value,
        KompensationsTyp.AUSGLEICH.value,
        KompensationsTyp.BENACHRICHTIGUNG.value,
    ]
