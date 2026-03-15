"""
OpenTelemetry Span-Contracts — Wave 28 AP2

Reiner Contract-Layer fuer Span-Namen, Attribute-Schemas und Sampling-Regeln.
Kein Import von `opentelemetry` — die Contracts sind bibliotheksunabhaengig
und koennen maschinell gegen Instrument-Code geprueft werden.

Naming Convention: valeo.{domain}.{operation}
  domain:    agrar | finance | inventory | compliance | workflow | process
  operation: snake_case Verb-Objekt (z.B. settlement_create, sla_evaluate)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


SPAN_CONTRACT_SCHEMA_VERSION = 1


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class SpanKind(str, Enum):
    SERVER   = "SERVER"    # Eingehende Anfrage (HTTP, gRPC)
    CLIENT   = "CLIENT"    # Ausgehende Anfrage (DB, HTTP-Client, NATS)
    INTERNAL = "INTERNAL"  # Interner Verarbeitungsschritt
    CONSUMER = "CONSUMER"  # Eingehende Nachrichten (NATS, Queue)
    PRODUCER = "PRODUCER"  # Ausgehende Nachrichten (NATS, Queue)


class SamplingRegel(str, Enum):
    ALWAYS  = "ALWAYS"   # Jede Instanz tracen
    RATIO   = "RATIO"    # Prozentuales Sampling (ratio_pct)
    ERROR   = "ERROR"    # Nur bei Fehler/Exception tracen
    NEVER   = "NEVER"    # Kein Tracing (z.B. Health-Checks)


class AttributTyp(str, Enum):
    STRING  = "string"
    INT     = "int"
    FLOAT   = "float"
    BOOL    = "bool"
    DECIMAL = "decimal"  # Als String serialisiert fuer monetaere Werte


# ---------------------------------------------------------------------------
# SpanAttributeSchema — Pflicht- und optionale Attribute eines Spans
# ---------------------------------------------------------------------------

@dataclass
class SpanAttributeDefinition:
    """Definition eines einzelnen Span-Attributs."""
    key: str
    typ: AttributTyp
    pflicht: bool
    beschreibung: str
    beispiel: Optional[str] = None

    def as_dict(self) -> dict:
        return {
            "key": self.key,
            "typ": self.typ.value,
            "pflicht": self.pflicht,
            "beschreibung": self.beschreibung,
            "beispiel": self.beispiel,
        }


@dataclass
class SpanAttributeSchema:
    """Schema aller Attribute fuer einen Span-Contract."""
    attribute: list[SpanAttributeDefinition] = field(default_factory=list)

    @property
    def pflicht_keys(self) -> list[str]:
        return [a.key for a in self.attribute if a.pflicht]

    @property
    def optionale_keys(self) -> list[str]:
        return [a.key for a in self.attribute if not a.pflicht]

    def as_dict(self) -> dict:
        return {
            "pflicht_keys": self.pflicht_keys,
            "optionale_keys": self.optionale_keys,
            "attribute": [a.as_dict() for a in self.attribute],
        }


# ---------------------------------------------------------------------------
# SpanContract — Vollstaendiger Contract fuer einen Span
# ---------------------------------------------------------------------------

@dataclass
class SpanContract:
    """
    Verbindlicher Contract fuer einen OpenTelemetry-Span.

    span_name folgt der Konvention: valeo.{domain}.{operation}
    """
    span_name: str              # z.B. "valeo.agrar.settlement_create"
    kind: SpanKind
    domain: str                 # z.B. "agrar"
    operation: str              # z.B. "settlement_create"
    beschreibung: str
    sampling: SamplingRegel
    sampling_ratio_pct: Optional[float] = None   # Nur wenn sampling == RATIO
    attribute_schema: SpanAttributeSchema = field(default_factory=SpanAttributeSchema)
    schema_version: int = SPAN_CONTRACT_SCHEMA_VERSION

    def validate_name(self) -> bool:
        """Prueft ob span_name der valeo.{domain}.{operation}-Konvention entspricht."""
        parts = self.span_name.split(".")
        return (
            len(parts) == 3
            and parts[0] == "valeo"
            and parts[1] == self.domain
            and parts[2] == self.operation
        )

    def as_dict(self) -> dict:
        return {
            "span_name": self.span_name,
            "kind": self.kind.value,
            "domain": self.domain,
            "operation": self.operation,
            "beschreibung": self.beschreibung,
            "sampling": self.sampling.value,
            "sampling_ratio_pct": self.sampling_ratio_pct,
            "convention_valid": self.validate_name(),
            "attribute_schema": self.attribute_schema.as_dict(),
            "schema_version": self.schema_version,
        }


# ---------------------------------------------------------------------------
# SpanRegistry — Pruefbarer Container fuer alle Contracts
# ---------------------------------------------------------------------------

@dataclass
class SpanRegistry:
    """Registry aller definierten SpanContracts eines Systems."""
    contracts: list[SpanContract] = field(default_factory=list)
    schema_version: int = SPAN_CONTRACT_SCHEMA_VERSION

    def by_domain(self, domain: str) -> list[SpanContract]:
        return [c for c in self.contracts if c.domain == domain]

    def by_name(self, span_name: str) -> Optional[SpanContract]:
        for c in self.contracts:
            if c.span_name == span_name:
                return c
        return None

    def validate_all_names(self) -> list[str]:
        """Gibt Liste der span_names zurueck, die nicht der Konvention entsprechen."""
        return [c.span_name for c in self.contracts if not c.validate_name()]

    def as_dict(self) -> dict:
        return {
            "contract_count": len(self.contracts),
            "domains": sorted({c.domain for c in self.contracts}),
            "convention_violations": self.validate_all_names(),
            "contracts": [c.as_dict() for c in self.contracts],
            "schema_version": self.schema_version,
        }


# ---------------------------------------------------------------------------
# Shared Attribute-Definitionen (Wiederverwendbar)
# ---------------------------------------------------------------------------

def _tenant_attr() -> SpanAttributeDefinition:
    return SpanAttributeDefinition(
        key="valeo.tenant_id",
        typ=AttributTyp.STRING,
        pflicht=True,
        beschreibung="Mandant-ID fuer Multi-Tenancy",
        beispiel="tenant-agrar-nord",
    )


def _prozess_key_attr() -> SpanAttributeDefinition:
    return SpanAttributeDefinition(
        key="valeo.prozess_key",
        typ=AttributTyp.STRING,
        pflicht=True,
        beschreibung="Technischer Prozess-Schluessel",
        beispiel="agrar_settlement",
    )


def _instanz_id_attr() -> SpanAttributeDefinition:
    return SpanAttributeDefinition(
        key="valeo.instanz_id",
        typ=AttributTyp.STRING,
        pflicht=True,
        beschreibung="Eindeutige Prozessinstanz-ID",
        beispiel="inst-20240901-0042",
    )


def _betrag_attr(key: str, beschreibung: str) -> SpanAttributeDefinition:
    return SpanAttributeDefinition(
        key=key,
        typ=AttributTyp.DECIMAL,
        pflicht=False,
        beschreibung=beschreibung,
        beispiel="1234.56",
    )


# ---------------------------------------------------------------------------
# AP2: get_process_kernel_spans()
# ---------------------------------------------------------------------------

def get_process_kernel_spans() -> SpanRegistry:
    """
    Liefert alle verbindlichen Span-Contracts des Process-Kernels.

    Abdeckung:
      - agrar: settlement, wareneingang, qualitaetspruefung, sla_evaluate, intrastat
      - finance: ap_invoice, payment_run, dunning
      - workflow: step_transition, migration_check
      - compliance: export, audit_hash_verify
      - process: command_dispatch, sla_policy_validate
    """
    contracts: list[SpanContract] = [

        # ---------------------------------------------------------------
        # Domain: agrar
        # ---------------------------------------------------------------
        SpanContract(
            span_name="valeo.agrar.settlement_create",
            kind=SpanKind.INTERNAL,
            domain="agrar",
            operation="settlement_create",
            beschreibung="Erstellt eine neue Abrechnungsinstanz fuer Agrar-Settlement",
            sampling=SamplingRegel.ALWAYS,
            attribute_schema=SpanAttributeSchema(attribute=[
                _tenant_attr(),
                _prozess_key_attr(),
                SpanAttributeDefinition("valeo.settlement_id", AttributTyp.STRING, True,
                                        "Settlement-ID", "SET-2024-001"),
                SpanAttributeDefinition("valeo.lieferant_id", AttributTyp.STRING, False,
                                        "Lieferant-Referenz", "LF-0815"),
                _betrag_attr("valeo.settlement.bruttobetrag_eur", "Bruttobetrag in EUR"),
            ]),
        ),

        SpanContract(
            span_name="valeo.agrar.wareneingang_annahme",
            kind=SpanKind.INTERNAL,
            domain="agrar",
            operation="wareneingang_annahme",
            beschreibung="Verarbeitet Wareneingang und Annahme-Ergebnis",
            sampling=SamplingRegel.ALWAYS,
            attribute_schema=SpanAttributeSchema(attribute=[
                _tenant_attr(),
                SpanAttributeDefinition("valeo.wiegeschein_nr", AttributTyp.STRING, True,
                                        "Wiegeschein-Nummer", "WS-240901-042"),
                SpanAttributeDefinition("valeo.menge_tonnen", AttributTyp.DECIMAL, True,
                                        "Angenommene Menge in Tonnen", "28.4"),
                SpanAttributeDefinition("valeo.fruchtart", AttributTyp.STRING, False,
                                        "Fruchtart-Code", "WW"),
            ]),
        ),

        SpanContract(
            span_name="valeo.agrar.qualitaetspruefung_ergebnis",
            kind=SpanKind.INTERNAL,
            domain="agrar",
            operation="qualitaetspruefung_ergebnis",
            beschreibung="Schreibt Qualitaetspruefungs-Ergebnis aus Labor",
            sampling=SamplingRegel.ALWAYS,
            attribute_schema=SpanAttributeSchema(attribute=[
                _tenant_attr(),
                SpanAttributeDefinition("valeo.probe_id", AttributTyp.STRING, True,
                                        "Labor-Proben-ID", "PRB-240901-007"),
                SpanAttributeDefinition("valeo.feuchte_pct", AttributTyp.DECIMAL, True,
                                        "Feuchtegehalt in %", "14.2"),
                SpanAttributeDefinition("valeo.hl_gewicht", AttributTyp.DECIMAL, False,
                                        "Hektolitergewicht kg/hl", "78.5"),
            ]),
        ),

        SpanContract(
            span_name="valeo.agrar.sla_evaluate",
            kind=SpanKind.INTERNAL,
            domain="agrar",
            operation="sla_evaluate",
            beschreibung="Wertet SLA-Status fuer eine Prozessinstanz aus",
            sampling=SamplingRegel.RATIO,
            sampling_ratio_pct=25.0,
            attribute_schema=SpanAttributeSchema(attribute=[
                _tenant_attr(),
                _prozess_key_attr(),
                _instanz_id_attr(),
                SpanAttributeDefinition("valeo.sla.stufe", AttributTyp.STRING, True,
                                        "Eskalationsstufe", "WARNUNG"),
                SpanAttributeDefinition("valeo.sla.ist_dauer_stunden", AttributTyp.DECIMAL, True,
                                        "Tatsaechliche Dauer in Stunden", "26.5"),
            ]),
        ),

        SpanContract(
            span_name="valeo.agrar.intrastat_meldung_validate",
            kind=SpanKind.INTERNAL,
            domain="agrar",
            operation="intrastat_meldung_validate",
            beschreibung="Validiert eine Intrastat-Meldung vor der Einreichung",
            sampling=SamplingRegel.ALWAYS,
            attribute_schema=SpanAttributeSchema(attribute=[
                _tenant_attr(),
                SpanAttributeDefinition("valeo.intrastat.meldezeitraum", AttributTyp.STRING, True,
                                        "Meldezeitraum YYYY-MM", "2024-01"),
                SpanAttributeDefinition("valeo.intrastat.positionen_count", AttributTyp.INT, True,
                                        "Anzahl Warenbewegungen", "42"),
                SpanAttributeDefinition("valeo.intrastat.violations_count", AttributTyp.INT, True,
                                        "Anzahl Validierungsfehler", "0"),
            ]),
        ),

        # ---------------------------------------------------------------
        # Domain: finance
        # ---------------------------------------------------------------
        SpanContract(
            span_name="valeo.finance.ap_invoice_post",
            kind=SpanKind.INTERNAL,
            domain="finance",
            operation="ap_invoice_post",
            beschreibung="Verbucht eine Kreditorenrechnung nach Freigabe",
            sampling=SamplingRegel.ALWAYS,
            attribute_schema=SpanAttributeSchema(attribute=[
                _tenant_attr(),
                SpanAttributeDefinition("valeo.rechnung_id", AttributTyp.STRING, True,
                                        "Rechnungs-ID", "RE-2024-1042"),
                SpanAttributeDefinition("valeo.lieferant_id", AttributTyp.STRING, False,
                                        "Lieferant-Referenz", "LF-0815"),
                _betrag_attr("valeo.finance.bruttobetrag_eur", "Rechnungsbetrag Brutto EUR"),
            ]),
        ),

        SpanContract(
            span_name="valeo.finance.payment_run_execute",
            kind=SpanKind.CLIENT,
            domain="finance",
            operation="payment_run_execute",
            beschreibung="Fuehrt einen Zahlungslauf aus (SEPA-Ueberweisung/Lastschrift)",
            sampling=SamplingRegel.ALWAYS,
            attribute_schema=SpanAttributeSchema(attribute=[
                _tenant_attr(),
                SpanAttributeDefinition("valeo.payment_run_id", AttributTyp.STRING, True,
                                        "Zahlungslauf-ID", "ZL-2024-003"),
                SpanAttributeDefinition("valeo.positionen_count", AttributTyp.INT, True,
                                        "Anzahl Zahlungspositionen", "87"),
                _betrag_attr("valeo.finance.gesamtbetrag_eur", "Gesamtbetrag des Zahlungslaufs"),
            ]),
        ),

        SpanContract(
            span_name="valeo.finance.dunning_generate",
            kind=SpanKind.INTERNAL,
            domain="finance",
            operation="dunning_generate",
            beschreibung="Erzeugt Mahnvorschlag fuer offene Posten",
            sampling=SamplingRegel.RATIO,
            sampling_ratio_pct=50.0,
            attribute_schema=SpanAttributeSchema(attribute=[
                _tenant_attr(),
                SpanAttributeDefinition("valeo.debitor_id", AttributTyp.STRING, False,
                                        "Debitor-Referenz", "DB-1234"),
                SpanAttributeDefinition("valeo.mahnstufe", AttributTyp.INT, True,
                                        "Mahnstufe 1-3", "1"),
            ]),
        ),

        # ---------------------------------------------------------------
        # Domain: workflow
        # ---------------------------------------------------------------
        SpanContract(
            span_name="valeo.workflow.step_transition",
            kind=SpanKind.INTERNAL,
            domain="workflow",
            operation="step_transition",
            beschreibung="Zustandsuebergang einer Workflow-Instanz",
            sampling=SamplingRegel.ALWAYS,
            attribute_schema=SpanAttributeSchema(attribute=[
                _tenant_attr(),
                _prozess_key_attr(),
                _instanz_id_attr(),
                SpanAttributeDefinition("valeo.workflow.von_schritt", AttributTyp.STRING, True,
                                        "Ausgangsschritt-ID", "AS-03-QUALITAET"),
                SpanAttributeDefinition("valeo.workflow.zu_schritt", AttributTyp.STRING, True,
                                        "Zielschritt-ID", "AS-04-PREISFESTSTELLUNG"),
                SpanAttributeDefinition("valeo.workflow.ausfuehrender", AttributTyp.STRING, False,
                                        "Benutzername oder Service", "user@valeo.de"),
            ]),
        ),

        SpanContract(
            span_name="valeo.workflow.migration_check",
            kind=SpanKind.INTERNAL,
            domain="workflow",
            operation="migration_check",
            beschreibung="Prueft Breaking Changes bei Workflow-Migrationspfad",
            sampling=SamplingRegel.ALWAYS,
            attribute_schema=SpanAttributeSchema(attribute=[
                _tenant_attr(),
                _prozess_key_attr(),
                SpanAttributeDefinition("valeo.workflow.von_version", AttributTyp.STRING, True,
                                        "Quell-Version", "1.0.0"),
                SpanAttributeDefinition("valeo.workflow.zu_version", AttributTyp.STRING, True,
                                        "Ziel-Version", "1.1.0"),
                SpanAttributeDefinition("valeo.workflow.risiko_klasse", AttributTyp.STRING, True,
                                        "SAFE/WARNUNG/BREAKING", "SAFE"),
            ]),
        ),

        # ---------------------------------------------------------------
        # Domain: compliance
        # ---------------------------------------------------------------
        SpanContract(
            span_name="valeo.compliance.export_generate",
            kind=SpanKind.INTERNAL,
            domain="compliance",
            operation="export_generate",
            beschreibung="Erzeugt GoBD/Compliance-Export-Datei",
            sampling=SamplingRegel.ALWAYS,
            attribute_schema=SpanAttributeSchema(attribute=[
                _tenant_attr(),
                SpanAttributeDefinition("valeo.compliance.export_typ", AttributTyp.STRING, True,
                                        "Exporttyp (GoBD/ELSTER/INTRASTAT)", "GoBD"),
                SpanAttributeDefinition("valeo.compliance.datensaetze_count", AttributTyp.INT, False,
                                        "Anzahl exportierter Datensaetze", "4200"),
            ]),
        ),

        SpanContract(
            span_name="valeo.compliance.audit_hash_verify",
            kind=SpanKind.INTERNAL,
            domain="compliance",
            operation="audit_hash_verify",
            beschreibung="Verifiziert SHA-256 Audit-Hash einer Abrechnungsposition",
            sampling=SamplingRegel.ERROR,
            attribute_schema=SpanAttributeSchema(attribute=[
                _tenant_attr(),
                SpanAttributeDefinition("valeo.compliance.dokument_id", AttributTyp.STRING, True,
                                        "Dokument-/Datensatz-ID", "SET-2024-001"),
                SpanAttributeDefinition("valeo.compliance.hash_ok", AttributTyp.BOOL, True,
                                        "Hash-Verifikation erfolgreich", "true"),
            ]),
        ),

        # ---------------------------------------------------------------
        # Domain: process
        # ---------------------------------------------------------------
        SpanContract(
            span_name="valeo.process.command_dispatch",
            kind=SpanKind.INTERNAL,
            domain="process",
            operation="command_dispatch",
            beschreibung="Dispatcht einen Business-Command an zustaendigen Handler",
            sampling=SamplingRegel.RATIO,
            sampling_ratio_pct=10.0,
            attribute_schema=SpanAttributeSchema(attribute=[
                _tenant_attr(),
                SpanAttributeDefinition("valeo.command.type", AttributTyp.STRING, True,
                                        "Command-Typ", "FREIGABE_ERTEILEN"),
                SpanAttributeDefinition("valeo.command.aggregat_id", AttributTyp.STRING, True,
                                        "Ziel-Aggregat-ID", "inst-20240901-0042"),
                SpanAttributeDefinition("valeo.command.idempotency_key", AttributTyp.STRING, False,
                                        "Idempotency-Key des Commands", "cmd-abc-123"),
            ]),
        ),

        SpanContract(
            span_name="valeo.process.sla_policy_validate",
            kind=SpanKind.INTERNAL,
            domain="process",
            operation="sla_policy_validate",
            beschreibung="Validiert SLA-Policy-Konsistenz (warnung < kritisch < max)",
            sampling=SamplingRegel.NEVER,
            attribute_schema=SpanAttributeSchema(attribute=[
                _tenant_attr(),
                SpanAttributeDefinition("valeo.sla.policy_id", AttributTyp.STRING, True,
                                        "Policy-ID", "SLA-AS-GESAMT"),
                SpanAttributeDefinition("valeo.sla.valid", AttributTyp.BOOL, True,
                                        "Policy ist konsistent", "true"),
                SpanAttributeDefinition("valeo.sla.violations_count", AttributTyp.INT, False,
                                        "Anzahl Verletzungen", "0"),
            ]),
        ),
    ]

    return SpanRegistry(contracts=contracts)
