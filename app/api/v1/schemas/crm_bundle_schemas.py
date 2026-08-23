"""Response-Schemas fuer das CRM-Buendel.

SPEC-P1-06 Welle 6: ersetzt ``response_model=dict[str, Any]`` in
``crm_lead_gen.py``, ``crm_ownership.py``, ``crm_gifts.py``, ``crm_kontakte.py``
und ``crm_contacts_ext.py`` (Marketingpraeferenzen).

Bei drei Endpunkten war die Deklaration nicht nur unscharf, sondern falsch:
sie fuehrten ``response_model=dict[str, Any]``, gaben aber eine **Liste**
zurueck. FastAPI validiert die Antwort gegen das Modell, das schlaegt bei einer
Liste immer fehl — die Endpunkte liefen in jedem Aufruf auf einen 500er:

  * ``GET /crm/kunden-kontakte/{kunden_nr}``
  * ``GET /crm/kim/customers/{kunden_nr}/gifts``
  * ``GET /crm/kim/contacts/{contact_id}/marketing-prefs``

Sie tragen jetzt ``list[...]``-Modelle.
"""

from __future__ import annotations

from typing import Optional

from pydantic import Field

from app.api.v1.schemas.base import BaseSchema


# ── Lead-Generierung ────────────────────────────────────────────────────────


class LeadKandidatOut(BaseSchema):
    """Kandidat aus GAP- oder LKV-Daten.

    Beide Quellen liefern dieselben fuenf Spalten; ``score_label`` benennt,
    was der ``score`` misst (Foerdersumme oder Milchleistung).
    """

    name: Optional[str] = None
    plz: Optional[str] = None
    ort: Optional[str] = None
    strasse: Optional[str] = None
    score: Optional[float] = None
    quelle: Optional[str] = Field(default=None, description="gap | lkv")
    score_label: Optional[str] = Field(
        default=None, description="Bedeutung des Scores, z. B. Foerdersumme EUR"
    )


class LeadPreviewOut(BaseSchema):
    """``GET /crm/lead-gen/preview``"""

    quelle: Optional[str] = None
    plz_min: Optional[str] = None
    plz_max: Optional[str] = None
    top_pct: Optional[float] = None
    anzahl: Optional[int] = None
    kandidaten: list[LeadKandidatOut] = Field(default_factory=list)


class LeadOut(BaseSchema):
    """Uebernommener CRM-Lead in der Frontend-Form.

    Die Liste liefert ``contact_person``, das Detail zusaetzlich die
    camelCase-Variante ``contactPerson`` sowie Notizen und Adresse — beide
    Formen sind hier vereinigt.
    """

    id: Optional[str] = None
    company: Optional[str] = None
    contact_person: Optional[str] = None
    contactPerson: Optional[str] = None  # noqa: N815 - Frontend-Form des Detailendpunkts
    email: Optional[str] = None
    phone: Optional[str] = None
    source: Optional[str] = None
    potential: Optional[float] = None
    priority: Optional[str] = None
    status: Optional[str] = Field(default=None, description="new | qualified | lost")
    notes: Optional[str] = None
    address: Optional[str] = None
    expectedCloseDate: Optional[str] = None  # noqa: N815 - Frontend-Form


class LeadListOut(BaseSchema):
    """``GET /crm/lead-gen/leads``"""

    data: list[LeadOut] = Field(default_factory=list)
    total: Optional[int] = None


class LeadCountOut(BaseSchema):
    """``GET /crm/lead-gen/leads-count``"""

    count: Optional[int] = None


class LeadUebernahmeOut(BaseSchema):
    """``POST /crm/lead-gen/uebernehmen``"""

    uebernommen: Optional[int] = None
    uebersprungen: Optional[int] = Field(
        default=None, description="Kandidaten, die schon als Lead existierten"
    )
    leads_gesamt: Optional[int] = None


class LeadConvertOut(BaseSchema):
    """``POST /crm/lead-gen/leads/{id}/convert``"""

    lead_id: Optional[str] = None
    kunden_nr: Optional[str] = None
    status: Optional[str] = None


# ── Ownership (Aussendienst-Zuordnung) ──────────────────────────────────────


class OwnershipKundeOut(BaseSchema):
    """Kunde in den Ownership-Worklisten."""

    kunden_nr: Optional[str] = None
    name1: Optional[str] = None
    plz: Optional[str] = None
    ort: Optional[str] = None
    dispatcher_disp: Optional[str] = Field(
        default=None, description="Nur in der Owner-Sicht gesetzt"
    )


class UnassignedOut(BaseSchema):
    """``GET /crm/kunden/ownership/unassigned``"""

    items: list[OwnershipKundeOut] = Field(default_factory=list)
    total: Optional[int] = None


class ByOwnerOut(BaseSchema):
    """``GET /crm/kunden/ownership/by-owner``"""

    sales_rep: Optional[str] = None
    items: list[OwnershipKundeOut] = Field(default_factory=list)
    total: Optional[int] = None


class OwnershipOut(BaseSchema):
    """``GET`` und ``PUT /crm/kunden/{kunden_nr}/ownership``.

    Das PUT ergaenzt ``ok`` und ``geaendert``.
    """

    kunden_nr: Optional[str] = None
    sales_rep: Optional[str] = None
    dispatcher: Optional[str] = None
    ok: Optional[bool] = None
    geaendert: list[str] = Field(
        default_factory=list, description="Tatsaechlich geaenderte Felder"
    )


class OwnershipHistoryEntryOut(BaseSchema):
    """Eintrag der Uebergabe-Historie."""

    feld: Optional[str] = None
    alt: Optional[str] = None
    neu: Optional[str] = None
    grund: Optional[str] = None
    bediener: Optional[str] = None
    created_at: Optional[str] = None


class OwnershipHistoryOut(BaseSchema):
    """``GET /crm/kunden/{kunden_nr}/ownership/history``"""

    items: list[OwnershipHistoryEntryOut] = Field(default_factory=list)


# ── Praesente ───────────────────────────────────────────────────────────────


class GiftOut(BaseSchema):
    """Zeile aus ``public.crm_gifts``."""

    id: Optional[str] = None
    tenant_id: Optional[str] = None
    kunden_nr: Optional[str] = None
    contact_id: Optional[str] = None
    year: Optional[int] = None
    gift_date: Optional[str] = None
    occasion: Optional[str] = None
    gift_name: Optional[str] = None
    quantity: Optional[float] = None
    sales_rep: Optional[str] = None
    operator: Optional[str] = None
    representative_officer: Optional[str] = None
    sequence_number: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# ── Kontakthistorie und Wiedervorlagen ──────────────────────────────────────


class KontaktOut(BaseSchema):
    """Zeile aus ``public.kunden_kontakte``.

    Die Wiedervorlagen-Sicht ergaenzt ``kunde`` (Kundenname) und
    ``ueberfaellig``.
    """

    id: Optional[str] = None
    kunden_nr: Optional[str] = None
    richtung: Optional[str] = Field(default=None, description="ein | aus")
    art: Optional[str] = Field(default=None, description="telefon, mail, besuch, …")
    kurzinfo: Optional[str] = None
    notiz: Optional[str] = None
    wiedervorlage: Optional[str] = None
    weiterleitung_an: Optional[str] = None
    bediener: Optional[str] = None
    verweis: Optional[str] = None
    erledigt: Optional[bool] = None
    created_at: Optional[str] = None
    kunde: Optional[str] = Field(default=None, description="Kundenname, nur in der Wiedervorlagen-Sicht")
    ueberfaellig: Optional[bool] = Field(
        default=None, description="Nur in der Wiedervorlagen-Sicht"
    )


class WiedervorlagenOut(BaseSchema):
    """``GET /crm/kunden-kontakte/wiedervorlagen``"""

    items: list[KontaktOut] = Field(default_factory=list)


# ── Marketingpraeferenzen ───────────────────────────────────────────────────


class MarketingPrefOut(BaseSchema):
    """Werbe-/Marketingpraeferenz eines Kontakts."""

    id: Optional[str] = None
    contact_id: Optional[str] = None
    kunden_nr: Optional[str] = None
    category_code: Optional[str] = None
    category_label: Optional[str] = None
    preference: Optional[str] = None
    updated_at: Optional[str] = None


class MarketingPrefSetOut(BaseSchema):
    """``PUT /crm/kim/contacts/{contact_id}/marketing-prefs``"""

    status: Optional[str] = None
    contact_id: Optional[str] = None
    category_code: Optional[str] = None
    preference: Optional[str] = None
