"""
tenant_rate_limits.py — Tenant-isolierte Caches/Rate-Limits (Wave 34, Gap 038)

Rate-Limit-Contracts fuer Tenant-Isolation.
Verhindert Cross-Tenant-Performance-Kollisionen durch deterministisches
Rate-Limit-Checking ohne echten Cache-Layer im Core.

Gap 038: Tenant-isolierte Caches/Rate Limits — 0 Cross-tenant Performance-Kollisionen.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class RateLimitGranularitaet(str, Enum):
    """Zeitfenster fuer Rate-Limit-Pruefung."""
    SEKUNDE  = "SEKUNDE"
    MINUTE   = "MINUTE"
    STUNDE   = "STUNDE"
    TAG      = "TAG"


class RateLimitBereich(str, Enum):
    """Auf welcher Ebene gilt das Limit."""
    TENANT   = "TENANT"    # Pro Tenant
    USER     = "USER"      # Pro User innerhalb eines Tenants
    ENDPOINT = "ENDPOINT"  # Pro API-Endpunkt (global)
    GLOBAL   = "GLOBAL"    # Systemweit


class RateLimitResultTyp(str, Enum):
    """Ergebnis der Rate-Limit-Pruefung."""
    ERLAUBT    = "ERLAUBT"     # Request darf durch
    GEDROSSELT = "GEDROSSELT"  # Soft-Limit — warnen aber durchlassen
    BLOCKIERT  = "BLOCKIERT"   # Hard-Limit — ablehnen


class CacheStrategie(str, Enum):
    """Cache-Strategie fuer Tenant-Daten."""
    KEIN_CACHE      = "KEIN_CACHE"     # Immer live lesen
    SHARED          = "SHARED"         # Gemeinsamer Cache (nur fuer unkritische Daten)
    TENANT_ISOLIERT = "TENANT_ISOLIERT" # Getrennter Cache-Namespace pro Tenant
    PRIVAT          = "PRIVAT"         # Nur fuer diesen User


# ---------------------------------------------------------------------------
# Rate-Limit-Policy
# ---------------------------------------------------------------------------

@dataclass
class RateLimitPolicy:
    """
    Konfigurierbare Rate-Limit-Policy fuer einen Endpoint/Domain.
    """
    policy_id: str
    domain: str
    endpoint_pattern: str           # z.B. "/api/v1/agrar/*" oder "*"
    bereich: RateLimitBereich
    granularitaet: RateLimitGranularitaet
    soft_limit: int                 # Anfragen pro Zeitfenster (Warnung)
    hard_limit: int                 # Anfragen pro Zeitfenster (Blockierung)
    beschreibung: str
    tenant_override_erlaubt: bool = True  # Darf Tenant eigene Limits setzen?
    aktiv: bool = True

    def as_dict(self) -> dict:
        return {
            "policy_id": self.policy_id,
            "domain": self.domain,
            "endpoint_pattern": self.endpoint_pattern,
            "bereich": self.bereich.value,
            "granularitaet": self.granularitaet.value,
            "soft_limit": self.soft_limit,
            "hard_limit": self.hard_limit,
            "beschreibung": self.beschreibung,
            "tenant_override_erlaubt": self.tenant_override_erlaubt,
            "aktiv": self.aktiv,
        }


# ---------------------------------------------------------------------------
# Tenant-Cache-Konfiguration
# ---------------------------------------------------------------------------

@dataclass
class TenantCacheConfig:
    """Cache-Konfiguration fuer einen Tenant."""
    tenant_id: str
    strategie: CacheStrategie
    ttl_sekunden: int
    max_cache_eintraege: int
    beschreibung: str = ""

    def as_dict(self) -> dict:
        return {
            "tenant_id": self.tenant_id,
            "strategie": self.strategie.value,
            "ttl_sekunden": self.ttl_sekunden,
            "max_cache_eintraege": self.max_cache_eintraege,
            "beschreibung": self.beschreibung,
        }


@dataclass
class TenantRateLimitOverview:
    """Tenant-spezifische Sicht auf Cache- und Rate-Limit-Isolation."""

    tenant_id: str
    cache_namespace: str
    cache_config: TenantCacheConfig
    policy_count: int
    tenant_isolated_policies: int
    tenant_override_allowed_policies: int
    domains: list[str] = field(default_factory=list)
    schema_version: int = 1

    def as_dict(self) -> dict[str, Any]:
        return {
            "tenant_id": self.tenant_id,
            "cache_namespace": self.cache_namespace,
            "cache_config": self.cache_config.as_dict(),
            "policy_count": self.policy_count,
            "tenant_isolated_policies": self.tenant_isolated_policies,
            "tenant_override_allowed_policies": self.tenant_override_allowed_policies,
            "domains": self.domains,
            "schema_version": self.schema_version,
        }


# ---------------------------------------------------------------------------
# Rate-Limit-Request + Result
# ---------------------------------------------------------------------------

@dataclass
class RateLimitRequest:
    """Anfrage an die Rate-Limit-Pruefung."""
    tenant_id: str
    user_id: str
    endpoint: str
    domain: str
    aktuelle_zaehlung: int          # Bisherige Anfragen in diesem Zeitfenster
    zeitfenster_sekunden: int = 60

    def as_dict(self) -> dict:
        return {
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "endpoint": self.endpoint,
            "domain": self.domain,
            "aktuelle_zaehlung": self.aktuelle_zaehlung,
            "zeitfenster_sekunden": self.zeitfenster_sekunden,
        }


@dataclass
class RateLimitResult:
    """Ergebnis der Rate-Limit-Pruefung."""
    typ: RateLimitResultTyp
    angewendete_policy_id: str | None
    tenant_id: str
    endpoint: str
    aktuelle_zaehlung: int
    soft_limit: int
    hard_limit: int
    empfohlener_http_status: int
    meldung: str
    retry_after_sekunden: int | None = None
    schema_version: int = 1

    def as_dict(self) -> dict:
        return {
            "typ": self.typ.value,
            "angewendete_policy_id": self.angewendete_policy_id,
            "tenant_id": self.tenant_id,
            "endpoint": self.endpoint,
            "aktuelle_zaehlung": self.aktuelle_zaehlung,
            "soft_limit": self.soft_limit,
            "hard_limit": self.hard_limit,
            "empfohlener_http_status": self.empfohlener_http_status,
            "meldung": self.meldung,
            "retry_after_sekunden": self.retry_after_sekunden,
            "schema_version": self.schema_version,
        }


# ---------------------------------------------------------------------------
# evaluate_rate_limit
# ---------------------------------------------------------------------------

def _endpoint_matches(pattern: str, endpoint: str) -> bool:
    """Einfaches Wildcard-Matching: '*' als Suffix-Platzhalter oder exakt."""
    if pattern == "*":
        return True
    if pattern.endswith("/*"):
        prefix = pattern[:-1]  # removes '*' but keeps '/'
        return endpoint.startswith(prefix) or endpoint == prefix.rstrip("/")
    return pattern == endpoint


def evaluate_rate_limit(
    request: RateLimitRequest,
    policies: list[RateLimitPolicy],
) -> RateLimitResult:
    """
    Bestimmt ob ein Request durchgelassen, gedrosselt oder blockiert wird.

    Matching-Logik:
    1. Aktive Policies fuer die Domain filtern (oder "*")
    2. Endpoint-Pattern pruefen
    3. Hoechstes hard_limit gewinnt bei mehreren Matches
       (konservativste Policy = niedrigstes hard_limit)

    Args:
        request: Der eingehende Request mit Zaehler.
        policies: Liste der konfigurierten Rate-Limit-Policies.

    Returns:
        RateLimitResult.
    """
    kandidaten = [
        p for p in policies
        if p.aktiv
        and (p.domain == request.domain or p.domain == "*")
        and _endpoint_matches(p.endpoint_pattern, request.endpoint)
    ]

    if not kandidaten:
        # Kein Limit konfiguriert -> durchlassen
        return RateLimitResult(
            typ=RateLimitResultTyp.ERLAUBT,
            angewendete_policy_id=None,
            tenant_id=request.tenant_id,
            endpoint=request.endpoint,
            aktuelle_zaehlung=request.aktuelle_zaehlung,
            soft_limit=0,
            hard_limit=0,
            empfohlener_http_status=200,
            meldung="Kein Rate-Limit konfiguriert — Request durchgelassen.",
        )

    # Konservativste Policy (niedrigstes hard_limit) gewinnt
    policy = min(kandidaten, key=lambda p: p.hard_limit)

    if request.aktuelle_zaehlung >= policy.hard_limit:
        return RateLimitResult(
            typ=RateLimitResultTyp.BLOCKIERT,
            angewendete_policy_id=policy.policy_id,
            tenant_id=request.tenant_id,
            endpoint=request.endpoint,
            aktuelle_zaehlung=request.aktuelle_zaehlung,
            soft_limit=policy.soft_limit,
            hard_limit=policy.hard_limit,
            empfohlener_http_status=429,
            meldung=(
                f"Rate-Limit erreicht: {request.aktuelle_zaehlung}/"
                f"{policy.hard_limit} ({policy.granularitaet.value}). "
                f"Tenant: {request.tenant_id}."
            ),
            retry_after_sekunden=request.zeitfenster_sekunden,
        )

    if request.aktuelle_zaehlung >= policy.soft_limit:
        return RateLimitResult(
            typ=RateLimitResultTyp.GEDROSSELT,
            angewendete_policy_id=policy.policy_id,
            tenant_id=request.tenant_id,
            endpoint=request.endpoint,
            aktuelle_zaehlung=request.aktuelle_zaehlung,
            soft_limit=policy.soft_limit,
            hard_limit=policy.hard_limit,
            empfohlener_http_status=200,
            meldung=(
                f"Soft-Limit erreicht: {request.aktuelle_zaehlung}/"
                f"{policy.soft_limit} — Drosselung aktiv."
            ),
        )

    return RateLimitResult(
        typ=RateLimitResultTyp.ERLAUBT,
        angewendete_policy_id=policy.policy_id,
        tenant_id=request.tenant_id,
        endpoint=request.endpoint,
        aktuelle_zaehlung=request.aktuelle_zaehlung,
        soft_limit=policy.soft_limit,
        hard_limit=policy.hard_limit,
        empfohlener_http_status=200,
        meldung=f"Erlaubt: {request.aktuelle_zaehlung}/{policy.hard_limit}.",
    )


# ---------------------------------------------------------------------------
# Default-Rate-Limit-Policies
# ---------------------------------------------------------------------------

def get_default_rate_limit_policies() -> list[RateLimitPolicy]:
    """
    Liefert Default-Rate-Limit-Policies fuer alle Domains.

    Deckung: Agrar, Finance, Compliance, Workflow, Global-Catch-all.
    """
    return [
        # --- Global ---
        RateLimitPolicy(
            policy_id="RL-GLOBAL-001",
            domain="*",
            endpoint_pattern="*",
            bereich=RateLimitBereich.TENANT,
            granularitaet=RateLimitGranularitaet.MINUTE,
            soft_limit=500,
            hard_limit=1000,
            beschreibung="Global: 1000 Anfragen/Minute pro Tenant (Hard-Limit)",
        ),
        # --- Agrar ---
        RateLimitPolicy(
            policy_id="RL-AGR-001",
            domain="agrar",
            endpoint_pattern="/api/v1/agrar/*",
            bereich=RateLimitBereich.TENANT,
            granularitaet=RateLimitGranularitaet.MINUTE,
            soft_limit=200,
            hard_limit=400,
            beschreibung="Agrar: 400 Anfragen/Minute pro Tenant",
        ),
        RateLimitPolicy(
            policy_id="RL-AGR-002",
            domain="agrar",
            endpoint_pattern="/api/v1/agrar/daily-prices/*",
            bereich=RateLimitBereich.TENANT,
            granularitaet=RateLimitGranularitaet.MINUTE,
            soft_limit=30,
            hard_limit=60,
            beschreibung="Agrar-Preise: 60 Anfragen/Minute (Marktdaten-Schutz)",
            tenant_override_erlaubt=False,
        ),
        # --- Finance ---
        RateLimitPolicy(
            policy_id="RL-FIN-001",
            domain="finance",
            endpoint_pattern="/api/v1/finance/*",
            bereich=RateLimitBereich.TENANT,
            granularitaet=RateLimitGranularitaet.MINUTE,
            soft_limit=100,
            hard_limit=300,
            beschreibung="Finance: 300 Anfragen/Minute pro Tenant",
        ),
        RateLimitPolicy(
            policy_id="RL-FIN-002",
            domain="finance",
            endpoint_pattern="/api/v1/finance/payment-runs",
            bereich=RateLimitBereich.TENANT,
            granularitaet=RateLimitGranularitaet.STUNDE,
            soft_limit=5,
            hard_limit=10,
            beschreibung="Zahlungslaeufe: max. 10 Starts/Stunde (Schutz vor Doppelzahlung)",
            tenant_override_erlaubt=False,
        ),
        # --- Compliance ---
        RateLimitPolicy(
            policy_id="RL-COM-001",
            domain="compliance",
            endpoint_pattern="/api/v1/compliance/*",
            bereich=RateLimitBereich.TENANT,
            granularitaet=RateLimitGranularitaet.MINUTE,
            soft_limit=50,
            hard_limit=100,
            beschreibung="Compliance: 100 Anfragen/Minute (Meldungen aendern sich selten)",
        ),
        # --- Process/Workflow ---
        RateLimitPolicy(
            policy_id="RL-WF-001",
            domain="workflow",
            endpoint_pattern="/api/v1/process/*",
            bereich=RateLimitBereich.TENANT,
            granularitaet=RateLimitGranularitaet.MINUTE,
            soft_limit=100,
            hard_limit=200,
            beschreibung="Workflow: 200 Anfragen/Minute pro Tenant",
        ),
        # --- Bulk-Operationen (strenger) ---
        RateLimitPolicy(
            policy_id="RL-BULK-001",
            domain="*",
            endpoint_pattern="/api/v1/process/bulk-operations/*",
            bereich=RateLimitBereich.TENANT,
            granularitaet=RateLimitGranularitaet.MINUTE,
            soft_limit=5,
            hard_limit=20,
            beschreibung="Bulk-Ops: max. 20 Batch-Requests/Minute pro Tenant",
        ),
    ]


# ---------------------------------------------------------------------------
# Tenant-Cache-Default-Konfigurationen
# ---------------------------------------------------------------------------

def get_default_cache_configs() -> list[TenantCacheConfig]:
    """Default-Cache-Konfiguration fuer Standard-, Premium- und System-Tenants."""
    return [
        TenantCacheConfig(
            tenant_id="DEFAULT",
            strategie=CacheStrategie.TENANT_ISOLIERT,
            ttl_sekunden=300,
            max_cache_eintraege=5000,
            beschreibung="Standard-Tenant: isolierter Cache, 5 Min TTL",
        ),
        TenantCacheConfig(
            tenant_id="PREMIUM",
            strategie=CacheStrategie.TENANT_ISOLIERT,
            ttl_sekunden=600,
            max_cache_eintraege=20000,
            beschreibung="Premium-Tenant: groesserer Cache, 10 Min TTL",
        ),
        TenantCacheConfig(
            tenant_id="SYSTEM",
            strategie=CacheStrategie.PRIVAT,
            ttl_sekunden=60,
            max_cache_eintraege=1000,
            beschreibung="System-Tenant: kurze TTL, privat",
        ),
    ]


@dataclass
class TenantIsolationRegistry:
    """Read-model registry for tenant-isolated cache and rate-limit views."""

    policies: list[RateLimitPolicy] = field(default_factory=get_default_rate_limit_policies)
    cache_configs: list[TenantCacheConfig] = field(default_factory=get_default_cache_configs)
    schema_version: int = 1

    def get_cache_config(self, tenant_id: str) -> TenantCacheConfig:
        normalized = tenant_id.strip().upper()
        for config in self.cache_configs:
            if config.tenant_id.upper() == normalized:
                return TenantCacheConfig(
                    tenant_id=tenant_id,
                    strategie=config.strategie,
                    ttl_sekunden=config.ttl_sekunden,
                    max_cache_eintraege=config.max_cache_eintraege,
                    beschreibung=config.beschreibung,
                )
        default = next((config for config in self.cache_configs if config.tenant_id.upper() == "DEFAULT"), self.cache_configs[0])
        return TenantCacheConfig(
            tenant_id=tenant_id,
            strategie=default.strategie,
            ttl_sekunden=default.ttl_sekunden,
            max_cache_eintraege=default.max_cache_eintraege,
            beschreibung=default.beschreibung,
        )

    def get_policies(self, domain: str = "") -> list[RateLimitPolicy]:
        if not domain:
            return list(self.policies)
        return [policy for policy in self.policies if policy.domain == domain or policy.domain == "*"]

    def build_overview(self, tenant_id: str, domain: str = "") -> TenantRateLimitOverview:
        policies = self.get_policies(domain)
        cache_config = self.get_cache_config(tenant_id)
        return TenantRateLimitOverview(
            tenant_id=tenant_id,
            cache_namespace=f"tenant:{tenant_id}",
            cache_config=cache_config,
            policy_count=len(policies),
            tenant_isolated_policies=sum(1 for policy in policies if policy.bereich == RateLimitBereich.TENANT),
            tenant_override_allowed_policies=sum(1 for policy in policies if policy.tenant_override_erlaubt),
            domains=sorted({policy.domain for policy in policies}),
        )

    def evaluate(self, request: RateLimitRequest) -> RateLimitResult:
        return evaluate_rate_limit(request, self.get_policies(request.domain))


_TENANT_ISOLATION_REGISTRY = TenantIsolationRegistry()


def get_tenant_isolation_registry() -> TenantIsolationRegistry:
    return _TENANT_ISOLATION_REGISTRY
