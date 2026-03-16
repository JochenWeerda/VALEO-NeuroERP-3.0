"""
Wave 58: Process Cost Allocation + Workflow Audit Trail Contracts
130+ tests covering both modules and FastAPI endpoints.
"""
import dataclasses
import pytest
from datetime import datetime, timedelta

# ─────────────────────────────────────────────
# Imports — Cost Allocation
# ─────────────────────────────────────────────
from app.core.process_cost_allocation_contracts import (
    KostenTyp,
    AllokationsMethode,
    KostenStatus,
    KostenPosition,
    KostenAllokation,
    verteile_kosten,
    get_default_kosten_allokationen,
)

# ─────────────────────────────────────────────
# Imports — Audit Trail
# ─────────────────────────────────────────────
from app.core.workflow_audit_trail_contracts import (
    AuditAktionsTyp,
    AuditIntegritaetsStatus,
    AuditEintrag,
    AuditTrail,
    erstelle_audit_eintrag,
    get_default_audit_trail,
)


# ═══════════════════════════════════════════════════════════════════
# SECTION 1 — KostenTyp / AllokationsMethode / KostenStatus Enums
# ═══════════════════════════════════════════════════════════════════

class TestKostenEnums:
    def test_kosten_typ_personal(self):
        assert KostenTyp.PERSONAL == "PERSONAL"

    def test_kosten_typ_system(self):
        assert KostenTyp.SYSTEM == "SYSTEM"

    def test_kosten_typ_extern(self):
        assert KostenTyp.EXTERN == "EXTERN"

    def test_kosten_typ_overhead(self):
        assert KostenTyp.OVERHEAD == "OVERHEAD"

    def test_kosten_typ_count(self):
        assert len(KostenTyp) == 4

    def test_allokations_methode_direkt(self):
        assert AllokationsMethode.DIREKT == "DIREKT"

    def test_allokations_methode_anteilig(self):
        assert AllokationsMethode.ANTEILIG == "ANTEILIG"

    def test_allokations_methode_gleich(self):
        assert AllokationsMethode.GLEICH == "GLEICH"

    def test_allokations_methode_gewichtet(self):
        assert AllokationsMethode.GEWICHTET == "GEWICHTET"

    def test_allokations_methode_count(self):
        assert len(AllokationsMethode) == 4

    def test_kosten_status_geplant(self):
        assert KostenStatus.GEPLANT == "GEPLANT"

    def test_kosten_status_gebucht(self):
        assert KostenStatus.GEBUCHT == "GEBUCHT"

    def test_kosten_status_storniert(self):
        assert KostenStatus.STORNIERT == "STORNIERT"

    def test_kosten_status_count(self):
        assert len(KostenStatus) == 3


# ═══════════════════════════════════════════════════════════════════
# SECTION 2 — KostenPosition dataclass
# ═══════════════════════════════════════════════════════════════════

class TestKostenPosition:
    def test_create_minimal(self):
        kp = KostenPosition("KP-X", KostenTyp.PERSONAL, 100.0)
        assert kp.position_id == "KP-X"
        assert kp.kosten_typ == KostenTyp.PERSONAL
        assert kp.betrag == 100.0

    def test_default_waehrung(self):
        kp = KostenPosition("KP-X", KostenTyp.SYSTEM, 50.0)
        assert kp.waehrung == "EUR"

    def test_default_status(self):
        kp = KostenPosition("KP-X", KostenTyp.OVERHEAD, 20.0)
        assert kp.status == KostenStatus.GEPLANT

    def test_default_beschreibung(self):
        kp = KostenPosition("KP-X", KostenTyp.EXTERN, 10.0)
        assert kp.beschreibung == ""

    def test_full_construction(self):
        kp = KostenPosition("KP-1", KostenTyp.EXTERN, 99.5, "USD", "Extern", KostenStatus.GEBUCHT)
        assert kp.waehrung == "USD"
        assert kp.beschreibung == "Extern"
        assert kp.status == KostenStatus.GEBUCHT

    def test_storniert_status(self):
        kp = KostenPosition("KP-S", KostenTyp.OVERHEAD, 75.0, "EUR", "", KostenStatus.STORNIERT)
        assert kp.status == KostenStatus.STORNIERT


# ═══════════════════════════════════════════════════════════════════
# SECTION 3 — KostenAllokation.gesamtkosten()
# ═══════════════════════════════════════════════════════════════════

class TestKostenAllokationGesamtkosten:
    def _make_allokation(self, anteil=1.0):
        return KostenAllokation("KA-T", "WI-T", "KST-T", [], AllokationsMethode.DIREKT, anteil)

    def test_empty_positionen(self):
        a = self._make_allokation()
        assert a.gesamtkosten() == 0.0

    def test_single_gebucht(self):
        a = self._make_allokation()
        a.positionen = [KostenPosition("KP-1", KostenTyp.PERSONAL, 100.0, status=KostenStatus.GEBUCHT)]
        assert a.gesamtkosten() == 100.0

    def test_storniert_excluded(self):
        a = self._make_allokation()
        a.positionen = [
            KostenPosition("KP-1", KostenTyp.PERSONAL, 100.0, status=KostenStatus.GEBUCHT),
            KostenPosition("KP-2", KostenTyp.EXTERN, 50.0, status=KostenStatus.STORNIERT),
        ]
        assert a.gesamtkosten() == 100.0

    def test_anteil_applied(self):
        a = self._make_allokation(anteil=0.5)
        a.positionen = [KostenPosition("KP-1", KostenTyp.PERSONAL, 200.0, status=KostenStatus.GEBUCHT)]
        assert a.gesamtkosten() == 100.0

    def test_anteil_0_6(self):
        a = self._make_allokation(anteil=0.6)
        a.positionen = [
            KostenPosition("KP-1", KostenTyp.PERSONAL, 200.0, status=KostenStatus.GEBUCHT),
            KostenPosition("KP-2", KostenTyp.OVERHEAD, 40.0, status=KostenStatus.GEPLANT),
        ]
        assert abs(a.gesamtkosten() - 144.0) < 0.001

    def test_anteil_1_0_full_sum(self):
        a = self._make_allokation(anteil=1.0)
        a.positionen = [
            KostenPosition("KP-1", KostenTyp.PERSONAL, 120.0, status=KostenStatus.GEBUCHT),
            KostenPosition("KP-2", KostenTyp.SYSTEM, 15.0, status=KostenStatus.GEBUCHT),
        ]
        assert a.gesamtkosten() == 135.0

    def test_multiple_storniert(self):
        a = self._make_allokation()
        a.positionen = [
            KostenPosition("KP-1", KostenTyp.PERSONAL, 100.0, status=KostenStatus.STORNIERT),
            KostenPosition("KP-2", KostenTyp.SYSTEM, 50.0, status=KostenStatus.STORNIERT),
        ]
        assert a.gesamtkosten() == 0.0

    def test_geplant_included(self):
        a = self._make_allokation()
        a.positionen = [
            KostenPosition("KP-1", KostenTyp.PERSONAL, 80.0, status=KostenStatus.GEPLANT),
        ]
        assert a.gesamtkosten() == 80.0

    def test_anteil_zero(self):
        a = self._make_allokation(anteil=0.0)
        a.positionen = [KostenPosition("KP-1", KostenTyp.PERSONAL, 500.0, status=KostenStatus.GEBUCHT)]
        assert a.gesamtkosten() == 0.0

    def test_mixed_statuses(self):
        a = self._make_allokation(anteil=1.0)
        a.positionen = [
            KostenPosition("KP-1", KostenTyp.PERSONAL, 100.0, status=KostenStatus.GEBUCHT),
            KostenPosition("KP-2", KostenTyp.OVERHEAD, 60.0, status=KostenStatus.GEPLANT),
            KostenPosition("KP-3", KostenTyp.EXTERN, 40.0, status=KostenStatus.STORNIERT),
        ]
        assert a.gesamtkosten() == 160.0


# ═══════════════════════════════════════════════════════════════════
# SECTION 4 — KostenAllokation.kosten_nach_typ()
# ═══════════════════════════════════════════════════════════════════

class TestKostenNachTyp:
    def _make_allokation(self, anteil=1.0):
        return KostenAllokation("KA-T", "WI-T", "KST-T", [], AllokationsMethode.DIREKT, anteil)

    def test_all_types_present_empty(self):
        a = self._make_allokation()
        result = a.kosten_nach_typ()
        for typ in KostenTyp:
            assert typ in result

    def test_all_types_zero_on_empty(self):
        a = self._make_allokation()
        result = a.kosten_nach_typ()
        assert all(v == 0.0 for v in result.values())

    def test_personal_accumulation(self):
        a = self._make_allokation()
        a.positionen = [
            KostenPosition("KP-1", KostenTyp.PERSONAL, 100.0, status=KostenStatus.GEBUCHT),
            KostenPosition("KP-2", KostenTyp.PERSONAL, 50.0, status=KostenStatus.GEBUCHT),
        ]
        result = a.kosten_nach_typ()
        assert result[KostenTyp.PERSONAL] == 150.0

    def test_storniert_excluded_per_typ(self):
        a = self._make_allokation()
        a.positionen = [
            KostenPosition("KP-1", KostenTyp.PERSONAL, 100.0, status=KostenStatus.GEBUCHT),
            KostenPosition("KP-2", KostenTyp.PERSONAL, 50.0, status=KostenStatus.STORNIERT),
        ]
        result = a.kosten_nach_typ()
        assert result[KostenTyp.PERSONAL] == 100.0

    def test_anteil_applied_per_typ(self):
        a = self._make_allokation(anteil=0.5)
        a.positionen = [
            KostenPosition("KP-1", KostenTyp.SYSTEM, 200.0, status=KostenStatus.GEBUCHT),
        ]
        result = a.kosten_nach_typ()
        assert result[KostenTyp.SYSTEM] == 100.0

    def test_multiple_types_split(self):
        a = self._make_allokation(anteil=1.0)
        a.positionen = [
            KostenPosition("KP-1", KostenTyp.PERSONAL, 120.0, status=KostenStatus.GEBUCHT),
            KostenPosition("KP-2", KostenTyp.SYSTEM, 15.0, status=KostenStatus.GEBUCHT),
            KostenPosition("KP-3", KostenTyp.EXTERN, 50.0, status=KostenStatus.STORNIERT),
        ]
        result = a.kosten_nach_typ()
        assert result[KostenTyp.PERSONAL] == 120.0
        assert result[KostenTyp.SYSTEM] == 15.0
        assert result[KostenTyp.EXTERN] == 0.0
        assert result[KostenTyp.OVERHEAD] == 0.0

    def test_overhead_only(self):
        a = self._make_allokation(anteil=1.0)
        a.positionen = [
            KostenPosition("KP-1", KostenTyp.OVERHEAD, 80.0, status=KostenStatus.GEPLANT),
        ]
        result = a.kosten_nach_typ()
        assert result[KostenTyp.OVERHEAD] == 80.0
        assert result[KostenTyp.PERSONAL] == 0.0

    def test_returns_dict(self):
        a = self._make_allokation()
        result = a.kosten_nach_typ()
        assert isinstance(result, dict)


# ═══════════════════════════════════════════════════════════════════
# SECTION 5 — verteile_kosten()
# ═══════════════════════════════════════════════════════════════════

class TestVerteileKosten:
    def test_empty_kostenstellen(self):
        result = verteile_kosten(1000.0, [], AllokationsMethode.GLEICH)
        assert result == []

    def test_direkt_single(self):
        ks = [{"kostenstelle_id": "KST-A", "gewicht": 1.0}]
        result = verteile_kosten(300.0, ks, AllokationsMethode.DIREKT)
        assert len(result) == 1
        assert result[0]["anteil"] == 1.0
        assert result[0]["betrag"] == 300.0
        assert result[0]["kostenstelle_id"] == "KST-A"

    def test_direkt_multiple_first_gets_all(self):
        ks = [
            {"kostenstelle_id": "KST-A", "gewicht": 1.0},
            {"kostenstelle_id": "KST-B", "gewicht": 1.0},
            {"kostenstelle_id": "KST-C", "gewicht": 1.0},
        ]
        result = verteile_kosten(300.0, ks, AllokationsMethode.DIREKT)
        assert result[0]["anteil"] == 1.0
        assert result[0]["betrag"] == 300.0
        assert result[1]["anteil"] == 0.0
        assert result[1]["betrag"] == 0.0
        assert result[2]["anteil"] == 0.0
        assert result[2]["betrag"] == 0.0

    def test_gleich_two(self):
        ks = [{"kostenstelle_id": "KST-A"}, {"kostenstelle_id": "KST-B"}]
        result = verteile_kosten(200.0, ks, AllokationsMethode.GLEICH)
        assert abs(result[0]["anteil"] - 0.5) < 0.001
        assert abs(result[0]["betrag"] - 100.0) < 0.001
        assert abs(result[1]["anteil"] - 0.5) < 0.001
        assert abs(result[1]["betrag"] - 100.0) < 0.001

    def test_gleich_three(self):
        ks = [{"kostenstelle_id": f"KST-{i}"} for i in range(3)]
        result = verteile_kosten(300.0, ks, AllokationsMethode.GLEICH)
        for r in result:
            assert abs(r["anteil"] - 1/3) < 0.001
            assert abs(r["betrag"] - 100.0) < 0.001

    def test_gleich_single(self):
        ks = [{"kostenstelle_id": "KST-A"}]
        result = verteile_kosten(500.0, ks, AllokationsMethode.GLEICH)
        assert result[0]["anteil"] == 1.0
        assert result[0]["betrag"] == 500.0

    def test_anteilig_proportional(self):
        ks = [
            {"kostenstelle_id": "KST-A", "gewicht": 3.0},
            {"kostenstelle_id": "KST-B", "gewicht": 1.0},
        ]
        result = verteile_kosten(400.0, ks, AllokationsMethode.ANTEILIG)
        assert abs(result[0]["betrag"] - 300.0) < 0.001
        assert abs(result[1]["betrag"] - 100.0) < 0.001
        assert abs(result[0]["anteil"] - 0.75) < 0.001
        assert abs(result[1]["anteil"] - 0.25) < 0.001

    def test_gewichtet_proportional(self):
        ks = [
            {"kostenstelle_id": "KST-A", "gewicht": 2.0},
            {"kostenstelle_id": "KST-B", "gewicht": 2.0},
        ]
        result = verteile_kosten(100.0, ks, AllokationsMethode.GEWICHTET)
        assert abs(result[0]["betrag"] - 50.0) < 0.001
        assert abs(result[1]["betrag"] - 50.0) < 0.001

    def test_zero_total_gewicht(self):
        ks = [
            {"kostenstelle_id": "KST-A", "gewicht": 0.0},
            {"kostenstelle_id": "KST-B", "gewicht": 0.0},
        ]
        result = verteile_kosten(300.0, ks, AllokationsMethode.ANTEILIG)
        assert all(r["anteil"] == 0.0 for r in result)
        assert all(r["betrag"] == 0.0 for r in result)

    def test_result_has_kostenstelle_id(self):
        ks = [{"kostenstelle_id": "KST-X", "gewicht": 1.0}]
        result = verteile_kosten(100.0, ks, AllokationsMethode.DIREKT)
        assert result[0]["kostenstelle_id"] == "KST-X"

    def test_anteilig_default_gewicht(self):
        ks = [
            {"kostenstelle_id": "KST-A"},
            {"kostenstelle_id": "KST-B"},
        ]
        result = verteile_kosten(200.0, ks, AllokationsMethode.ANTEILIG)
        # default gewicht=1.0 each → equal split
        assert abs(result[0]["betrag"] - 100.0) < 0.001
        assert abs(result[1]["betrag"] - 100.0) < 0.001

    def test_direkt_returns_all_kostenstellen(self):
        ks = [{"kostenstelle_id": f"KST-{i}"} for i in range(4)]
        result = verteile_kosten(1000.0, ks, AllokationsMethode.DIREKT)
        assert len(result) == 4

    def test_gleich_anteil_sums_to_1(self):
        ks = [{"kostenstelle_id": f"KST-{i}"} for i in range(5)]
        result = verteile_kosten(500.0, ks, AllokationsMethode.GLEICH)
        assert abs(sum(r["anteil"] for r in result) - 1.0) < 0.001

    def test_anteilig_anteil_sums_to_1(self):
        ks = [
            {"kostenstelle_id": "KST-A", "gewicht": 1.0},
            {"kostenstelle_id": "KST-B", "gewicht": 2.0},
            {"kostenstelle_id": "KST-C", "gewicht": 3.0},
        ]
        result = verteile_kosten(600.0, ks, AllokationsMethode.ANTEILIG)
        assert abs(sum(r["anteil"] for r in result) - 1.0) < 0.001


# ═══════════════════════════════════════════════════════════════════
# SECTION 6 — get_default_kosten_allokationen()
# ═══════════════════════════════════════════════════════════════════

class TestDefaultKostenAllokationen:
    def setup_method(self):
        self.allokationen = get_default_kosten_allokationen()
        self.by_id = {a.allokation_id: a for a in self.allokationen}

    def test_returns_two(self):
        assert len(self.allokationen) == 2

    def test_ka_001_exists(self):
        assert "KA-001" in self.by_id

    def test_ka_002_exists(self):
        assert "KA-002" in self.by_id

    def test_ka_001_workflow_instanz(self):
        assert self.by_id["KA-001"].workflow_instanz_id == "WI-K-001"

    def test_ka_001_kostenstelle(self):
        assert self.by_id["KA-001"].kostenstelle_id == "KST-AGRAR"

    def test_ka_001_methode(self):
        assert self.by_id["KA-001"].methode == AllokationsMethode.DIREKT

    def test_ka_001_anteil(self):
        assert self.by_id["KA-001"].allokations_anteil == 1.0

    def test_ka_001_positionen_count(self):
        assert len(self.by_id["KA-001"].positionen) == 3

    def test_ka_001_gesamtkosten(self):
        # 120+15 active, 50 storniert → 135.0 * 1.0
        assert abs(self.by_id["KA-001"].gesamtkosten() - 135.0) < 0.001

    def test_ka_002_workflow_instanz(self):
        assert self.by_id["KA-002"].workflow_instanz_id == "WI-S-002"

    def test_ka_002_kostenstelle(self):
        assert self.by_id["KA-002"].kostenstelle_id == "KST-FIBU"

    def test_ka_002_methode(self):
        assert self.by_id["KA-002"].methode == AllokationsMethode.ANTEILIG

    def test_ka_002_anteil(self):
        assert abs(self.by_id["KA-002"].allokations_anteil - 0.6) < 0.001

    def test_ka_002_positionen_count(self):
        assert len(self.by_id["KA-002"].positionen) == 2

    def test_ka_002_gesamtkosten(self):
        # (200+40) * 0.6 = 144.0
        assert abs(self.by_id["KA-002"].gesamtkosten() - 144.0) < 0.001

    def test_ka_001_kp_003_storniert(self):
        kp3 = next(p for p in self.by_id["KA-001"].positionen if p.position_id == "KP-003")
        assert kp3.status == KostenStatus.STORNIERT

    def test_ka_002_no_storniert(self):
        storniert = [p for p in self.by_id["KA-002"].positionen if p.status == KostenStatus.STORNIERT]
        assert len(storniert) == 0


# ═══════════════════════════════════════════════════════════════════
# SECTION 7 — AuditAktionsTyp / AuditIntegritaetsStatus Enums
# ═══════════════════════════════════════════════════════════════════

class TestAuditEnums:
    def test_erstellt(self):
        assert AuditAktionsTyp.ERSTELLT == "ERSTELLT"

    def test_geaendert(self):
        assert AuditAktionsTyp.GEAENDERT == "GEAENDERT"

    def test_freigegeben(self):
        assert AuditAktionsTyp.FREIGEGEBEN == "FREIGEGEBEN"

    def test_abgelehnt(self):
        assert AuditAktionsTyp.ABGELEHNT == "ABGELEHNT"

    def test_geloescht(self):
        assert AuditAktionsTyp.GELOESCHT == "GELOESCHT"

    def test_exportiert(self):
        assert AuditAktionsTyp.EXPORTIERT == "EXPORTIERT"

    def test_angemeldet(self):
        assert AuditAktionsTyp.ANGEMELDET == "ANGEMELDET"

    def test_aktion_typ_count(self):
        assert len(AuditAktionsTyp) == 7

    def test_integritaet_gueltig(self):
        assert AuditIntegritaetsStatus.GUELTIG == "GUELTIG"

    def test_integritaet_ungueltig(self):
        assert AuditIntegritaetsStatus.UNGUELTIG == "UNGUELTIG"

    def test_integritaet_unbekannt(self):
        assert AuditIntegritaetsStatus.UNBEKANNT == "UNBEKANNT"


# ═══════════════════════════════════════════════════════════════════
# SECTION 8 — AuditEintrag.berechne_hash()
# ═══════════════════════════════════════════════════════════════════

class TestAuditEintragHash:
    BASE_TS = datetime(2026, 3, 16, 10, 0, 0)

    def _make_eintrag(self, **kwargs):
        defaults = dict(
            eintrag_id="AE-T",
            workflow_instanz_id="WI-T",
            aktion=AuditAktionsTyp.ERSTELLT,
            ausgefuehrt_von="user-X",
            zeitstempel=self.BASE_TS,
            nutzlast={},
            vorgaenger_hash="",
            eintrag_hash="",
        )
        defaults.update(kwargs)
        return AuditEintrag(**defaults)

    def test_hash_is_string(self):
        e = self._make_eintrag()
        assert isinstance(e.berechne_hash(), str)

    def test_hash_length_64(self):
        e = self._make_eintrag()
        assert len(e.berechne_hash()) == 64

    def test_hash_is_hex(self):
        e = self._make_eintrag()
        h = e.berechne_hash()
        int(h, 16)  # should not raise

    def test_hash_deterministic(self):
        e = self._make_eintrag()
        assert e.berechne_hash() == e.berechne_hash()

    def test_different_id_different_hash(self):
        e1 = self._make_eintrag(eintrag_id="AE-1")
        e2 = self._make_eintrag(eintrag_id="AE-2")
        assert e1.berechne_hash() != e2.berechne_hash()

    def test_different_workflow_different_hash(self):
        e1 = self._make_eintrag(workflow_instanz_id="WI-A")
        e2 = self._make_eintrag(workflow_instanz_id="WI-B")
        assert e1.berechne_hash() != e2.berechne_hash()

    def test_different_aktion_different_hash(self):
        e1 = self._make_eintrag(aktion=AuditAktionsTyp.ERSTELLT)
        e2 = self._make_eintrag(aktion=AuditAktionsTyp.GELOESCHT)
        assert e1.berechne_hash() != e2.berechne_hash()

    def test_different_user_different_hash(self):
        e1 = self._make_eintrag(ausgefuehrt_von="user-A")
        e2 = self._make_eintrag(ausgefuehrt_von="user-B")
        assert e1.berechne_hash() != e2.berechne_hash()

    def test_different_zeitstempel_different_hash(self):
        e1 = self._make_eintrag(zeitstempel=self.BASE_TS)
        e2 = self._make_eintrag(zeitstempel=self.BASE_TS + timedelta(seconds=1))
        assert e1.berechne_hash() != e2.berechne_hash()

    def test_different_vorgaenger_hash_different_hash(self):
        e1 = self._make_eintrag(vorgaenger_hash="")
        e2 = self._make_eintrag(vorgaenger_hash="abc123")
        assert e1.berechne_hash() != e2.berechne_hash()

    def test_different_nutzlast_different_hash(self):
        e1 = self._make_eintrag(nutzlast={"a": 1})
        e2 = self._make_eintrag(nutzlast={"a": 2})
        assert e1.berechne_hash() != e2.berechne_hash()

    def test_nutzlast_sort_keys_stable(self):
        e1 = self._make_eintrag(nutzlast={"b": 2, "a": 1})
        e2 = self._make_eintrag(nutzlast={"a": 1, "b": 2})
        assert e1.berechne_hash() == e2.berechne_hash()


# ═══════════════════════════════════════════════════════════════════
# SECTION 9 — AuditEintrag.ist_hash_gueltig()
# ═══════════════════════════════════════════════════════════════════

class TestAuditEintragIstHashGueltig:
    BASE_TS = datetime(2026, 3, 16, 10, 0, 0)

    def test_valid_after_erstelle(self):
        e = erstelle_audit_eintrag("AE-1", "WI-1", AuditAktionsTyp.ERSTELLT, "u", self.BASE_TS, {})
        assert e.ist_hash_gueltig() is True

    def test_invalid_after_tamper(self):
        e = erstelle_audit_eintrag("AE-1", "WI-1", AuditAktionsTyp.ERSTELLT, "u", self.BASE_TS, {})
        e = dataclasses.replace(e, eintrag_hash="tampered")
        assert e.ist_hash_gueltig() is False

    def test_invalid_empty_hash(self):
        e = erstelle_audit_eintrag("AE-1", "WI-1", AuditAktionsTyp.ERSTELLT, "u", self.BASE_TS, {})
        e = dataclasses.replace(e, eintrag_hash="")
        assert e.ist_hash_gueltig() is False

    def test_valid_with_nutzlast(self):
        e = erstelle_audit_eintrag("AE-2", "WI-1", AuditAktionsTyp.GEAENDERT, "u", self.BASE_TS, {"x": 42})
        assert e.ist_hash_gueltig() is True

    def test_invalid_after_id_change(self):
        e = erstelle_audit_eintrag("AE-1", "WI-1", AuditAktionsTyp.ERSTELLT, "u", self.BASE_TS, {})
        old_hash = e.eintrag_hash
        e2 = dataclasses.replace(e, eintrag_id="AE-CHANGED", eintrag_hash=old_hash)
        assert e2.ist_hash_gueltig() is False


# ═══════════════════════════════════════════════════════════════════
# SECTION 10 — AuditTrail.pruefe_integritaet()
# ═══════════════════════════════════════════════════════════════════

class TestAuditTrailPruefeIntegritaet:
    BASE_TS = datetime(2026, 3, 16, 10, 0, 0)

    def test_empty_trail_unbekannt(self):
        trail = AuditTrail("AT-T")
        assert trail.pruefe_integritaet() == AuditIntegritaetsStatus.UNBEKANNT

    def test_single_valid_entry(self):
        trail = AuditTrail("AT-T")
        e = erstelle_audit_eintrag("AE-1", "WI-1", AuditAktionsTyp.ERSTELLT, "u", self.BASE_TS, {})
        trail.eintraege = [e]
        assert trail.pruefe_integritaet() == AuditIntegritaetsStatus.GUELTIG

    def test_valid_two_entry_chain(self):
        trail = AuditTrail("AT-T")
        e1 = erstelle_audit_eintrag("AE-1", "WI-1", AuditAktionsTyp.ERSTELLT, "u", self.BASE_TS, {})
        e2 = erstelle_audit_eintrag("AE-2", "WI-1", AuditAktionsTyp.GEAENDERT, "u",
                                     self.BASE_TS + timedelta(minutes=1), {}, e1.eintrag_hash)
        trail.eintraege = [e1, e2]
        assert trail.pruefe_integritaet() == AuditIntegritaetsStatus.GUELTIG

    def test_first_entry_non_empty_vorgaenger_ungueltig(self):
        trail = AuditTrail("AT-T")
        e = erstelle_audit_eintrag("AE-1", "WI-1", AuditAktionsTyp.ERSTELLT, "u",
                                    self.BASE_TS, {}, "non_empty_hash")
        # manually set eintrag_hash to match (simulate correct hash but wrong chain)
        e = dataclasses.replace(e, eintrag_hash=e.berechne_hash())
        trail.eintraege = [e]
        assert trail.pruefe_integritaet() == AuditIntegritaetsStatus.UNGUELTIG

    def test_tampered_eintrag_hash_ungueltig(self):
        trail = AuditTrail("AT-T")
        e = erstelle_audit_eintrag("AE-1", "WI-1", AuditAktionsTyp.ERSTELLT, "u", self.BASE_TS, {})
        e = dataclasses.replace(e, eintrag_hash="0000tampered")
        trail.eintraege = [e]
        assert trail.pruefe_integritaet() == AuditIntegritaetsStatus.UNGUELTIG

    def test_broken_chain_link_ungueltig(self):
        trail = AuditTrail("AT-T")
        e1 = erstelle_audit_eintrag("AE-1", "WI-1", AuditAktionsTyp.ERSTELLT, "u", self.BASE_TS, {})
        # e2 references wrong vorgaenger_hash
        e2 = erstelle_audit_eintrag("AE-2", "WI-1", AuditAktionsTyp.GEAENDERT, "u",
                                     self.BASE_TS + timedelta(minutes=1), {}, "wrong_hash")
        trail.eintraege = [e1, e2]
        assert trail.pruefe_integritaet() == AuditIntegritaetsStatus.UNGUELTIG

    def test_default_trail_gueltig(self):
        trail = get_default_audit_trail()
        assert trail.pruefe_integritaet() == AuditIntegritaetsStatus.GUELTIG

    def test_three_entry_chain_gueltig(self):
        trail = AuditTrail("AT-T")
        e1 = erstelle_audit_eintrag("AE-1", "WI-1", AuditAktionsTyp.ERSTELLT, "u", self.BASE_TS, {})
        e2 = erstelle_audit_eintrag("AE-2", "WI-1", AuditAktionsTyp.GEAENDERT, "u",
                                     self.BASE_TS + timedelta(minutes=1), {}, e1.eintrag_hash)
        e3 = erstelle_audit_eintrag("AE-3", "WI-1", AuditAktionsTyp.FREIGEGEBEN, "u",
                                     self.BASE_TS + timedelta(minutes=2), {}, e2.eintrag_hash)
        trail.eintraege = [e1, e2, e3]
        assert trail.pruefe_integritaet() == AuditIntegritaetsStatus.GUELTIG

    def test_middle_entry_tampered_ungueltig(self):
        trail = AuditTrail("AT-T")
        e1 = erstelle_audit_eintrag("AE-1", "WI-1", AuditAktionsTyp.ERSTELLT, "u", self.BASE_TS, {})
        e2 = erstelle_audit_eintrag("AE-2", "WI-1", AuditAktionsTyp.GEAENDERT, "u",
                                     self.BASE_TS + timedelta(minutes=1), {}, e1.eintrag_hash)
        e3 = erstelle_audit_eintrag("AE-3", "WI-1", AuditAktionsTyp.FREIGEGEBEN, "u",
                                     self.BASE_TS + timedelta(minutes=2), {}, e2.eintrag_hash)
        # tamper e2
        e2_tampered = dataclasses.replace(e2, eintrag_hash="tampered")
        trail.eintraege = [e1, e2_tampered, e3]
        assert trail.pruefe_integritaet() == AuditIntegritaetsStatus.UNGUELTIG


# ═══════════════════════════════════════════════════════════════════
# SECTION 11 — AuditTrail.letzter_eintrag()
# ═══════════════════════════════════════════════════════════════════

class TestAuditTrailLetzterEintrag:
    BASE_TS = datetime(2026, 3, 16, 10, 0, 0)

    def test_empty_returns_none(self):
        trail = AuditTrail("AT-T")
        assert trail.letzter_eintrag() is None

    def test_single_entry_returns_it(self):
        trail = AuditTrail("AT-T")
        e = erstelle_audit_eintrag("AE-1", "WI-1", AuditAktionsTyp.ERSTELLT, "u", self.BASE_TS, {})
        trail.eintraege = [e]
        assert trail.letzter_eintrag() is e

    def test_multiple_entries_latest_zeitstempel(self):
        trail = AuditTrail("AT-T")
        e1 = erstelle_audit_eintrag("AE-1", "WI-1", AuditAktionsTyp.ERSTELLT, "u", self.BASE_TS, {})
        e2 = erstelle_audit_eintrag("AE-2", "WI-1", AuditAktionsTyp.GEAENDERT, "u",
                                     self.BASE_TS + timedelta(minutes=5), {}, e1.eintrag_hash)
        trail.eintraege = [e1, e2]
        assert trail.letzter_eintrag().eintrag_id == "AE-2"

    def test_default_trail_letzter_ae004(self):
        trail = get_default_audit_trail()
        assert trail.letzter_eintrag().eintrag_id == "AE-004"

    def test_unordered_list_still_finds_latest(self):
        trail = AuditTrail("AT-T")
        e1 = erstelle_audit_eintrag("AE-1", "WI-1", AuditAktionsTyp.ERSTELLT, "u", self.BASE_TS, {})
        e2 = erstelle_audit_eintrag("AE-2", "WI-1", AuditAktionsTyp.GEAENDERT, "u",
                                     self.BASE_TS + timedelta(hours=1), {}, e1.eintrag_hash)
        trail.eintraege = [e2, e1]  # reversed order
        assert trail.letzter_eintrag().eintrag_id == "AE-2"


# ═══════════════════════════════════════════════════════════════════
# SECTION 12 — erstelle_audit_eintrag()
# ═══════════════════════════════════════════════════════════════════

class TestErstelleAuditEintrag:
    BASE_TS = datetime(2026, 3, 16, 10, 0, 0)

    def test_fields_assigned(self):
        e = erstelle_audit_eintrag("AE-1", "WI-1", AuditAktionsTyp.ERSTELLT, "u", self.BASE_TS, {})
        assert e.eintrag_id == "AE-1"
        assert e.workflow_instanz_id == "WI-1"
        assert e.aktion == AuditAktionsTyp.ERSTELLT
        assert e.ausgefuehrt_von == "u"
        assert e.zeitstempel == self.BASE_TS

    def test_hash_computed(self):
        e = erstelle_audit_eintrag("AE-1", "WI-1", AuditAktionsTyp.ERSTELLT, "u", self.BASE_TS, {})
        assert e.eintrag_hash != ""
        assert len(e.eintrag_hash) == 64

    def test_ist_hash_gueltig_true(self):
        e = erstelle_audit_eintrag("AE-1", "WI-1", AuditAktionsTyp.ERSTELLT, "u", self.BASE_TS, {})
        assert e.ist_hash_gueltig() is True

    def test_vorgaenger_hash_stored(self):
        e = erstelle_audit_eintrag("AE-2", "WI-1", AuditAktionsTyp.GEAENDERT, "u",
                                    self.BASE_TS, {}, "prevhash123")
        assert e.vorgaenger_hash == "prevhash123"

    def test_nutzlast_stored(self):
        e = erstelle_audit_eintrag("AE-1", "WI-1", AuditAktionsTyp.ERSTELLT, "u",
                                    self.BASE_TS, {"key": "value"})
        assert e.nutzlast == {"key": "value"}

    def test_empty_vorgaenger_hash_default(self):
        e = erstelle_audit_eintrag("AE-1", "WI-1", AuditAktionsTyp.ERSTELLT, "u", self.BASE_TS, {})
        assert e.vorgaenger_hash == ""


# ═══════════════════════════════════════════════════════════════════
# SECTION 13 — get_default_audit_trail()
# ═══════════════════════════════════════════════════════════════════

class TestDefaultAuditTrail:
    def setup_method(self):
        self.trail = get_default_audit_trail()
        self.by_id = {e.eintrag_id: e for e in self.trail.eintraege}

    def test_trail_id(self):
        assert self.trail.trail_id == "AT-001"

    def test_four_eintraege(self):
        assert len(self.trail.eintraege) == 4

    def test_all_entry_ids_present(self):
        assert "AE-001" in self.by_id
        assert "AE-002" in self.by_id
        assert "AE-003" in self.by_id
        assert "AE-004" in self.by_id

    def test_ae_001_aktion(self):
        assert self.by_id["AE-001"].aktion == AuditAktionsTyp.ERSTELLT

    def test_ae_002_aktion(self):
        assert self.by_id["AE-002"].aktion == AuditAktionsTyp.GEAENDERT

    def test_ae_003_aktion(self):
        assert self.by_id["AE-003"].aktion == AuditAktionsTyp.FREIGEGEBEN

    def test_ae_004_aktion(self):
        assert self.by_id["AE-004"].aktion == AuditAktionsTyp.EXPORTIERT

    def test_ae_001_vorgaenger_hash_empty(self):
        assert self.by_id["AE-001"].vorgaenger_hash == ""

    def test_chain_link_ae001_ae002(self):
        assert self.by_id["AE-002"].vorgaenger_hash == self.by_id["AE-001"].eintrag_hash

    def test_chain_link_ae002_ae003(self):
        assert self.by_id["AE-003"].vorgaenger_hash == self.by_id["AE-002"].eintrag_hash

    def test_chain_link_ae003_ae004(self):
        assert self.by_id["AE-004"].vorgaenger_hash == self.by_id["AE-003"].eintrag_hash

    def test_integritaet_gueltig(self):
        assert self.trail.pruefe_integritaet() == AuditIntegritaetsStatus.GUELTIG

    def test_letzter_eintrag_ae004(self):
        assert self.trail.letzter_eintrag().eintrag_id == "AE-004"

    def test_all_hashes_valid(self):
        for e in self.trail.eintraege:
            assert e.ist_hash_gueltig() is True

    def test_ae_001_user(self):
        assert self.by_id["AE-001"].ausgefuehrt_von == "user-001"

    def test_ae_004_user(self):
        assert self.by_id["AE-004"].ausgefuehrt_von == "system"

    def test_ae_003_nutzlast(self):
        assert self.by_id["AE-003"].nutzlast == {"kommentar": "OK"}


# ═══════════════════════════════════════════════════════════════════
# SECTION 14 — FastAPI Endpoint Tests
# ═══════════════════════════════════════════════════════════════════

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


BASE_URL = "/api/v1/process"


class TestKostenAllokationenEndpoint:
    def test_get_returns_200(self):
        r = client.get(f"{BASE_URL}/kosten/allokationen")
        assert r.status_code == 200

    def test_get_returns_list(self):
        r = client.get(f"{BASE_URL}/kosten/allokationen")
        data = r.json()
        assert isinstance(data, list)

    def test_get_returns_two_items(self):
        r = client.get(f"{BASE_URL}/kosten/allokationen")
        assert len(r.json()) == 2

    def test_allokation_id_present(self):
        r = client.get(f"{BASE_URL}/kosten/allokationen")
        ids = [item["allokation_id"] for item in r.json()]
        assert "KA-001" in ids
        assert "KA-002" in ids

    def test_gesamtkosten_ka001(self):
        r = client.get(f"{BASE_URL}/kosten/allokationen")
        item = next(i for i in r.json() if i["allokation_id"] == "KA-001")
        assert abs(item["gesamtkosten"] - 135.0) < 0.001

    def test_gesamtkosten_ka002(self):
        r = client.get(f"{BASE_URL}/kosten/allokationen")
        item = next(i for i in r.json() if i["allokation_id"] == "KA-002")
        assert abs(item["gesamtkosten"] - 144.0) < 0.001

    def test_kosten_nach_typ_present(self):
        r = client.get(f"{BASE_URL}/kosten/allokationen")
        item = r.json()[0]
        assert "kosten_nach_typ" in item

    def test_methode_present(self):
        r = client.get(f"{BASE_URL}/kosten/allokationen")
        item = r.json()[0]
        assert "methode" in item


class TestVerteileKostenEndpoint:
    def test_gleich_split(self):
        payload = {
            "gesamt_betrag": 300.0,
            "methode": "GLEICH",
            "kostenstellen": [
                {"kostenstelle_id": "KST-A"},
                {"kostenstelle_id": "KST-B"},
                {"kostenstelle_id": "KST-C"},
            ],
        }
        r = client.post(f"{BASE_URL}/kosten/verteile", json=payload)
        assert r.status_code == 200
        data = r.json()
        assert "verteilung" in data
        assert len(data["verteilung"]) == 3

    def test_direkt_split(self):
        payload = {
            "gesamt_betrag": 100.0,
            "methode": "DIREKT",
            "kostenstellen": [
                {"kostenstelle_id": "KST-A"},
                {"kostenstelle_id": "KST-B"},
            ],
        }
        r = client.post(f"{BASE_URL}/kosten/verteile", json=payload)
        assert r.status_code == 200
        data = r.json()["verteilung"]
        assert abs(data[0]["betrag"] - 100.0) < 0.001
        assert data[1]["betrag"] == 0.0

    def test_empty_kostenstellen(self):
        payload = {"gesamt_betrag": 100.0, "methode": "GLEICH", "kostenstellen": []}
        r = client.post(f"{BASE_URL}/kosten/verteile", json=payload)
        assert r.status_code == 200
        assert r.json()["verteilung"] == []

    def test_anteilig_split(self):
        payload = {
            "gesamt_betrag": 400.0,
            "methode": "ANTEILIG",
            "kostenstellen": [
                {"kostenstelle_id": "KST-A", "gewicht": 3.0},
                {"kostenstelle_id": "KST-B", "gewicht": 1.0},
            ],
        }
        r = client.post(f"{BASE_URL}/kosten/verteile", json=payload)
        assert r.status_code == 200
        data = r.json()["verteilung"]
        assert abs(data[0]["betrag"] - 300.0) < 0.001


class TestAuditTrailEndpoint:
    def test_get_trail_200(self):
        r = client.get(f"{BASE_URL}/audit-trail/trail")
        assert r.status_code == 200

    def test_trail_id(self):
        r = client.get(f"{BASE_URL}/audit-trail/trail")
        assert r.json()["trail_id"] == "AT-001"

    def test_eintraege_anzahl(self):
        r = client.get(f"{BASE_URL}/audit-trail/trail")
        assert r.json()["eintraege_anzahl"] == 4

    def test_integritaet_gueltig(self):
        r = client.get(f"{BASE_URL}/audit-trail/trail")
        assert r.json()["integritaet"] == "GUELTIG"

    def test_letzter_eintrag_id(self):
        r = client.get(f"{BASE_URL}/audit-trail/trail")
        assert r.json()["letzter_eintrag_id"] == "AE-004"


class TestPruefeIntegritaetEndpoint:
    def test_valid_trail_gueltig(self):
        r = client.post(f"{BASE_URL}/audit-trail/pruefe-integritaet",
                        json={"trail_id": "AT-001", "manipuliert": False})
        assert r.status_code == 200
        assert r.json()["integritaet"] == "GUELTIG"

    def test_manipuliert_ungueltig(self):
        r = client.post(f"{BASE_URL}/audit-trail/pruefe-integritaet",
                        json={"trail_id": "AT-001", "manipuliert": True})
        assert r.status_code == 200
        assert r.json()["integritaet"] == "UNGUELTIG"

    def test_trail_id_in_response(self):
        r = client.post(f"{BASE_URL}/audit-trail/pruefe-integritaet",
                        json={"trail_id": "AT-001", "manipuliert": False})
        assert r.json()["trail_id"] == "AT-001"

    def test_no_manipulation_flag_defaults_gueltig(self):
        r = client.post(f"{BASE_URL}/audit-trail/pruefe-integritaet",
                        json={"trail_id": "AT-001"})
        assert r.json()["integritaet"] == "GUELTIG"
