"""
Wave 67 Tests — Process Cache Contracts + Workflow Schema Migration Contracts
148+ pytest tests
"""
import pytest
from datetime import datetime, timedelta

# ─────────────────────────────────────────────────────────────────────────────
# Imports
# ─────────────────────────────────────────────────────────────────────────────
from app.core.process_cache_contracts import (
    CacheStrategie,
    CacheStatus,
    CacheEintrag,
    CacheKonfiguration,
    CacheStatistik,
    CacheInvalidierungsRegel,
    CACHE_REGELN,
)
from app.core.workflow_schema_migration_contracts import (
    SchemaKompatibilitaet,
    MigrationsStatus,
    FeldAenderungsTyp,
    FeldAenderung,
    SchemaVersion,
    MigrationsSchritt,
    SchemaMigration,
    SchemaRegistry,
    SCHEMA_VERSIONEN,
)

T0 = datetime(2026, 3, 1, 12, 0, 0)


# ─────────────────────────────────────────────────────────────────────────────
# Helper factories
# ─────────────────────────────────────────────────────────────────────────────
def make_eintrag(schluessel="key1", wert="val", ttl=None, tags=None, offset_sek=0):
    erstellt = T0 - timedelta(seconds=offset_sek)
    return CacheEintrag(
        schluessel=schluessel,
        wert=wert,
        erstellt_am=erstellt,
        letzter_zugriff=erstellt,
        ttl_sekunden=ttl,
        tags=tags or [],
    )


def make_schema_version(version="1.0.0", aenderungen=None):
    return SchemaVersion(
        schema_id="TEST",
        version=version,
        felder=["id", "name"],
        erstellt_am=T0,
        aenderungen=aenderungen or [],
    )


def make_migration(schritte=None, status=MigrationsStatus.AUSSTEHEND):
    return SchemaMigration(
        migrations_id="M-001",
        von_version="1.0.0",
        zu_version="2.0.0",
        schritte=schritte or [],
        status=status,
    )


# ─────────────────────────────────────────────────────────────────────────────
# CacheEintrag tests (30+)
# ─────────────────────────────────────────────────────────────────────────────
class TestCacheEintragStatus:
    def test_treffer_when_ttl_not_expired(self):
        e = make_eintrag(ttl=300, offset_sek=100)
        assert e.status(T0) == CacheStatus.TREFFER

    def test_veraltet_when_ttl_expired(self):
        e = make_eintrag(ttl=60, offset_sek=120)
        assert e.status(T0) == CacheStatus.VERALTET

    def test_treffer_when_no_ttl(self):
        e = make_eintrag(ttl=None, offset_sek=99999)
        assert e.status(T0) == CacheStatus.TREFFER

    def test_veraltet_just_over_boundary(self):
        # alter = ttl + 1 → VERALTET
        e = make_eintrag(ttl=100, offset_sek=101)
        assert e.status(T0) == CacheStatus.VERALTET

    def test_treffer_just_under_boundary(self):
        # alter = 99, ttl = 100 → TREFFER
        e = make_eintrag(ttl=100, offset_sek=99)
        assert e.status(T0) == CacheStatus.TREFFER

    def test_exact_at_boundary_veraltet(self):
        # alter == ttl → NOT > ttl → TREFFER (boundary: alter must be > ttl for VERALTET)
        e = make_eintrag(ttl=100, offset_sek=100)
        # alter == 100, ttl == 100 → 100 > 100 is False → TREFFER
        assert e.status(T0) == CacheStatus.TREFFER

    def test_just_over_boundary_is_veraltet(self):
        e = make_eintrag(ttl=100, offset_sek=101)
        assert e.status(T0) == CacheStatus.VERALTET

    def test_zero_ttl_immediately_veraltet(self):
        # alter > 0 when any positive offset
        e = make_eintrag(ttl=0, offset_sek=1)
        assert e.status(T0) == CacheStatus.VERALTET

    def test_none_ttl_never_veraltet(self):
        e = make_eintrag(ttl=None, offset_sek=1_000_000)
        assert e.status(T0) == CacheStatus.TREFFER

    def test_large_ttl_treffer(self):
        e = make_eintrag(ttl=86400, offset_sek=1000)
        assert e.status(T0) == CacheStatus.TREFFER

    def test_large_ttl_expired(self):
        e = make_eintrag(ttl=86400, offset_sek=86401)
        assert e.status(T0) == CacheStatus.VERALTET

    def test_status_uses_erstellt_am_not_letzter_zugriff(self):
        # Create entry "old" but letzter_zugriff recently
        e = CacheEintrag(
            schluessel="x",
            wert=1,
            erstellt_am=T0 - timedelta(seconds=200),
            letzter_zugriff=T0 - timedelta(seconds=10),  # recent access
            ttl_sekunden=100,
        )
        # alter based on erstellt_am = 200s > ttl 100s → VERALTET
        assert e.status(T0) == CacheStatus.VERALTET


class TestCacheEintragAktualisierung:
    def test_aktualisiere_zugriff_increments(self):
        e = make_eintrag()
        e2 = e.aktualisiere_zugriff(T0)
        assert e2.zugriffe == 1

    def test_aktualisiere_zugriff_twice(self):
        e = make_eintrag()
        e2 = e.aktualisiere_zugriff(T0)
        e3 = e2.aktualisiere_zugriff(T0)
        assert e3.zugriffe == 2

    def test_aktualisiere_zugriff_updates_letzter_zugriff(self):
        e = make_eintrag()
        jetzt = T0 + timedelta(seconds=60)
        e2 = e.aktualisiere_zugriff(jetzt)
        assert e2.letzter_zugriff == jetzt

    def test_aktualisiere_zugriff_immutable(self):
        e = make_eintrag()
        e2 = e.aktualisiere_zugriff(T0)
        assert e.zugriffe == 0  # original unchanged

    def test_aktualisiere_zugriff_preserves_schluessel(self):
        e = make_eintrag(schluessel="mykey")
        e2 = e.aktualisiere_zugriff(T0)
        assert e2.schluessel == "mykey"

    def test_aktualisiere_zugriff_preserves_ttl(self):
        e = make_eintrag(ttl=300)
        e2 = e.aktualisiere_zugriff(T0)
        assert e2.ttl_sekunden == 300

    def test_aktualisiere_zugriff_preserves_wert(self):
        e = make_eintrag(wert={"data": 42})
        e2 = e.aktualisiere_zugriff(T0)
        assert e2.wert == {"data": 42}

    def test_aktualisiere_zugriff_preserves_tags(self):
        e = make_eintrag(tags=["agrar", "kontrakt"])
        e2 = e.aktualisiere_zugriff(T0)
        assert e2.tags == ["agrar", "kontrakt"]


class TestCacheEintragTags:
    def test_tags_default_empty(self):
        e = CacheEintrag(
            schluessel="k", wert=None,
            erstellt_am=T0, letzter_zugriff=T0,
            ttl_sekunden=None,
        )
        assert e.tags == []

    def test_tags_stored_correctly(self):
        e = make_eintrag(tags=["a", "b", "c"])
        assert "a" in e.tags
        assert "b" in e.tags
        assert "c" in e.tags

    def test_tags_multiple(self):
        e = make_eintrag(tags=["finance", "report", "agrar"])
        assert len(e.tags) == 3

    def test_zugriffe_default_zero(self):
        e = make_eintrag()
        assert e.zugriffe == 0


# ─────────────────────────────────────────────────────────────────────────────
# CacheStatistik tests (15+)
# ─────────────────────────────────────────────────────────────────────────────
class TestCacheStatistik:
    def test_trefferquote_zero_when_no_requests(self):
        s = CacheStatistik(treffer=0, verfehlt=0, invalidierungen=0, evictions=0)
        assert s.trefferquote_pct() == 0.0

    def test_trefferquote_100_all_hits(self):
        s = CacheStatistik(treffer=100, verfehlt=0, invalidierungen=0, evictions=0)
        assert s.trefferquote_pct() == 100.0

    def test_trefferquote_0_all_misses(self):
        s = CacheStatistik(treffer=0, verfehlt=100, invalidierungen=0, evictions=0)
        assert s.trefferquote_pct() == 0.0

    def test_trefferquote_50_equal(self):
        s = CacheStatistik(treffer=50, verfehlt=50, invalidierungen=0, evictions=0)
        assert s.trefferquote_pct() == 50.0

    def test_trefferquote_75(self):
        s = CacheStatistik(treffer=75, verfehlt=25, invalidierungen=0, evictions=0)
        assert s.trefferquote_pct() == 75.0

    def test_trefferquote_33(self):
        s = CacheStatistik(treffer=1, verfehlt=2, invalidierungen=0, evictions=0)
        assert s.trefferquote_pct() == 33.33

    def test_trefferquote_rounds_to_2_decimal(self):
        s = CacheStatistik(treffer=2, verfehlt=3, invalidierungen=0, evictions=0)
        result = s.trefferquote_pct()
        assert result == round(2 / 5 * 100, 2)

    def test_invalidierungen_stored(self):
        s = CacheStatistik(treffer=10, verfehlt=5, invalidierungen=3, evictions=2)
        assert s.invalidierungen == 3

    def test_evictions_stored(self):
        s = CacheStatistik(treffer=10, verfehlt=5, invalidierungen=3, evictions=7)
        assert s.evictions == 7

    def test_trefferquote_single_hit(self):
        s = CacheStatistik(treffer=1, verfehlt=0, invalidierungen=0, evictions=0)
        assert s.trefferquote_pct() == 100.0

    def test_trefferquote_single_miss(self):
        s = CacheStatistik(treffer=0, verfehlt=1, invalidierungen=0, evictions=0)
        assert s.trefferquote_pct() == 0.0

    def test_trefferquote_large_numbers(self):
        s = CacheStatistik(treffer=9999, verfehlt=1, invalidierungen=0, evictions=0)
        result = s.trefferquote_pct()
        assert result == round(9999 / 10000 * 100, 2)

    def test_trefferquote_ignores_invalidierungen(self):
        s1 = CacheStatistik(treffer=50, verfehlt=50, invalidierungen=0, evictions=0)
        s2 = CacheStatistik(treffer=50, verfehlt=50, invalidierungen=100, evictions=50)
        assert s1.trefferquote_pct() == s2.trefferquote_pct()

    def test_trefferquote_type_float(self):
        s = CacheStatistik(treffer=3, verfehlt=1, invalidierungen=0, evictions=0)
        assert isinstance(s.trefferquote_pct(), float)

    def test_trefferquote_25(self):
        s = CacheStatistik(treffer=1, verfehlt=3, invalidierungen=0, evictions=0)
        assert s.trefferquote_pct() == 25.0


# ─────────────────────────────────────────────────────────────────────────────
# CacheInvalidierungsRegel tests (20+)
# ─────────────────────────────────────────────────────────────────────────────
class TestCacheInvalidierungsRegel:
    def _rule(self, tags=None, muster=None):
        return CacheInvalidierungsRegel(
            regel_id="R-001",
            tags=tags or [],
            muster=muster,
        )

    def test_trifft_zu_tag_overlap(self):
        r = self._rule(tags=["agrar"])
        e = make_eintrag(tags=["agrar", "finance"])
        assert r.trifft_zu(e) is True

    def test_trifft_zu_no_overlap(self):
        r = self._rule(tags=["agrar"])
        e = make_eintrag(tags=["finance", "report"])
        assert r.trifft_zu(e) is False

    def test_trifft_zu_key_prefix_match(self):
        r = self._rule(muster="agrar:")
        e = make_eintrag(schluessel="agrar:kontrakt:1")
        assert r.trifft_zu(e) is True

    def test_trifft_zu_key_prefix_no_match(self):
        r = self._rule(muster="agrar:")
        e = make_eintrag(schluessel="finance:report:1")
        assert r.trifft_zu(e) is False

    def test_trifft_zu_empty_tags_no_muster_false(self):
        r = self._rule(tags=[], muster=None)
        e = make_eintrag(tags=["any", "tag"], schluessel="any:key")
        assert r.trifft_zu(e) is False

    def test_trifft_zu_tag_wins_over_muster(self):
        r = self._rule(tags=["agrar"], muster="finance:")
        e = make_eintrag(tags=["agrar"], schluessel="finance:report")
        assert r.trifft_zu(e) is True

    def test_trifft_zu_muster_with_no_tags(self):
        r = self._rule(tags=[], muster="session:")
        e = make_eintrag(schluessel="session:user:42", tags=[])
        assert r.trifft_zu(e) is True

    def test_trifft_zu_empty_entry_tags(self):
        r = self._rule(tags=["agrar"])
        e = make_eintrag(tags=[])
        assert r.trifft_zu(e) is False

    def test_trifft_zu_multiple_rule_tags(self):
        r = self._rule(tags=["a", "b", "c"])
        e = make_eintrag(tags=["c"])
        assert r.trifft_zu(e) is True

    def test_trifft_zu_exact_prefix_match(self):
        r = self._rule(muster="report")
        e = make_eintrag(schluessel="report")
        assert r.trifft_zu(e) is True

    def test_trifft_zu_partial_prefix_not_match(self):
        # "rep" is NOT a prefix of "report:" if muster="repo:"
        r = self._rule(muster="repo:")
        e = make_eintrag(schluessel="report:1")
        assert r.trifft_zu(e) is False

    def test_trifft_zu_both_tag_and_prefix_false(self):
        r = self._rule(tags=["x"], muster="y:")
        e = make_eintrag(tags=["z"], schluessel="w:1")
        assert r.trifft_zu(e) is False

    def test_regel_beschreibung_default_empty(self):
        r = CacheInvalidierungsRegel(regel_id="R", tags=[])
        assert r.beschreibung == ""

    def test_regel_muster_default_none(self):
        r = CacheInvalidierungsRegel(regel_id="R", tags=[])
        assert r.muster is None

    def test_trifft_zu_tag_exact_match(self):
        r = self._rule(tags=["finance"])
        e = make_eintrag(tags=["finance"])
        assert r.trifft_zu(e) is True

    def test_trifft_zu_muster_longer_key(self):
        r = self._rule(muster="agrar:schlaege:")
        e = make_eintrag(schluessel="agrar:schlaege:123:details")
        assert r.trifft_zu(e) is True

    def test_trifft_zu_muster_shorter_key_no_match(self):
        r = self._rule(muster="agrar:schlaege:")
        e = make_eintrag(schluessel="agrar:")
        assert r.trifft_zu(e) is False

    def test_trifft_zu_multiple_tags_none_match(self):
        r = self._rule(tags=["a", "b", "c"])
        e = make_eintrag(tags=["d", "e"])
        assert r.trifft_zu(e) is False

    def test_trifft_zu_muster_empty_string_no_match(self):
        # Empty string muster is falsy → guard `if self.muster` skips prefix check
        r = self._rule(muster="")
        e = make_eintrag(schluessel="anything", tags=[])
        assert r.trifft_zu(e) is False

    def test_trifft_zu_none_muster_does_not_check_prefix(self):
        r = self._rule(tags=[], muster=None)
        e = make_eintrag(schluessel="agrar:kontrakt:1", tags=[])
        assert r.trifft_zu(e) is False


# ─────────────────────────────────────────────────────────────────────────────
# CACHE_REGELN tests (10+)
# ─────────────────────────────────────────────────────────────────────────────
class TestCacheRegeln:
    def test_five_configs_present(self):
        assert len(CACHE_REGELN) == 5

    def test_all_have_names(self):
        for r in CACHE_REGELN:
            assert r.name

    def test_unique_names(self):
        names = [r.name for r in CACHE_REGELN]
        assert len(set(names)) == 5

    def test_lru_config_no_ttl(self):
        lru = next(r for r in CACHE_REGELN if r.strategie == CacheStrategie.LRU)
        assert lru.default_ttl_sekunden is None

    def test_ttl_configs_have_ttl(self):
        ttl_configs = [r for r in CACHE_REGELN if r.strategie == CacheStrategie.TTL]
        for c in ttl_configs:
            assert c.default_ttl_sekunden is not None
            assert c.default_ttl_sekunden > 0

    def test_write_through_config_exists(self):
        wt = [r for r in CACHE_REGELN if r.strategie == CacheStrategie.WRITE_THROUGH]
        assert len(wt) == 1

    def test_write_back_config_exists(self):
        wb = [r for r in CACHE_REGELN if r.strategie == CacheStrategie.WRITE_BACK]
        assert len(wb) == 1

    def test_all_have_positive_max_eintraege(self):
        for r in CACHE_REGELN:
            assert r.max_eintraege > 0

    def test_prozessdaten_cache_ttl_300(self):
        p = next(r for r in CACHE_REGELN if "Prozessdaten" in r.name)
        assert p.default_ttl_sekunden == 300

    def test_bericht_cache_max_eintraege_2000(self):
        b = next(r for r in CACHE_REGELN if "Bericht" in r.name)
        assert b.max_eintraege == 2000

    def test_session_cache_ttl_900(self):
        s = next(r for r in CACHE_REGELN if "Session" in r.name)
        assert s.default_ttl_sekunden == 900

    def test_stammdaten_cache_lru(self):
        s = next(r for r in CACHE_REGELN if "Stammdaten" in r.name)
        assert s.strategie == CacheStrategie.LRU


# ─────────────────────────────────────────────────────────────────────────────
# FeldAenderung tests (20+)
# ─────────────────────────────────────────────────────────────────────────────
class TestFeldAenderung:
    def test_ist_brechend_entfernt(self):
        a = FeldAenderung("name", FeldAenderungsTyp.ENTFERNT)
        assert a.ist_brechend() is True

    def test_ist_brechend_typ_geaendert(self):
        a = FeldAenderung("status", FeldAenderungsTyp.TYP_GEAENDERT)
        assert a.ist_brechend() is True

    def test_ist_brechend_pflicht_gemacht(self):
        a = FeldAenderung("feld", FeldAenderungsTyp.PFLICHT_GEMACHT)
        assert a.ist_brechend() is True

    def test_nicht_brechend_hinzugefuegt(self):
        a = FeldAenderung("neues_feld", FeldAenderungsTyp.HINZUGEFUEGT)
        assert a.ist_brechend() is False

    def test_nicht_brechend_optional_gemacht(self):
        a = FeldAenderung("feld", FeldAenderungsTyp.OPTIONAL_GEMACHT)
        assert a.ist_brechend() is False

    def test_nicht_brechend_umbenannt(self):
        a = FeldAenderung("feld", FeldAenderungsTyp.UMBENANNT)
        assert a.ist_brechend() is False

    def test_alter_wert_stored(self):
        a = FeldAenderung("name", FeldAenderungsTyp.TYP_GEAENDERT, alter_wert="int", neuer_wert="str")
        assert a.alter_wert == "int"

    def test_neuer_wert_stored(self):
        a = FeldAenderung("name", FeldAenderungsTyp.TYP_GEAENDERT, alter_wert="int", neuer_wert="str")
        assert a.neuer_wert == "str"

    def test_migrations_ausdruck_default_none(self):
        a = FeldAenderung("name", FeldAenderungsTyp.HINZUGEFUEGT)
        assert a.migrations_ausdruck is None

    def test_migrations_ausdruck_stored(self):
        a = FeldAenderung("name", FeldAenderungsTyp.HINZUGEFUEGT, migrations_ausdruck="COALESCE(name, '')")
        assert a.migrations_ausdruck == "COALESCE(name, '')"

    def test_feld_name_stored(self):
        a = FeldAenderung("my_field", FeldAenderungsTyp.ENTFERNT)
        assert a.feld_name == "my_field"

    def test_alle_typen_definiert(self):
        typen = list(FeldAenderungsTyp)
        assert FeldAenderungsTyp.HINZUGEFUEGT in typen
        assert FeldAenderungsTyp.ENTFERNT in typen
        assert FeldAenderungsTyp.UMBENANNT in typen
        assert FeldAenderungsTyp.TYP_GEAENDERT in typen
        assert FeldAenderungsTyp.OPTIONAL_GEMACHT in typen
        assert FeldAenderungsTyp.PFLICHT_GEMACHT in typen

    def test_brechende_typen_count(self):
        brechend = [t for t in FeldAenderungsTyp
                    if FeldAenderung("x", t).ist_brechend()]
        assert len(brechend) == 3

    def test_nicht_brechende_typen_count(self):
        nicht_brechend = [t for t in FeldAenderungsTyp
                          if not FeldAenderung("x", t).ist_brechend()]
        assert len(nicht_brechend) == 3

    def test_alter_wert_default_none(self):
        a = FeldAenderung("f", FeldAenderungsTyp.ENTFERNT)
        assert a.alter_wert is None

    def test_neuer_wert_default_none(self):
        a = FeldAenderung("f", FeldAenderungsTyp.HINZUGEFUEGT)
        assert a.neuer_wert is None

    def test_hinzugefuegt_with_neuer_typ(self):
        a = FeldAenderung("f", FeldAenderungsTyp.HINZUGEFUEGT, neuer_wert="datetime")
        assert a.neuer_wert == "datetime"
        assert a.ist_brechend() is False

    def test_entfernt_always_brechend(self):
        a = FeldAenderung("critical_field", FeldAenderungsTyp.ENTFERNT,
                          alter_wert="str", migrations_ausdruck="NULL")
        assert a.ist_brechend() is True

    def test_umbenannt_not_brechend(self):
        a = FeldAenderung("name", FeldAenderungsTyp.UMBENANNT,
                          alter_wert="name", neuer_wert="bezeichnung")
        assert a.ist_brechend() is False


# ─────────────────────────────────────────────────────────────────────────────
# SchemaVersion tests (25+)
# ─────────────────────────────────────────────────────────────────────────────
class TestSchemaVersion:
    def test_version_tuple_1_0_0(self):
        v = make_schema_version("1.0.0")
        assert v.version_tuple() == (1, 0, 0)

    def test_version_tuple_2_1_0(self):
        v = make_schema_version("2.1.0")
        assert v.version_tuple() == (2, 1, 0)

    def test_version_tuple_3_0_0(self):
        v = make_schema_version("3.0.0")
        assert v.version_tuple() == (3, 0, 0)

    def test_version_tuple_10_2_5(self):
        v = make_schema_version("10.2.5")
        assert v.version_tuple() == (10, 2, 5)

    def test_kompatibilitaet_vollstaendig_no_changes(self):
        v = make_schema_version(aenderungen=[])
        assert v.berechne_kompatibilitaet() == SchemaKompatibilitaet.VOLLSTAENDIG

    def test_kompatibilitaet_rueckwaerts_only_hinzugefuegt(self):
        v = make_schema_version(aenderungen=[
            FeldAenderung("new_field", FeldAenderungsTyp.HINZUGEFUEGT),
        ])
        assert v.berechne_kompatibilitaet() == SchemaKompatibilitaet.RUECKWAERTS

    def test_kompatibilitaet_rueckwaerts_only_optional_gemacht(self):
        v = make_schema_version(aenderungen=[
            FeldAenderung("f", FeldAenderungsTyp.OPTIONAL_GEMACHT),
        ])
        assert v.berechne_kompatibilitaet() == SchemaKompatibilitaet.RUECKWAERTS

    def test_kompatibilitaet_keine_entfernt(self):
        v = make_schema_version(aenderungen=[
            FeldAenderung("name", FeldAenderungsTyp.ENTFERNT),
        ])
        assert v.berechne_kompatibilitaet() == SchemaKompatibilitaet.KEINE

    def test_kompatibilitaet_keine_typ_geaendert(self):
        v = make_schema_version(aenderungen=[
            FeldAenderung("status", FeldAenderungsTyp.TYP_GEAENDERT),
        ])
        assert v.berechne_kompatibilitaet() == SchemaKompatibilitaet.KEINE

    def test_kompatibilitaet_keine_pflicht_gemacht(self):
        v = make_schema_version(aenderungen=[
            FeldAenderung("f", FeldAenderungsTyp.PFLICHT_GEMACHT),
        ])
        assert v.berechne_kompatibilitaet() == SchemaKompatibilitaet.KEINE

    def test_kompatibilitaet_keine_mixed_breaking_wins(self):
        v = make_schema_version(aenderungen=[
            FeldAenderung("new", FeldAenderungsTyp.HINZUGEFUEGT),
            FeldAenderung("old", FeldAenderungsTyp.ENTFERNT),
        ])
        assert v.berechne_kompatibilitaet() == SchemaKompatibilitaet.KEINE

    def test_version_ordering(self):
        v1 = make_schema_version("1.0.0")
        v2 = make_schema_version("2.0.0")
        assert v1.version_tuple() < v2.version_tuple()

    def test_version_ordering_minor(self):
        v1 = make_schema_version("1.0.0")
        v2 = make_schema_version("1.1.0")
        assert v1.version_tuple() < v2.version_tuple()

    def test_version_ordering_patch(self):
        v1 = make_schema_version("1.0.0")
        v2 = make_schema_version("1.0.1")
        assert v1.version_tuple() < v2.version_tuple()

    def test_schema_id_stored(self):
        v = SchemaVersion("SV-999", "1.0.0", ["id"], T0)
        assert v.schema_id == "SV-999"

    def test_felder_stored(self):
        v = SchemaVersion("SV-X", "1.0.0", ["id", "name", "status"], T0)
        assert "name" in v.felder

    def test_aenderungen_default_empty(self):
        v = SchemaVersion("SV-X", "1.0.0", ["id"], T0)
        assert v.aenderungen == []

    def test_erstellt_am_stored(self):
        v = SchemaVersion("SV-X", "1.0.0", ["id"], T0)
        assert v.erstellt_am == T0

    def test_kompatibilitaet_rueckwaerts_umbenannt(self):
        v = make_schema_version(aenderungen=[
            FeldAenderung("f", FeldAenderungsTyp.UMBENANNT),
        ])
        assert v.berechne_kompatibilitaet() == SchemaKompatibilitaet.RUECKWAERTS

    def test_kompatibilitaet_vollstaendig_returns_enum(self):
        v = make_schema_version()
        result = v.berechne_kompatibilitaet()
        assert isinstance(result, SchemaKompatibilitaet)

    def test_multiple_non_breaking_rueckwaerts(self):
        v = make_schema_version(aenderungen=[
            FeldAenderung("f1", FeldAenderungsTyp.HINZUGEFUEGT),
            FeldAenderung("f2", FeldAenderungsTyp.OPTIONAL_GEMACHT),
            FeldAenderung("f3", FeldAenderungsTyp.UMBENANNT),
        ])
        assert v.berechne_kompatibilitaet() == SchemaKompatibilitaet.RUECKWAERTS

    def test_version_tuple_returns_tuple(self):
        v = make_schema_version("1.2.3")
        assert isinstance(v.version_tuple(), tuple)

    def test_version_tuple_length_3(self):
        v = make_schema_version("1.2.3")
        assert len(v.version_tuple()) == 3

    def test_kompatibilitaet_keine_only_pflicht_gemacht(self):
        v = make_schema_version(aenderungen=[
            FeldAenderung("required_now", FeldAenderungsTyp.PFLICHT_GEMACHT),
        ])
        assert v.berechne_kompatibilitaet() == SchemaKompatibilitaet.KEINE


# ─────────────────────────────────────────────────────────────────────────────
# SchemaMigration tests (20+)
# ─────────────────────────────────────────────────────────────────────────────
class TestSchemaMigration:
    def _step(self, nr=1, optional=False, rueckgaengig=None):
        return MigrationsSchritt(
            schritt_nr=nr,
            beschreibung=f"Schritt {nr}",
            sql_ausdruck=f"ALTER TABLE x ADD COLUMN s{nr} TEXT",
            rueckgaengig_ausdruck=rueckgaengig,
            ist_optional=optional,
        )

    def test_fortschritt_no_schritte_100(self):
        m = make_migration(schritte=[])
        assert m.fortschritt_pct(0) == 100.0

    def test_fortschritt_0_of_4(self):
        schritte = [self._step(i) for i in range(1, 5)]
        m = make_migration(schritte=schritte)
        assert m.fortschritt_pct(0) == 0.0

    def test_fortschritt_2_of_4(self):
        schritte = [self._step(i) for i in range(1, 5)]
        m = make_migration(schritte=schritte)
        assert m.fortschritt_pct(2) == 50.0

    def test_fortschritt_4_of_4(self):
        schritte = [self._step(i) for i in range(1, 5)]
        m = make_migration(schritte=schritte)
        assert m.fortschritt_pct(4) == 100.0

    def test_fortschritt_1_of_3(self):
        schritte = [self._step(i) for i in range(1, 4)]
        m = make_migration(schritte=schritte)
        result = m.fortschritt_pct(1)
        assert result == round(1 / 3 * 100, 2)

    def test_hat_rueckgaengig_pfad_all_have_rollback(self):
        schritte = [self._step(i, rueckgaengig=f"DROP COLUMN s{i}") for i in range(1, 4)]
        m = make_migration(schritte=schritte)
        assert m.hat_rueckgaengig_pfad() is True

    def test_hat_rueckgaengig_pfad_missing_one(self):
        schritte = [
            self._step(1, rueckgaengig="DROP COLUMN s1"),
            self._step(2, rueckgaengig=None),  # missing rollback
            self._step(3, rueckgaengig="DROP COLUMN s3"),
        ]
        m = make_migration(schritte=schritte)
        assert m.hat_rueckgaengig_pfad() is False

    def test_hat_rueckgaengig_pfad_empty_schritte(self):
        m = make_migration(schritte=[])
        assert m.hat_rueckgaengig_pfad() is True

    def test_hat_rueckgaengig_optional_ohne_rollback_ignoriert(self):
        schritte = [
            self._step(1, rueckgaengig="ROLLBACK1"),
            self._step(2, optional=True, rueckgaengig=None),  # optional, no rollback → ignored
        ]
        m = make_migration(schritte=schritte)
        assert m.hat_rueckgaengig_pfad() is True

    def test_status_default_ausstehend(self):
        m = make_migration()
        assert m.status == MigrationsStatus.AUSSTEHEND

    def test_migrations_id_stored(self):
        m = make_migration()
        assert m.migrations_id == "M-001"

    def test_von_version_stored(self):
        m = make_migration()
        assert m.von_version == "1.0.0"

    def test_zu_version_stored(self):
        m = make_migration()
        assert m.zu_version == "2.0.0"

    def test_begonnen_am_default_none(self):
        m = make_migration()
        assert m.begonnen_am is None

    def test_abgeschlossen_am_default_none(self):
        m = make_migration()
        assert m.abgeschlossen_am is None

    def test_fehler_meldung_default_none(self):
        m = make_migration()
        assert m.fehler_meldung is None

    def test_fortschritt_rounds_to_2_decimal(self):
        schritte = [self._step(i) for i in range(1, 4)]
        m = make_migration(schritte=schritte)
        result = m.fortschritt_pct(1)
        assert result == round(1 / 3 * 100, 2)

    def test_hat_rueckgaengig_pflicht_without_rollback_false(self):
        schritte = [
            self._step(1, rueckgaengig=None),  # mandatory, no rollback
        ]
        m = make_migration(schritte=schritte)
        assert m.hat_rueckgaengig_pfad() is False

    def test_status_can_be_laufend(self):
        m = make_migration(status=MigrationsStatus.LAUFEND)
        assert m.status == MigrationsStatus.LAUFEND

    def test_status_can_be_abgeschlossen(self):
        m = make_migration(status=MigrationsStatus.ABGESCHLOSSEN)
        assert m.status == MigrationsStatus.ABGESCHLOSSEN

    def test_fortschritt_over_100_allowed(self):
        schritte = [self._step(i) for i in range(1, 3)]
        m = make_migration(schritte=schritte)
        result = m.fortschritt_pct(3)  # more completed than total
        assert result == 150.0


# ─────────────────────────────────────────────────────────────────────────────
# SchemaRegistry tests (15+)
# ─────────────────────────────────────────────────────────────────────────────
class TestSchemaRegistry:
    def test_aktuellste_version_none_wenn_leer(self):
        r = SchemaRegistry(registry_id="R-001")
        assert r.aktuellste_version() is None

    def test_aktuellste_version_single(self):
        v = make_schema_version("1.0.0")
        r = SchemaRegistry(registry_id="R", versionen=[v])
        assert r.aktuellste_version() == v

    def test_aktuellste_version_highest_semver(self):
        v1 = make_schema_version("1.0.0")
        v2 = make_schema_version("2.0.0")
        v3 = make_schema_version("1.5.0")
        r = SchemaRegistry(registry_id="R", versionen=[v1, v2, v3])
        assert r.aktuellste_version().version == "2.0.0"

    def test_aktuellste_version_not_by_insertion_order(self):
        v1 = make_schema_version("3.0.0")
        v2 = make_schema_version("1.0.0")
        r = SchemaRegistry(registry_id="R", versionen=[v2, v1])
        assert r.aktuellste_version().version == "3.0.0"

    def test_finde_migration_found(self):
        m = SchemaMigration("M-001", "1.0.0", "2.0.0", [])
        r = SchemaRegistry(registry_id="R", migrationen=[m])
        assert r.finde_migration("1.0.0", "2.0.0") == m

    def test_finde_migration_not_found(self):
        m = SchemaMigration("M-001", "1.0.0", "2.0.0", [])
        r = SchemaRegistry(registry_id="R", migrationen=[m])
        assert r.finde_migration("2.0.0", "3.0.0") is None

    def test_finde_migration_empty(self):
        r = SchemaRegistry(registry_id="R")
        assert r.finde_migration("1.0.0", "2.0.0") is None

    def test_finde_migration_multiple(self):
        m1 = SchemaMigration("M-001", "1.0.0", "2.0.0", [])
        m2 = SchemaMigration("M-002", "2.0.0", "3.0.0", [])
        r = SchemaRegistry(registry_id="R", migrationen=[m1, m2])
        assert r.finde_migration("2.0.0", "3.0.0") == m2

    def test_versionen_default_empty(self):
        r = SchemaRegistry(registry_id="R")
        assert r.versionen == []

    def test_migrationen_default_empty(self):
        r = SchemaRegistry(registry_id="R")
        assert r.migrationen == []

    def test_registry_id_stored(self):
        r = SchemaRegistry(registry_id="MY-REGISTRY")
        assert r.registry_id == "MY-REGISTRY"

    def test_finde_migration_wrong_direction(self):
        m = SchemaMigration("M-001", "1.0.0", "2.0.0", [])
        r = SchemaRegistry(registry_id="R", migrationen=[m])
        # Wrong direction
        assert r.finde_migration("2.0.0", "1.0.0") is None

    def test_aktuellste_version_minor_wins(self):
        v1 = make_schema_version("2.0.0")
        v2 = make_schema_version("2.1.0")
        r = SchemaRegistry(registry_id="R", versionen=[v1, v2])
        assert r.aktuellste_version().version == "2.1.0"

    def test_aktuellste_version_patch_wins(self):
        v1 = make_schema_version("2.1.0")
        v2 = make_schema_version("2.1.3")
        r = SchemaRegistry(registry_id="R", versionen=[v1, v2])
        assert r.aktuellste_version().version == "2.1.3"

    def test_finde_migration_first_match_returned(self):
        m1 = SchemaMigration("M-001", "1.0.0", "2.0.0", [])
        m2 = SchemaMigration("M-002", "1.0.0", "2.0.0", [])  # duplicate
        r = SchemaRegistry(registry_id="R", migrationen=[m1, m2])
        result = r.finde_migration("1.0.0", "2.0.0")
        assert result.migrations_id == "M-001"


# ─────────────────────────────────────────────────────────────────────────────
# SCHEMA_VERSIONEN tests (10+)
# ─────────────────────────────────────────────────────────────────────────────
class TestSchemaVersionen:
    def test_five_versions_present(self):
        assert len(SCHEMA_VERSIONEN) == 5

    def test_sv001_version_1_0_0(self):
        sv = next(v for v in SCHEMA_VERSIONEN if v.schema_id == "SV-001")
        assert sv.version == "1.0.0"

    def test_sv001_no_changes(self):
        sv = next(v for v in SCHEMA_VERSIONEN if v.schema_id == "SV-001")
        assert sv.aenderungen == []
        assert sv.berechne_kompatibilitaet() == SchemaKompatibilitaet.VOLLSTAENDIG

    def test_sv002_rueckwaerts(self):
        sv = next(v for v in SCHEMA_VERSIONEN if v.schema_id == "SV-002")
        assert sv.berechne_kompatibilitaet() == SchemaKompatibilitaet.RUECKWAERTS

    def test_sv003_breaking_pflicht_gemacht(self):
        sv = next(v for v in SCHEMA_VERSIONEN if v.schema_id == "SV-003")
        assert sv.berechne_kompatibilitaet() == SchemaKompatibilitaet.KEINE

    def test_sv004_rueckwaerts_optional_gemacht(self):
        sv = next(v for v in SCHEMA_VERSIONEN if v.schema_id == "SV-004")
        assert sv.berechne_kompatibilitaet() == SchemaKompatibilitaet.RUECKWAERTS

    def test_sv005_breaking_entfernt(self):
        sv = next(v for v in SCHEMA_VERSIONEN if v.schema_id == "SV-005")
        assert sv.berechne_kompatibilitaet() == SchemaKompatibilitaet.KEINE

    def test_sv005_version_3_0_0(self):
        sv = next(v for v in SCHEMA_VERSIONEN if v.schema_id == "SV-005")
        assert sv.version == "3.0.0"

    def test_version_ordering_sv001_lt_sv005(self):
        sv1 = next(v for v in SCHEMA_VERSIONEN if v.schema_id == "SV-001")
        sv5 = next(v for v in SCHEMA_VERSIONEN if v.schema_id == "SV-005")
        assert sv1.version_tuple() < sv5.version_tuple()

    def test_all_have_unique_schema_ids(self):
        ids = [v.schema_id for v in SCHEMA_VERSIONEN]
        assert len(set(ids)) == 5

    def test_sv002_has_hinzugefuegt(self):
        sv = next(v for v in SCHEMA_VERSIONEN if v.schema_id == "SV-002")
        typen = [a.aenderungs_typ for a in sv.aenderungen]
        assert FeldAenderungsTyp.HINZUGEFUEGT in typen

    def test_sv005_has_entfernt(self):
        sv = next(v for v in SCHEMA_VERSIONEN if v.schema_id == "SV-005")
        typen = [a.aenderungs_typ for a in sv.aenderungen]
        assert FeldAenderungsTyp.ENTFERNT in typen


# ─────────────────────────────────────────────────────────────────────────────
# MigrationsSchritt tests (5+)
# ─────────────────────────────────────────────────────────────────────────────
class TestMigrationsSchritt:
    def test_ist_optional_default_false(self):
        s = MigrationsSchritt(1, "Schritt 1")
        assert s.ist_optional is False

    def test_sql_ausdruck_default_none(self):
        s = MigrationsSchritt(1, "Schritt 1")
        assert s.sql_ausdruck is None

    def test_rueckgaengig_ausdruck_default_none(self):
        s = MigrationsSchritt(1, "Schritt 1")
        assert s.rueckgaengig_ausdruck is None

    def test_schritt_nr_stored(self):
        s = MigrationsSchritt(42, "The answer")
        assert s.schritt_nr == 42

    def test_beschreibung_stored(self):
        s = MigrationsSchritt(1, "Add column beschreibung")
        assert s.beschreibung == "Add column beschreibung"

    def test_optional_schritt_with_rollback(self):
        s = MigrationsSchritt(1, "Optional step", rueckgaengig_ausdruck="ROLLBACK",
                              ist_optional=True)
        assert s.ist_optional is True
        assert s.rueckgaengig_ausdruck == "ROLLBACK"

    def test_mandatory_schritt_affects_hat_rueckgaengig(self):
        # Mandatory step without rollback → hat_rueckgaengig_pfad = False
        pflicht = MigrationsSchritt(1, "Mandatory", rueckgaengig_ausdruck=None, ist_optional=False)
        m = SchemaMigration("M", "1.0", "2.0", [pflicht])
        assert m.hat_rueckgaengig_pfad() is False


# ─────────────────────────────────────────────────────────────────────────────
# Architecture constraint tests (2)
# ─────────────────────────────────────────────────────────────────────────────
class TestArchitekturConstraints:
    def test_process_cache_contracts_no_api_import(self):
        import ast
        import pathlib
        src = pathlib.Path("app/core/process_cache_contracts.py").read_text(encoding="utf-8")
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.ImportFrom) and node.module:
                    assert "app.api" not in node.module, (
                        f"process_cache_contracts imports from app.api: {node.module}"
                    )

    def test_workflow_schema_migration_contracts_no_api_import(self):
        import ast
        import pathlib
        src = pathlib.Path("app/core/workflow_schema_migration_contracts.py").read_text(encoding="utf-8")
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.ImportFrom) and node.module:
                    assert "app.api" not in node.module, (
                        f"workflow_schema_migration_contracts imports from app.api: {node.module}"
                    )


# ─────────────────────────────────────────────────────────────────────────────
# CacheStrategie enum tests (5+)
# ─────────────────────────────────────────────────────────────────────────────
class TestCacheStrategieEnum:
    def test_lru_value(self):
        assert CacheStrategie.LRU.value == "LRU"

    def test_ttl_value(self):
        assert CacheStrategie.TTL.value == "TTL"

    def test_write_through_value(self):
        assert CacheStrategie.WRITE_THROUGH.value == "WRITE_THROUGH"

    def test_write_back_value(self):
        assert CacheStrategie.WRITE_BACK.value == "WRITE_BACK"

    def test_four_strategies(self):
        assert len(list(CacheStrategie)) == 4


# ─────────────────────────────────────────────────────────────────────────────
# CacheStatus enum tests (4+)
# ─────────────────────────────────────────────────────────────────────────────
class TestCacheStatusEnum:
    def test_treffer_value(self):
        assert CacheStatus.TREFFER.value == "TREFFER"

    def test_verfehlt_value(self):
        assert CacheStatus.VERFEHLT.value == "VERFEHLT"

    def test_veraltet_value(self):
        assert CacheStatus.VERALTET.value == "VERALTET"

    def test_invalidiert_value(self):
        assert CacheStatus.INVALIDIERT.value == "INVALIDIERT"

    def test_four_statuses(self):
        assert len(list(CacheStatus)) == 4


# ─────────────────────────────────────────────────────────────────────────────
# SchemaKompatibilitaet enum tests (4+)
# ─────────────────────────────────────────────────────────────────────────────
class TestSchemaKompatibilitaetEnum:
    def test_vollstaendig_value(self):
        assert SchemaKompatibilitaet.VOLLSTAENDIG.value == "VOLLSTAENDIG"

    def test_rueckwaerts_value(self):
        assert SchemaKompatibilitaet.RUECKWAERTS.value == "RUECKWAERTS"

    def test_vorwaerts_value(self):
        assert SchemaKompatibilitaet.VORWAERTS.value == "VORWAERTS"

    def test_keine_value(self):
        assert SchemaKompatibilitaet.KEINE.value == "KEINE"

    def test_four_kompatibilitaeten(self):
        assert len(list(SchemaKompatibilitaet)) == 4


# ─────────────────────────────────────────────────────────────────────────────
# MigrationsStatus enum tests (5+)
# ─────────────────────────────────────────────────────────────────────────────
class TestMigrationsStatusEnum:
    def test_ausstehend_value(self):
        assert MigrationsStatus.AUSSTEHEND.value == "AUSSTEHEND"

    def test_laufend_value(self):
        assert MigrationsStatus.LAUFEND.value == "LAUFEND"

    def test_abgeschlossen_value(self):
        assert MigrationsStatus.ABGESCHLOSSEN.value == "ABGESCHLOSSEN"

    def test_fehlgeschlagen_value(self):
        assert MigrationsStatus.FEHLGESCHLAGEN.value == "FEHLGESCHLAGEN"

    def test_zurueckgerollt_value(self):
        assert MigrationsStatus.ZURUECKGEROLLT.value == "ZURUECKGEROLLT"

    def test_five_statuses(self):
        assert len(list(MigrationsStatus)) == 5
