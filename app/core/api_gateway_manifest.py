from __future__ import annotations
from pydantic import BaseModel
from enum import Enum
from typing import Optional
from datetime import datetime
import uuid

class ApiPartnerTyp(str, Enum):
    SUPPLIER = "supplier"
    BANK = "bank"
    BEHOERDE = "behoerde"
    ANALYTIK_DIENSTLEISTER = "analytik_dienstleister"
    LOGISTIK = "logistik"

class ApiScope(str, Enum):
    READ_CONTRACTS = "read_contracts"
    READ_DELIVERIES = "read_deliveries"
    WRITE_INVOICES = "write_invoices"
    READ_QUALITY = "read_quality"
    READ_SETTLEMENTS = "read_settlements"
    READ_PRICES = "read_prices"

class ApiAccessDecision(str, Enum):
    ALLOWED = "allowed"
    DENIED = "denied"
    RATE_LIMITED = "rate_limited"
    PARTNER_INAKTIV = "partner_inaktiv"

class ApiRateLimitStatus(BaseModel):
    partner_id: str
    requests_this_minute: int
    limit_rpm: int
    schema_version: int = 1

    @property
    def ist_rate_limited(self) -> bool:
        return self.requests_this_minute >= self.limit_rpm

class ApiPartnerManifest(BaseModel):
    partner_id: str
    name: str
    typ: ApiPartnerTyp
    tenant_id: str
    erlaubte_scopes: list[ApiScope]
    rate_limit_rpm: int = 60        # Requests per minute
    ip_whitelist: list[str] = []    # Leer = alle IPs erlaubt
    aktiv: bool = True
    schema_version: int = 1

    def hat_scope(self, scope: ApiScope) -> bool:
        return scope in self.erlaubte_scopes

    def ip_erlaubt(self, ip: str) -> bool:
        if not self.ip_whitelist:
            return True
        return ip in self.ip_whitelist

class ApiGatewayRegistry(BaseModel):
    partner: dict[str, ApiPartnerManifest] = {}
    request_counts: dict[str, int] = {}    # partner_id -> requests_this_minute
    schema_version: int = 1

    def add_partner(self, p: ApiPartnerManifest) -> ApiPartnerManifest:
        self.partner[p.partner_id] = p
        return p

    def get_partner(self, partner_id: str) -> Optional[ApiPartnerManifest]:
        return self.partner.get(partner_id)

    def pruefe_api_zugriff(
        self,
        partner_id: str,
        scope: ApiScope,
        tenant_id: str,
        client_ip: str = "",
    ) -> ApiAccessDecision:
        p = self.partner.get(partner_id)
        if p is None:
            return ApiAccessDecision.DENIED
        if not p.aktiv:
            return ApiAccessDecision.PARTNER_INAKTIV
        if p.tenant_id != tenant_id:
            return ApiAccessDecision.DENIED
        if not p.hat_scope(scope):
            return ApiAccessDecision.DENIED
        if client_ip and not p.ip_erlaubt(client_ip):
            return ApiAccessDecision.DENIED
        # Rate-Limit-Check
        count = self.request_counts.get(partner_id, 0)
        if count >= p.rate_limit_rpm:
            return ApiAccessDecision.RATE_LIMITED
        self.request_counts[partner_id] = count + 1
        return ApiAccessDecision.ALLOWED

    def reset_rate_limits(self) -> None:
        self.request_counts.clear()

    def partner_by_typ(self, typ: ApiPartnerTyp) -> list[ApiPartnerManifest]:
        return [p for p in self.partner.values() if p.typ == typ]
