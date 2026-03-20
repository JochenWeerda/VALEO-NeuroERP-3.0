"""
Landhandel terminology registry.

Provides a machine-readable bilingual glossary for the commercial landhandel
domain. The registry is intentionally read-only and can be surfaced via API
and frontend pages for consistent DE/EN terminology.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


TERMINOLOGY_SCHEMA_VERSION = 1
TERMINOLOGY_MANIFEST_KIND = "LANDHANDEL_TERMINOLOGY_REGISTRY"


class TerminologyDomain(str, Enum):
    LANDHANDEL = "landhandel"
    CRM = "crm"
    DMS = "dms"
    FINANCE = "finance"
    QUALITY = "quality"
    SUPPLY_CHAIN = "supply_chain"
    MASTER_DATA = "master_data"
    GENERAL = "general"


@dataclass(frozen=True)
class TerminologyRule:
    rule_key: str
    title_de: str
    title_en: str
    description_de: str
    description_en: str
    examples: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "rule_key": self.rule_key,
            "title_de": self.title_de,
            "title_en": self.title_en,
            "description_de": self.description_de,
            "description_en": self.description_en,
            "examples": self.examples,
        }


@dataclass(frozen=True)
class TerminologyEntry:
    term_key: str
    domain: TerminologyDomain
    canonical_de: str
    canonical_en: str
    description_de: str
    description_en: str
    synonyms_de: list[str] = field(default_factory=list)
    synonyms_en: list[str] = field(default_factory=list)
    avoid_de: list[str] = field(default_factory=list)
    avoid_en: list[str] = field(default_factory=list)
    usage_notes_de: list[str] = field(default_factory=list)
    usage_notes_en: list[str] = field(default_factory=list)
    related_terms: list[str] = field(default_factory=list)
    module_refs: list[str] = field(default_factory=list)

    def search_text(self) -> str:
        parts = [
            self.term_key,
            self.domain.value,
            self.canonical_de,
            self.canonical_en,
            self.description_de,
            self.description_en,
            " ".join(self.synonyms_de),
            " ".join(self.synonyms_en),
            " ".join(self.avoid_de),
            " ".join(self.avoid_en),
            " ".join(self.usage_notes_de),
            " ".join(self.usage_notes_en),
            " ".join(self.related_terms),
            " ".join(self.module_refs),
        ]
        return " ".join(part for part in parts if part).lower()

    def match_score(self, query: str) -> tuple[int, list[str]]:
        tokens = [token for token in query.lower().split() if token]
        if not tokens:
            return 1, []

        score = 0
        matched_fields: set[str] = set()
        haystack = self.search_text()
        for token in tokens:
            if token in self.term_key.lower():
                score += 6
                matched_fields.add("term_key")
            if token in self.canonical_de.lower():
                score += 5
                matched_fields.add("canonical_de")
            if token in self.canonical_en.lower():
                score += 5
                matched_fields.add("canonical_en")
            if token in haystack:
                score += 1
                matched_fields.add("full_text")
        return score, sorted(matched_fields)

    def as_dict(self, match_score: int | None = None, matched_fields: list[str] | None = None) -> dict[str, Any]:
        payload = {
            "term_key": self.term_key,
            "domain": self.domain.value,
            "canonical_de": self.canonical_de,
            "canonical_en": self.canonical_en,
            "description_de": self.description_de,
            "description_en": self.description_en,
            "synonyms_de": self.synonyms_de,
            "synonyms_en": self.synonyms_en,
            "avoid_de": self.avoid_de,
            "avoid_en": self.avoid_en,
            "usage_notes_de": self.usage_notes_de,
            "usage_notes_en": self.usage_notes_en,
            "related_terms": self.related_terms,
            "module_refs": self.module_refs,
        }
        if match_score is not None:
            payload["match_score"] = match_score
        if matched_fields is not None:
            payload["matched_fields"] = matched_fields
        return payload


@dataclass
class TerminologyRegistry:
    entries: list[TerminologyEntry] = field(default_factory=list)
    rules: list[TerminologyRule] = field(default_factory=list)
    schema_version: int = TERMINOLOGY_SCHEMA_VERSION
    manifest_kind: str = TERMINOLOGY_MANIFEST_KIND
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def term_count(self) -> int:
        return len(self.entries)

    @property
    def domains(self) -> list[str]:
        return sorted({entry.domain.value for entry in self.entries})

    @property
    def languages(self) -> list[str]:
        return ["de", "en"]

    def by_term_key(self, term_key: str) -> TerminologyEntry | None:
        normalized = term_key.strip().lower()
        for entry in self.entries:
            if entry.term_key.lower() == normalized:
                return entry
        return None

    def by_domain(self, domain: str) -> list[TerminologyEntry]:
        normalized = domain.strip().lower()
        return [entry for entry in self.entries if entry.domain.value == normalized]

    def search(self, query: str | None = None, domain: str | None = None) -> list[tuple[TerminologyEntry, int, list[str]]]:
        entries = self.entries
        if domain:
            entries = [entry for entry in entries if entry.domain.value == domain.strip().lower()]

        results: list[tuple[TerminologyEntry, int, list[str]]] = []
        for entry in entries:
            if query:
                score, fields = entry.match_score(query)
                if score <= 0:
                    continue
                results.append((entry, score, fields))
            else:
                results.append((entry, 1, []))

        results.sort(key=lambda item: (-item[1], item[0].canonical_de.lower(), item[0].term_key))
        return results

    def as_dict(self, query: str | None = None, domain: str | None = None) -> dict[str, Any]:
        hits = self.search(query=query, domain=domain)
        return {
            "schema_version": self.schema_version,
            "manifest_kind": self.manifest_kind,
            "generated_at": self.generated_at,
            "query": query,
            "domain": domain,
            "term_count": len(hits),
            "domains": self.domains,
            "languages": self.languages,
            "global_rules": [rule.as_dict() for rule in self.rules],
            "terms": [
                entry.as_dict(match_score=score, matched_fields=fields)
                for entry, score, fields in hits
            ],
        }


def _build_rules() -> list[TerminologyRule]:
    return [
        TerminologyRule(
            rule_key="use_canonical_settlement",
            title_de="Settlement konsequent verwenden",
            title_en="Use settlement consistently",
            description_de="Fachlich bleibt 'Settlement' der Canonical-Term fuer die Abrechnung im Landhandel.",
            description_en="Use 'settlement' as the canonical business term for commercial settlement flows.",
            examples=["Abrechnung / settlement", "Settlement-Status", "Settlement-Audit"],
        ),
        TerminologyRule(
            rule_key="complaint_claim_alignment",
            title_de="Reklamation und Claim abgleichen",
            title_en="Align complaint and claim terminology",
            description_de="CRM- und DMS-Fluesse verwenden 'Reklamation' als deutschen Fachbegriff und 'claim' als englisches Gegenstueck.",
            description_en="CRM and DMS flows use 'claim' as the English equivalent of the German business term 'Reklamation'.",
            examples=["Reklamation E2E", "claim handling", "claim audit trail"],
        ),
        TerminologyRule(
            rule_key="avoid_generic_billing",
            title_de="Generisches Billing vermeiden",
            title_en="Avoid generic billing phrasing",
            description_de="Im Landhandel ist 'Abrechnung' fachlich stabiler als ein generisches 'billing'.",
            description_en="In landhandel contexts, 'settlement' is preferred over a generic 'billing' wording.",
            examples=["settlement", "credit memo", "debit memo"],
        ),
        TerminologyRule(
            rule_key="bilingual_labels_synced",
            title_de="DE/EN-Labels synchron halten",
            title_en="Keep DE/EN labels synchronized",
            description_de="UI-Labels, API-Feldnamen und Registry-Eintraege sollen dieselbe Canonical-Fachsprache teilen.",
            description_en="UI labels, API field names and registry entries must share the same canonical business language.",
            examples=["canonical_de", "canonical_en", "synonyms_de", "synonyms_en"],
        ),
    ]


def _build_entries() -> list[TerminologyEntry]:
    return [
        TerminologyEntry(
            term_key="mandant",
            domain=TerminologyDomain.GENERAL,
            canonical_de="Mandant",
            canonical_en="Tenant",
            description_de="Isolierte betriebliche Einheit mit eigenen Daten, Rollen und Standards.",
            description_en="Isolated business unit with its own data, roles and standards.",
            synonyms_de=["Kunde", "Gesellschaft"],
            synonyms_en=["Client", "Business unit"],
            avoid_de=["globale Instanz"],
            avoid_en=["global instance"],
            usage_notes_de=["In API- und UI-Labels einheitlich als Mandant verwenden."],
            usage_notes_en=["Use tenant consistently in API and UI labels."],
            module_refs=["app/core/tenant.py", "app/core/database.py"],
        ),
        TerminologyEntry(
            term_key="stammdaten",
            domain=TerminologyDomain.MASTER_DATA,
            canonical_de="Stammdaten",
            canonical_en="Master data",
            description_de="Kernstammsatz fuer Partner, Artikel, Fahrzeuge, Lagerorte und weitere Referenzobjekte.",
            description_en="Core reference data for partners, items, vehicles, locations and other reference objects.",
            synonyms_de=["Basisdaten"],
            synonyms_en=["Reference data"],
            avoid_de=["Grunddaten"],
            avoid_en=["base data"],
            usage_notes_de=["Nicht mit transaktionalen Belegen vermischen."],
            usage_notes_en=["Keep separate from transactional documents."],
            module_refs=["app/core/master_data.py", "app/api/v1/endpoints/master_data.py"],
        ),
        TerminologyEntry(
            term_key="kontrakt",
            domain=TerminologyDomain.LANDHANDEL,
            canonical_de="Kontrakt",
            canonical_en="Contract",
            description_de="Vertragliche Basis fuer Mengen, Preise, Qualitaet und Lieferkonditionen.",
            description_en="Commercial basis for quantities, prices, quality and delivery conditions.",
            synonyms_de=["Lieferkontrakt"],
            synonyms_en=["Purchase contract"],
            avoid_de=["Deal"],
            avoid_en=["Deal"],
            usage_notes_de=["Bei landhandelsspezifischen Flows den Fachbegriff Kontrakt bevorzugen."],
            usage_notes_en=["Prefer contract for landhandel-specific flows."],
            module_refs=["app/domains/agrar", "app/api/v1/endpoints/agrar_contracts.py"],
        ),
        TerminologyEntry(
            term_key="annahme",
            domain=TerminologyDomain.SUPPLY_CHAIN,
            canonical_de="Annahme",
            canonical_en="Intake",
            description_de="Physische oder fachliche Uebernahme von Ware in den Prozess.",
            description_en="Physical or business intake of goods into the process.",
            synonyms_de=["Wareneingang"],
            synonyms_en=["Goods receipt"],
            avoid_de=["Eingang", "Receipt"],
            avoid_en=["entry"],
            usage_notes_de=["In Lager- und Waageflows als Annahme kennzeichnen."],
            usage_notes_en=["Use intake in weighbridge and warehouse flows."],
            module_refs=["app/api/v1/endpoints/harvest_acceptance.py", "app/api/v1/endpoints/waage.py"],
        ),
        TerminologyEntry(
            term_key="waage",
            domain=TerminologyDomain.SUPPLY_CHAIN,
            canonical_de="Waage",
            canonical_en="Weighbridge",
            description_de="Mess- und Kontrollpunkt fuer Gewichte, Abweichungen und Belegzuordnung.",
            description_en="Measurement and control point for weights, deviations and document matching.",
            synonyms_de=["Brueckenwaage"],
            synonyms_en=["Scale"],
            avoid_de=["Gewichtsanlage"],
            avoid_en=["weight system"],
            usage_notes_de=["Fachlich bei Anlieferung und Abrechnung referenzieren."],
            usage_notes_en=["Reference in intake and settlement flows."],
            module_refs=["app/api/v1/endpoints/waage.py", "app/core/weighting.py"],
        ),
        TerminologyEntry(
            term_key="qualitaetsprotokoll",
            domain=TerminologyDomain.QUALITY,
            canonical_de="Qualitaetsprotokoll",
            canonical_en="Quality protocol",
            description_de="Dokumentierter Qualitaetsstatus mit Messwerten, Pruefpunkten und Freigaben.",
            description_en="Documented quality status with measurements, checkpoints and approvals.",
            synonyms_de=["Pruefprotokoll"],
            synonyms_en=["Inspection protocol"],
            avoid_de=["QC sheet"],
            avoid_en=["QC sheet"],
            usage_notes_de=["In Fachflows als protocol statt loose notes behandeln."],
            usage_notes_en=["Treat as a controlled protocol, not loose notes."],
            module_refs=["app/api/v1/endpoints/quality_protocols.py"],
        ),
        TerminologyEntry(
            term_key="trocknungscharge",
            domain=TerminologyDomain.QUALITY,
            canonical_de="Trocknungscharge",
            canonical_en="Drying batch",
            description_de="Chargenbezogene Trocknungs- und Abzugslogik im Agrarfluss.",
            description_en="Batch-based drying and deduction logic in the agrar flow.",
            synonyms_de=["Trocknungslauf"],
            synonyms_en=["Drying run"],
            avoid_de=["Trocknungsvorgang"],
            avoid_en=["drying operation"],
            usage_notes_de=["Bei Abrechnung und Qualitaet mit Chargen-ID verknuepfen."],
            usage_notes_en=["Link to batch ID in settlement and quality flows."],
            module_refs=["app/api/v1/endpoints/agrar_settlements.py", "app/core/drying.py"],
        ),
        TerminologyEntry(
            term_key="settlement",
            domain=TerminologyDomain.FINANCE,
            canonical_de="Abrechnung",
            canonical_en="Settlement",
            description_de="Fachliche Endabrechnung mit Mengen, Qualitaet, Preisen und Nebenleistungen.",
            description_en="Commercial final settlement covering quantities, quality, prices and ancillary charges.",
            synonyms_de=["Endabrechnung"],
            synonyms_en=["Commercial settlement"],
            avoid_de=["Billing"],
            avoid_en=["Billing"],
            usage_notes_de=["In gemischten DE/EN-Kontexten Settlement nur in Klammern ergaenzen."],
            usage_notes_en=["Use settlement in the canonical English wording."],
            module_refs=["app/core/reklamation.py", "app/api/v1/endpoints/agrar_settlements.py"],
        ),
        TerminologyEntry(
            term_key="gutschrift",
            domain=TerminologyDomain.FINANCE,
            canonical_de="Gutschrift",
            canonical_en="Credit memo",
            description_de="Positiver Korrekturbeleg fuer Preis-, Qualitaets- oder Mengenanpassungen.",
            description_en="Positive correction document for price, quality or quantity adjustments.",
            synonyms_de=["Korrekturgutschrift"],
            synonyms_en=["Credit note"],
            avoid_de=["Erstattung"],
            avoid_en=["refund"],
            usage_notes_de=["Bei Settlement-Korrekturen und Reklamationen bevorzugen."],
            usage_notes_en=["Prefer in settlement corrections and claims."],
            module_refs=["app/api/v1/endpoints/journal_entries.py"],
        ),
        TerminologyEntry(
            term_key="belastung",
            domain=TerminologyDomain.FINANCE,
            canonical_de="Belastung",
            canonical_en="Debit memo",
            description_de="Negativer Korrekturbeleg fuer nachtraegliche Abzuege oder Kosten.",
            description_en="Negative correction document for later deductions or costs.",
            synonyms_de=["Belastungsanzeige"],
            synonyms_en=["Debit note"],
            avoid_de=["Abzug"],
            avoid_en=["deduction"],
            usage_notes_de=["Mit klarer Ursache und Audit-Referenz verwenden."],
            usage_notes_en=["Use with explicit cause and audit reference."],
            module_refs=["app/api/v1/endpoints/journal_entries.py"],
        ),
        TerminologyEntry(
            term_key="reklamation",
            domain=TerminologyDomain.CRM,
            canonical_de="Reklamation",
            canonical_en="Claim",
            description_de="End-to-End Reklamationsfall mit CRM-Bezug, DMS-Nachweisen und SLA.",
            description_en="End-to-end claim case with CRM linkage, DMS evidence and SLA handling.",
            synonyms_de=["Beschwerde"],
            synonyms_en=["Complaint"],
            avoid_de=["Ticket"],
            avoid_en=["ticket"],
            usage_notes_de=["In Landhandel-Flows als Reklamation statt generische Beschwerde bezeichnen."],
            usage_notes_en=["Prefer claim over generic complaint in landhandel flows."],
            module_refs=["app/core/reklamation.py", "app/api/v1/endpoints/reklamation_api.py"],
        ),
        TerminologyEntry(
            term_key="dms_artifact",
            domain=TerminologyDomain.DMS,
            canonical_de="Dokumentreferenz",
            canonical_en="Document artifact",
            description_de="Verweis auf ein revisionssicheres Dokument, Anhang oder Extraktionsobjekt.",
            description_en="Reference to an audit-safe document, attachment or extracted object.",
            synonyms_de=["DMS-Beleg", "Dokumentobjekt"],
            synonyms_en=["Document reference"],
            avoid_de=["Attachment only"],
            avoid_en=["attachment only"],
            usage_notes_de=["DMS-Referenzen immer mit fachlichem Vorgang koppeln."],
            usage_notes_en=["Always bind DMS references to a business case."],
            module_refs=["app/api/v1/endpoints/dms_images.py", "app/api/v1/endpoints/gobd_archiv.py"],
        ),
        TerminologyEntry(
            term_key="freigabe",
            domain=TerminologyDomain.GENERAL,
            canonical_de="Freigabe",
            canonical_en="Approval",
            description_de="Menschliche oder regelbasierte Zustimmung vor der Ausfuehrung.",
            description_en="Human or rule-based approval before execution.",
            synonyms_de=["Genehmigung"],
            synonyms_en=["Authorization"],
            avoid_de=["OK"],
            avoid_en=["OK"],
            usage_notes_de=["Bei kritischen Aktionen mit Audit-Trail dokumentieren."],
            usage_notes_en=["Document critical actions with audit trail."],
            module_refs=["app/core/human_approval_gate.py", "app/api/v1/endpoints/channel_work_surfaces.py"],
        ),
        TerminologyEntry(
            term_key="lieferkette",
            domain=TerminologyDomain.SUPPLY_CHAIN,
            canonical_de="Lieferkette",
            canonical_en="Supply chain",
            description_de="Verbund aus Lieferanten, Transport, Annahme, Lagerung und Auslieferung.",
            description_en="Network of suppliers, transport, intake, storage and outbound delivery.",
            synonyms_de=["Logistikkette"],
            synonyms_en=["Logistics chain"],
            avoid_de=["Supply chain"],
            avoid_en=["logistics chain"],
            usage_notes_de=["Daten, ETA und Abweichungen entlang der Lieferkette verknuepfen."],
            usage_notes_en=["Link data, ETA and deviations across the supply chain."],
            module_refs=["app/core/supply_chain_tracking.py"],
        ),
        TerminologyEntry(
            term_key="lagergeld",
            domain=TerminologyDomain.FINANCE,
            canonical_de="Lagergeld",
            canonical_en="Storage fee",
            description_de="Kostenposition fuer Lagerung und Vorhaltung von Ware.",
            description_en="Cost item for warehousing and storage of goods.",
            synonyms_de=["Lagerkosten"],
            synonyms_en=["Storage cost"],
            avoid_de=["Storage rent"],
            avoid_en=["storage rent"],
            usage_notes_de=["Bei Settlement und Abrechnung sauber ausweisen."],
            usage_notes_en=["Disclose clearly in settlement and billing."],
            module_refs=["app/api/v1/endpoints/agrar_settlements.py"],
        ),
        TerminologyEntry(
            term_key="commodity_position",
            domain=TerminologyDomain.LANDHANDEL,
            canonical_de="Warenposition",
            canonical_en="Commodity position",
            description_de="Fachposition fuer konkrete Ware, Menge, Qualitaet und Preislogik.",
            description_en="Business position for a concrete commodity, quantity, quality and pricing logic.",
            synonyms_de=["Artikelposition"],
            synonyms_en=["Item position"],
            avoid_de=["Line item"],
            avoid_en=["line item"],
            usage_notes_de=["In Fachberichten und Prozessen als Warenposition bezeichnen."],
            usage_notes_en=["Use commodity position in business reports and flows."],
            module_refs=["app/core/commodity_positions.py", "app/api/v1/endpoints/commodity_positions.py"],
        ),
    ]


def build_landhandel_terminology_registry() -> TerminologyRegistry:
    return TerminologyRegistry(entries=_build_entries(), rules=_build_rules())

