"""
Policy-as-Code Engine — Wave 29 AP1/AP2

Geschaeftsregeln als versionierte, pruefbare PolicySets.
Tenant-Overrides erlauben genossenschaftsspezifische Ausnahmen ohne Code-Aenderung.

Gap 014: Policy-as-Code mit Tenant Overrides — 100% Ausnahmen regelbasiert dokumentiert.

Aktionen:
  ERLAUBT    — Regel erlaubt die Aktion explizit
  ABGELEHNT  — Regel lehnt die Aktion ab (hoechste Prioritaet)
  WARNUNG    — Aktion erlaubt, aber mit Hinweis
  ESKALATION — Eskalation an Teamleiter erforderlich
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from datetime import date, datetime, time
from enum import Enum
from typing import Any, Optional


POLICY_ENGINE_SCHEMA_VERSION = 1


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class PolicyBedingungsTyp(str, Enum):
    GLEICH            = "GLEICH"             # feld == wert
    UNGLEICH          = "UNGLEICH"           # feld != wert
    GROESSER          = "GROESSER"           # feld > wert (numerisch)
    GROESSER_GLEICH   = "GROESSER_GLEICH"    # feld >= wert
    KLEINER           = "KLEINER"            # feld < wert
    KLEINER_GLEICH    = "KLEINER_GLEICH"     # feld <= wert
    ENTHAELT          = "ENTHAELT"           # wert in feld (Liste oder String)
    NICHT_LEER        = "NICHT_LEER"         # feld ist gesetzt und nicht leer
    # Wave 2: Temporale Bedingungen
    WOCHENTAG         = "WOCHENTAG"          # wert = Liste von Wochentag-Ints (0=Mo..6=So)
    ZEITRAUM          = "ZEITRAUM"           # wert = {"von": "YYYY-MM-DD", "bis": "YYYY-MM-DD"}
    UHRZEIT           = "UHRZEIT"            # wert = {"von": "HH:MM", "bis": "HH:MM"}


class PolicyAktion(str, Enum):
    ERLAUBT    = "ERLAUBT"
    ABGELEHNT  = "ABGELEHNT"
    WARNUNG    = "WARNUNG"
    ESKALATION = "ESKALATION"


class PolicyViolationCode(str, Enum):
    KONFLIKT_ERLAUBT_ABGELEHNT   = "KONFLIKT_ERLAUBT_ABGELEHNT"
    DOPPELTE_REGEL_ID            = "DOPPELTE_REGEL_ID"
    UNBEKANNTES_FELD             = "UNBEKANNTES_FELD"
    PROZESS_KEY_LEER             = "PROZESS_KEY_LEER"
    UNGUELTIGE_OVERRIDE_REGEL_ID = "UNGUELTIGE_OVERRIDE_REGEL_ID"


# ---------------------------------------------------------------------------
# AP1: PolicyRegel + PolicySet
# ---------------------------------------------------------------------------

@dataclass
class PolicyBedingung:
    """Einzelne Auswertungsbedingung einer Regel."""
    typ: PolicyBedingungsTyp
    feld: str           # Schluessel im Kontext-Dict (z.B. "betrag_eur", "rolle", "land")
    wert: Any = None    # Vergleichswert; bei NICHT_LEER ignoriert

    def evaluate(self, kontext: dict[str, Any], *, now: datetime | None = None) -> bool:
        """Wertet die Bedingung gegen den Prozesskontext aus."""
        # Wave 2: Temporale Bedingungen (nutzen Systemzeit, nicht Kontext-Feld)
        if self.typ in (PolicyBedingungsTyp.WOCHENTAG, PolicyBedingungsTyp.ZEITRAUM, PolicyBedingungsTyp.UHRZEIT):
            return self._evaluate_temporal(now or datetime.now())

        feldwert = kontext.get(self.feld)
        try:
            if self.typ == PolicyBedingungsTyp.NICHT_LEER:
                return feldwert is not None and feldwert != "" and feldwert != []
            if feldwert is None:
                return False
            if self.typ == PolicyBedingungsTyp.GLEICH:
                return feldwert == self.wert
            if self.typ == PolicyBedingungsTyp.UNGLEICH:
                return feldwert != self.wert
            if self.typ == PolicyBedingungsTyp.ENTHAELT:
                if isinstance(feldwert, (list, tuple, set)):
                    return self.wert in feldwert
                return str(self.wert) in str(feldwert)
            # Numerische Vergleiche
            num_feld = float(feldwert)
            num_wert = float(self.wert)
            if self.typ == PolicyBedingungsTyp.GROESSER:
                return num_feld > num_wert
            if self.typ == PolicyBedingungsTyp.GROESSER_GLEICH:
                return num_feld >= num_wert
            if self.typ == PolicyBedingungsTyp.KLEINER:
                return num_feld < num_wert
            if self.typ == PolicyBedingungsTyp.KLEINER_GLEICH:
                return num_feld <= num_wert
        except (TypeError, ValueError):
            return False
        return False

    def _evaluate_temporal(self, now: datetime) -> bool:
        """Wave 2: Temporale Bedingungsauswertung."""
        try:
            if self.typ == PolicyBedingungsTyp.WOCHENTAG:
                return now.weekday() in self.wert
            if self.typ == PolicyBedingungsTyp.ZEITRAUM:
                von = date.fromisoformat(self.wert["von"])
                bis = date.fromisoformat(self.wert["bis"])
                return von <= now.date() <= bis
            if self.typ == PolicyBedingungsTyp.UHRZEIT:
                von = time.fromisoformat(self.wert["von"])
                bis = time.fromisoformat(self.wert["bis"])
                return von <= now.time() <= bis
        except (TypeError, ValueError, KeyError):
            return False
        return False

    def as_dict(self) -> dict:
        return {
            "typ": self.typ.value,
            "feld": self.feld,
            "wert": self.wert,
        }


@dataclass
class PolicyBedingungsGruppe:
    """
    Wave 2: Rekursive AND/OR-Gruppe fuer verschachtelte Bedingungen.

    operator = "AND" → alle Kinder muessen zutreffen
    operator = "OR"  → mindestens ein Kind muss zutreffen
    Kinder koennen PolicyBedingung oder weitere PolicyBedingungsGruppe sein.
    """
    operator: str  # "AND" | "OR"
    kinder: list[Any] = field(default_factory=list)  # PolicyBedingung | PolicyBedingungsGruppe

    def evaluate(self, kontext: dict[str, Any], *, now: datetime | None = None) -> bool:
        if not self.kinder:
            return True
        results = (
            child.evaluate(kontext, now=now) if isinstance(child, (PolicyBedingung, PolicyBedingungsGruppe))
            else child.evaluate(kontext)
            for child in self.kinder
        )
        if self.operator == "OR":
            return any(results)
        return all(results)

    def as_dict(self) -> dict:
        return {
            "operator": self.operator,
            "kinder": [k.as_dict() for k in self.kinder],
        }


@dataclass
class PolicyRegel:
    """
    Einzelne Geschaeftsregel innerhalb eines PolicySets.

    Alle Bedingungen muessen zutreffen (AND-Logik) damit die Aktion greift.
    Optional: bedingungsgruppe fuer verschachtelte AND/OR-Logik (Wave 2).
    """
    regel_id: str
    bezeichnung: str
    bedingungen: list[PolicyBedingung]
    aktion: PolicyAktion
    prioritaet: int = 100          # Niedrigerer Wert = hoehere Prioritaet
    pflicht: bool = False          # Pflichtregeln koennen durch Overrides nicht deaktiviert werden
    begruendung: str = ""          # Erklaerung fuer Audit-Trail
    bedingungsgruppe: Optional[PolicyBedingungsGruppe] = None  # Wave 2: verschachtelte Logik

    def matches(self, kontext: dict[str, Any], *, now: datetime | None = None) -> bool:
        """Gibt True zurueck wenn alle Bedingungen erfuellt sind."""
        if self.bedingungsgruppe is not None:
            return self.bedingungsgruppe.evaluate(kontext, now=now)
        return all(b.evaluate(kontext, now=now) for b in self.bedingungen)

    def as_dict(self) -> dict:
        return {
            "regel_id": self.regel_id,
            "bezeichnung": self.bezeichnung,
            "bedingungen": [b.as_dict() for b in self.bedingungen],
            "aktion": self.aktion.value,
            "prioritaet": self.prioritaet,
            "pflicht": self.pflicht,
            "begruendung": self.begruendung,
        }


@dataclass
class PolicySet:
    """Versioniertes Regelset fuer einen Prozessschritt oder -gesamtprozess."""
    policy_set_id: str
    prozess_key: str
    bezeichnung: str
    regeln: list[PolicyRegel] = field(default_factory=list)
    schema_version: int = POLICY_ENGINE_SCHEMA_VERSION

    def as_dict(self) -> dict:
        return {
            "policy_set_id": self.policy_set_id,
            "prozess_key": self.prozess_key,
            "bezeichnung": self.bezeichnung,
            "regel_count": len(self.regeln),
            "regeln": [r.as_dict() for r in self.regeln],
            "schema_version": self.schema_version,
        }


# ---------------------------------------------------------------------------
# AP1: evaluate_policy_set()
# ---------------------------------------------------------------------------

@dataclass
class PolicyRegelTreffer:
    """Eine ausgeloeste Regel im Auswertungsergebnis."""
    regel_id: str
    bezeichnung: str
    aktion: PolicyAktion
    prioritaet: int
    begruendung: str

    def as_dict(self) -> dict:
        return {
            "regel_id": self.regel_id,
            "bezeichnung": self.bezeichnung,
            "aktion": self.aktion.value,
            "prioritaet": self.prioritaet,
            "begruendung": self.begruendung,
        }


# Aktions-Prioritaet: ABGELEHNT > ESKALATION > WARNUNG > ERLAUBT
_AKTION_RANG: dict[PolicyAktion, int] = {
    PolicyAktion.ABGELEHNT:  4,
    PolicyAktion.ESKALATION: 3,
    PolicyAktion.WARNUNG:    2,
    PolicyAktion.ERLAUBT:    1,
}


@dataclass
class PolicyEvaluationResult:
    """Ergebnis der PolicySet-Auswertung fuer einen Kontext."""
    policy_set_id: str
    prozess_key: str
    wirksame_aktion: PolicyAktion       # Schwerste ausgeloeste Aktion
    treffer: list[PolicyRegelTreffer]   # Alle passenden Regeln
    kein_treffer: bool                  # True wenn keine Regel passte → implizit ERLAUBT
    schema_version: int = POLICY_ENGINE_SCHEMA_VERSION

    @property
    def abgelehnt(self) -> bool:
        return self.wirksame_aktion == PolicyAktion.ABGELEHNT

    @property
    def eskalation_erforderlich(self) -> bool:
        return self.wirksame_aktion in (PolicyAktion.ABGELEHNT, PolicyAktion.ESKALATION)

    def as_dict(self) -> dict:
        return {
            "policy_set_id": self.policy_set_id,
            "prozess_key": self.prozess_key,
            "wirksame_aktion": self.wirksame_aktion.value,
            "abgelehnt": self.abgelehnt,
            "eskalation_erforderlich": self.eskalation_erforderlich,
            "treffer_count": len(self.treffer),
            "kein_treffer": self.kein_treffer,
            "treffer": [t.as_dict() for t in self.treffer],
            "schema_version": self.schema_version,
        }


def evaluate_policy_set(
    policy_set: PolicySet,
    kontext: dict[str, Any],
) -> PolicyEvaluationResult:
    """
    Wertet alle Regeln des PolicySets gegen den Prozesskontext aus.

    Semantik:
    - Alle passenden Regeln werden gesammelt.
    - Die wirksame Aktion ist die mit dem hoechsten Rang (ABGELEHNT > ESKALATION > WARNUNG > ERLAUBT).
    - Wenn keine Regel passt → implizit ERLAUBT.
    - Regeln werden nach Prioritaet sortiert ausgewertet (niedrig = hoch).
    """
    treffer: list[PolicyRegelTreffer] = []

    for regel in sorted(policy_set.regeln, key=lambda r: r.prioritaet):
        if regel.matches(kontext):
            treffer.append(PolicyRegelTreffer(
                regel_id=regel.regel_id,
                bezeichnung=regel.bezeichnung,
                aktion=regel.aktion,
                prioritaet=regel.prioritaet,
                begruendung=regel.begruendung,
            ))

    if not treffer:
        return PolicyEvaluationResult(
            policy_set_id=policy_set.policy_set_id,
            prozess_key=policy_set.prozess_key,
            wirksame_aktion=PolicyAktion.ERLAUBT,
            treffer=[],
            kein_treffer=True,
        )

    wirksame = max(treffer, key=lambda t: _AKTION_RANG[t.aktion])

    return PolicyEvaluationResult(
        policy_set_id=policy_set.policy_set_id,
        prozess_key=policy_set.prozess_key,
        wirksame_aktion=wirksame.aktion,
        treffer=treffer,
        kein_treffer=False,
    )


# ---------------------------------------------------------------------------
# AP2: TenantPolicyOverride + apply_tenant_overrides()
# ---------------------------------------------------------------------------

@dataclass
class TenantPolicyOverride:
    """
    Tenant-spezifische Erweiterung/Deaktivierung eines PolicySets.

    Pflichtregeln (pflicht=True) koennen nicht deaktiviert werden.
    """
    tenant_id: str
    policy_set_id: str
    zusaetzliche_regeln: list[PolicyRegel] = field(default_factory=list)
    deaktivierte_regel_ids: list[str] = field(default_factory=list)
    regel_parameter_overrides: dict[str, dict[str, Any]] = field(default_factory=dict)
    schema_version: int = POLICY_ENGINE_SCHEMA_VERSION

    def as_dict(self) -> dict:
        return {
            "tenant_id": self.tenant_id,
            "policy_set_id": self.policy_set_id,
            "zusaetzliche_regeln_count": len(self.zusaetzliche_regeln),
            "deaktivierte_regel_ids": self.deaktivierte_regel_ids,
            "regel_parameter_overrides": self.regel_parameter_overrides,
            "schema_version": self.schema_version,
        }


def _coerce_policy_bedingung(data: Any) -> PolicyBedingung:
    if isinstance(data, PolicyBedingung):
        return deepcopy(data)
    return PolicyBedingung(
        typ=PolicyBedingungsTyp(data["typ"]),
        feld=data["feld"],
        wert=data.get("wert"),
    )


def _coerce_policy_bedingungsgruppe(data: Any) -> PolicyBedingungsGruppe:
    if isinstance(data, PolicyBedingungsGruppe):
        return deepcopy(data)
    return PolicyBedingungsGruppe(
        operator=data["operator"],
        kinder=[
            _coerce_policy_bedingungsgruppe(kind)
            if isinstance(kind, dict) and "operator" in kind
            else _coerce_policy_bedingung(kind)
            for kind in data.get("kinder", [])
        ],
    )


def _coerce_policy_regel(data: Any) -> PolicyRegel:
    if isinstance(data, PolicyRegel):
        return deepcopy(data)
    return PolicyRegel(
        regel_id=data["regel_id"],
        bezeichnung=data["bezeichnung"],
        bedingungen=[_coerce_policy_bedingung(item) for item in data.get("bedingungen", [])],
        aktion=PolicyAktion(data["aktion"]),
        prioritaet=data.get("prioritaet", 100),
        pflicht=data.get("pflicht", False),
        begruendung=data.get("begruendung", ""),
        bedingungsgruppe=(
            _coerce_policy_bedingungsgruppe(data["bedingungsgruppe"])
            if data.get("bedingungsgruppe") is not None
            else None
        ),
    )


def _apply_parameter_overrides_to_gruppe(
    gruppe: PolicyBedingungsGruppe | None,
    feld_overrides: dict[str, Any],
) -> PolicyBedingungsGruppe | None:
    if gruppe is None:
        return None
    neue_kinder: list[Any] = []
    for kind in gruppe.kinder:
        if isinstance(kind, PolicyBedingungsGruppe):
            neue_kinder.append(_apply_parameter_overrides_to_gruppe(kind, feld_overrides))
        else:
            neuer_wert = feld_overrides.get(kind.feld, kind.wert)
            neue_kinder.append(
                PolicyBedingung(
                    typ=kind.typ,
                    feld=kind.feld,
                    wert=neuer_wert,
                )
            )
    return PolicyBedingungsGruppe(operator=gruppe.operator, kinder=neue_kinder)


def _apply_parameter_overrides_to_regel(
    regel: PolicyRegel,
    feld_overrides: dict[str, Any],
) -> PolicyRegel:
    if not feld_overrides:
        return deepcopy(regel)
    return PolicyRegel(
        regel_id=regel.regel_id,
        bezeichnung=regel.bezeichnung,
        bedingungen=[
            PolicyBedingung(
                typ=bedingung.typ,
                feld=bedingung.feld,
                wert=feld_overrides.get(bedingung.feld, bedingung.wert),
            )
            for bedingung in regel.bedingungen
        ],
        aktion=regel.aktion,
        prioritaet=regel.prioritaet,
        pflicht=regel.pflicht,
        begruendung=regel.begruendung,
        bedingungsgruppe=_apply_parameter_overrides_to_gruppe(
            regel.bedingungsgruppe,
            feld_overrides,
        ),
    )


def normalize_tenant_policy_overrides(
    tenant_id: str,
    overrides: Any,
    *,
    policy_sets: list[PolicySet] | None = None,
) -> list[TenantPolicyOverride]:
    """
    Normalize runtime tenant override payloads into typed overrides.

    Supported formats:
    - list[dict|TenantPolicyOverride] with explicit `policy_set_id`
    - dict keyed by `policy_set_id`
    - legacy admin/settings dict keyed by `regel_id` with `enabled` / `params_override`
    """
    if not overrides:
        return []

    def _normalize_single(item: Any, default_policy_set_id: str | None = None) -> TenantPolicyOverride:
        if isinstance(item, TenantPolicyOverride):
            return deepcopy(item)

        policy_set_id = item.get("policy_set_id") or default_policy_set_id
        if not policy_set_id:
            raise ValueError("tenant policy override requires policy_set_id")

        return TenantPolicyOverride(
            tenant_id=item.get("tenant_id", tenant_id),
            policy_set_id=policy_set_id,
            deaktivierte_regel_ids=list(item.get("deaktivierte_regel_ids", [])),
            zusaetzliche_regeln=[
                _coerce_policy_regel(regel)
                for regel in item.get("zusaetzliche_regeln", [])
            ],
            regel_parameter_overrides={
                regel_id: dict(params)
                for regel_id, params in item.get("regel_parameter_overrides", {}).items()
                if isinstance(params, dict)
            },
        )

    if isinstance(overrides, list):
        return [_normalize_single(item) for item in overrides]

    if not isinstance(overrides, dict):
        return []

    explicit_keys = {
        "policy_set_id",
        "tenant_id",
        "deaktivierte_regel_ids",
        "zusaetzliche_regeln",
        "regel_parameter_overrides",
    }
    if explicit_keys & set(overrides.keys()):
        return [_normalize_single(overrides)]

    policy_set_ids = {ps.policy_set_id for ps in policy_sets or []}
    if set(overrides.keys()) & policy_set_ids:
        return [
            _normalize_single(value, default_policy_set_id=policy_set_id)
            for policy_set_id, value in overrides.items()
            if isinstance(value, dict)
        ]

    normalized: list[TenantPolicyOverride] = []
    for policy_set in policy_sets or []:
        disabled_ids: list[str] = []
        parameter_overrides: dict[str, dict[str, Any]] = {}
        for regel in policy_set.regeln:
            legacy = overrides.get(regel.regel_id)
            if not isinstance(legacy, dict):
                continue
            if legacy.get("enabled") is False:
                disabled_ids.append(regel.regel_id)
            if isinstance(legacy.get("params_override"), dict):
                parameter_overrides[regel.regel_id] = dict(legacy["params_override"])

        if disabled_ids or parameter_overrides:
            normalized.append(
                TenantPolicyOverride(
                    tenant_id=tenant_id,
                    policy_set_id=policy_set.policy_set_id,
                    deaktivierte_regel_ids=disabled_ids,
                    regel_parameter_overrides=parameter_overrides,
                )
            )
    return normalized


def resolve_tenant_policy_sets(
    policy_sets: list[PolicySet],
    tenant_id: str,
    overrides: Any,
) -> list[PolicySet]:
    """Apply matching tenant overrides to all provided policy sets."""
    normalized = normalize_tenant_policy_overrides(
        tenant_id,
        overrides,
        policy_sets=policy_sets,
    )
    override_map = {override.policy_set_id: override for override in normalized}
    resolved: list[PolicySet] = []
    for policy_set in policy_sets:
        override = override_map.get(policy_set.policy_set_id)
        resolved.append(apply_tenant_overrides(policy_set, override) if override else deepcopy(policy_set))
    return resolved


def apply_tenant_overrides(
    base_set: PolicySet,
    override: TenantPolicyOverride,
) -> PolicySet:
    """
    Wendet Tenant-Override auf ein Basis-PolicySet an.

    - Pflichtregeln koennen nicht deaktiviert werden (werden stillschweigend uebersprungen).
    - Zusaetzliche Regeln werden ans Ende der Regel-Liste angehaengt.
    - Gibt ein neues PolicySet zurueck (keine Mutation).
    """
    deaktiviert = set(override.deaktivierte_regel_ids)

    parameter_overrides = override.regel_parameter_overrides or {}

    gefilterte_regeln = [
        _apply_parameter_overrides_to_regel(r, parameter_overrides.get(r.regel_id, {}))
        for r in base_set.regeln
        if r.regel_id not in deaktiviert or r.pflicht
    ]

    merged_regeln = gefilterte_regeln + [_coerce_policy_regel(regel) for regel in override.zusaetzliche_regeln]

    return PolicySet(
        policy_set_id=base_set.policy_set_id,
        prozess_key=base_set.prozess_key,
        bezeichnung=f"{base_set.bezeichnung} [Tenant: {override.tenant_id}]",
        regeln=merged_regeln,
        schema_version=base_set.schema_version,
    )


# ---------------------------------------------------------------------------
# AP2: validate_policy_set()
# ---------------------------------------------------------------------------

@dataclass
class PolicySetViolation:
    code: PolicyViolationCode
    message: str
    regel_ids: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "code": self.code.value,
            "message": self.message,
            "regel_ids": self.regel_ids,
        }


@dataclass
class PolicySetValidationResult:
    policy_set_id: str
    valid: bool
    violations: list[PolicySetViolation] = field(default_factory=list)
    schema_version: int = POLICY_ENGINE_SCHEMA_VERSION

    def as_dict(self) -> dict:
        return {
            "policy_set_id": self.policy_set_id,
            "valid": self.valid,
            "violation_count": len(self.violations),
            "violations": [v.as_dict() for v in self.violations],
            "schema_version": self.schema_version,
        }


def validate_policy_set(policy_set: PolicySet) -> PolicySetValidationResult:
    """
    Prueft Konsistenz eines PolicySets.

    Checks:
    - prozess_key nicht leer
    - Keine doppelten regel_ids
    - Kein ERLAUBT+ABGELEHNT Konflikt fuer identische Felder/Werte
    """
    violations: list[PolicySetViolation] = []

    if not policy_set.prozess_key or not policy_set.prozess_key.strip():
        violations.append(PolicySetViolation(
            code=PolicyViolationCode.PROZESS_KEY_LEER,
            message="prozess_key darf nicht leer sein",
        ))

    # Doppelte regel_ids
    ids_seen: set[str] = set()
    doppelt: list[str] = []
    for r in policy_set.regeln:
        if r.regel_id in ids_seen:
            doppelt.append(r.regel_id)
        ids_seen.add(r.regel_id)
    if doppelt:
        violations.append(PolicySetViolation(
            code=PolicyViolationCode.DOPPELTE_REGEL_ID,
            message=f"Doppelte regel_ids: {doppelt}",
            regel_ids=doppelt,
        ))

    # ERLAUBT vs ABGELEHNT Konflikte (identische Feld+Wert-Kombination)
    erlaubt_keys: set[tuple] = set()
    abgelehnt_keys: set[tuple] = set()
    for r in policy_set.regeln:
        for b in r.bedingungen:
            key = (b.feld, b.typ.value, str(b.wert))
            if r.aktion == PolicyAktion.ERLAUBT:
                erlaubt_keys.add(key)
            elif r.aktion == PolicyAktion.ABGELEHNT:
                abgelehnt_keys.add(key)

    konflikte = erlaubt_keys & abgelehnt_keys
    if konflikte:
        violations.append(PolicySetViolation(
            code=PolicyViolationCode.KONFLIKT_ERLAUBT_ABGELEHNT,
            message=f"ERLAUBT und ABGELEHNT fuer dieselbe Bedingung: {list(konflikte)[:3]}",
        ))

    return PolicySetValidationResult(
        policy_set_id=policy_set.policy_set_id,
        valid=len(violations) == 0,
        violations=violations,
    )


# ---------------------------------------------------------------------------
# Default-PolicySets fuer Agrar-Kernprozesse
# ---------------------------------------------------------------------------

def get_default_agrar_policy_sets() -> list[PolicySet]:
    """
    Default-PolicySets fuer agrar_settlement und wareneingang.

    Deckt typische Landhandel-Geschaeftsregeln ab:
    - Betragsfreigabe-Schwellen
    - Qualitaetsmindestanforderungen
    - Rollenbasierte Zugangskontrolle
    """
    return [
        PolicySet(
            policy_set_id="PS-AS-FREIGABE",
            prozess_key="agrar_settlement",
            bezeichnung="Settlement Freigabe-Regeln",
            regeln=[
                PolicyRegel(
                    regel_id="AS-FR-001",
                    bezeichnung="Grossbetrag braucht 4-Augen-Freigabe",
                    bedingungen=[
                        PolicyBedingung(PolicyBedingungsTyp.GROESSER_GLEICH, "brutto_eur", 50000),
                    ],
                    aktion=PolicyAktion.ESKALATION,
                    prioritaet=10,
                    pflicht=True,
                    begruendung="Betraege ab 50.000 EUR erfordern Vier-Augen-Freigabe (Kompetenzmatrix)",
                ),
                PolicyRegel(
                    regel_id="AS-FR-002",
                    bezeichnung="Fremdbetrieb-Lieferung immer eskalieren",
                    bedingungen=[
                        PolicyBedingung(PolicyBedingungsTyp.GLEICH, "lieferant_typ", "FREMDBETRIEB"),
                        PolicyBedingung(PolicyBedingungsTyp.GROESSER, "brutto_eur", 10000),
                    ],
                    aktion=PolicyAktion.ESKALATION,
                    prioritaet=20,
                    pflicht=False,
                    begruendung="Fremdbetriebs-Lieferungen ueber 10k EUR mit erhoehtem Pruefungsaufwand",
                ),
                PolicyRegel(
                    regel_id="AS-FR-003",
                    bezeichnung="Negatives Nettogewicht ablehnen",
                    bedingungen=[
                        PolicyBedingung(PolicyBedingungsTyp.KLEINER, "netto_tonnen", 0),
                    ],
                    aktion=PolicyAktion.ABGELEHNT,
                    prioritaet=1,
                    pflicht=True,
                    begruendung="Negatives Gewicht ist physikalisch unmoeglich",
                ),
                PolicyRegel(
                    regel_id="AS-FR-004",
                    bezeichnung="Standardfreigabe Mitgliedsbetrieb",
                    bedingungen=[
                        PolicyBedingung(PolicyBedingungsTyp.GLEICH, "lieferant_typ", "MITGLIED"),
                        PolicyBedingung(PolicyBedingungsTyp.KLEINER, "brutto_eur", 50000),
                    ],
                    aktion=PolicyAktion.ERLAUBT,
                    prioritaet=50,
                    pflicht=False,
                    begruendung="Mitgliedsbetriebe unter 50k EUR ohne Sonderfreigabe",
                ),
            ],
        ),

        PolicySet(
            policy_set_id="PS-WE-ANNAHME",
            prozess_key="wareneingang",
            bezeichnung="Wareneingang Annahme-Regeln",
            regeln=[
                PolicyRegel(
                    regel_id="WE-AN-001",
                    bezeichnung="Feuchte ueber Trocknungsgrenze: Warnung",
                    bedingungen=[
                        PolicyBedingung(PolicyBedingungsTyp.GROESSER, "feuchte_pct", 15.0),
                        PolicyBedingung(PolicyBedingungsTyp.KLEINER_GLEICH, "feuchte_pct", 20.0),
                    ],
                    aktion=PolicyAktion.WARNUNG,
                    prioritaet=20,
                    pflicht=False,
                    begruendung="Feuchte 15-20%: Trocknung erforderlich, Abzug berechnen",
                ),
                PolicyRegel(
                    regel_id="WE-AN-002",
                    bezeichnung="Feuchte ueber 20%: Annahme ablehnen",
                    bedingungen=[
                        PolicyBedingung(PolicyBedingungsTyp.GROESSER, "feuchte_pct", 20.0),
                    ],
                    aktion=PolicyAktion.ABGELEHNT,
                    prioritaet=5,
                    pflicht=True,
                    begruendung="Feuchte >20% nicht lagerfaehig; Annahme gesperrt",
                ),
                PolicyRegel(
                    regel_id="WE-AN-003",
                    bezeichnung="Qualitaetsprotokoll fehlt: Eskalation",
                    bedingungen=[
                        PolicyBedingung(PolicyBedingungsTyp.GLEICH, "qualitaetsprotokoll_vorhanden", False),
                    ],
                    aktion=PolicyAktion.ESKALATION,
                    prioritaet=10,
                    pflicht=True,
                    begruendung="Ohne Qualitaetsprotokoll keine automatische Freigabe",
                ),
                PolicyRegel(
                    regel_id="WE-AN-004",
                    bezeichnung="Normalannahme: feuchte ok, protokoll vorhanden",
                    bedingungen=[
                        PolicyBedingung(PolicyBedingungsTyp.KLEINER_GLEICH, "feuchte_pct", 15.0),
                        PolicyBedingung(PolicyBedingungsTyp.GLEICH, "qualitaetsprotokoll_vorhanden", True),
                    ],
                    aktion=PolicyAktion.ERLAUBT,
                    prioritaet=100,
                    pflicht=False,
                    begruendung="Standardfall: Feuchte OK und Protokoll vorhanden",
                ),
            ],
        ),
    ]
