"""
Wave 66: Concurrency + Resource Lock Contracts — 130+ Tests
"""
import pytest
from datetime import datetime, timedelta

from app.core.process_concurrency_contracts import (
    KonkurrenzModus,
    AusfuehrungsSlotStatus,
    KonkurrenzRegel,
    AusfuehrungsSlot,
    KonkurrenzWaechter,
    get_default_konkurrenz_waechter,
)
from app.core.workflow_resource_lock_contracts import (
    RessourceLockTyp,
    DeadlockStatus,
    RessourceLock,
    WarteschlangenEintrag,
    DeadlockAnalyse,
    pruefe_lock_kompatibilitaet,
    erkenne_deadlock,
    get_default_resource_locks,
)

# Fixed reference time
NOW = datetime(2026, 3, 16, 10, 0, 0)


# ============================================================
# KonkurrenzModus Enum
# ============================================================

class TestKonkurrenzModus:
    def test_mutex_value(self):
        assert KonkurrenzModus.MUTEX == "MUTEX"

    def test_semaphore_value(self):
        assert KonkurrenzModus.SEMAPHORE == "SEMAPHORE"

    def test_read_write_value(self):
        assert KonkurrenzModus.READ_WRITE == "READ_WRITE"

    def test_single_writer_value(self):
        assert KonkurrenzModus.SINGLE_WRITER == "SINGLE_WRITER"

    def test_all_members(self):
        members = {m.value for m in KonkurrenzModus}
        assert "MUTEX" in members
        assert "SEMAPHORE" in members
        assert "READ_WRITE" in members
        assert "SINGLE_WRITER" in members


# ============================================================
# AusfuehrungsSlotStatus Enum
# ============================================================

class TestAusfuehrungsSlotStatus:
    def test_frei_value(self):
        assert AusfuehrungsSlotStatus.FREI == "FREI"

    def test_belegt_value(self):
        assert AusfuehrungsSlotStatus.BELEGT == "BELEGT"

    def test_reserviert_value(self):
        assert AusfuehrungsSlotStatus.RESERVIERT == "RESERVIERT"


# ============================================================
# KonkurrenzRegel.effektives_limit()
# ============================================================

class TestKonkurrenzRegelEffektivesLimit:
    def test_mutex_always_returns_1(self):
        regel = KonkurrenzRegel("R1", "res", KonkurrenzModus.MUTEX, 5)
        assert regel.effektives_limit() == 1

    def test_mutex_ignores_max_gleichzeitig(self):
        regel = KonkurrenzRegel("R1", "res", KonkurrenzModus.MUTEX, 999)
        assert regel.effektives_limit() == 1

    def test_semaphore_returns_max_gleichzeitig(self):
        regel = KonkurrenzRegel("R2", "res", KonkurrenzModus.SEMAPHORE, 5)
        assert regel.effektives_limit() == 5

    def test_semaphore_max_3(self):
        regel = KonkurrenzRegel("R2", "res", KonkurrenzModus.SEMAPHORE, 3)
        assert regel.effektives_limit() == 3

    def test_read_write_returns_max_gleichzeitig(self):
        regel = KonkurrenzRegel("R3", "res", KonkurrenzModus.READ_WRITE, 10)
        assert regel.effektives_limit() == 10

    def test_single_writer_returns_max_gleichzeitig(self):
        regel = KonkurrenzRegel("R4", "res", KonkurrenzModus.SINGLE_WRITER, 7)
        assert regel.effektives_limit() == 7

    def test_semaphore_limit_1(self):
        regel = KonkurrenzRegel("R5", "res", KonkurrenzModus.SEMAPHORE, 1)
        assert regel.effektives_limit() == 1

    def test_read_write_limit_1(self):
        regel = KonkurrenzRegel("R6", "res", KonkurrenzModus.READ_WRITE, 1)
        assert regel.effektives_limit() == 1

    def test_default_timeout(self):
        regel = KonkurrenzRegel("R7", "res", KonkurrenzModus.MUTEX, 1)
        assert regel.timeout_sekunden == 300

    def test_custom_timeout(self):
        regel = KonkurrenzRegel("R8", "res", KonkurrenzModus.MUTEX, 1, 600)
        assert regel.timeout_sekunden == 600


# ============================================================
# AusfuehrungsSlot.ist_abgelaufen()
# ============================================================

class TestAusfuehrungsSlotIstAbgelaufen:
    def test_none_ablauf_am_returns_false(self):
        slot = AusfuehrungsSlot("S1", "R1", "H1", ablauf_am=None)
        assert slot.ist_abgelaufen(NOW) is False

    def test_future_ablauf_am_returns_false(self):
        slot = AusfuehrungsSlot("S1", "R1", "H1", ablauf_am=NOW + timedelta(minutes=5))
        assert slot.ist_abgelaufen(NOW) is False

    def test_past_ablauf_am_returns_true(self):
        slot = AusfuehrungsSlot("S1", "R1", "H1", ablauf_am=NOW - timedelta(seconds=1))
        assert slot.ist_abgelaufen(NOW) is True

    def test_exact_now_ablauf_am_returns_true(self):
        slot = AusfuehrungsSlot("S1", "R1", "H1", ablauf_am=NOW)
        assert slot.ist_abgelaufen(NOW) is True

    def test_one_second_future_not_abgelaufen(self):
        slot = AusfuehrungsSlot("S1", "R1", "H1", ablauf_am=NOW + timedelta(seconds=1))
        assert slot.ist_abgelaufen(NOW) is False

    def test_long_past_ablauf_am_returns_true(self):
        slot = AusfuehrungsSlot("S1", "R1", "H1", ablauf_am=NOW - timedelta(hours=2))
        assert slot.ist_abgelaufen(NOW) is True


# ============================================================
# AusfuehrungsSlot.ist_verfuegbar()
# ============================================================

class TestAusfuehrungsSlotIstVerfuegbar:
    def test_frei_slot_is_verfuegbar(self):
        slot = AusfuehrungsSlot("S1", "R1", "H1", AusfuehrungsSlotStatus.FREI)
        assert slot.ist_verfuegbar(NOW) is True

    def test_frei_slot_with_no_ablauf_verfuegbar(self):
        slot = AusfuehrungsSlot("S1", "R1", "H1", AusfuehrungsSlotStatus.FREI, ablauf_am=None)
        assert slot.ist_verfuegbar(NOW) is True

    def test_belegt_not_expired_not_verfuegbar(self):
        slot = AusfuehrungsSlot("S1", "R1", "H1", AusfuehrungsSlotStatus.BELEGT,
                                 ablauf_am=NOW + timedelta(minutes=5))
        assert slot.ist_verfuegbar(NOW) is False

    def test_belegt_expired_is_verfuegbar(self):
        slot = AusfuehrungsSlot("S1", "R1", "H1", AusfuehrungsSlotStatus.BELEGT,
                                 ablauf_am=NOW - timedelta(minutes=1))
        assert slot.ist_verfuegbar(NOW) is True

    def test_reserviert_not_verfuegbar(self):
        slot = AusfuehrungsSlot("S1", "R1", "H1", AusfuehrungsSlotStatus.RESERVIERT)
        assert slot.ist_verfuegbar(NOW) is False

    def test_reserviert_with_future_ablauf_not_verfuegbar(self):
        slot = AusfuehrungsSlot("S1", "R1", "H1", AusfuehrungsSlotStatus.RESERVIERT,
                                 ablauf_am=NOW + timedelta(minutes=10))
        assert slot.ist_verfuegbar(NOW) is False

    def test_belegt_none_ablauf_not_verfuegbar(self):
        slot = AusfuehrungsSlot("S1", "R1", "H1", AusfuehrungsSlotStatus.BELEGT, ablauf_am=None)
        assert slot.ist_verfuegbar(NOW) is False

    def test_belegt_exact_now_ablauf_verfuegbar(self):
        slot = AusfuehrungsSlot("S1", "R1", "H1", AusfuehrungsSlotStatus.BELEGT,
                                 ablauf_am=NOW)
        assert slot.ist_verfuegbar(NOW) is True


# ============================================================
# KonkurrenzWaechter.belegte_slots()
# ============================================================

class TestKonkurrenzWaechterBelegteSlots:
    def make_waechter(self):
        regel = KonkurrenzRegel("R1", "res", KonkurrenzModus.SEMAPHORE, 5)
        return KonkurrenzWaechter("KW-T", regel)

    def test_empty_slots_returns_empty(self):
        w = self.make_waechter()
        assert w.belegte_slots(NOW) == []

    def test_frei_slot_not_counted(self):
        w = self.make_waechter()
        w.slots = [AusfuehrungsSlot("S1", "R1", "H1", AusfuehrungsSlotStatus.FREI)]
        assert len(w.belegte_slots(NOW)) == 0

    def test_belegt_not_expired_counted(self):
        w = self.make_waechter()
        w.slots = [AusfuehrungsSlot("S1", "R1", "H1", AusfuehrungsSlotStatus.BELEGT,
                                     ablauf_am=NOW + timedelta(minutes=5))]
        assert len(w.belegte_slots(NOW)) == 1

    def test_belegt_expired_not_counted(self):
        w = self.make_waechter()
        w.slots = [AusfuehrungsSlot("S1", "R1", "H1", AusfuehrungsSlotStatus.BELEGT,
                                     ablauf_am=NOW - timedelta(minutes=5))]
        assert len(w.belegte_slots(NOW)) == 0

    def test_mixed_slots_only_non_expired_belegt(self):
        w = self.make_waechter()
        w.slots = [
            AusfuehrungsSlot("S1", "R1", "H1", AusfuehrungsSlotStatus.BELEGT,
                              ablauf_am=NOW + timedelta(minutes=5)),
            AusfuehrungsSlot("S2", "R1", "H2", AusfuehrungsSlotStatus.BELEGT,
                              ablauf_am=NOW - timedelta(minutes=5)),  # expired
            AusfuehrungsSlot("S3", "R1", "H3", AusfuehrungsSlotStatus.FREI),
            AusfuehrungsSlot("S4", "R1", "H4", AusfuehrungsSlotStatus.RESERVIERT),
        ]
        result = w.belegte_slots(NOW)
        assert len(result) == 1
        assert result[0].slot_id == "S1"

    def test_reserviert_not_counted(self):
        w = self.make_waechter()
        w.slots = [AusfuehrungsSlot("S1", "R1", "H1", AusfuehrungsSlotStatus.RESERVIERT,
                                     ablauf_am=NOW + timedelta(minutes=5))]
        assert len(w.belegte_slots(NOW)) == 0

    def test_multiple_belegt_non_expired_all_counted(self):
        w = self.make_waechter()
        w.slots = [
            AusfuehrungsSlot(f"S{i}", "R1", f"H{i}", AusfuehrungsSlotStatus.BELEGT,
                              ablauf_am=NOW + timedelta(minutes=i+1))
            for i in range(3)
        ]
        assert len(w.belegte_slots(NOW)) == 3


# ============================================================
# KonkurrenzWaechter.kann_ausfuehren()
# ============================================================

class TestKonkurrenzWaechterKannAusfuehren:
    def test_no_slots_can_execute(self):
        regel = KonkurrenzRegel("R1", "res", KonkurrenzModus.MUTEX, 1)
        w = KonkurrenzWaechter("KW-T", regel)
        assert w.kann_ausfuehren(NOW) is True

    def test_mutex_at_limit_cannot_execute(self):
        regel = KonkurrenzRegel("R1", "res", KonkurrenzModus.MUTEX, 1)
        w = KonkurrenzWaechter("KW-T", regel)
        w.slots = [AusfuehrungsSlot("S1", "R1", "H1", AusfuehrungsSlotStatus.BELEGT,
                                     ablauf_am=NOW + timedelta(minutes=5))]
        assert w.kann_ausfuehren(NOW) is False

    def test_mutex_expired_slot_can_execute(self):
        regel = KonkurrenzRegel("R1", "res", KonkurrenzModus.MUTEX, 1)
        w = KonkurrenzWaechter("KW-T", regel)
        w.slots = [AusfuehrungsSlot("S1", "R1", "H1", AusfuehrungsSlotStatus.BELEGT,
                                     ablauf_am=NOW - timedelta(minutes=5))]
        assert w.kann_ausfuehren(NOW) is True

    def test_semaphore_below_limit_can_execute(self):
        regel = KonkurrenzRegel("R1", "res", KonkurrenzModus.SEMAPHORE, 3)
        w = KonkurrenzWaechter("KW-T", regel)
        w.slots = [
            AusfuehrungsSlot("S1", "R1", "H1", AusfuehrungsSlotStatus.BELEGT,
                              ablauf_am=NOW + timedelta(minutes=5)),
            AusfuehrungsSlot("S2", "R1", "H2", AusfuehrungsSlotStatus.BELEGT,
                              ablauf_am=NOW + timedelta(minutes=5)),
        ]
        assert w.kann_ausfuehren(NOW) is True

    def test_semaphore_at_limit_cannot_execute(self):
        regel = KonkurrenzRegel("R1", "res", KonkurrenzModus.SEMAPHORE, 2)
        w = KonkurrenzWaechter("KW-T", regel)
        w.slots = [
            AusfuehrungsSlot(f"S{i}", "R1", f"H{i}", AusfuehrungsSlotStatus.BELEGT,
                              ablauf_am=NOW + timedelta(minutes=5))
            for i in range(2)
        ]
        assert w.kann_ausfuehren(NOW) is False

    def test_semaphore_over_limit_due_to_expired_can_execute(self):
        regel = KonkurrenzRegel("R1", "res", KonkurrenzModus.SEMAPHORE, 2)
        w = KonkurrenzWaechter("KW-T", regel)
        w.slots = [
            AusfuehrungsSlot("S1", "R1", "H1", AusfuehrungsSlotStatus.BELEGT,
                              ablauf_am=NOW + timedelta(minutes=5)),
            AusfuehrungsSlot("S2", "R1", "H2", AusfuehrungsSlotStatus.BELEGT,
                              ablauf_am=NOW - timedelta(minutes=5)),  # expired
        ]
        assert w.kann_ausfuehren(NOW) is True

    def test_read_write_below_limit_can_execute(self):
        regel = KonkurrenzRegel("R1", "res", KonkurrenzModus.READ_WRITE, 5)
        w = KonkurrenzWaechter("KW-T", regel)
        assert w.kann_ausfuehren(NOW) is True


# ============================================================
# KonkurrenzWaechter.auslastung_pct()
# ============================================================

class TestKonkurrenzWaechterAuslastungPct:
    def test_zero_limit_returns_zero(self):
        regel = KonkurrenzRegel("R1", "res", KonkurrenzModus.SEMAPHORE, 0)
        w = KonkurrenzWaechter("KW-T", regel)
        assert w.auslastung_pct(NOW) == 0.0

    def test_no_slots_returns_zero(self):
        regel = KonkurrenzRegel("R1", "res", KonkurrenzModus.MUTEX, 1)
        w = KonkurrenzWaechter("KW-T", regel)
        assert w.auslastung_pct(NOW) == 0.0

    def test_full_mutex_returns_100(self):
        regel = KonkurrenzRegel("R1", "res", KonkurrenzModus.MUTEX, 1)
        w = KonkurrenzWaechter("KW-T", regel)
        w.slots = [AusfuehrungsSlot("S1", "R1", "H1", AusfuehrungsSlotStatus.BELEGT,
                                     ablauf_am=NOW + timedelta(minutes=5))]
        assert w.auslastung_pct(NOW) == 100.0

    def test_half_semaphore_returns_50(self):
        regel = KonkurrenzRegel("R1", "res", KonkurrenzModus.SEMAPHORE, 4)
        w = KonkurrenzWaechter("KW-T", regel)
        w.slots = [
            AusfuehrungsSlot(f"S{i}", "R1", f"H{i}", AusfuehrungsSlotStatus.BELEGT,
                              ablauf_am=NOW + timedelta(minutes=5))
            for i in range(2)
        ]
        assert w.auslastung_pct(NOW) == 50.0

    def test_one_third_semaphore(self):
        regel = KonkurrenzRegel("R1", "res", KonkurrenzModus.SEMAPHORE, 3)
        w = KonkurrenzWaechter("KW-T", regel)
        w.slots = [AusfuehrungsSlot("S1", "R1", "H1", AusfuehrungsSlotStatus.BELEGT,
                                     ablauf_am=NOW + timedelta(minutes=5))]
        assert abs(w.auslastung_pct(NOW) - 33.333333333333336) < 0.01

    def test_expired_slots_not_counted_in_auslastung(self):
        regel = KonkurrenzRegel("R1", "res", KonkurrenzModus.SEMAPHORE, 2)
        w = KonkurrenzWaechter("KW-T", regel)
        w.slots = [
            AusfuehrungsSlot("S1", "R1", "H1", AusfuehrungsSlotStatus.BELEGT,
                              ablauf_am=NOW - timedelta(minutes=5)),  # expired
        ]
        assert w.auslastung_pct(NOW) == 0.0


# ============================================================
# Default Waechter Tests
# ============================================================

class TestDefaultKonkurrenzWaechter:
    def setup_method(self):
        self.waechter = get_default_konkurrenz_waechter()
        self.kw001 = next(w for w in self.waechter if w.waechter_id == "KW-001")
        self.kw002 = next(w for w in self.waechter if w.waechter_id == "KW-002")

    def test_returns_two_waechter(self):
        assert len(self.waechter) == 2

    def test_kw001_exists(self):
        assert self.kw001 is not None

    def test_kw002_exists(self):
        assert self.kw002 is not None

    def test_kw001_is_mutex(self):
        assert self.kw001.regel.modus == KonkurrenzModus.MUTEX

    def test_kw001_ressource_typ(self):
        assert self.kw001.regel.ressource_typ == "settlement_run"

    def test_kw001_effektives_limit_is_1(self):
        assert self.kw001.regel.effektives_limit() == 1

    def test_kw001_has_1_belegt_slot(self):
        assert len(self.kw001.belegte_slots(NOW)) == 1

    def test_kw001_cannot_execute(self):
        assert self.kw001.kann_ausfuehren(NOW) is False

    def test_kw001_auslastung_is_100(self):
        assert self.kw001.auslastung_pct(NOW) == 100.0

    def test_kw002_is_semaphore(self):
        assert self.kw002.regel.modus == KonkurrenzModus.SEMAPHORE

    def test_kw002_ressource_typ(self):
        assert self.kw002.regel.ressource_typ == "batch_import"

    def test_kw002_effektives_limit_is_3(self):
        assert self.kw002.regel.effektives_limit() == 3

    def test_kw002_has_3_total_slots(self):
        assert len(self.kw002.slots) == 3

    def test_kw002_has_2_non_expired_belegt(self):
        # AS-004 is expired
        assert len(self.kw002.belegte_slots(NOW)) == 2

    def test_kw002_can_execute(self):
        assert self.kw002.kann_ausfuehren(NOW) is True

    def test_kw002_auslastung_approx_67(self):
        pct = self.kw002.auslastung_pct(NOW)
        assert abs(pct - 66.66666666666667) < 0.01

    def test_kw001_slot_as001_not_expired(self):
        slot = next(s for s in self.kw001.slots if s.slot_id == "AS-001")
        assert slot.ist_abgelaufen(NOW) is False

    def test_kw002_slot_as004_is_expired(self):
        slot = next(s for s in self.kw002.slots if s.slot_id == "AS-004")
        assert slot.ist_abgelaufen(NOW) is True

    def test_kw002_slot_as002_not_expired(self):
        slot = next(s for s in self.kw002.slots if s.slot_id == "AS-002")
        assert slot.ist_abgelaufen(NOW) is False

    def test_kw002_slot_as003_not_expired(self):
        slot = next(s for s in self.kw002.slots if s.slot_id == "AS-003")
        assert slot.ist_abgelaufen(NOW) is False


# ============================================================
# RessourceLock.__post_init__ and ist_aktiv()
# ============================================================

class TestRessourceLock:
    def test_ablauf_am_computed_from_erstellt_am(self):
        erstellt = datetime(2026, 3, 16, 10, 0, 0)
        lock = RessourceLock("L1", "R1", "H1", RessourceLockTyp.EXKLUSIV, erstellt, 300)
        expected = erstellt + timedelta(seconds=300)
        assert lock.ablauf_am == expected

    def test_ablauf_am_ttl_600(self):
        erstellt = datetime(2026, 3, 16, 10, 0, 0)
        lock = RessourceLock("L1", "R1", "H1", RessourceLockTyp.GETEILT, erstellt, 600)
        assert lock.ablauf_am == erstellt + timedelta(seconds=600)

    def test_ist_aktiv_before_expiry(self):
        erstellt = NOW
        lock = RessourceLock("L1", "R1", "H1", RessourceLockTyp.EXKLUSIV, erstellt, 300)
        # Check 1 second after creation
        assert lock.ist_aktiv(NOW + timedelta(seconds=1)) is True

    def test_ist_aktiv_after_expiry(self):
        erstellt = NOW - timedelta(hours=1)
        lock = RessourceLock("L1", "R1", "H1", RessourceLockTyp.EXKLUSIV, erstellt, 60)
        assert lock.ist_aktiv(NOW) is False

    def test_ist_aktiv_exactly_at_expiry_false(self):
        erstellt = NOW
        lock = RessourceLock("L1", "R1", "H1", RessourceLockTyp.EXKLUSIV, erstellt, 300)
        # At exactly ablauf_am, jetzt < ablauf_am is False
        assert lock.ist_aktiv(lock.ablauf_am) is False

    def test_ist_aktiv_one_second_before_expiry(self):
        erstellt = NOW
        lock = RessourceLock("L1", "R1", "H1", RessourceLockTyp.EXKLUSIV, erstellt, 300)
        assert lock.ist_aktiv(lock.ablauf_am - timedelta(seconds=1)) is True

    def test_geteilt_lock_aktiv(self):
        lock = RessourceLock("L1", "R1", "H1", RessourceLockTyp.GETEILT, NOW, 600)
        assert lock.ist_aktiv(NOW + timedelta(seconds=1)) is True

    def test_upgrade_lock_aktiv(self):
        lock = RessourceLock("L1", "R1", "H1", RessourceLockTyp.UPGRADE, NOW, 120)
        assert lock.ist_aktiv(NOW + timedelta(seconds=60)) is True

    def test_upgrade_lock_expired(self):
        lock = RessourceLock("L1", "R1", "H1", RessourceLockTyp.UPGRADE, NOW, 120)
        assert lock.ist_aktiv(NOW + timedelta(seconds=121)) is False

    def test_lock_fields_stored(self):
        lock = RessourceLock("L-TEST", "RES-X", "INH-Y", RessourceLockTyp.EXKLUSIV, NOW, 300)
        assert lock.lock_id == "L-TEST"
        assert lock.ressource_id == "RES-X"
        assert lock.inhaber_id == "INH-Y"
        assert lock.lock_typ == RessourceLockTyp.EXKLUSIV


# ============================================================
# RessourceLockTyp Enum
# ============================================================

class TestRessourceLockTyp:
    def test_exklusiv_value(self):
        assert RessourceLockTyp.EXKLUSIV == "EXKLUSIV"

    def test_geteilt_value(self):
        assert RessourceLockTyp.GETEILT == "GETEILT"

    def test_upgrade_value(self):
        assert RessourceLockTyp.UPGRADE == "UPGRADE"


# ============================================================
# DeadlockStatus Enum
# ============================================================

class TestDeadlockStatus:
    def test_kein_deadlock_value(self):
        assert DeadlockStatus.KEIN_DEADLOCK == "KEIN_DEADLOCK"

    def test_deadlock_erkannt_value(self):
        assert DeadlockStatus.DEADLOCK_ERKANNT == "DEADLOCK_ERKANNT"

    def test_deadlock_aufgeloest_value(self):
        assert DeadlockStatus.DEADLOCK_AUFGELOEST == "DEADLOCK_AUFGELOEST"


# ============================================================
# WarteschlangenEintrag
# ============================================================

class TestWarteschlangenEintrag:
    def test_creates_successfully(self):
        entry = WarteschlangenEintrag("E1", "H1", "R1", RessourceLockTyp.EXKLUSIV, NOW)
        assert entry.eintrag_id == "E1"
        assert entry.inhaber_id == "H1"
        assert entry.ressource_id == "R1"
        assert entry.benoetigt_lock_typ == RessourceLockTyp.EXKLUSIV

    def test_wartet_seit_stored(self):
        entry = WarteschlangenEintrag("E1", "H1", "R1", RessourceLockTyp.GETEILT, NOW)
        assert entry.wartet_seit == NOW


# ============================================================
# DeadlockAnalyse
# ============================================================

class TestDeadlockAnalyse:
    def test_creates_with_kein_deadlock(self):
        da = DeadlockAnalyse("DA-1", DeadlockStatus.KEIN_DEADLOCK)
        assert da.status == DeadlockStatus.KEIN_DEADLOCK
        assert da.beteiligte_inhaber == []

    def test_creates_with_deadlock_erkannt(self):
        da = DeadlockAnalyse("DA-2", DeadlockStatus.DEADLOCK_ERKANNT, ["A", "B"], "Abbreche A")
        assert da.status == DeadlockStatus.DEADLOCK_ERKANNT
        assert "A" in da.beteiligte_inhaber
        assert da.aufloesungs_vorschlag == "Abbreche A"

    def test_empty_vorschlag_default(self):
        da = DeadlockAnalyse("DA-3", DeadlockStatus.KEIN_DEADLOCK)
        assert da.aufloesungs_vorschlag == ""


# ============================================================
# pruefe_lock_kompatibilitaet()
# ============================================================

class TestPruefeLockKompatibilitaet:
    def test_geteilt_geteilt_true(self):
        assert pruefe_lock_kompatibilitaet(RessourceLockTyp.GETEILT, RessourceLockTyp.GETEILT) is True

    def test_geteilt_exklusiv_false(self):
        assert pruefe_lock_kompatibilitaet(RessourceLockTyp.GETEILT, RessourceLockTyp.EXKLUSIV) is False

    def test_exklusiv_geteilt_false(self):
        assert pruefe_lock_kompatibilitaet(RessourceLockTyp.EXKLUSIV, RessourceLockTyp.GETEILT) is False

    def test_exklusiv_exklusiv_false(self):
        assert pruefe_lock_kompatibilitaet(RessourceLockTyp.EXKLUSIV, RessourceLockTyp.EXKLUSIV) is False

    def test_upgrade_geteilt_true(self):
        assert pruefe_lock_kompatibilitaet(RessourceLockTyp.UPGRADE, RessourceLockTyp.GETEILT) is True

    def test_upgrade_exklusiv_false(self):
        assert pruefe_lock_kompatibilitaet(RessourceLockTyp.UPGRADE, RessourceLockTyp.EXKLUSIV) is False

    def test_upgrade_upgrade_false(self):
        assert pruefe_lock_kompatibilitaet(RessourceLockTyp.UPGRADE, RessourceLockTyp.UPGRADE) is False

    def test_geteilt_upgrade_false(self):
        # Not explicitly listed as True — defaults to False
        assert pruefe_lock_kompatibilitaet(RessourceLockTyp.GETEILT, RessourceLockTyp.UPGRADE) is False

    def test_exklusiv_upgrade_false(self):
        assert pruefe_lock_kompatibilitaet(RessourceLockTyp.EXKLUSIV, RessourceLockTyp.UPGRADE) is False


# ============================================================
# erkenne_deadlock()
# ============================================================

class TestErkenneDeadlock:
    def test_empty_returns_kein_deadlock(self):
        result = erkenne_deadlock([])
        assert result.status == DeadlockStatus.KEIN_DEADLOCK

    def test_single_node_no_cycle(self):
        result = erkenne_deadlock([{"wartet": "A", "auf": "B"}])
        assert result.status == DeadlockStatus.KEIN_DEADLOCK

    def test_simple_cycle_a_b_a(self):
        result = erkenne_deadlock([
            {"wartet": "A", "auf": "B"},
            {"wartet": "B", "auf": "A"},
        ])
        assert result.status == DeadlockStatus.DEADLOCK_ERKANNT

    def test_simple_cycle_beteiligte_non_empty(self):
        result = erkenne_deadlock([
            {"wartet": "A", "auf": "B"},
            {"wartet": "B", "auf": "A"},
        ])
        assert len(result.beteiligte_inhaber) > 0

    def test_simple_cycle_contains_known_nodes(self):
        result = erkenne_deadlock([
            {"wartet": "A", "auf": "B"},
            {"wartet": "B", "auf": "A"},
        ])
        # At least one of A or B should be in the cycle
        assert any(n in result.beteiligte_inhaber for n in ["A", "B"])

    def test_three_node_cycle(self):
        result = erkenne_deadlock([
            {"wartet": "A", "auf": "B"},
            {"wartet": "B", "auf": "C"},
            {"wartet": "C", "auf": "A"},
        ])
        assert result.status == DeadlockStatus.DEADLOCK_ERKANNT

    def test_three_node_cycle_beteiligte_non_empty(self):
        result = erkenne_deadlock([
            {"wartet": "A", "auf": "B"},
            {"wartet": "B", "auf": "C"},
            {"wartet": "C", "auf": "A"},
        ])
        assert len(result.beteiligte_inhaber) >= 2

    def test_chain_no_cycle(self):
        result = erkenne_deadlock([
            {"wartet": "A", "auf": "B"},
            {"wartet": "B", "auf": "C"},
        ])
        assert result.status == DeadlockStatus.KEIN_DEADLOCK

    def test_chain_no_cycle_beteiligte_empty(self):
        result = erkenne_deadlock([
            {"wartet": "A", "auf": "B"},
            {"wartet": "B", "auf": "C"},
        ])
        assert result.beteiligte_inhaber == []

    def test_self_loop_is_cycle(self):
        result = erkenne_deadlock([{"wartet": "A", "auf": "A"}])
        assert result.status == DeadlockStatus.DEADLOCK_ERKANNT

    def test_disconnected_nodes_no_cycle(self):
        result = erkenne_deadlock([
            {"wartet": "A", "auf": "B"},
            {"wartet": "C", "auf": "D"},
        ])
        assert result.status == DeadlockStatus.KEIN_DEADLOCK

    def test_cycle_with_extra_tail(self):
        # X → A → B → A (cycle is A→B→A)
        result = erkenne_deadlock([
            {"wartet": "X", "auf": "A"},
            {"wartet": "A", "auf": "B"},
            {"wartet": "B", "auf": "A"},
        ])
        assert result.status == DeadlockStatus.DEADLOCK_ERKANNT

    def test_aufloesungs_vorschlag_non_empty_on_deadlock(self):
        result = erkenne_deadlock([
            {"wartet": "A", "auf": "B"},
            {"wartet": "B", "auf": "A"},
        ])
        assert len(result.aufloesungs_vorschlag) > 0

    def test_kein_deadlock_empty_beteiligte(self):
        result = erkenne_deadlock([])
        assert result.beteiligte_inhaber == []

    def test_analyse_id_set(self):
        result = erkenne_deadlock([])
        assert result.analyse_id == "DA-AUTO"

    def test_four_node_cycle(self):
        result = erkenne_deadlock([
            {"wartet": "A", "auf": "B"},
            {"wartet": "B", "auf": "C"},
            {"wartet": "C", "auf": "D"},
            {"wartet": "D", "auf": "A"},
        ])
        assert result.status == DeadlockStatus.DEADLOCK_ERKANNT

    def test_two_separate_chains_no_cycle(self):
        result = erkenne_deadlock([
            {"wartet": "A", "auf": "B"},
            {"wartet": "C", "auf": "D"},
            {"wartet": "D", "auf": "E"},
        ])
        assert result.status == DeadlockStatus.KEIN_DEADLOCK


# ============================================================
# Default Resource Locks Tests
# ============================================================

class TestDefaultResourceLocks:
    def setup_method(self):
        self.locks = get_default_resource_locks()
        self.by_id = {l.lock_id: l for l in self.locks}

    def test_returns_four_locks(self):
        assert len(self.locks) == 4

    def test_rl001_exists(self):
        assert "RL-001" in self.by_id

    def test_rl002_exists(self):
        assert "RL-002" in self.by_id

    def test_rl003_exists(self):
        assert "RL-003" in self.by_id

    def test_rl004_exists(self):
        assert "RL-004" in self.by_id

    def test_rl001_is_exklusiv(self):
        assert self.by_id["RL-001"].lock_typ == RessourceLockTyp.EXKLUSIV

    def test_rl001_ressource_kontrakt(self):
        assert self.by_id["RL-001"].ressource_id == "KONTRAKT-001"

    def test_rl001_is_aktiv(self):
        assert self.by_id["RL-001"].ist_aktiv(NOW) is True

    def test_rl001_ttl_300(self):
        assert self.by_id["RL-001"].ttl_sekunden == 300

    def test_rl002_is_geteilt(self):
        assert self.by_id["RL-002"].lock_typ == RessourceLockTyp.GETEILT

    def test_rl002_settlement_ressource(self):
        assert self.by_id["RL-002"].ressource_id == "SETTLEMENT-001"

    def test_rl002_is_aktiv(self):
        assert self.by_id["RL-002"].ist_aktiv(NOW) is True

    def test_rl003_is_geteilt(self):
        assert self.by_id["RL-003"].lock_typ == RessourceLockTyp.GETEILT

    def test_rl003_settlement_ressource(self):
        assert self.by_id["RL-003"].ressource_id == "SETTLEMENT-001"

    def test_rl003_is_aktiv(self):
        assert self.by_id["RL-003"].ist_aktiv(NOW) is True

    def test_rl004_is_exklusiv(self):
        assert self.by_id["RL-004"].lock_typ == RessourceLockTyp.EXKLUSIV

    def test_rl004_batch_ressource(self):
        assert self.by_id["RL-004"].ressource_id == "BATCH-001"

    def test_rl004_is_expired(self):
        # Created 1h ago, TTL 60s → definitely expired
        assert self.by_id["RL-004"].ist_aktiv(NOW) is False

    def test_rl004_ttl_60(self):
        assert self.by_id["RL-004"].ttl_sekunden == 60

    def test_rl002_rl003_same_ressource_compatible(self):
        # Two GETEILT locks on same resource are compatible
        assert pruefe_lock_kompatibilitaet(
            self.by_id["RL-002"].lock_typ,
            self.by_id["RL-003"].lock_typ
        ) is True

    def test_rl001_rl002_incompatible(self):
        # EXKLUSIV + GETEILT → False
        assert pruefe_lock_kompatibilitaet(
            self.by_id["RL-001"].lock_typ,
            self.by_id["RL-002"].lock_typ
        ) is False

    def test_active_lock_count(self):
        active = [l for l in self.locks if l.ist_aktiv(NOW)]
        assert len(active) == 3

    def test_expired_lock_count(self):
        expired = [l for l in self.locks if not l.ist_aktiv(NOW)]
        assert len(expired) == 1
        assert expired[0].lock_id == "RL-004"


# ============================================================
# FastAPI Endpoint Tests
# ============================================================

class TestFastAPIEndpoints:
    def setup_method(self):
        from fastapi.testclient import TestClient
        from app.api.v1.endpoints.process_kernel_api import router
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        self.client = TestClient(app, raise_server_exceptions=True)

    def test_get_konkurrenz_waechter_status_200(self):
        resp = self.client.get("/process/konkurrenz/waechter")
        assert resp.status_code == 200

    def test_get_konkurrenz_waechter_returns_list(self):
        resp = self.client.get("/process/konkurrenz/waechter")
        data = resp.json()
        assert isinstance(data, list)

    def test_get_konkurrenz_waechter_has_two_entries(self):
        resp = self.client.get("/process/konkurrenz/waechter")
        assert len(resp.json()) == 2

    def test_get_konkurrenz_waechter_kw001_cannot_execute(self):
        resp = self.client.get("/process/konkurrenz/waechter")
        kw001 = next(w for w in resp.json() if w["waechter_id"] == "KW-001")
        assert kw001["kann_ausfuehren"] is False

    def test_get_konkurrenz_waechter_kw001_auslastung_100(self):
        resp = self.client.get("/process/konkurrenz/waechter")
        kw001 = next(w for w in resp.json() if w["waechter_id"] == "KW-001")
        assert kw001["auslastung_pct"] == 100.0

    def test_get_konkurrenz_waechter_kw002_can_execute(self):
        resp = self.client.get("/process/konkurrenz/waechter")
        kw002 = next(w for w in resp.json() if w["waechter_id"] == "KW-002")
        assert kw002["kann_ausfuehren"] is True

    def test_get_konkurrenz_waechter_kw002_belegte_slots_2(self):
        resp = self.client.get("/process/konkurrenz/waechter")
        kw002 = next(w for w in resp.json() if w["waechter_id"] == "KW-002")
        assert kw002["belegte_slots"] == 2

    def test_pruefe_ausfuehrbarkeit_mutex_0_active(self):
        resp = self.client.post("/process/konkurrenz/pruefe-ausfuehrbarkeit",
                                json={"modus": "MUTEX", "max_gleichzeitig": 5, "aktive_ausfuehrungen": 0})
        assert resp.status_code == 200
        data = resp.json()
        assert data["kann_ausfuehren"] is True
        assert data["effektives_limit"] == 1

    def test_pruefe_ausfuehrbarkeit_mutex_1_active_cannot(self):
        resp = self.client.post("/process/konkurrenz/pruefe-ausfuehrbarkeit",
                                json={"modus": "MUTEX", "max_gleichzeitig": 1, "aktive_ausfuehrungen": 1})
        assert resp.json()["kann_ausfuehren"] is False

    def test_pruefe_ausfuehrbarkeit_semaphore_below_limit(self):
        resp = self.client.post("/process/konkurrenz/pruefe-ausfuehrbarkeit",
                                json={"modus": "SEMAPHORE", "max_gleichzeitig": 3, "aktive_ausfuehrungen": 2})
        data = resp.json()
        assert data["kann_ausfuehren"] is True
        assert data["effektives_limit"] == 3

    def test_pruefe_ausfuehrbarkeit_semaphore_at_limit(self):
        resp = self.client.post("/process/konkurrenz/pruefe-ausfuehrbarkeit",
                                json={"modus": "SEMAPHORE", "max_gleichzeitig": 3, "aktive_ausfuehrungen": 3})
        assert resp.json()["kann_ausfuehren"] is False

    def test_get_resource_locks_status_200(self):
        resp = self.client.get("/process/resource-lock/locks")
        assert resp.status_code == 200

    def test_get_resource_locks_returns_list(self):
        resp = self.client.get("/process/resource-lock/locks")
        assert isinstance(resp.json(), list)

    def test_get_resource_locks_has_four_entries(self):
        resp = self.client.get("/process/resource-lock/locks")
        assert len(resp.json()) == 4

    def test_get_resource_locks_rl001_aktiv(self):
        resp = self.client.get("/process/resource-lock/locks")
        rl001 = next(l for l in resp.json() if l["lock_id"] == "RL-001")
        assert rl001["ist_aktiv"] is True

    def test_get_resource_locks_rl004_not_aktiv(self):
        resp = self.client.get("/process/resource-lock/locks")
        rl004 = next(l for l in resp.json() if l["lock_id"] == "RL-004")
        assert rl004["ist_aktiv"] is False

    def test_erkenne_deadlock_no_cycle(self):
        resp = self.client.post("/process/resource-lock/erkenne-deadlock",
                                json={"warte_relationen": [{"wartet": "A", "auf": "B"}]})
        assert resp.status_code == 200
        assert resp.json()["status"] == "KEIN_DEADLOCK"

    def test_erkenne_deadlock_simple_cycle(self):
        resp = self.client.post("/process/resource-lock/erkenne-deadlock",
                                json={"warte_relationen": [
                                    {"wartet": "A", "auf": "B"},
                                    {"wartet": "B", "auf": "A"},
                                ]})
        assert resp.json()["status"] == "DEADLOCK_ERKANNT"

    def test_erkenne_deadlock_empty(self):
        resp = self.client.post("/process/resource-lock/erkenne-deadlock",
                                json={"warte_relationen": []})
        assert resp.json()["status"] == "KEIN_DEADLOCK"

    def test_erkenne_deadlock_cycle_beteiligte_non_empty(self):
        resp = self.client.post("/process/resource-lock/erkenne-deadlock",
                                json={"warte_relationen": [
                                    {"wartet": "X", "auf": "Y"},
                                    {"wartet": "Y", "auf": "X"},
                                ]})
        assert len(resp.json()["beteiligte_inhaber"]) > 0

    def test_erkenne_deadlock_aufloesungs_vorschlag_non_empty_on_deadlock(self):
        resp = self.client.post("/process/resource-lock/erkenne-deadlock",
                                json={"warte_relationen": [
                                    {"wartet": "P1", "auf": "P2"},
                                    {"wartet": "P2", "auf": "P1"},
                                ]})
        assert len(resp.json()["aufloesungs_vorschlag"]) > 0
