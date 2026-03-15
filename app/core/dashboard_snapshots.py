"""
dashboard_snapshots.py — Dashboard Read-Model Snapshots (Wave 32, Gap 033)

Typisierte Snapshot-Definitionen fuer alle Kern-Cockpits.
Staleness-Erkennung und Rebuild-Trigger ohne Datenbankzugriff im Core-Layer.

Gap 033: Read-Models fuer Dashboards statt teurer Live-Joins — p95 Dashboard API <250ms
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class SnapshotTyp(str, Enum):
    FINANCE_KPIS           = "FINANCE_KPIS"
    SETTLEMENT_COCKPIT     = "SETTLEMENT_COCKPIT"
    WARENEINGANG_UEBERSICHT = "WARENEINGANG_UEBERSICHT"
    AP_INVOICE_COCKPIT     = "AP_INVOICE_COCKPIT"
    COMPLIANCE_OVERVIEW    = "COMPLIANCE_OVERVIEW"
    PROZESS_HEALTH         = "PROZESS_HEALTH"


class SnapshotStatus(str, Enum):
    AKTUELL   = "AKTUELL"
    VERALTET  = "VERALTET"
    FEHLEND   = "FEHLEND"
    REBUILD   = "REBUILD"


# ---------------------------------------------------------------------------
# Snapshot-Felddefinition
# ---------------------------------------------------------------------------

@dataclass
class SnapshotFeld:
    """Definition eines typisierten Snapshot-Feldes."""
    name: str
    typ: str            # "decimal", "int", "str", "bool", "datetime", "list"
    pflicht: bool
    beschreibung: str
    beispiel: Any = None

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "typ": self.typ,
            "pflicht": self.pflicht,
            "beschreibung": self.beschreibung,
            "beispiel": str(self.beispiel) if self.beispiel is not None else None,
        }


# ---------------------------------------------------------------------------
# Dashboard-Snapshot
# ---------------------------------------------------------------------------

@dataclass
class DashboardSnapshot:
    """
    Typisierter Read-Model-Snapshot fuer ein Cockpit-Dashboard.

    Kapselt:
    - Snapshot-Typ und -Felder (Schema-Kontrakt)
    - Staleness-Konfiguration (max_alter_sekunden)
    - Letzte Aktualisierung (wenn bekannt)
    - Aktuellen Status
    """
    snapshot_typ: SnapshotTyp
    beschreibung: str
    felder: list[SnapshotFeld]
    max_alter_sekunden: int        # Maximale Staleness in Sekunden
    rebuild_endpoint: str          # REST-Endpunkt fuer manuellen Rebuild
    letzte_aktualisierung: datetime | None = None
    status: SnapshotStatus = SnapshotStatus.FEHLEND
    schema_version: int = 1

    @property
    def pflicht_felder(self) -> list[SnapshotFeld]:
        return [f for f in self.felder if f.pflicht]

    def ist_veraltet(self, jetzt: datetime | None = None) -> bool:
        """Prueft ob der Snapshot die max_alter_sekunden ueberschritten hat."""
        if self.letzte_aktualisierung is None:
            return True
        now = jetzt or datetime.now(timezone.utc)
        # Sicherstellen dass beide timezone-aware sind
        letzt = self.letzte_aktualisierung
        if letzt.tzinfo is None:
            letzt = letzt.replace(tzinfo=timezone.utc)
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)
        alter = (now - letzt).total_seconds()
        return alter > self.max_alter_sekunden

    def as_dict(self) -> dict:
        return {
            "snapshot_typ": self.snapshot_typ.value,
            "beschreibung": self.beschreibung,
            "max_alter_sekunden": self.max_alter_sekunden,
            "rebuild_endpoint": self.rebuild_endpoint,
            "letzte_aktualisierung": (
                self.letzte_aktualisierung.isoformat()
                if self.letzte_aktualisierung else None
            ),
            "status": self.status.value,
            "pflicht_felder_count": len(self.pflicht_felder),
            "felder": [f.as_dict() for f in self.felder],
            "schema_version": self.schema_version,
        }


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

@dataclass
class SnapshotValidationResult:
    """Ergebnis der Snapshot-Validierung."""
    snapshot_typ: SnapshotTyp
    gueltig: bool
    status: SnapshotStatus
    fehlende_felder: list[str]
    meldungen: list[str]
    schema_version: int = 1

    def as_dict(self) -> dict:
        return {
            "snapshot_typ": self.snapshot_typ.value,
            "gueltig": self.gueltig,
            "status": self.status.value,
            "fehlende_felder": self.fehlende_felder,
            "meldungen": self.meldungen,
            "schema_version": self.schema_version,
        }


def validate_snapshot(
    snapshot: DashboardSnapshot,
    daten: dict,
    jetzt: datetime | None = None,
) -> SnapshotValidationResult:
    """
    Validiert einen befuellten Snapshot-Datensatz gegen das Schema.

    Args:
        snapshot: Das Snapshot-Schema.
        daten: Die gelieferten Snapshot-Daten (Read-Model-Payload).
        jetzt: Aktueller Zeitpunkt (fuer Staleness-Check; Standard: UTC now).

    Returns:
        SnapshotValidationResult.
    """
    fehlende: list[str] = []
    meldungen: list[str] = []

    for feld in snapshot.pflicht_felder:
        if feld.name not in daten or daten[feld.name] is None:
            fehlende.append(feld.name)

    if fehlende:
        meldungen.append(f"Pflichtfelder fehlen: {fehlende}")

    ist_veraltet = snapshot.ist_veraltet(jetzt)
    if ist_veraltet:
        meldungen.append(
            f"Snapshot ist veraltet (max_alter={snapshot.max_alter_sekunden}s)."
        )

    if fehlende:
        status = SnapshotStatus.FEHLEND
    elif ist_veraltet:
        status = SnapshotStatus.VERALTET
    else:
        status = SnapshotStatus.AKTUELL

    return SnapshotValidationResult(
        snapshot_typ=snapshot.snapshot_typ,
        gueltig=len(fehlende) == 0 and not ist_veraltet,
        status=status,
        fehlende_felder=fehlende,
        meldungen=meldungen,
    )


# ---------------------------------------------------------------------------
# Rebuild-Request
# ---------------------------------------------------------------------------

@dataclass
class SnapshotRebuildRequest:
    """Request fuer einen manuellen Snapshot-Rebuild."""
    snapshot_typ: SnapshotTyp
    angefordert_von: str
    begruendung: str = ""

    def as_dict(self) -> dict:
        return {
            "snapshot_typ": self.snapshot_typ.value,
            "angefordert_von": self.angefordert_von,
            "begruendung": self.begruendung,
        }


@dataclass
class SnapshotRebuildResult:
    """Ergebnis eines Snapshot-Rebuild-Triggers."""
    snapshot_typ: SnapshotTyp
    ausgeloest: bool
    meldung: str
    schema_version: int = 1

    def as_dict(self) -> dict:
        return {
            "snapshot_typ": self.snapshot_typ.value,
            "ausgeloest": self.ausgeloest,
            "meldung": self.meldung,
            "schema_version": self.schema_version,
        }


# ---------------------------------------------------------------------------
# Snapshot-Registry
# ---------------------------------------------------------------------------

@dataclass
class SnapshotRegistry:
    """Registry aller Dashboard-Snapshots."""
    snapshots: list[DashboardSnapshot] = field(default_factory=list)
    schema_version: int = 1

    def by_typ(self, typ: SnapshotTyp) -> DashboardSnapshot | None:
        for s in self.snapshots:
            if s.snapshot_typ == typ:
                return s
        return None

    def by_typ_str(self, typ_str: str) -> DashboardSnapshot | None:
        for s in self.snapshots:
            if s.snapshot_typ.value == typ_str:
                return s
        return None

    def veraltete(self, jetzt: datetime | None = None) -> list[DashboardSnapshot]:
        return [s for s in self.snapshots if s.ist_veraltet(jetzt)]

    def as_dict(self) -> dict:
        return {
            "snapshot_count": len(self.snapshots),
            "typen": [s.snapshot_typ.value for s in self.snapshots],
            "snapshots": [s.as_dict() for s in self.snapshots],
            "schema_version": self.schema_version,
        }


# ---------------------------------------------------------------------------
# build_snapshot_from_fields
# ---------------------------------------------------------------------------

def build_snapshot_from_fields(
    snapshot: DashboardSnapshot,
    daten: dict,
    aktualisiert_um: datetime | None = None,
) -> DashboardSnapshot:
    """
    Gibt eine aktualisierte Kopie des Snapshots mit neuem Status zurueck.
    Mutiert das Original nicht — gibt neues Objekt zurueck.
    """
    jetzt = aktualisiert_um or datetime.now(timezone.utc)
    validation = validate_snapshot(snapshot, daten, jetzt)
    return DashboardSnapshot(
        snapshot_typ=snapshot.snapshot_typ,
        beschreibung=snapshot.beschreibung,
        felder=snapshot.felder,
        max_alter_sekunden=snapshot.max_alter_sekunden,
        rebuild_endpoint=snapshot.rebuild_endpoint,
        letzte_aktualisierung=jetzt,
        status=validation.status,
        schema_version=snapshot.schema_version,
    )


# ---------------------------------------------------------------------------
# Default-Snapshots
# ---------------------------------------------------------------------------

def get_default_dashboard_snapshots() -> SnapshotRegistry:
    """Liefert die Default-Snapshot-Registry mit 6 Cockpit-Snapshots."""

    finance_kpis = DashboardSnapshot(
        snapshot_typ=SnapshotTyp.FINANCE_KPIS,
        beschreibung="Finance-KPI-Cockpit: Umsatz, OP-Saldo, Zahlungslauf-Status",
        max_alter_sekunden=300,       # 5 Minuten
        rebuild_endpoint="POST /api/v1/finance/read-models/_rebuild",
        felder=[
            SnapshotFeld("umsatz_mtd_eur", "decimal", True, "Monatsumsatz aktuell", 1250000.0),
            SnapshotFeld("op_saldo_debitoren_eur", "decimal", True, "Offene Posten Debitoren", 340000.0),
            SnapshotFeld("op_saldo_kreditoren_eur", "decimal", True, "Offene Posten Kreditoren", 180000.0),
            SnapshotFeld("zahlungslauf_offen_count", "int", True, "Ausstehende Zahlungslaeufe", 3),
            SnapshotFeld("faellige_rechnungen_count", "int", True, "Heute faellige Rechnungen", 12),
            SnapshotFeld("liquiditaets_reserve_eur", "decimal", False, "Verfuegbare Liquiditaet", 500000.0),
        ],
    )

    settlement_cockpit = DashboardSnapshot(
        snapshot_typ=SnapshotTyp.SETTLEMENT_COCKPIT,
        beschreibung="Settlement-Cockpit: Abrechnungsstatus Agrar-Kampagne",
        max_alter_sekunden=600,       # 10 Minuten
        rebuild_endpoint="POST /api/v1/finance/read-models/_rebuild",
        felder=[
            SnapshotFeld("abrechnungen_offen_count", "int", True, "Offene Abrechnungen", 47),
            SnapshotFeld("abrechnungen_freigegeben_count", "int", True, "Freigegebene Abrechnungen", 213),
            SnapshotFeld("gesamtgewicht_abgerechnet_t", "decimal", True, "Abgerechnetes Gesamtgewicht (t)", 8450.5),
            SnapshotFeld("gesamtbetrag_eur", "decimal", True, "Abrechnungsbetrag gesamt (EUR)", 2105000.0),
            SnapshotFeld("durchschnittspreis_eur_pro_t", "decimal", False, "Durchschnittspreis EUR/t", 249.1),
            SnapshotFeld("letzte_kampagne_id", "str", False, "Aktive Kampagnen-ID", "ERNTE_2025"),
        ],
    )

    wareneingang = DashboardSnapshot(
        snapshot_typ=SnapshotTyp.WARENEINGANG_UEBERSICHT,
        beschreibung="Wareneingang-Uebersicht: Wiegescheine, Qualitaet, Chargen",
        max_alter_sekunden=120,       # 2 Minuten (Echtzeit-nah)
        rebuild_endpoint="POST /api/v1/process/dashboards/rebuild",
        felder=[
            SnapshotFeld("wiegescheine_heute_count", "int", True, "Wiegescheine heute", 34),
            SnapshotFeld("gesamtgewicht_heute_t", "decimal", True, "Bruttogewicht heute (t)", 820.3),
            SnapshotFeld("qualitaet_bestanden_pct", "decimal", True, "Qualitaetspruefung bestanden (%)", 94.1),
            SnapshotFeld("chargen_aktiv_count", "int", True, "Aktive Chargen", 8),
            SnapshotFeld("lkw_wartend_count", "int", False, "LKW in Warteschleife", 2),
        ],
    )

    ap_invoice = DashboardSnapshot(
        snapshot_typ=SnapshotTyp.AP_INVOICE_COCKPIT,
        beschreibung="AP-Invoice-Cockpit: Eingangsrechnungen, Freigaben, Faelligkeiten",
        max_alter_sekunden=300,       # 5 Minuten
        rebuild_endpoint="POST /api/v1/finance/read-models/_rebuild",
        felder=[
            SnapshotFeld("rechnungen_eingegangen_count", "int", True, "Eingegangene Rechnungen (offen)", 28),
            SnapshotFeld("rechnungen_in_pruefung_count", "int", True, "Rechnungen in Pruefung", 11),
            SnapshotFeld("rechnungen_freigegeben_count", "int", True, "Freigegebene Rechnungen", 9),
            SnapshotFeld("gesamtbetrag_offen_eur", "decimal", True, "Gesamtbetrag offene Rechnungen (EUR)", 145000.0),
            SnapshotFeld("ueberfaellig_count", "int", True, "Ueberfaellige Rechnungen", 3),
            SnapshotFeld("naechste_faelligkeit_datum", "str", False, "Naechste Faelligkeit", "2026-03-20"),
        ],
    )

    compliance = DashboardSnapshot(
        snapshot_typ=SnapshotTyp.COMPLIANCE_OVERVIEW,
        beschreibung="Compliance-Uebersicht: Intrastat, Cross-Compliance, Sachkunde",
        max_alter_sekunden=3600,      # 1 Stunde
        rebuild_endpoint="POST /api/v1/process/dashboards/rebuild",
        felder=[
            SnapshotFeld("intrastat_meldungen_offen_count", "int", True, "Offene Intrastat-Meldungen", 2),
            SnapshotFeld("cross_compliance_score_pct", "decimal", True, "Cross-Compliance Score (%)", 98.5),
            SnapshotFeld("sachkunde_ablaufend_count", "int", True, "Sachkundenachweise ablaufend (<30d)", 1),
            SnapshotFeld("zulassungen_aktiv_count", "int", True, "Aktive Zulassungen", 47),
            SnapshotFeld("letzte_pruefung_datum", "str", False, "Letzte Compliance-Pruefung", "2026-03-01"),
        ],
    )

    prozess_health = DashboardSnapshot(
        snapshot_typ=SnapshotTyp.PROZESS_HEALTH,
        beschreibung="Prozess-Health-Monitor: SLA, Eskalationen, Workflow-Fehler",
        max_alter_sekunden=60,        # 1 Minute (Monitoring-nah)
        rebuild_endpoint="POST /api/v1/process/dashboards/rebuild",
        felder=[
            SnapshotFeld("sla_einhaltung_pct", "decimal", True, "SLA-Einhaltung gesamt (%)", 97.3),
            SnapshotFeld("eskalationen_offen_count", "int", True, "Offene Eskalationen", 1),
            SnapshotFeld("workflow_fehler_24h_count", "int", True, "Workflow-Fehler letzte 24h", 0),
            SnapshotFeld("approval_pending_count", "int", True, "Ausstehende Human-Approvals", 4),
            SnapshotFeld("durchlaufzeit_median_min", "decimal", False, "Median Durchlaufzeit Settlement (min)", 38.5),
        ],
    )

    return SnapshotRegistry(
        snapshots=[
            finance_kpis,
            settlement_cockpit,
            wareneingang,
            ap_invoice,
            compliance,
            prozess_health,
        ]
    )
