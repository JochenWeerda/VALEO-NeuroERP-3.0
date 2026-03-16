"""Wave 53: Rate Limiting + Idempotency Contracts — 130+ Tests"""
import pytest
from datetime import datetime, timedelta

from app.core.process_rate_limit_contracts import (
    RateLimitFenster,
    RateLimitErgebnis,
    RateLimitGranularitaet,
    RateLimitRegel,
    RateLimitZaehler,
    get_default_rate_limit_regeln,
)
from app.core.workflow_idempotency_contracts import (
    IdempotenzStatus,
    DeduplizierungsStrategie,
    IdempotenzEintrag,
    IdempotenzPruefung,
    pruefe_idempotenz,
    get_default_idempotenz_eintraege,
)


# ============================================================
# RateLimitFenster enum
# ============================================================

class TestRateLimitFensterEnum:
    def test_sekunde_value(self):
        assert RateLimitFenster.SEKUNDE == "SEKUNDE"

    def test_minute_value(self):
        assert RateLimitFenster.MINUTE == "MINUTE"

    def test_stunde_value(self):
        assert RateLimitFenster.STUNDE == "STUNDE"

    def test_tag_value(self):
        assert RateLimitFenster.TAG == "TAG"

    def test_all_members(self):
        assert len(RateLimitFenster) == 4


# ============================================================
# RateLimitErgebnis enum
# ============================================================

class TestRateLimitErgebnisEnum:
    def test_erlaubt_value(self):
        assert RateLimitErgebnis.ERLAUBT == "ERLAUBT"

    def test_gedrosselt_value(self):
        assert RateLimitErgebnis.GEDROSSELT == "GEDROSSELT"

    def test_blockiert_value(self):
        assert RateLimitErgebnis.BLOCKIERT == "BLOCKIERT"

    def test_all_members(self):
        assert len(RateLimitErgebnis) == 3


# ============================================================
# RateLimitGranularitaet enum
# ============================================================

class TestRateLimitGranularitaetEnum:
    def test_tenant(self):
        assert RateLimitGranularitaet.TENANT == "TENANT"

    def test_benutzer(self):
        assert RateLimitGranularitaet.BENUTZER == "BENUTZER"

    def test_endpunkt(self):
        assert RateLimitGranularitaet.ENDPUNKT == "ENDPUNKT"

    def test_global(self):
        assert RateLimitGranularitaet.GLOBAL == "GLOBAL"


# ============================================================
# RateLimitRegel.fenster_sekunden()
# ============================================================

class TestRateLimitRegelFensterSekunden:
    def _make_regel(self, fenster):
        return RateLimitRegel("R", RateLimitGranularitaet.TENANT, fenster, 100, 80)

    def test_sekunde_returns_1(self):
        assert self._make_regel(RateLimitFenster.SEKUNDE).fenster_sekunden() == 1

    def test_minute_returns_60(self):
        assert self._make_regel(RateLimitFenster.MINUTE).fenster_sekunden() == 60

    def test_stunde_returns_3600(self):
        assert self._make_regel(RateLimitFenster.STUNDE).fenster_sekunden() == 3600

    def test_tag_returns_86400(self):
        assert self._make_regel(RateLimitFenster.TAG).fenster_sekunden() == 86400

    def test_regel_beschreibung_default_empty(self):
        r = RateLimitRegel("R", RateLimitGranularitaet.TENANT, RateLimitFenster.MINUTE, 100, 80)
        assert r.beschreibung == ""

    def test_regel_beschreibung_set(self):
        r = RateLimitRegel("R", RateLimitGranularitaet.TENANT, RateLimitFenster.MINUTE, 100, 80, "Test")
        assert r.beschreibung == "Test"


# ============================================================
# RateLimitZaehler.ist_fenster_abgelaufen()
# ============================================================

class TestRateLimitZaehlerFensterAbgelaufen:
    def _make_zaehler(self, beginn: datetime):
        return RateLimitZaehler("Z", "R", 0, beginn)

    def test_not_expired_within_window(self):
        jetzt = datetime(2026, 3, 16, 10, 0, 0)
        beginn = datetime(2026, 3, 16, 9, 59, 30)  # 30s ago, window=60s
        z = self._make_zaehler(beginn)
        assert z.ist_fenster_abgelaufen(jetzt, 60) is False

    def test_expired_past_window(self):
        jetzt = datetime(2026, 3, 16, 10, 0, 0)
        beginn = datetime(2026, 3, 16, 9, 58, 59)  # 61s ago, window=60s
        z = self._make_zaehler(beginn)
        assert z.ist_fenster_abgelaufen(jetzt, 60) is True

    def test_exactly_at_boundary_expired(self):
        jetzt = datetime(2026, 3, 16, 10, 0, 0)
        beginn = jetzt - timedelta(seconds=60)
        z = self._make_zaehler(beginn)
        assert z.ist_fenster_abgelaufen(jetzt, 60) is True

    def test_one_second_before_expiry(self):
        jetzt = datetime(2026, 3, 16, 10, 0, 0)
        beginn = jetzt - timedelta(seconds=59)
        z = self._make_zaehler(beginn)
        assert z.ist_fenster_abgelaufen(jetzt, 60) is False

    def test_tag_window_not_expired(self):
        jetzt = datetime(2026, 3, 16, 10, 0, 0)
        beginn = jetzt - timedelta(hours=12)
        z = self._make_zaehler(beginn)
        assert z.ist_fenster_abgelaufen(jetzt, 86400) is False

    def test_tag_window_expired(self):
        jetzt = datetime(2026, 3, 16, 10, 0, 0)
        beginn = jetzt - timedelta(hours=25)
        z = self._make_zaehler(beginn)
        assert z.ist_fenster_abgelaufen(jetzt, 86400) is True


# ============================================================
# RateLimitZaehler.pruefe_und_inkrementiere()
# ============================================================

class TestRateLimitZaehlerPruefeUndInkrementiere:
    def _make_regel(self, max_anfragen=100, weich_limit=80, fenster=RateLimitFenster.MINUTE):
        return RateLimitRegel("R", RateLimitGranularitaet.TENANT, fenster, max_anfragen, weich_limit)

    def _make_zaehler(self, anfragen=0, abgelaufen=False, fenster_sek=60):
        jetzt = datetime(2026, 3, 16, 10, 0, 0)
        if abgelaufen:
            beginn = jetzt - timedelta(seconds=fenster_sek + 1)
        else:
            beginn = jetzt
        return RateLimitZaehler("Z", "R", anfragen, beginn)

    def test_expired_window_resets_to_1_erlaubt(self):
        jetzt = datetime(2026, 3, 16, 10, 0, 0)
        regel = self._make_regel()
        z = self._make_zaehler(50, abgelaufen=True)
        ergebnis, neuer = z.pruefe_und_inkrementiere(regel, jetzt)
        assert ergebnis == RateLimitErgebnis.ERLAUBT
        assert neuer.anfragen_im_fenster == 1
        assert neuer.fenster_beginn == jetzt

    def test_expired_window_original_unchanged(self):
        jetzt = datetime(2026, 3, 16, 10, 0, 0)
        regel = self._make_regel()
        z = self._make_zaehler(50, abgelaufen=True)
        _, _ = z.pruefe_und_inkrementiere(regel, jetzt)
        assert z.anfragen_im_fenster == 50  # unchanged

    def test_first_request_erlaubt(self):
        jetzt = datetime(2026, 3, 16, 10, 0, 0)
        regel = self._make_regel(100, 80)
        z = self._make_zaehler(0)
        ergebnis, neuer = z.pruefe_und_inkrementiere(regel, jetzt)
        assert ergebnis == RateLimitErgebnis.ERLAUBT
        assert neuer.anfragen_im_fenster == 1

    def test_below_weich_limit_erlaubt(self):
        jetzt = datetime(2026, 3, 16, 10, 0, 0)
        regel = self._make_regel(100, 80)
        z = self._make_zaehler(50)
        ergebnis, neuer = z.pruefe_und_inkrementiere(regel, jetzt)
        assert ergebnis == RateLimitErgebnis.ERLAUBT
        assert neuer.anfragen_im_fenster == 51

    def test_at_weich_limit_gedrosselt(self):
        # 80 + 1 = 81 > 80 → GEDROSSELT
        jetzt = datetime(2026, 3, 16, 10, 0, 0)
        regel = self._make_regel(100, 80)
        z = self._make_zaehler(80)
        ergebnis, neuer = z.pruefe_und_inkrementiere(regel, jetzt)
        assert ergebnis == RateLimitErgebnis.GEDROSSELT
        assert neuer.anfragen_im_fenster == 81

    def test_at_max_anfragen_blockiert(self):
        # 100 + 1 = 101 > 100 → BLOCKIERT
        jetzt = datetime(2026, 3, 16, 10, 0, 0)
        regel = self._make_regel(100, 80)
        z = self._make_zaehler(100)
        ergebnis, neuer = z.pruefe_und_inkrementiere(regel, jetzt)
        assert ergebnis == RateLimitErgebnis.BLOCKIERT

    def test_blockiert_does_not_increment(self):
        jetzt = datetime(2026, 3, 16, 10, 0, 0)
        regel = self._make_regel(100, 80)
        z = self._make_zaehler(100)
        _, neuer = z.pruefe_und_inkrementiere(regel, jetzt)
        assert neuer.anfragen_im_fenster == 100  # unchanged

    def test_gedrosselt_increments_counter(self):
        jetzt = datetime(2026, 3, 16, 10, 0, 0)
        regel = self._make_regel(100, 80)
        z = self._make_zaehler(90)
        ergebnis, neuer = z.pruefe_und_inkrementiere(regel, jetzt)
        assert ergebnis == RateLimitErgebnis.GEDROSSELT
        assert neuer.anfragen_im_fenster == 91

    def test_exactly_weich_limit_plus_1_gedrosselt(self):
        jetzt = datetime(2026, 3, 16, 10, 0, 0)
        regel = self._make_regel(100, 80)
        z = self._make_zaehler(80)  # 80+1=81 > 80
        ergebnis, _ = z.pruefe_und_inkrementiere(regel, jetzt)
        assert ergebnis == RateLimitErgebnis.GEDROSSELT

    def test_exactly_max_plus_1_blockiert(self):
        jetzt = datetime(2026, 3, 16, 10, 0, 0)
        regel = self._make_regel(100, 80)
        z = self._make_zaehler(100)  # 100+1=101 > 100
        ergebnis, _ = z.pruefe_und_inkrementiere(regel, jetzt)
        assert ergebnis == RateLimitErgebnis.BLOCKIERT

    def test_immutability_original_unchanged_on_erlaubt(self):
        jetzt = datetime(2026, 3, 16, 10, 0, 0)
        regel = self._make_regel(100, 80)
        z = self._make_zaehler(10)
        _, neuer = z.pruefe_und_inkrementiere(regel, jetzt)
        assert z.anfragen_im_fenster == 10
        assert neuer.anfragen_im_fenster == 11

    def test_immutability_original_unchanged_on_gedrosselt(self):
        jetzt = datetime(2026, 3, 16, 10, 0, 0)
        regel = self._make_regel(100, 80)
        z = self._make_zaehler(85)
        _, neuer = z.pruefe_und_inkrementiere(regel, jetzt)
        assert z.anfragen_im_fenster == 85
        assert neuer.anfragen_im_fenster == 86

    def test_sekunde_window(self):
        jetzt = datetime(2026, 3, 16, 10, 0, 0)
        regel = self._make_regel(50, 40, RateLimitFenster.SEKUNDE)
        beginn = jetzt - timedelta(seconds=2)
        z = RateLimitZaehler("Z", "R", 30, beginn)
        ergebnis, neuer = z.pruefe_und_inkrementiere(regel, jetzt)
        assert ergebnis == RateLimitErgebnis.ERLAUBT
        assert neuer.anfragen_im_fenster == 1

    def test_high_counter_blockiert(self):
        jetzt = datetime(2026, 3, 16, 10, 0, 0)
        regel = self._make_regel(1000, 800)
        z = self._make_zaehler(999)
        ergebnis, neuer = z.pruefe_und_inkrementiere(regel, jetzt)
        assert ergebnis == RateLimitErgebnis.GEDROSSELT  # 1000 > 800 but <= 1000

    def test_one_over_max_blockiert_exactly(self):
        jetzt = datetime(2026, 3, 16, 10, 0, 0)
        regel = self._make_regel(1000, 800)
        z = self._make_zaehler(1000)  # 1001 > 1000 → BLOCKIERT
        ergebnis, _ = z.pruefe_und_inkrementiere(regel, jetzt)
        assert ergebnis == RateLimitErgebnis.BLOCKIERT


# ============================================================
# get_default_rate_limit_regeln()
# ============================================================

class TestGetDefaultRateLimitRegeln:
    def setup_method(self):
        self.regeln = get_default_rate_limit_regeln()

    def test_returns_5_rules(self):
        assert len(self.regeln) == 5

    def test_all_are_regel_instances(self):
        for r in self.regeln:
            assert isinstance(r, RateLimitRegel)

    def test_rl001_id(self):
        assert self.regeln[0].regel_id == "RL-001"

    def test_rl002_id(self):
        assert self.regeln[1].regel_id == "RL-002"

    def test_rl003_id(self):
        assert self.regeln[2].regel_id == "RL-003"

    def test_rl004_id(self):
        assert self.regeln[3].regel_id == "RL-004"

    def test_rl005_id(self):
        assert self.regeln[4].regel_id == "RL-005"

    def test_rl001_granularitaet_tenant(self):
        assert self.regeln[0].granularitaet == RateLimitGranularitaet.TENANT

    def test_rl002_granularitaet_benutzer(self):
        assert self.regeln[1].granularitaet == RateLimitGranularitaet.BENUTZER

    def test_rl003_granularitaet_endpunkt(self):
        assert self.regeln[2].granularitaet == RateLimitGranularitaet.ENDPUNKT

    def test_rl004_granularitaet_global(self):
        assert self.regeln[3].granularitaet == RateLimitGranularitaet.GLOBAL

    def test_rl005_granularitaet_tenant(self):
        assert self.regeln[4].granularitaet == RateLimitGranularitaet.TENANT

    def test_rl001_fenster_minute(self):
        assert self.regeln[0].fenster == RateLimitFenster.MINUTE

    def test_rl003_fenster_sekunde(self):
        assert self.regeln[2].fenster == RateLimitFenster.SEKUNDE

    def test_rl004_fenster_stunde(self):
        assert self.regeln[3].fenster == RateLimitFenster.STUNDE

    def test_rl005_fenster_tag(self):
        assert self.regeln[4].fenster == RateLimitFenster.TAG

    def test_rl001_max_anfragen(self):
        assert self.regeln[0].max_anfragen == 1000

    def test_rl001_weich_limit(self):
        assert self.regeln[0].weich_limit == 800

    def test_rl002_max_anfragen(self):
        assert self.regeln[1].max_anfragen == 100

    def test_rl002_weich_limit(self):
        assert self.regeln[1].weich_limit == 80

    def test_rl003_max_anfragen(self):
        assert self.regeln[2].max_anfragen == 50

    def test_rl003_weich_limit(self):
        assert self.regeln[2].weich_limit == 40

    def test_rl004_max_anfragen(self):
        assert self.regeln[3].max_anfragen == 100000

    def test_rl004_weich_limit(self):
        assert self.regeln[3].weich_limit == 80000

    def test_rl005_max_anfragen(self):
        assert self.regeln[4].max_anfragen == 50000

    def test_rl005_weich_limit(self):
        assert self.regeln[4].weich_limit == 40000

    def test_all_have_beschreibung(self):
        for r in self.regeln:
            assert len(r.beschreibung) > 0

    def test_fenster_sekunden_rl001(self):
        assert self.regeln[0].fenster_sekunden() == 60

    def test_fenster_sekunden_rl003(self):
        assert self.regeln[2].fenster_sekunden() == 1

    def test_fenster_sekunden_rl004(self):
        assert self.regeln[3].fenster_sekunden() == 3600

    def test_fenster_sekunden_rl005(self):
        assert self.regeln[4].fenster_sekunden() == 86400


# ============================================================
# IdempotenzStatus enum
# ============================================================

class TestIdempotenzStatusEnum:
    def test_neu_value(self):
        assert IdempotenzStatus.NEU == "NEU"

    def test_duplikat_value(self):
        assert IdempotenzStatus.DUPLIKAT == "DUPLIKAT"

    def test_verarbeitung_value(self):
        assert IdempotenzStatus.VERARBEITUNG == "VERARBEITUNG"

    def test_fehlgeschlagen_value(self):
        assert IdempotenzStatus.FEHLGESCHLAGEN == "FEHLGESCHLAGEN"

    def test_abgelaufen_value(self):
        assert IdempotenzStatus.ABGELAUFEN == "ABGELAUFEN"

    def test_all_members(self):
        assert len(IdempotenzStatus) == 5


# ============================================================
# IdempotenzEintrag.ist_abgelaufen() + aktueller_status()
# ============================================================

class TestIdempotenzEintragStatus:
    def _make_eintrag(self, erstellt_vor_sekunden, ttl=86400, status=IdempotenzStatus.DUPLIKAT):
        jetzt = datetime(2026, 3, 16, 10, 0, 0)
        erstellt = jetzt - timedelta(seconds=erstellt_vor_sekunden)
        return IdempotenzEintrag("K", "cmd", "T", status, {}, erstellt, None, ttl)

    def test_not_expired_within_ttl(self):
        jetzt = datetime(2026, 3, 16, 10, 0, 0)
        e = self._make_eintrag(3600)  # 1h ago, ttl=24h
        assert e.ist_abgelaufen(jetzt) is False

    def test_expired_past_ttl(self):
        jetzt = datetime(2026, 3, 16, 10, 0, 0)
        e = self._make_eintrag(86401)  # 24h+1s ago, ttl=24h
        assert e.ist_abgelaufen(jetzt) is True

    def test_not_expired_returns_actual_status(self):
        jetzt = datetime(2026, 3, 16, 10, 0, 0)
        e = self._make_eintrag(3600, status=IdempotenzStatus.DUPLIKAT)
        assert e.aktueller_status(jetzt) == IdempotenzStatus.DUPLIKAT

    def test_expired_returns_abgelaufen(self):
        jetzt = datetime(2026, 3, 16, 10, 0, 0)
        e = self._make_eintrag(86401, status=IdempotenzStatus.DUPLIKAT)
        assert e.aktueller_status(jetzt) == IdempotenzStatus.ABGELAUFEN

    def test_verarbeitung_not_expired(self):
        jetzt = datetime(2026, 3, 16, 10, 0, 0)
        e = self._make_eintrag(100, status=IdempotenzStatus.VERARBEITUNG)
        assert e.aktueller_status(jetzt) == IdempotenzStatus.VERARBEITUNG

    def test_fehlgeschlagen_not_expired(self):
        jetzt = datetime(2026, 3, 16, 10, 0, 0)
        e = self._make_eintrag(100, status=IdempotenzStatus.FEHLGESCHLAGEN)
        assert e.aktueller_status(jetzt) == IdempotenzStatus.FEHLGESCHLAGEN

    def test_neu_not_expired(self):
        jetzt = datetime(2026, 3, 16, 10, 0, 0)
        e = self._make_eintrag(100, status=IdempotenzStatus.NEU)
        assert e.aktueller_status(jetzt) == IdempotenzStatus.NEU

    def test_short_ttl_expired(self):
        jetzt = datetime(2026, 3, 16, 10, 0, 0)
        e = self._make_eintrag(3601, ttl=3600)
        assert e.ist_abgelaufen(jetzt) is True

    def test_short_ttl_not_expired(self):
        jetzt = datetime(2026, 3, 16, 10, 0, 0)
        e = self._make_eintrag(3599, ttl=3600)
        assert e.ist_abgelaufen(jetzt) is False


# ============================================================
# pruefe_idempotenz() — STRIKTE_EINMALIGKEIT
# ============================================================

class TestPruefeIdempotenzStrikteEinmaligkeit:
    def setup_method(self):
        self.jetzt = datetime(2026, 3, 16, 10, 0, 0)
        self.strategie = DeduplizierungsStrategie.STRIKTE_EINMALIGKEIT
        self.eintraege = [
            IdempotenzEintrag("KEY-DUP", "cmd", "T", IdempotenzStatus.DUPLIKAT,
                              {"result": "ok"}, self.jetzt, self.jetzt, 86400),
            IdempotenzEintrag("KEY-VER", "cmd", "T", IdempotenzStatus.VERARBEITUNG,
                              {}, self.jetzt, None, 86400),
            IdempotenzEintrag("KEY-FAIL", "cmd", "T", IdempotenzStatus.FEHLGESCHLAGEN,
                              {}, self.jetzt, self.jetzt, 86400),
            IdempotenzEintrag("KEY-NEU", "cmd", "T", IdempotenzStatus.NEU,
                              {}, self.jetzt, None, 86400),
            IdempotenzEintrag("KEY-OLD", "cmd", "T", IdempotenzStatus.DUPLIKAT,
                              {}, self.jetzt - timedelta(days=2), None, 86400),
        ]

    def test_unknown_key_neu_soll_verarbeiten(self):
        p = pruefe_idempotenz("UNKNOWN", self.eintraege, self.strategie, self.jetzt)
        assert p.soll_verarbeiten is True
        assert p.status == IdempotenzStatus.NEU

    def test_unknown_key_no_stored_result(self):
        p = pruefe_idempotenz("UNKNOWN", self.eintraege, self.strategie, self.jetzt)
        assert p.gespeichertes_ergebnis is None

    def test_duplikat_soll_nicht_verarbeiten(self):
        p = pruefe_idempotenz("KEY-DUP", self.eintraege, self.strategie, self.jetzt)
        assert p.soll_verarbeiten is False

    def test_duplikat_returns_stored_result(self):
        p = pruefe_idempotenz("KEY-DUP", self.eintraege, self.strategie, self.jetzt)
        assert p.gespeichertes_ergebnis == {"result": "ok"}
        assert p.status == IdempotenzStatus.DUPLIKAT

    def test_verarbeitung_soll_nicht_verarbeiten(self):
        p = pruefe_idempotenz("KEY-VER", self.eintraege, self.strategie, self.jetzt)
        assert p.soll_verarbeiten is False
        assert p.status == IdempotenzStatus.VERARBEITUNG

    def test_fehlgeschlagen_soll_nicht_verarbeiten(self):
        p = pruefe_idempotenz("KEY-FAIL", self.eintraege, self.strategie, self.jetzt)
        assert p.soll_verarbeiten is False
        assert p.status == IdempotenzStatus.FEHLGESCHLAGEN

    def test_abgelaufen_soll_verarbeiten(self):
        p = pruefe_idempotenz("KEY-OLD", self.eintraege, self.strategie, self.jetzt)
        assert p.soll_verarbeiten is True
        assert p.status == IdempotenzStatus.ABGELAUFEN

    def test_schluessel_echoed_back(self):
        p = pruefe_idempotenz("KEY-DUP", self.eintraege, self.strategie, self.jetzt)
        assert p.schluessel == "KEY-DUP"

    def test_neu_status_soll_nicht_verarbeiten_strikte(self):
        # NEU key that exists in the list — STRIKTE_EINMALIGKEIT blocks it
        p = pruefe_idempotenz("KEY-NEU", self.eintraege, self.strategie, self.jetzt)
        assert p.soll_verarbeiten is False
        assert p.status == IdempotenzStatus.NEU


# ============================================================
# pruefe_idempotenz() — WIEDERHOLUNG_BEI_FEHLER
# ============================================================

class TestPruefeIdempotenzWiederholungBeiFehler:
    def setup_method(self):
        self.jetzt = datetime(2026, 3, 16, 10, 0, 0)
        self.strategie = DeduplizierungsStrategie.WIEDERHOLUNG_BEI_FEHLER
        self.eintraege = [
            IdempotenzEintrag("KEY-DUP", "cmd", "T", IdempotenzStatus.DUPLIKAT,
                              {"result": "ok"}, self.jetzt, self.jetzt, 86400),
            IdempotenzEintrag("KEY-VER", "cmd", "T", IdempotenzStatus.VERARBEITUNG,
                              {}, self.jetzt, None, 86400),
            IdempotenzEintrag("KEY-FAIL", "cmd", "T", IdempotenzStatus.FEHLGESCHLAGEN,
                              {}, self.jetzt, self.jetzt, 86400),
            IdempotenzEintrag("KEY-OLD", "cmd", "T", IdempotenzStatus.DUPLIKAT,
                              {}, self.jetzt - timedelta(days=2), None, 86400),
        ]

    def test_fehlgeschlagen_soll_verarbeiten(self):
        p = pruefe_idempotenz("KEY-FAIL", self.eintraege, self.strategie, self.jetzt)
        assert p.soll_verarbeiten is True
        assert p.status == IdempotenzStatus.FEHLGESCHLAGEN

    def test_duplikat_soll_nicht_verarbeiten(self):
        p = pruefe_idempotenz("KEY-DUP", self.eintraege, self.strategie, self.jetzt)
        assert p.soll_verarbeiten is False
        assert p.status == IdempotenzStatus.DUPLIKAT

    def test_duplikat_returns_stored_result(self):
        p = pruefe_idempotenz("KEY-DUP", self.eintraege, self.strategie, self.jetzt)
        assert p.gespeichertes_ergebnis == {"result": "ok"}

    def test_verarbeitung_soll_nicht_verarbeiten(self):
        p = pruefe_idempotenz("KEY-VER", self.eintraege, self.strategie, self.jetzt)
        assert p.soll_verarbeiten is False
        assert p.status == IdempotenzStatus.VERARBEITUNG

    def test_unknown_key_soll_verarbeiten(self):
        p = pruefe_idempotenz("UNKNOWN", self.eintraege, self.strategie, self.jetzt)
        assert p.soll_verarbeiten is True
        assert p.status == IdempotenzStatus.NEU

    def test_abgelaufen_soll_verarbeiten(self):
        p = pruefe_idempotenz("KEY-OLD", self.eintraege, self.strategie, self.jetzt)
        assert p.soll_verarbeiten is True
        assert p.status == IdempotenzStatus.ABGELAUFEN

    def test_fehlgeschlagen_no_stored_result_returned(self):
        p = pruefe_idempotenz("KEY-FAIL", self.eintraege, self.strategie, self.jetzt)
        assert p.gespeichertes_ergebnis is None


# ============================================================
# pruefe_idempotenz() — ZEITFENSTER
# ============================================================

class TestPruefeIdempotenzZeitfenster:
    def setup_method(self):
        self.jetzt = datetime(2026, 3, 16, 10, 0, 0)
        self.strategie = DeduplizierungsStrategie.ZEITFENSTER
        self.eintraege = [
            IdempotenzEintrag("KEY-DUP", "cmd", "T", IdempotenzStatus.DUPLIKAT,
                              {"result": "ok"}, self.jetzt, self.jetzt, 86400),
            IdempotenzEintrag("KEY-FAIL", "cmd", "T", IdempotenzStatus.FEHLGESCHLAGEN,
                              {}, self.jetzt, self.jetzt, 86400),
            IdempotenzEintrag("KEY-NEU", "cmd", "T", IdempotenzStatus.NEU,
                              {}, self.jetzt, None, 86400),
            IdempotenzEintrag("KEY-OLD", "cmd", "T", IdempotenzStatus.DUPLIKAT,
                              {}, self.jetzt - timedelta(days=2), None, 86400),
        ]

    def test_duplikat_soll_nicht_verarbeiten(self):
        p = pruefe_idempotenz("KEY-DUP", self.eintraege, self.strategie, self.jetzt)
        assert p.soll_verarbeiten is False
        assert p.status == IdempotenzStatus.DUPLIKAT

    def test_abgelaufen_soll_verarbeiten(self):
        p = pruefe_idempotenz("KEY-OLD", self.eintraege, self.strategie, self.jetzt)
        assert p.soll_verarbeiten is True
        assert p.status == IdempotenzStatus.ABGELAUFEN

    def test_fehlgeschlagen_within_window_soll_verarbeiten(self):
        p = pruefe_idempotenz("KEY-FAIL", self.eintraege, self.strategie, self.jetzt)
        assert p.soll_verarbeiten is True
        assert p.status == IdempotenzStatus.FEHLGESCHLAGEN

    def test_neu_within_window_soll_verarbeiten(self):
        p = pruefe_idempotenz("KEY-NEU", self.eintraege, self.strategie, self.jetzt)
        assert p.soll_verarbeiten is True
        assert p.status == IdempotenzStatus.NEU

    def test_unknown_key_soll_verarbeiten(self):
        p = pruefe_idempotenz("UNKNOWN", self.eintraege, self.strategie, self.jetzt)
        assert p.soll_verarbeiten is True
        assert p.status == IdempotenzStatus.NEU

    def test_duplikat_returns_stored_result(self):
        p = pruefe_idempotenz("KEY-DUP", self.eintraege, self.strategie, self.jetzt)
        assert p.gespeichertes_ergebnis == {"result": "ok"}


# ============================================================
# get_default_idempotenz_eintraege()
# ============================================================

class TestGetDefaultIdempotenzEintraege:
    def setup_method(self):
        self.eintraege = get_default_idempotenz_eintraege()
        self.jetzt = datetime(2026, 3, 16, 10, 0, 0)

    def test_returns_5_entries(self):
        assert len(self.eintraege) == 5

    def test_all_are_eintrag_instances(self):
        for e in self.eintraege:
            assert isinstance(e, IdempotenzEintrag)

    def test_key001_schluessel(self):
        assert self.eintraege[0].schluessel == "KEY-001"

    def test_key002_schluessel(self):
        assert self.eintraege[1].schluessel == "KEY-002"

    def test_key003_schluessel(self):
        assert self.eintraege[2].schluessel == "KEY-003"

    def test_key004_schluessel(self):
        assert self.eintraege[3].schluessel == "KEY-004"

    def test_key005_schluessel(self):
        assert self.eintraege[4].schluessel == "KEY-005-ALT"

    def test_key001_status_duplikat(self):
        assert self.eintraege[0].status == IdempotenzStatus.DUPLIKAT

    def test_key002_status_verarbeitung(self):
        assert self.eintraege[1].status == IdempotenzStatus.VERARBEITUNG

    def test_key003_status_fehlgeschlagen(self):
        assert self.eintraege[2].status == IdempotenzStatus.FEHLGESCHLAGEN

    def test_key004_status_neu(self):
        assert self.eintraege[3].status == IdempotenzStatus.NEU

    def test_key005_status_duplikat(self):
        assert self.eintraege[4].status == IdempotenzStatus.DUPLIKAT

    def test_key005_is_expired(self):
        e = self.eintraege[4]
        assert e.ist_abgelaufen(self.jetzt) is True

    def test_key001_not_expired(self):
        assert self.eintraege[0].ist_abgelaufen(self.jetzt) is False

    def test_key001_aktueller_status_duplikat(self):
        assert self.eintraege[0].aktueller_status(self.jetzt) == IdempotenzStatus.DUPLIKAT

    def test_key005_aktueller_status_abgelaufen(self):
        assert self.eintraege[4].aktueller_status(self.jetzt) == IdempotenzStatus.ABGELAUFEN

    def test_key001_ergebnis_nutzlast(self):
        assert self.eintraege[0].ergebnis_nutzlast == {"kontrakt_id": "K-001"}

    def test_key003_ergebnis_nutzlast(self):
        assert self.eintraege[2].ergebnis_nutzlast == {"fehler": "DB-Fehler"}

    def test_key001_tenant_a(self):
        assert self.eintraege[0].tenant_id == "TENANT-A"

    def test_key003_tenant_b(self):
        assert self.eintraege[2].tenant_id == "TENANT-B"

    def test_key001_befehl_typ(self):
        assert self.eintraege[0].befehl_typ == "kontrakt_erstellen"

    def test_key002_befehl_typ(self):
        assert self.eintraege[1].befehl_typ == "settlement_ausfuehren"

    def test_key004_ttl(self):
        assert self.eintraege[3].ttl_sekunden == 86400

    def test_key002_ttl_shorter(self):
        assert self.eintraege[1].ttl_sekunden == 3600

    def test_key004_no_verarbeitet_am(self):
        assert self.eintraege[3].verarbeitet_am is None

    def test_key001_verarbeitet_am_set(self):
        assert self.eintraege[0].verarbeitet_am is not None

    def test_key005_created_2_days_before(self):
        e = self.eintraege[4]
        diff = (self.jetzt - e.erstellt_am).total_seconds()
        assert diff > 86400 * 1.5  # clearly more than 1 day


# ============================================================
# IdempotenzPruefung dataclass
# ============================================================

class TestIdempotenzPruefungDataclass:
    def test_basic_construction(self):
        p = IdempotenzPruefung("K", True, IdempotenzStatus.NEU)
        assert p.schluessel == "K"
        assert p.soll_verarbeiten is True
        assert p.status == IdempotenzStatus.NEU
        assert p.gespeichertes_ergebnis is None

    def test_with_stored_result(self):
        p = IdempotenzPruefung("K", False, IdempotenzStatus.DUPLIKAT, {"x": 1})
        assert p.gespeichertes_ergebnis == {"x": 1}

    def test_soll_verarbeiten_false(self):
        p = IdempotenzPruefung("K", False, IdempotenzStatus.VERARBEITUNG)
        assert p.soll_verarbeiten is False


# ============================================================
# DeduplizierungsStrategie enum
# ============================================================

class TestDeduplizierungsStrategieEnum:
    def test_strikte_einmaligkeit(self):
        assert DeduplizierungsStrategie.STRIKTE_EINMALIGKEIT == "STRIKTE_EINMALIGKEIT"

    def test_wiederholung_bei_fehler(self):
        assert DeduplizierungsStrategie.WIEDERHOLUNG_BEI_FEHLER == "WIEDERHOLUNG_BEI_FEHLER"

    def test_zeitfenster(self):
        assert DeduplizierungsStrategie.ZEITFENSTER == "ZEITFENSTER"

    def test_all_members(self):
        assert len(DeduplizierungsStrategie) == 3


# ============================================================
# Additional edge-case / integration tests
# ============================================================

class TestIntegrationRateLimit:
    def test_sequence_erlaubt_then_gedrosselt_then_blockiert(self):
        """Simulate increasing load through all three states."""
        jetzt = datetime(2026, 3, 16, 10, 0, 0)
        regel = RateLimitRegel("R", RateLimitGranularitaet.TENANT, RateLimitFenster.MINUTE, 5, 3)
        z = RateLimitZaehler("Z", "R", 0, jetzt)

        # Requests 1-3 → ERLAUBT
        for i in range(3):
            ergebnis, z = z.pruefe_und_inkrementiere(regel, jetzt)
            assert ergebnis == RateLimitErgebnis.ERLAUBT

        # Requests 4-5 → GEDROSSELT
        for i in range(2):
            ergebnis, z = z.pruefe_und_inkrementiere(regel, jetzt)
            assert ergebnis == RateLimitErgebnis.GEDROSSELT

        # Request 6 → BLOCKIERT
        ergebnis, z = z.pruefe_und_inkrementiere(regel, jetzt)
        assert ergebnis == RateLimitErgebnis.BLOCKIERT
        assert z.anfragen_im_fenster == 5  # not incremented

    def test_window_reset_after_expiry(self):
        """After window expires, counter resets and ERLAUBT again."""
        jetzt = datetime(2026, 3, 16, 10, 0, 0)
        spaeter = jetzt + timedelta(seconds=61)
        regel = RateLimitRegel("R", RateLimitGranularitaet.TENANT, RateLimitFenster.MINUTE, 5, 3)
        z = RateLimitZaehler("Z", "R", 5, jetzt)

        # Currently at max
        ergebnis, z2 = z.pruefe_und_inkrementiere(regel, jetzt)
        assert ergebnis == RateLimitErgebnis.BLOCKIERT

        # After window expires
        ergebnis, z3 = z.pruefe_und_inkrementiere(regel, spaeter)
        assert ergebnis == RateLimitErgebnis.ERLAUBT
        assert z3.anfragen_im_fenster == 1


class TestIntegrationIdempotenz:
    def test_new_command_then_mark_as_processed(self):
        """Simulate processing a new command and verifying it becomes DUPLIKAT."""
        jetzt = datetime(2026, 3, 16, 10, 0, 0)
        eintraege = []

        # First check: key not known
        p = pruefe_idempotenz("NEW-KEY", eintraege, DeduplizierungsStrategie.STRIKTE_EINMALIGKEIT, jetzt)
        assert p.soll_verarbeiten is True
        assert p.status == IdempotenzStatus.NEU

        # After processing, add DUPLIKAT entry
        eintraege.append(IdempotenzEintrag("NEW-KEY", "cmd", "T", IdempotenzStatus.DUPLIKAT,
                                           {"result": "done"}, jetzt, jetzt, 86400))

        # Second check: now blocked
        p2 = pruefe_idempotenz("NEW-KEY", eintraege, DeduplizierungsStrategie.STRIKTE_EINMALIGKEIT, jetzt)
        assert p2.soll_verarbeiten is False
        assert p2.gespeichertes_ergebnis == {"result": "done"}

    def test_expired_entry_retriggered(self):
        """Expired entry should be re-processable across all strategies."""
        jetzt = datetime(2026, 3, 16, 10, 0, 0)
        old = jetzt - timedelta(days=2)
        eintraege = [
            IdempotenzEintrag("EXP-KEY", "cmd", "T", IdempotenzStatus.DUPLIKAT,
                              {"old": True}, old, old, 86400),
        ]
        for strategie in DeduplizierungsStrategie:
            p = pruefe_idempotenz("EXP-KEY", eintraege, strategie, jetzt)
            assert p.soll_verarbeiten is True, f"Expected soll_verarbeiten=True for {strategie}"
            assert p.status == IdempotenzStatus.ABGELAUFEN
