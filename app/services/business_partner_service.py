"""Service layer for BusinessPartner aggregate management."""

from __future__ import annotations

import logging
import re
from decimal import Decimal
from typing import Any, List, Optional, Tuple

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, OperationalError, ProgrammingError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, EntityNotFoundError, ValidationFailedError
from app.core.uuid7 import uuid7
from app.infrastructure.models import (
    BusinessPartner,
    BusinessPartnerAddress,
    BusinessPartnerBillingConfig,
    BusinessPartnerCommunity,
    BusinessPartnerCommunityMember,
    BusinessPartnerContact,
    BusinessPartnerCooperativeMembership,
    BusinessPartnerCpdAccount,
    BusinessPartnerDispatchMedium,
    BusinessPartnerDiscountItem,
    BusinessPartnerEmailDistribution,
    BusinessPartnerInstruction,
    BusinessPartnerInterfaceProfile,
    BusinessPartnerInterestSetting,
    BusinessPartnerPriceAgreement,
    BusinessPartnerPricingRule,
    BusinessPartnerProfile,
)
from app.repositories.business_partner_repository import BusinessPartnerRepository

logger = logging.getLogger(__name__)


def build_customer_match_lookup(db: Session) -> dict[tuple, dict]:
    """Kanonischer Cross-Source-Kundenlookup für die Stammdaten-Konsolidierung.

    Vereint die **Business-Partner-Identität** (``domain_crm.business_partners``,
    System of Record) mit dem **operativen ERP-Sitz** (``public.kunden``) zu
    ``{(tokenset(name), plz): {business_partner_id, partner_number, kunden_nr}}``.

    ``tokenset`` macht den Namensabgleich reihenfolge-unabhängig (GAP „Nachname
    Vorname" ↔ Stamm „Vorname Nachname"). Einziger Einstieg für GAP/Dairy/Geo-
    Matching — kein Roh-SQL auf Kundentabellen mehr in den Pipelines.
    """
    from app.services.gap_pipeline import tokenset

    lookup: dict[tuple, dict] = {}

    # 1) Business Partner = SoR-Identität (führend)
    try:
        bp_rows = db.execute(
            text(
                """
                SELECT partner_id, partner_number, name_1, postal_code
                FROM domain_crm.business_partners
                WHERE name_1 IS NOT NULL AND postal_code IS NOT NULL
                """
            )
        ).all()
    except Exception:  # noqa: BLE001 — BP-Tabelle evtl. nicht vorhanden (Teilumgebung)
        db.rollback()
        bp_rows = []
    for partner_id, partner_number, name, plz in bp_rows:
        key = (tokenset(name), str(plz).strip())
        entry = lookup.setdefault(key, {"business_partner_id": None, "partner_number": None, "kunden_nr": None})
        entry["business_partner_id"] = str(partner_id) if partner_id else entry["business_partner_id"]
        entry["partner_number"] = str(partner_number) if partner_number else entry["partner_number"]

    # 2) ERP-Kunden = operativer Sitz; ergänzt kunden_nr + Brücke.
    #    PLZ kommt bevorzugt aus dem Adress-Satelliten (kunden_adressen, haupt),
    #    Fallback auf die public.kunden-Altspalte (Übergang bis Backfill komplett).
    try:
        kunden_rows = db.execute(
            text(
                """
                SELECT k.kunden_nr, k.name1,
                       coalesce(a.plz, k.plz) AS plz,
                       k.business_partner_id
                FROM public.kunden k
                LEFT JOIN public.kunden_adressen a
                       ON a.kunden_nr = k.kunden_nr AND a.adress_typ = 'haupt'
                WHERE k.name1 IS NOT NULL AND coalesce(a.plz, k.plz) IS NOT NULL
                """
            )
        ).all()
    except Exception:  # noqa: BLE001 — kunden-Tabelle evtl. nicht vorhanden
        db.rollback()
        kunden_rows = []
    for kunden_nr, name, plz, bp_id in kunden_rows:
        key = (tokenset(name), str(plz).strip())
        entry = lookup.setdefault(key, {"business_partner_id": None, "partner_number": None, "kunden_nr": None})
        if entry.get("kunden_nr") is None:
            entry["kunden_nr"] = str(kunden_nr)
        if bp_id and not entry.get("business_partner_id"):
            entry["business_partner_id"] = str(bp_id)

    return lookup


def resolve_customer_ref(entry: dict) -> Optional[str]:
    """Stabiler Kunden-Handle aus einem Lookup-Eintrag (BP-Identität bevorzugt)."""
    if not entry:
        return None
    return entry.get("business_partner_id") or entry.get("partner_number") or entry.get("kunden_nr")


class BusinessPartnerService:
    """Facade over BusinessPartnerRepository with additional aggregate operations."""

    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id
        self.repo = BusinessPartnerRepository(db, tenant_id)

    # ── core CRUD ─────────────────────────────────────────────────────────────

    def list_partners(
        self,
        query: Optional[str] = None,
        is_customer: Optional[bool] = None,
        is_supplier: Optional[bool] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[BusinessPartner], int]:
        return self.repo.search(
            query=query,
            is_customer=is_customer,
            is_supplier=is_supplier,
            status=status,
            skip=skip,
            limit=limit,
        )

    def get_partner(self, partner_id: str) -> BusinessPartner:
        return self.repo.get_by_id(partner_id)

    # ── Cross-Domain-Auflösung (kanonisch; Stammdaten-Konsolidierung) ─────────

    def resolve_partner_sales_flags(self, crm_customer_id: str) -> Optional[dict]:
        """Löst einen CRM-Kunden (``domain_crm.customers.id``) auf BP-Sperr-/Lieferflags auf.

        Bridge: ``customers.business_partner_id`` → BP; Fallback über
        ``partner_number`` / ``debtor_account`` = Kundennummer. Kanonischer
        Einstieg für die Verkaufs-/Lieferfähigkeitsprüfung (statt Roh-SQL im
        Konsumenten). Returns ``None`` wenn der Kunde nicht existiert, sonst ein
        Dict (mit ``partner_id=None``, falls (noch) kein BP verknüpft ist).
        """
        row = self.db.execute(
            text(
                """
                SELECT c.customer_number, c.business_partner_id,
                       bp.partner_id AS bp_id, bp.status AS bp_status,
                       bp.blocked_for_delivery, bp.blocked_for_invoice
                FROM domain_crm.customers c
                LEFT JOIN domain_crm.business_partners bp
                  ON bp.partner_id = c.business_partner_id AND bp.tenant_id = c.tenant_id
                WHERE c.id = :cid AND c.tenant_id = :tid
                """
            ),
            {"cid": crm_customer_id, "tid": self.tenant_id},
        ).fetchone()
        if not row:
            return None
        pid, st = row.bp_id, row.bp_status
        bfd = bool(row.blocked_for_delivery) if row.blocked_for_delivery is not None else False
        bfi = bool(row.blocked_for_invoice) if row.blocked_for_invoice is not None else False
        cn = (row.customer_number or "").strip()
        if not pid and cn:
            r2 = self.db.execute(
                text(
                    """
                    SELECT partner_id, status, blocked_for_delivery, blocked_for_invoice
                    FROM domain_crm.business_partners
                    WHERE tenant_id = :tid AND (partner_number = :cn OR debtor_account = :cn)
                    LIMIT 1
                    """
                ),
                {"tid": self.tenant_id, "cn": cn},
            ).fetchone()
            if r2:
                pid, st = r2.partner_id, r2.status
                bfd, bfi = bool(r2.blocked_for_delivery), bool(r2.blocked_for_invoice)
        return {
            "partner_id": str(pid) if pid else None,
            "status": str(st or "active") if pid else None,
            "blocked_for_delivery": bfd if pid else False,
            "blocked_for_invoice": bfi if pid else False,
        }

    def get_customer_credit_limit(self, crm_customer_id: str) -> float:
        """Kreditlimit eines CRM-Kunden (Fallback-Feld am Kundensatz). 0.0 wenn keins."""
        row = self.db.execute(
            text("SELECT credit_limit FROM domain_crm.customers WHERE id = :cid AND tenant_id = :tid"),
            {"cid": crm_customer_id, "tid": self.tenant_id},
        ).mappings().first()
        return float(row["credit_limit"]) if row and row.get("credit_limit") else 0.0

    def list_active_customer_ids(self) -> list[str]:
        """IDs aller nicht gelöschten CRM-Kunden des Tenants."""
        rows = self.db.execute(
            text("SELECT id FROM domain_crm.customers WHERE tenant_id = :tid AND deleted_at IS NULL"),
            {"tid": self.tenant_id},
        ).mappings().all()
        return [str(r["id"]) for r in rows]

    def get_customer_discount(self, crm_customer_id: str) -> Optional[Decimal]:
        """Effektiver Kundenrabatt (discount_percent bevorzugt, sonst discount). None wenn keiner.

        Hinweis: ``domain_crm.customers`` führt aktuell keine Rabattspalten — fehlt die
        Spalte/Tabelle, wird sauber ``None`` geliefert (Fallback auf Basispreis) statt
        zu scheitern. Zielquelle künftig BP-Rabatt-Satelliten (BusinessPartnerDiscountItem
        /PriceAgreement).
        """
        try:
            row = self.db.execute(
                text("SELECT discount, discount_percent FROM domain_crm.customers WHERE id = :id AND tenant_id = :tid"),
                {"id": crm_customer_id, "tid": self.tenant_id},
            ).mappings().first()
        except (OperationalError, ProgrammingError):
            self.db.rollback()
            return None
        if not row:
            return None
        if row.get("discount_percent"):
            return Decimal(str(row["discount_percent"]))
        if row.get("discount"):
            return Decimal(str(row["discount"]))
        return None

    def get_customer_party(self, crm_customer_id: str) -> dict:
        """Rechnungs-Partyadresse (E-Rechnung) für einen CRM-Kunden.

        Bevorzugt die BusinessPartner-Stammadresse (SoR, via business_partner_id)
        und ergänzt aus dem CRM-Kundensatz. Robust: fehlende Felder/Tabellen →
        Fallback ``{"name": <id>}``, nie Exception. Behebt nebenbei das frühere
        Fehl-Mapping (name/street/country_code/vat_id existierten so nicht).
        """
        party: dict = {"name": crm_customer_id}
        try:
            cust = self.db.execute(
                text(
                    "SELECT company_name, postal_code, city, country, tax_id, email, business_partner_id "
                    "FROM domain_crm.customers WHERE id = :id AND tenant_id = :tid"
                ),
                {"id": crm_customer_id, "tid": self.tenant_id},
            ).mappings().first()
        except (OperationalError, ProgrammingError):
            self.db.rollback()
            return party
        if not cust:
            return party
        bp = None
        if cust.get("business_partner_id"):
            try:
                bp = self.db.execute(
                    text(
                        "SELECT name_1, street, house_number, postal_code, city, vat_id "
                        "FROM domain_crm.business_partners WHERE partner_id = :pid AND tenant_id = :tid"
                    ),
                    {"pid": cust["business_partner_id"], "tid": self.tenant_id},
                ).mappings().first()
            except (OperationalError, ProgrammingError):
                self.db.rollback()

        def pick(*vals: Any) -> str:
            for v in vals:
                if v:
                    return str(v)
            return ""

        street = ""
        if bp:
            street = " ".join(p for p in [bp.get("street"), bp.get("house_number")] if p).strip()
        return {
            "name": pick(bp.get("name_1") if bp else None, cust.get("company_name"), crm_customer_id),
            "street": street,
            "postal_code": pick(bp.get("postal_code") if bp else None, cust.get("postal_code")),
            "city": pick(bp.get("city") if bp else None, cust.get("city")),
            "country_code": pick(cust.get("country"), "DE"),
            "vat_id": pick(bp.get("vat_id") if bp else None, cust.get("tax_id")),
            "email": cust.get("email") or "",
        }

    def search_lookup(self, query: str = "", limit: int = 20) -> list[dict]:
        """Schnelle Kunden-Auswahl/Autocomplete aus der View ``kunden_lookup``.

        Lädt nur such-/listenrelevante Felder (kunden_nr, name, matchcode, plz, ort,
        aktiv, betreuer, sperrgrund); Detaildaten werden erst beim Öffnen über die
        Domänen-Methoden nachgeladen (Phase-2D-Trennung). Sucht über Matchcode-Präfix,
        Name/Kundennummer (enthält) und PLZ-Präfix.
        """
        q = (query or "").strip()
        if not q:
            rows = self.db.execute(
                text("SELECT * FROM public.kunden_lookup ORDER BY name LIMIT :lim"),
                {"lim": limit},
            ).mappings().all()
        else:
            mc = re.sub(r"[^a-z0-9]", "", q.lower())
            rows = self.db.execute(
                text(
                    "SELECT * FROM public.kunden_lookup "
                    "WHERE matchcode LIKE :mc OR kunden_nr ILIKE :term OR name ILIKE :term OR plz LIKE :plz "
                    "ORDER BY name LIMIT :lim"
                ),
                {"mc": f"{mc}%", "term": f"%{q}%", "plz": f"{q}%", "lim": limit},
            ).mappings().all()
        return [
            {**dict(r), "business_partner_id": str(r["business_partner_id"]) if r.get("business_partner_id") else None}
            for r in rows
        ]

    # ── Domänen-Detail aus Satelliten (Phase-2D-Trennung) ─────────────────────
    # Konsumenten lesen Adresse/Zahlung/Refs über diese Methoden statt direkt aus
    # public.kunden, damit dessen Altspalten später entfallen können. Jede Methode
    # bevorzugt den Satelliten und fällt während des Übergangs auf die
    # public.kunden-Altspalte zurück (solange Backfill nicht für alle Kunden gilt).

    def get_customer_address(self, kunden_nr: str, adress_typ: str = "haupt") -> dict:
        """Adresse eines Kunden — bevorzugt aus ``kunden_adressen``, Fallback ``public.kunden``."""
        addr_cols = "strasse, plz, ort, land, postfach, postfach_plz, postfach_ort"
        try:
            row = self.db.execute(
                text(
                    f"SELECT {addr_cols} FROM public.kunden_adressen "
                    "WHERE kunden_nr = :k AND adress_typ = :t "
                    "ORDER BY ist_standard DESC LIMIT 1"
                ),
                {"k": kunden_nr, "t": adress_typ},
            ).mappings().first()
        except (OperationalError, ProgrammingError):
            self.db.rollback()
            row = None
        if row:
            return dict(row)
        try:
            row = self.db.execute(
                text(f"SELECT {addr_cols} FROM public.kunden WHERE kunden_nr = :k"),
                {"k": kunden_nr},
            ).mappings().first()
        except (OperationalError, ProgrammingError):
            self.db.rollback()
            row = None
        if row:
            logger.warning(
                "kunden_adressen-Fallback auf public.kunden fuer %s - Adress-Satellit fehlt (deprecated)",
                kunden_nr,
            )
            return dict(row)
        return {}

    def get_customer_payment(self, kunden_nr: str) -> dict:
        """Zahl-/Abrechnungs-Flags — bevorzugt aus ``kunden_zahlung``, Fallback ``public.kunden``."""
        pay_cols = (
            "zahlungsbedingungen_tage, skonto, netto_kasse, mahnwesen, lastschriftverfahren, "
            "sepa_verfahren, mandat, kontonutzung_rechnung, kontoauszug_gewuenscht"
        )
        try:
            row = self.db.execute(
                text(f"SELECT {pay_cols} FROM public.kunden_zahlung WHERE kunden_nr = :k"),
                {"k": kunden_nr},
            ).mappings().first()
        except (OperationalError, ProgrammingError):
            self.db.rollback()
            row = None
        if row:
            return dict(row)
        try:
            row = self.db.execute(
                text(f"SELECT {pay_cols} FROM public.kunden WHERE kunden_nr = :k"),
                {"k": kunden_nr},
            ).mappings().first()
        except (OperationalError, ProgrammingError):
            self.db.rollback()
            row = None
        if row:
            logger.warning(
                "kunden_zahlung-Fallback auf public.kunden fuer %s - Zahlungs-Satellit fehlt (deprecated)",
                kunden_nr,
            )
            return dict(row)
        return {}

    def get_customer_external_refs(self, kunden_nr: str) -> dict[str, str]:
        """Fremdschlüssel/Altnummern als ``{ref_typ: ref_wert}`` aus ``kunden_external_refs``.

        Fallback auf die public.kunden-Altspalten (legacy/webshop/tankkarte/kundenkarte).
        """
        try:
            rows = self.db.execute(
                text("SELECT ref_typ, ref_wert FROM public.kunden_external_refs WHERE kunden_nr = :k"),
                {"k": kunden_nr},
            ).all()
            if rows:
                return {rt: rw for rt, rw in rows}
        except (OperationalError, ProgrammingError):
            self.db.rollback()
        try:
            row = self.db.execute(
                text(
                    "SELECT legacy_kunden_nr, webshop_kunden_nr, tankkarte_ean_code, kundenkarten_kennzeichen "
                    "FROM public.kunden WHERE kunden_nr = :k"
                ),
                {"k": kunden_nr},
            ).mappings().first()
        except (OperationalError, ProgrammingError):
            self.db.rollback()
            return {}
        if not row:
            return {}
        mapping = {
            "legacy_kunden_nr": row.get("legacy_kunden_nr"),
            "webshop_kunden_nr": row.get("webshop_kunden_nr"),
            "tankkarte_ean": row.get("tankkarte_ean_code"),
            "kundenkarte": row.get("kundenkarten_kennzeichen"),
        }
        result = {k: str(v) for k, v in mapping.items() if v}
        if result:
            logger.warning(
                "kunden_external_refs-Fallback auf public.kunden fuer %s - Ref-Satellit fehlt (deprecated)",
                kunden_nr,
            )
        return result

    def get_customer_detail(self, kunden_nr: str) -> dict:
        """On-demand-Detail eines Kunden aus den Domänensatelliten (Gegenstück zu ``search_lookup``).

        Aggregiert Adresse, Zahlung und External Refs; UI/Endpoints laden dies erst
        beim Öffnen eines Kunden (Listen-/Suchfelder kommen aus ``search_lookup``).
        """
        return {
            "kunden_nr": kunden_nr,
            "adresse": self.get_customer_address(kunden_nr),
            "zahlung": self.get_customer_payment(kunden_nr),
            "external_refs": self.get_customer_external_refs(kunden_nr),
        }

    # ── Identitaetsbruecke business_partner_id <-> kunden_nr (Schritt-5-Vorbereitung) ──
    # Kanonische Aufloesung zwischen den drei Kunden-Identitaeten: fachliche
    # kunden_nr (public.kunden, Satelliten), technische business_partner_id (SoR)
    # und CRM-Kundensatz (domain_crm.customers). Bruecke ist public.kunden.
    # business_partner_id (per kunden_merge gefuellt) + domain_crm.customers.

    def partner_id_for_kunden_nr(self, kunden_nr: str) -> Optional[str]:
        """business_partner_id zu einer kunden_nr (aus public.kunden.business_partner_id)."""
        try:
            bp = self.db.execute(
                text("SELECT business_partner_id FROM public.kunden WHERE kunden_nr = :k"),
                {"k": kunden_nr},
            ).scalar()
        except (OperationalError, ProgrammingError):
            self.db.rollback()
            return None
        return str(bp) if bp else None

    def kunden_nr_for_partner(self, business_partner_id: str) -> Optional[str]:
        """kunden_nr zu einer business_partner_id (Rueckrichtung ueber public.kunden)."""
        try:
            kn = self.db.execute(
                text(
                    "SELECT kunden_nr FROM public.kunden "
                    "WHERE business_partner_id = :bp AND coalesce(geloescht, FALSE) = FALSE "
                    "ORDER BY kunden_nr LIMIT 1"
                ),
                {"bp": business_partner_id},
            ).scalar()
        except (OperationalError, ProgrammingError):
            self.db.rollback()
            return None
        return str(kn) if kn else None

    def kunden_nr_for_crm_customer(self, crm_customer_id: str) -> Optional[str]:
        """kunden_nr zu einem CRM-Kunden: ueber dessen business_partner_id, sonst
        ueber den deterministischen Fallback customer_number == kunden_nr."""
        try:
            row = self.db.execute(
                text(
                    "SELECT business_partner_id, customer_number FROM domain_crm.customers "
                    "WHERE id = :id AND tenant_id = :tid"
                ),
                {"id": crm_customer_id, "tid": self.tenant_id},
            ).mappings().first()
        except (OperationalError, ProgrammingError):
            self.db.rollback()
            return None
        if not row:
            return None
        if row.get("business_partner_id"):
            kn = self.kunden_nr_for_partner(str(row["business_partner_id"]))
            if kn:
                return kn
        cn = row.get("customer_number")
        if cn:
            try:
                hit = self.db.execute(
                    text("SELECT 1 FROM public.kunden WHERE kunden_nr = :k"), {"k": cn}
                ).scalar()
            except (OperationalError, ProgrammingError):
                self.db.rollback()
                hit = None
            if hit:
                return str(cn)
        return None

    def resolve_customer_identity(
        self,
        *,
        kunden_nr: Optional[str] = None,
        business_partner_id: Optional[str] = None,
        crm_customer_id: Optional[str] = None,
    ) -> dict:
        """Vereinheitlicht die drei Kunden-Identitaeten zu einem Tripel.

        Erwartet genau einen Eingabeschluessel und loest die uebrigen auf, soweit
        die Bruecke reicht. Rueckgabe: {kunden_nr, business_partner_id,
        partner_number, crm_customer_id} (nicht aufloesbare Felder bleiben None).
        """
        kn = kunden_nr
        bp = business_partner_id
        if kn is None and bp is not None:
            kn = self.kunden_nr_for_partner(bp)
        if kn is None and crm_customer_id is not None:
            kn = self.kunden_nr_for_crm_customer(crm_customer_id)
        if bp is None and kn is not None:
            bp = self.partner_id_for_kunden_nr(kn)
        partner_number = None
        if bp:
            try:
                partner_number = self.db.execute(
                    text(
                        "SELECT partner_number FROM domain_crm.business_partners "
                        "WHERE partner_id = :p AND tenant_id = :t"
                    ),
                    {"p": bp, "t": self.tenant_id},
                ).scalar()
            except (OperationalError, ProgrammingError):
                self.db.rollback()
        return {
            "kunden_nr": kn,
            "business_partner_id": str(bp) if bp else None,
            "partner_number": str(partner_number) if partner_number else None,
            "crm_customer_id": crm_customer_id,
        }

    def list_customers_with_coordinates(self) -> list[dict]:
        """Kunden mit Geo-Koordinaten (für Umkreissuche). Graceful [] wenn Spalten fehlen."""
        try:
            rows = self.db.execute(
                text(
                    "SELECT kunden_nr, name, adresse, breitengrad, laengengrad FROM domain_crm.customers "
                    "WHERE tenant_id = :tid AND breitengrad IS NOT NULL AND laengengrad IS NOT NULL"
                ),
                {"tid": self.tenant_id},
            ).mappings().all()
            return [dict(r) for r in rows]
        except (OperationalError, ProgrammingError):
            self.db.rollback()
            return []

    def create_customer_record(
        self, customer_id: str, customer_number: str, name: str,
        email: Optional[str] = None, phone: Optional[str] = None,
    ) -> bool:
        """Legt einen Kundensatz mit korrektem Schema an (z.B. Interessenten-Konvertierung).

        Pflichtfelder id/customer_number/company_name/tenant_id werden gesetzt.
        Returns True bei Erfolg, False (graceful) bei Schema-/Integritätsfehler.
        Behebt das frühere Fehl-Mapping (kunden_nr/name/telefon/erstellt_am existieren nicht).
        """
        try:
            self.db.execute(
                text(
                    "INSERT INTO domain_crm.customers "
                    "(id, tenant_id, customer_number, company_name, email, phone, is_active, created_at, updated_at) "
                    "VALUES (:id, :tid, :cnum, :name, :email, :phone, TRUE, NOW(), NOW())"
                ),
                {"id": customer_id, "tid": self.tenant_id, "cnum": customer_number,
                 "name": name, "email": email, "phone": phone},
            )
            self.db.commit()
            return True
        except (OperationalError, ProgrammingError, IntegrityError):
            self.db.rollback()
            return False

    def ensure_partner_belongs_to_tenant(self, partner_id: str) -> None:
        """Validiert, dass der BusinessPartner im Mandanten existiert (sonst ValidationFailedError).

        Kanonische BP-Tenant-Prüfung — von CustomerService u.a. genutzt, damit die
        BP-Domänenlogik an EINER Stelle liegt.
        """
        ok = self.db.execute(
            text("SELECT 1 FROM domain_crm.business_partners WHERE partner_id = :pid AND tenant_id = :tid"),
            {"pid": partner_id, "tid": self.tenant_id},
        ).scalar()
        if not ok:
            raise ValidationFailedError("business_partner_id ungültig oder nicht im Mandanten gefunden.")

    def customer_exists(self, crm_customer_id: str) -> bool:
        """True, wenn der CRM-Kunde (domain_crm.customers.id) im Tenant existiert."""
        return self.db.execute(
            text("SELECT 1 FROM domain_crm.customers WHERE id = :id AND tenant_id = :tid"),
            {"id": crm_customer_id, "tid": self.tenant_id},
        ).first() is not None

    def find_customer_id_by_name(self, name: str) -> Optional[str]:
        """Findet die CRM-Kunden-ID per Firmenname (ILIKE, erster Treffer). None wenn keiner."""
        if not name or not name.strip():
            return None
        row = self.db.execute(
            text(
                "SELECT id FROM domain_crm.customers "
                "WHERE tenant_id = :tid AND company_name ILIKE :name LIMIT 1"
            ),
            {"tid": self.tenant_id, "name": f"%{name.strip()}%"},
        ).fetchone()
        return str(row[0]) if row else None

    def create_partner(self, payload: dict) -> BusinessPartner:
        existing = self.repo.get_by_partner_number(payload.get("partner_number", ""))
        if existing:
            raise ConflictError(f"partner_number '{payload['partner_number']}' already exists")
        partner_id = payload.pop("partner_id", None) or uuid7()
        partner = BusinessPartner(partner_id=partner_id, tenant_id=self.tenant_id, **payload)
        try:
            return self.repo.create(partner)
        except IntegrityError as exc:
            self.db.rollback()
            raise ConflictError("Business partner with this number already exists") from exc

    def update_partner(self, partner_id: str, data: dict) -> BusinessPartner:
        partner = self.repo.get_by_id(partner_id)
        return self.repo.update(partner, data)

    def delete_partner(self, partner_id: str) -> None:
        self.repo.delete(partner_id)

    # ── discount items ────────────────────────────────────────────────────────

    def list_discount_items(
        self, partner_id: str, article_number: Optional[str] = None
    ) -> List[BusinessPartnerDiscountItem]:
        self.repo.get_by_id(partner_id)  # ownership check
        q = self.db.query(BusinessPartnerDiscountItem).filter(
            BusinessPartnerDiscountItem.partner_id == partner_id,
            BusinessPartnerDiscountItem.tenant_id == self.tenant_id,
        )
        if article_number:
            q = q.filter(BusinessPartnerDiscountItem.article_number.ilike(f"%{article_number}%"))
        return q.order_by(
            BusinessPartnerDiscountItem.article_number.asc(),
            BusinessPartnerDiscountItem.created_at.desc(),
        ).all()

    def get_discount_item(self, item_id: str) -> BusinessPartnerDiscountItem:
        obj = self.db.query(BusinessPartnerDiscountItem).filter(
            BusinessPartnerDiscountItem.id == item_id,
            BusinessPartnerDiscountItem.tenant_id == self.tenant_id,
        ).first()
        if obj is None:
            raise EntityNotFoundError("BusinessPartnerDiscountItem", item_id)
        return obj

    def create_discount_item(self, partner_id: str, payload: dict) -> BusinessPartnerDiscountItem:
        self.repo.get_by_id(partner_id)
        item = BusinessPartnerDiscountItem(id=uuid7(), partner_id=partner_id, tenant_id=self.tenant_id, **payload)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def update_discount_item(self, item_id: str, data: dict) -> BusinessPartnerDiscountItem:
        item = self.get_discount_item(item_id)
        for k, v in data.items():
            setattr(item, k, v)
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete_discount_item(self, item_id: str) -> None:
        item = self.get_discount_item(item_id)
        self.db.delete(item)
        self.db.commit()

    # ── price agreements ──────────────────────────────────────────────────────

    def list_price_agreements(
        self, partner_id: str, article_number: Optional[str] = None
    ) -> List[BusinessPartnerPriceAgreement]:
        self.repo.get_by_id(partner_id)
        q = self.db.query(BusinessPartnerPriceAgreement).filter(
            BusinessPartnerPriceAgreement.partner_id == partner_id,
            BusinessPartnerPriceAgreement.tenant_id == self.tenant_id,
        )
        if article_number:
            q = q.filter(BusinessPartnerPriceAgreement.article_number.ilike(f"%{article_number}%"))
        return q.order_by(
            BusinessPartnerPriceAgreement.article_number.asc(),
            BusinessPartnerPriceAgreement.created_at.desc(),
        ).all()

    def get_price_agreement(self, agreement_id: str) -> BusinessPartnerPriceAgreement:
        obj = self.db.query(BusinessPartnerPriceAgreement).filter(
            BusinessPartnerPriceAgreement.id == agreement_id,
            BusinessPartnerPriceAgreement.tenant_id == self.tenant_id,
        ).first()
        if obj is None:
            raise EntityNotFoundError("BusinessPartnerPriceAgreement", agreement_id)
        return obj

    def create_price_agreement(self, partner_id: str, payload: dict) -> BusinessPartnerPriceAgreement:
        self.repo.get_by_id(partner_id)
        obj = BusinessPartnerPriceAgreement(id=uuid7(), partner_id=partner_id, tenant_id=self.tenant_id, **payload)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update_price_agreement(self, agreement_id: str, data: dict) -> BusinessPartnerPriceAgreement:
        obj = self.get_price_agreement(agreement_id)
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete_price_agreement(self, agreement_id: str) -> None:
        obj = self.get_price_agreement(agreement_id)
        self.db.delete(obj)
        self.db.commit()

    # ── instructions ──────────────────────────────────────────────────────────

    def list_instructions(self, partner_id: str) -> List[BusinessPartnerInstruction]:
        self.repo.get_by_id(partner_id)
        return (
            self.db.query(BusinessPartnerInstruction)
            .filter(
                BusinessPartnerInstruction.partner_id == partner_id,
                BusinessPartnerInstruction.tenant_id == self.tenant_id,
            )
            .all()
        )

    def get_instruction(self, instruction_id: str) -> BusinessPartnerInstruction:
        obj = self.db.query(BusinessPartnerInstruction).filter(
            BusinessPartnerInstruction.id == instruction_id,
            BusinessPartnerInstruction.tenant_id == self.tenant_id,
        ).first()
        if obj is None:
            raise EntityNotFoundError("BusinessPartnerInstruction", instruction_id)
        return obj

    def create_instruction(self, partner_id: str, payload: dict) -> BusinessPartnerInstruction:
        self.repo.get_by_id(partner_id)
        obj = BusinessPartnerInstruction(id=uuid7(), partner_id=partner_id, tenant_id=self.tenant_id, **payload)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update_instruction(self, instruction_id: str, data: dict) -> BusinessPartnerInstruction:
        obj = self.get_instruction(instruction_id)
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete_instruction(self, instruction_id: str) -> None:
        obj = self.get_instruction(instruction_id)
        self.db.delete(obj)
        self.db.commit()

    # ── contacts ──────────────────────────────────────────────────────────────

    def list_contacts(self, partner_id: str) -> List[BusinessPartnerContact]:
        self.repo.get_by_id(partner_id)
        return self.repo.list_contacts(partner_id)

    def get_contact(self, contact_id: str) -> BusinessPartnerContact:
        obj = self.db.query(BusinessPartnerContact).filter(
            BusinessPartnerContact.id == contact_id,
            BusinessPartnerContact.tenant_id == self.tenant_id,
        ).first()
        if obj is None:
            raise EntityNotFoundError("BusinessPartnerContact", contact_id)
        return obj

    def create_contact(self, partner_id: str, payload: dict) -> BusinessPartnerContact:
        self.repo.get_by_id(partner_id)
        obj = BusinessPartnerContact(id=uuid7(), partner_id=partner_id, tenant_id=self.tenant_id, **payload)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update_contact(self, contact_id: str, data: dict) -> BusinessPartnerContact:
        obj = self.get_contact(contact_id)
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete_contact(self, contact_id: str) -> None:
        obj = self.get_contact(contact_id)
        self.db.delete(obj)
        self.db.commit()

    # ── addresses ─────────────────────────────────────────────────────────────

    def list_addresses(
        self, partner_id: str, address_type: Optional[str] = None, skip: int = 0, limit: int = 50
    ) -> List[BusinessPartnerAddress]:
        self.repo.get_by_id(partner_id)
        q = self.db.query(BusinessPartnerAddress).filter(
            BusinessPartnerAddress.partner_id == partner_id,
            BusinessPartnerAddress.tenant_id == self.tenant_id,
        )
        if address_type:
            q = q.filter(BusinessPartnerAddress.address_type == address_type)
        return q.order_by(
            BusinessPartnerAddress.is_default.desc(),
            BusinessPartnerAddress.created_at.asc(),
        ).offset(skip).limit(limit).all()

    def get_address(self, address_id: str) -> BusinessPartnerAddress:
        obj = self.db.query(BusinessPartnerAddress).filter(
            BusinessPartnerAddress.id == address_id,
            BusinessPartnerAddress.tenant_id == self.tenant_id,
        ).first()
        if obj is None:
            raise EntityNotFoundError("BusinessPartnerAddress", address_id)
        return obj

    def create_address(self, partner_id: str, payload: dict) -> BusinessPartnerAddress:
        self.repo.get_by_id(partner_id)
        obj = BusinessPartnerAddress(id=uuid7(), partner_id=partner_id, tenant_id=self.tenant_id, **payload)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update_address(self, address_id: str, data: dict) -> BusinessPartnerAddress:
        obj = self.get_address(address_id)
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete_address(self, address_id: str) -> None:
        obj = self.get_address(address_id)
        self.db.delete(obj)
        self.db.commit()

    # ── billing config (singleton upsert) ─────────────────────────────────────

    def get_billing_config(self, partner_id: str) -> BusinessPartnerBillingConfig:
        self.repo.get_by_id(partner_id)
        obj = self.db.query(BusinessPartnerBillingConfig).filter(
            BusinessPartnerBillingConfig.partner_id == partner_id,
            BusinessPartnerBillingConfig.tenant_id == self.tenant_id,
        ).first()
        if obj is None:
            raise EntityNotFoundError("BusinessPartnerBillingConfig", partner_id)
        return obj

    def upsert_billing_config(self, partner_id: str, data: dict) -> BusinessPartnerBillingConfig:
        self.repo.get_by_id(partner_id)
        obj = self.db.query(BusinessPartnerBillingConfig).filter(
            BusinessPartnerBillingConfig.partner_id == partner_id,
            BusinessPartnerBillingConfig.tenant_id == self.tenant_id,
        ).first()
        is_new = obj is None
        if is_new:
            obj = BusinessPartnerBillingConfig(id=uuid7(), partner_id=partner_id, tenant_id=self.tenant_id)
            self.db.add(obj)
        for k, v in data.items():
            if k == "created_by" and not is_new:
                continue
            setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    # ── cpd accounts ──────────────────────────────────────────────────────────

    def list_cpd_accounts(self, partner_id: str, skip: int = 0, limit: int = 50) -> List[BusinessPartnerCpdAccount]:
        self.repo.get_by_id(partner_id)
        return (
            self.db.query(BusinessPartnerCpdAccount)
            .filter(
                BusinessPartnerCpdAccount.partner_id == partner_id,
                BusinessPartnerCpdAccount.tenant_id == self.tenant_id,
            )
            .order_by(BusinessPartnerCpdAccount.cpd_customer_number.asc())
            .offset(skip).limit(limit).all()
        )

    def get_cpd_account(self, account_id: str) -> BusinessPartnerCpdAccount:
        obj = self.db.query(BusinessPartnerCpdAccount).filter(
            BusinessPartnerCpdAccount.id == account_id,
            BusinessPartnerCpdAccount.tenant_id == self.tenant_id,
        ).first()
        if obj is None:
            raise EntityNotFoundError("BusinessPartnerCpdAccount", account_id)
        return obj

    def create_cpd_account(self, partner_id: str, data: dict) -> BusinessPartnerCpdAccount:
        self.repo.get_by_id(partner_id)
        obj = BusinessPartnerCpdAccount(id=uuid7(), partner_id=partner_id, tenant_id=self.tenant_id, **data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update_cpd_account(self, account_id: str, data: dict) -> BusinessPartnerCpdAccount:
        obj = self.get_cpd_account(account_id)
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete_cpd_account(self, account_id: str) -> None:
        obj = self.get_cpd_account(account_id)
        self.db.delete(obj)
        self.db.commit()

    # ── pricing rules ─────────────────────────────────────────────────────────

    def list_pricing_rules(self, partner_id: str, skip: int = 0, limit: int = 50) -> List[BusinessPartnerPricingRule]:
        self.repo.get_by_id(partner_id)
        return (
            self.db.query(BusinessPartnerPricingRule)
            .filter(
                BusinessPartnerPricingRule.partner_id == partner_id,
                BusinessPartnerPricingRule.tenant_id == self.tenant_id,
            )
            .order_by(BusinessPartnerPricingRule.created_at.desc())
            .offset(skip).limit(limit).all()
        )

    def get_pricing_rule(self, rule_id: str) -> BusinessPartnerPricingRule:
        obj = self.db.query(BusinessPartnerPricingRule).filter(
            BusinessPartnerPricingRule.id == rule_id,
            BusinessPartnerPricingRule.tenant_id == self.tenant_id,
        ).first()
        if obj is None:
            raise EntityNotFoundError("BusinessPartnerPricingRule", rule_id)
        return obj

    def create_pricing_rule(self, partner_id: str, data: dict) -> BusinessPartnerPricingRule:
        self.repo.get_by_id(partner_id)
        obj = BusinessPartnerPricingRule(id=uuid7(), partner_id=partner_id, tenant_id=self.tenant_id, **data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update_pricing_rule(self, rule_id: str, data: dict) -> BusinessPartnerPricingRule:
        obj = self.get_pricing_rule(rule_id)
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete_pricing_rule(self, rule_id: str) -> None:
        obj = self.get_pricing_rule(rule_id)
        self.db.delete(obj)
        self.db.commit()

    # ── interest settings ─────────────────────────────────────────────────────

    def list_interest_settings(self, partner_id: str, skip: int = 0, limit: int = 50) -> List[BusinessPartnerInterestSetting]:
        self.repo.get_by_id(partner_id)
        return (
            self.db.query(BusinessPartnerInterestSetting)
            .filter(
                BusinessPartnerInterestSetting.partner_id == partner_id,
                BusinessPartnerInterestSetting.tenant_id == self.tenant_id,
            )
            .order_by(BusinessPartnerInterestSetting.created_at.desc())
            .offset(skip).limit(limit).all()
        )

    def get_interest_setting(self, setting_id: str) -> BusinessPartnerInterestSetting:
        obj = self.db.query(BusinessPartnerInterestSetting).filter(
            BusinessPartnerInterestSetting.id == setting_id,
            BusinessPartnerInterestSetting.tenant_id == self.tenant_id,
        ).first()
        if obj is None:
            raise EntityNotFoundError("BusinessPartnerInterestSetting", setting_id)
        return obj

    def create_interest_setting(self, partner_id: str, data: dict) -> BusinessPartnerInterestSetting:
        self.repo.get_by_id(partner_id)
        obj = BusinessPartnerInterestSetting(id=uuid7(), partner_id=partner_id, tenant_id=self.tenant_id, **data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update_interest_setting(self, setting_id: str, data: dict) -> BusinessPartnerInterestSetting:
        obj = self.get_interest_setting(setting_id)
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete_interest_setting(self, setting_id: str) -> None:
        obj = self.get_interest_setting(setting_id)
        self.db.delete(obj)
        self.db.commit()

    # ── dispatch media ────────────────────────────────────────────────────────

    def list_dispatch_media(self, partner_id: str, skip: int = 0, limit: int = 50) -> List[BusinessPartnerDispatchMedium]:
        self.repo.get_by_id(partner_id)
        return (
            self.db.query(BusinessPartnerDispatchMedium)
            .filter(
                BusinessPartnerDispatchMedium.partner_id == partner_id,
                BusinessPartnerDispatchMedium.tenant_id == self.tenant_id,
            )
            .order_by(
                BusinessPartnerDispatchMedium.document_type.asc(),
                BusinessPartnerDispatchMedium.dispatch_channel.asc(),
            )
            .offset(skip).limit(limit).all()
        )

    def get_dispatch_medium(self, medium_id: str) -> BusinessPartnerDispatchMedium:
        obj = self.db.query(BusinessPartnerDispatchMedium).filter(
            BusinessPartnerDispatchMedium.id == medium_id,
            BusinessPartnerDispatchMedium.tenant_id == self.tenant_id,
        ).first()
        if obj is None:
            raise EntityNotFoundError("BusinessPartnerDispatchMedium", medium_id)
        return obj

    def create_dispatch_medium(self, partner_id: str, data: dict) -> BusinessPartnerDispatchMedium:
        self.repo.get_by_id(partner_id)
        obj = BusinessPartnerDispatchMedium(id=uuid7(), partner_id=partner_id, tenant_id=self.tenant_id, **data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update_dispatch_medium(self, medium_id: str, data: dict) -> BusinessPartnerDispatchMedium:
        obj = self.get_dispatch_medium(medium_id)
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete_dispatch_medium(self, medium_id: str) -> None:
        obj = self.get_dispatch_medium(medium_id)
        self.db.delete(obj)
        self.db.commit()

    # ── cooperative memberships ───────────────────────────────────────────────

    def list_cooperative_memberships(self, partner_id: str, skip: int = 0, limit: int = 50) -> List[BusinessPartnerCooperativeMembership]:
        self.repo.get_by_id(partner_id)
        return (
            self.db.query(BusinessPartnerCooperativeMembership)
            .filter(
                BusinessPartnerCooperativeMembership.partner_id == partner_id,
                BusinessPartnerCooperativeMembership.tenant_id == self.tenant_id,
            )
            .order_by(BusinessPartnerCooperativeMembership.created_at.desc())
            .offset(skip).limit(limit).all()
        )

    def get_cooperative_membership(self, membership_id: str) -> BusinessPartnerCooperativeMembership:
        obj = self.db.query(BusinessPartnerCooperativeMembership).filter(
            BusinessPartnerCooperativeMembership.id == membership_id,
            BusinessPartnerCooperativeMembership.tenant_id == self.tenant_id,
        ).first()
        if obj is None:
            raise EntityNotFoundError("BusinessPartnerCooperativeMembership", membership_id)
        return obj

    def create_cooperative_membership(self, partner_id: str, data: dict) -> BusinessPartnerCooperativeMembership:
        self.repo.get_by_id(partner_id)
        obj = BusinessPartnerCooperativeMembership(id=uuid7(), partner_id=partner_id, tenant_id=self.tenant_id, **data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def patch_cooperative_membership(self, membership_id: str, data: dict) -> BusinessPartnerCooperativeMembership:
        obj = self.get_cooperative_membership(membership_id)
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete_cooperative_membership(self, membership_id: str) -> None:
        obj = self.get_cooperative_membership(membership_id)
        self.db.delete(obj)
        self.db.commit()

    # ── email distributions ───────────────────────────────────────────────────

    def list_email_distributions(self, partner_id: str, skip: int = 0, limit: int = 50) -> List[BusinessPartnerEmailDistribution]:
        self.repo.get_by_id(partner_id)
        return (
            self.db.query(BusinessPartnerEmailDistribution)
            .filter(
                BusinessPartnerEmailDistribution.partner_id == partner_id,
                BusinessPartnerEmailDistribution.tenant_id == self.tenant_id,
            )
            .order_by(
                BusinessPartnerEmailDistribution.distribution_name.asc(),
                BusinessPartnerEmailDistribution.email.asc(),
            )
            .offset(skip).limit(limit).all()
        )

    def get_email_distribution(self, distribution_id: str) -> BusinessPartnerEmailDistribution:
        obj = self.db.query(BusinessPartnerEmailDistribution).filter(
            BusinessPartnerEmailDistribution.id == distribution_id,
            BusinessPartnerEmailDistribution.tenant_id == self.tenant_id,
        ).first()
        if obj is None:
            raise EntityNotFoundError("BusinessPartnerEmailDistribution", distribution_id)
        return obj

    def create_email_distribution(self, partner_id: str, data: dict) -> BusinessPartnerEmailDistribution:
        self.repo.get_by_id(partner_id)
        obj = BusinessPartnerEmailDistribution(id=uuid7(), partner_id=partner_id, tenant_id=self.tenant_id, **data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def patch_email_distribution(self, distribution_id: str, data: dict) -> BusinessPartnerEmailDistribution:
        obj = self.get_email_distribution(distribution_id)
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete_email_distribution(self, distribution_id: str) -> None:
        obj = self.get_email_distribution(distribution_id)
        self.db.delete(obj)
        self.db.commit()

    # ── profile (singleton upsert) ────────────────────────────────────────────

    def get_profile(self, partner_id: str) -> BusinessPartnerProfile:
        self.repo.get_by_id(partner_id)
        obj = self.db.query(BusinessPartnerProfile).filter(
            BusinessPartnerProfile.partner_id == partner_id,
            BusinessPartnerProfile.tenant_id == self.tenant_id,
        ).first()
        if obj is None:
            raise EntityNotFoundError("BusinessPartnerProfile", partner_id)
        return obj

    def upsert_profile(self, partner_id: str, data: dict) -> BusinessPartnerProfile:
        self.repo.get_by_id(partner_id)
        obj = self.db.query(BusinessPartnerProfile).filter(
            BusinessPartnerProfile.partner_id == partner_id,
            BusinessPartnerProfile.tenant_id == self.tenant_id,
        ).first()
        if obj is None:
            obj = BusinessPartnerProfile(id=uuid7(), partner_id=partner_id, tenant_id=self.tenant_id)
            self.db.add(obj)
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def patch_profile(self, partner_id: str, data: dict) -> BusinessPartnerProfile:
        obj = self.get_profile(partner_id)
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    # ── interface profile (singleton upsert) ──────────────────────────────────

    def get_interface_profile(self, partner_id: str) -> BusinessPartnerInterfaceProfile:
        self.repo.get_by_id(partner_id)
        obj = self.db.query(BusinessPartnerInterfaceProfile).filter(
            BusinessPartnerInterfaceProfile.partner_id == partner_id,
            BusinessPartnerInterfaceProfile.tenant_id == self.tenant_id,
        ).first()
        if obj is None:
            raise EntityNotFoundError("BusinessPartnerInterfaceProfile", partner_id)
        return obj

    def upsert_interface_profile(self, partner_id: str, data: dict) -> BusinessPartnerInterfaceProfile:
        self.repo.get_by_id(partner_id)
        obj = self.db.query(BusinessPartnerInterfaceProfile).filter(
            BusinessPartnerInterfaceProfile.partner_id == partner_id,
            BusinessPartnerInterfaceProfile.tenant_id == self.tenant_id,
        ).first()
        if obj is None:
            obj = BusinessPartnerInterfaceProfile(id=uuid7(), partner_id=partner_id, tenant_id=self.tenant_id)
            self.db.add(obj)
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def patch_interface_profile(self, partner_id: str, data: dict) -> BusinessPartnerInterfaceProfile:
        obj = self.get_interface_profile(partner_id)
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    # ── envelope create / update (with number-range assignment) ─────────────

    def assign_account_numbers(self, row: BusinessPartner) -> None:
        """Assign debtor/creditor account from number range if not set."""
        from app.services.number_range_service import NumberRangeService
        nrs = NumberRangeService(self.db)
        if row.is_customer and not row.debtor_account:
            try:
                row.debtor_account = nrs.next_number("debtor_account", self.tenant_id)
            except ValueError:
                pass
        if row.is_supplier and not row.creditor_account:
            try:
                row.creditor_account = nrs.next_number("creditor_account", self.tenant_id)
            except ValueError:
                pass

    def persist_new_partner(self, row: BusinessPartner) -> BusinessPartner:
        """Add, commit, and refresh a newly constructed BusinessPartner row."""
        self.db.add(row)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise ConflictError("Business partner with this number already exists") from exc
        self.db.refresh(row)
        return row

    def persist_updated_partner(self, row: BusinessPartner) -> BusinessPartner:
        """Commit and refresh an existing BusinessPartner row after field mutations."""
        self.db.commit()
        self.db.refresh(row)
        return row

    def check_partner_number_unique(self, partner_number: str, exclude_id: Optional[str] = None) -> None:
        existing = self.repo.get_by_partner_number(partner_number)
        if existing and existing.partner_id != exclude_id:
            raise ConflictError(f"partner_number '{partner_number}' already exists")

    # ── community catalog (tenant-agnostic) ───────────────────────────────────

    def list_communities(self) -> list:
        return self.db.query(BusinessPartnerCommunity).order_by(
            BusinessPartnerCommunity.description.asc()
        ).all()

    def create_community(self, data: dict) -> BusinessPartnerCommunity:
        row = BusinessPartnerCommunity(id=uuid7(), **data)
        self.db.add(row)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise ConflictError("Community code already exists") from exc
        self.db.refresh(row)
        return row

    def patch_community(self, community_id: str, data: dict) -> BusinessPartnerCommunity:
        row = self.db.query(BusinessPartnerCommunity).filter(
            BusinessPartnerCommunity.id == community_id
        ).first()
        if row is None:
            raise EntityNotFoundError("BusinessPartnerCommunity", community_id)
        for k, v in data.items():
            setattr(row, k, v)
        self.db.commit()
        self.db.refresh(row)
        return row

    def delete_community(self, community_id: str) -> None:
        row = self.db.query(BusinessPartnerCommunity).filter(
            BusinessPartnerCommunity.id == community_id
        ).first()
        if row is None:
            raise EntityNotFoundError("BusinessPartnerCommunity", community_id)
        self.db.delete(row)
        self.db.commit()

    def list_community_members(self, community_id: str) -> list:
        return self.db.query(BusinessPartnerCommunityMember).filter(
            BusinessPartnerCommunityMember.community_id == community_id
        ).order_by(BusinessPartnerCommunityMember.partner_id).all()

    def create_community_member(self, community_id: str, data: dict) -> BusinessPartnerCommunityMember:
        row = BusinessPartnerCommunityMember(id=uuid7(), community_id=community_id, **data)
        self.db.add(row)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise ConflictError("Member already in community") from exc
        self.db.refresh(row)
        return row

    def patch_community_member(self, member_id: str, data: dict) -> BusinessPartnerCommunityMember:
        row = self.db.query(BusinessPartnerCommunityMember).filter(
            BusinessPartnerCommunityMember.id == member_id
        ).first()
        if row is None:
            raise EntityNotFoundError("BusinessPartnerCommunityMember", member_id)
        for k, v in data.items():
            setattr(row, k, v)
        self.db.commit()
        self.db.refresh(row)
        return row

    def delete_community_member(self, member_id: str) -> None:
        row = self.db.query(BusinessPartnerCommunityMember).filter(
            BusinessPartnerCommunityMember.id == member_id
        ).first()
        if row is None:
            raise EntityNotFoundError("BusinessPartnerCommunityMember", member_id)
        self.db.delete(row)
        self.db.commit()
