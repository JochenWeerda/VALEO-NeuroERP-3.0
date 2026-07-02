"""Helper functions for the Articles domain."""

from __future__ import annotations

from typing import Optional

from fastapi import HTTPException
from sqlalchemy import func, or_, text
from sqlalchemy.orm import Session

from app.infrastructure.models import Article as ArticleModel
from app.api.v1.schemas.inventory import Article


def resolve_article_tenant(payload_tenant_id: Optional[str], tenant_id: str) -> str:
    requested_tenant = (payload_tenant_id or "").strip()
    if requested_tenant and requested_tenant != tenant_id:
        raise HTTPException(status_code=403, detail="Article payload belongs to a different tenant")
    return tenant_id


def get_article_or_404(db: Session, article_id: str, tenant_id: str) -> ArticleModel:
    article = (
        db.query(ArticleModel)
        .filter(
            ArticleModel.id == article_id,
            ArticleModel.tenant_id == tenant_id,
            ArticleModel.is_active == True,  # noqa: E712
            ArticleModel.deleted_at.is_(None),
        )
        .first()
    )
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


def build_article_dq_datensatz(data: dict) -> dict[str, object]:
    return {
        "artikel_nr": data.get("article_number"),
        "bezeichnung": data.get("name"),
        "einheit": data.get("unit"),
        "mehrwertsteuersatz_pct": float(data["mehrwertsteuer_prozent"]) if data.get("mehrwertsteuer_prozent") is not None else None,
        "ean_code": data.get("ean_code") or data.get("barcode"),
    }


def fulltext_filter(query, search_term: str):
    """Apply PostgreSQL fulltext search with relevance ranking.

    For terms >= 2 chars, uses plainto_tsquery against the GIN-indexed
    search_vector column.  Falls back to ILIKE for very short terms
    where stemming adds no value.
    """
    if len(search_term) < 2:
        like = f"%{search_term}%"
        return query.filter(
            or_(
                ArticleModel.name.ilike(like),
                ArticleModel.article_number.ilike(like),
            )
        ), None

    ts_query = func.plainto_tsquery(text("'german'"), search_term)
    rank = func.ts_rank(ArticleModel.search_vector, ts_query)

    like = f"%{search_term}%"
    filtered = query.filter(
        or_(
            ArticleModel.search_vector.op("@@")(ts_query),
            ArticleModel.name.ilike(like),
            ArticleModel.article_number.ilike(like),
            ArticleModel.barcode.ilike(like),
        )
    )
    return filtered, rank


def to_article_schema(row: ArticleModel) -> Article:
    return Article.model_validate(
        {
            "id": str(row.id),
            "tenant_id": str(row.tenant_id),
            "article_number": row.article_number,
            "name": row.name,
            "description": row.description,
            "description2": getattr(row, "description2", None),
            "short_description": getattr(row, "short_description", None),
            "suchbegriff": row.suchbegriff,
            "matchcode2": getattr(row, "matchcode2", None),
            "hersteller": row.hersteller,
            "herkunftsland": row.herkunftsland,
            "naehrwertangaben": row.naehrwertangaben,
            "mhd_erforderlich": bool(row.mhd_erforderlich),
            "lagerartikel": bool(row.lagerartikel),
            "mehrwertsteuer_prozent": row.mehrwertsteuer_prozent,
            "warengruppe": row.warengruppe,
            "gefahrgutklasse": row.gefahrgutklasse,
            "gefahrgut_un_nummer": getattr(row, "gefahrgut_un_nummer", None),
            "gefahrgut_verpackungsgruppe": getattr(row, "gefahrgut_verpackungsgruppe", None),
            "gefahrgut_anhaenge": getattr(row, "gefahrgut_anhaenge", None),
            "lagerorte": row.lagerorte or [],
            "chargenpflicht": bool(row.chargenpflicht),
            "qs_pruefung_erforderlich": bool(row.qs_pruefung_erforderlich),
            "zolltarifnummer": row.zolltarifnummer,
            "bio_kennzeichnung": bool(row.bio_kennzeichnung),
            "gmp_plus_relevanz": bool(row.gmp_plus_relevanz),
            "kennzeichnung_bio": getattr(row, "kennzeichnung_bio", None),
            "kennzeichnung_vegan": getattr(row, "kennzeichnung_vegan", None),
            "kennzeichnung_vegetarisch": getattr(row, "kennzeichnung_vegetarisch", None),
            "kennzeichnung_allergene": getattr(row, "kennzeichnung_allergene", None),
            "kennzeichnung_herkunft": getattr(row, "kennzeichnung_herkunft", None),
            "lager_min_temperatur": getattr(row, "lager_min_temperatur", None),
            "lager_max_temperatur": getattr(row, "lager_max_temperatur", None),
            "lager_lagerdauer_tage": getattr(row, "lager_lagerdauer_tage", None),
            "lager_zentral": getattr(row, "lager_zentral", False),
            "lager_silo": getattr(row, "lager_silo", False),
            "analyse_protein": getattr(row, "analyse_protein", None),
            "analyse_feuchtigkeit": getattr(row, "analyse_feuchtigkeit", None),
            "analyse_schadex": getattr(row, "analyse_schadex", None),
            "analyse_fremdstoffe": getattr(row, "analyse_fremdstoffe", None),
            "analyse_sonstiges": getattr(row, "analyse_sonstiges", None),
            "ean_code": getattr(row, "ean_code", None),
            "alt_ean_code": getattr(row, "alt_ean_code", None),
            "lieferanten_artikelnummer": getattr(row, "lieferanten_artikelnummer", None),
            "kunden_artikelnummer": getattr(row, "kunden_artikelnummer", None),
            "verwendungszweck": getattr(row, "verwendungszweck", None),
            "nachhaltige_biomasse": getattr(row, "nachhaltige_biomasse", False),
            "pool_artikel": getattr(row, "pool_artikel", False),
            "rabatt_auftrag_rechnung": getattr(row, "rabatt_auftrag_rechnung", None),
            "rabatt_lose": getattr(row, "rabatt_lose", None),
            "rabatt_selbstabholer": getattr(row, "rabatt_selbstabholer", None),
            "zu_abschlag_1_code": getattr(row, "zu_abschlag_1_code", None),
            "zu_abschlag_1_prozent": getattr(row, "zu_abschlag_1_prozent", None),
            "zu_abschlag_2_code": getattr(row, "zu_abschlag_2_code", None),
            "zu_abschlag_2_prozent": getattr(row, "zu_abschlag_2_prozent", None),
            "berechne_zu_abschlag_auf_netto": getattr(row, "berechne_zu_abschlag_auf_netto", False),
            "einfuegen_summe_nach_zu_abschlag": getattr(row, "einfuegen_summe_nach_zu_abschlag", False),
            "skontofaehig": getattr(row, "skontofaehig", True),
            "warenrueckverguetung": getattr(row, "warenrueckverguetung", False),
            "bonus_faehig": getattr(row, "bonus_faehig", False),
            "rabattfaehig": getattr(row, "rabattfaehig", True),
            "lieferantennummer": row.lieferantennummer,
            "unit": row.unit,
            "category": row.category,
            "subcategory": row.subcategory,
            "barcode": row.barcode,
            "supplier_number": row.supplier_number,
            "customer_article_number": getattr(row, "customer_article_number", None),
            "purchase_price": row.purchase_price,
            "sales_price": row.sales_price,
            "currency": row.currency or "EUR",
            "min_stock": row.min_stock,
            "max_stock": row.max_stock,
            "weight": row.weight,
            "dimensions": row.dimensions,
            "einheit_typ": getattr(row, "einheit_typ", None),
            "einheit_faktor": getattr(row, "einheit_faktor", None),
            "einheit_preiseinheit": getattr(row, "einheit_preiseinheit", None),
            "gebinde_groesse": getattr(row, "gebinde_groesse", None),
            "gebinde_einheit": getattr(row, "gebinde_einheit", None),
            "current_stock": row.current_stock or 0,
            "reserved_stock": row.reserved_stock or 0,
            "available_stock": row.available_stock or 0,
            "is_active": row.is_active,
            "image_url": getattr(row, "image_url", None),
            "created_at": row.created_at,
            "updated_at": row.updated_at,
            "deleted_at": row.deleted_at,
        }
    )
