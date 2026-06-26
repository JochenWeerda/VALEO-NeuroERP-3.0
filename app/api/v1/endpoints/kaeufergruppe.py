"""Käufergruppen-Klassifikation — lesen, vorschlagen, bestätigen, überschreiben.

Erklärbar (Begründung + Signale), durch den Vertrieb korrigierbar, mit Audit-Log.
"""

from __future__ import annotations

import uuid
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.kaeufergruppe import GRUPPEN, BuyingGroup, profil
from app.services.kaeufer_klassifikator import klassifiziere_mit
from app.services.kaeufer_signal_service import KaeuferSignalService
from app.services.bedarfsdeckung_service import BedarfsdeckungService

router = APIRouter(prefix="/crm/kaeufergruppe", tags=["crm", "kaeufergruppe"])


class SetGroupIn(BaseModel):
    group: str
    source: str = "manual"        # manual | ai_confirmed
    bediener: Optional[str] = None
    kommentar: Optional[str] = None


def _row(r) -> dict:
    d = dict(r)
    for k in ("buying_group_confidence", "target_share_override", "offer_win_rate_12m",
              "average_discount_rate", "multi_supplier_prob", "season_concentration",
              "loyalty_score", "churn_risk_score"):
        if d.get(k) is not None:
            d[k] = float(d[k])
    p = profil(d.get("buying_group", "unbekannt"))
    d["label"] = p.label
    d["ansatz"] = p.ansatz
    d["ziel_anteil_korridor"] = [p.ziel_anteil_min, p.ziel_anteil_max]
    return d


@router.get("/katalog", response_model=list[dict[str, Any]], summary="Käufergruppen-Katalog (Label/Zielanteil/Ansatz)")
def katalog() -> list[dict[str, Any]]:
    return [
        {"group": g.value, "label": p.label, "ziel_anteil_min": p.ziel_anteil_min,
         "ziel_anteil_max": p.ziel_anteil_max, "abschluss_faktor": p.abschluss_faktor,
         "grenzaufwand": p.grenzaufwand, "ansatz": p.ansatz}
        for g, p in GRUPPEN.items()
    ]


@router.get("/{kunden_nr}", response_model=dict[str, Any], summary="Käufergruppen-Profil eines Betriebs")
def get_profil(kunden_nr: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> dict[str, Any]:
    r = db.execute(
        text("SELECT * FROM public.kunden_kaeufer_profil WHERE kunden_nr = :k AND tenant_id = :t"),
        {"k": kunden_nr, "t": tenant_id},
    ).mappings().first()
    if not r:
        raise HTTPException(status_code=404, detail="Kein Käufergruppen-Profil")
    return _row(r)


def _reklassifiziere(db: Session, tenant_id: str, kunden_nr: str, prefer_ai: bool) -> dict[str, Any]:
    """Baut echte Signale (aus Belegen/Kontakten/Bezug), klassifiziert (KI oder
    regelbasiert mit Fallback) und speichert mit Audit. Deckung/Bedarf kommen aus
    dem Bedarfsdeckungs-Cockpit (autoritativ)."""
    alt = db.execute(
        text("SELECT buying_group FROM public.kunden_kaeufer_profil WHERE kunden_nr = :k AND tenant_id = :t"),
        {"k": kunden_nr, "t": tenant_id},
    ).scalar()
    cp = BedarfsdeckungService(db, tenant_id).cockpit(kunden_nr)
    if not cp:
        raise HTTPException(status_code=404, detail="Kein Bedarfsprofil für diesen Betrieb")
    sig, signal_source = KaeuferSignalService(db, tenant_id).aggregiere(
        kunden_nr, float(cp["deckung_pct_gesamt"]), float(cp["bedarf_jahr_eur_gesamt"])
    )
    kl, source = klassifiziere_mit(sig, prefer_ai=prefer_ai)
    db.execute(
        text("UPDATE public.kunden_kaeufer_profil SET signal_source = :s, "
             "price_request_count_12m = :pa, offer_count_12m = :ang, offer_win_rate_12m = :win, "
             "purchase_frequency_12m = :freq, multi_supplier_prob = :multi, updated_at = now() "
             "WHERE kunden_nr = :k AND tenant_id = :t"),
        {"s": signal_source, "pa": sig.preisabfragen_12m, "ang": sig.angebote_12m,
         "win": sig.abschlussquote, "freq": sig.kauffrequenz_12m, "multi": sig.multi_lieferant_wahrsch,
         "k": kunden_nr, "t": tenant_id},
    )
    _set_group(db, tenant_id, kunden_nr, alt, kl.gruppe.value, source,
               kl.confidence, kl.begruendung, None, f"Neuklassifikation ({source}, Signale: {signal_source})")
    db.commit()
    return get_profil(kunden_nr, db, tenant_id)


@router.post("/{kunden_nr}/neu-klassifizieren", response_model=dict[str, Any], summary="Regelbasiert neu klassifizieren (aus echten Belegsignalen)")
def neu_klassifizieren(kunden_nr: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> dict[str, Any]:
    return _reklassifiziere(db, tenant_id, kunden_nr, prefer_ai=False)


@router.post("/{kunden_nr}/ki-klassifizieren", response_model=dict[str, Any], summary="KI-gestützt einschätzen (Claude, Fallback regelbasiert)")
def ki_klassifizieren(kunden_nr: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> dict[str, Any]:
    return _reklassifiziere(db, tenant_id, kunden_nr, prefer_ai=True)


@router.post("/{kunden_nr}/produktgruppen-klassifizieren", response_model=dict[str, Any], summary="Käufergruppe je Produktgruppe ableiten")
def produktgruppen_klassifizieren(kunden_nr: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> dict[str, Any]:
    """Leitet je Produktgruppe eine eigene Käufergruppe aus deren Deckung/Bezug ab
    (ein Betrieb kann je Gruppe unterschiedlich ticken)."""
    cp = BedarfsdeckungService(db, tenant_id).cockpit(kunden_nr)
    if not cp:
        raise HTTPException(status_code=404, detail="Kein Bedarfsprofil für diesen Betrieb")
    svc = KaeuferSignalService(db, tenant_id)
    n = 0
    for g in cp.get("produktgruppen", []):
        sig = svc.aggregiere_gruppe(
            kunden_nr, float(g["deckung_pct"]), float(g["bedarf_jahr_eur"]), bool(g["ist_12m_eur"] > 0)
        )
        kl, source = klassifiziere_mit(sig, prefer_ai=False)
        db.execute(
            text("UPDATE public.kunden_produktgruppen_bezug SET buying_group = :g, buying_group_reason = :r, "
                 "buying_group_source = :s, buying_group_confidence = :c, updated_at = now() "
                 "WHERE kunden_nr = :k AND produktgruppe = :pg AND tenant_id = :t"),
            {"g": kl.gruppe.value, "r": kl.begruendung, "s": source, "c": kl.confidence,
             "k": kunden_nr, "pg": g["key"], "t": tenant_id},
        )
        n += 1
    db.commit()
    return {"kunden_nr": kunden_nr, "klassifiziert": n}


@router.post("/{kunden_nr}/setzen", response_model=dict[str, Any], summary="Käufergruppe bestätigen/überschreiben (mit Audit)")
def setzen(kunden_nr: str, body: SetGroupIn, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> dict[str, Any]:
    if body.group not in {g.value for g in BuyingGroup}:
        raise HTTPException(status_code=422, detail="Unbekannte Käufergruppe")
    r = db.execute(
        text("SELECT buying_group FROM public.kunden_kaeufer_profil WHERE kunden_nr = :k AND tenant_id = :t"),
        {"k": kunden_nr, "t": tenant_id},
    ).mappings().first()
    alt = r["buying_group"] if r else None
    conf = 1.0 if body.source in ("manual", "ai_confirmed") else 0.6
    _set_group(db, tenant_id, kunden_nr, alt, body.group, body.source, conf,
               body.kommentar, body.bediener, body.kommentar)
    db.commit()
    return get_profil(kunden_nr, db, tenant_id)


def _set_group(db, tenant_id, kunden_nr, alt, neu, source, conf, reason, bediener, kommentar) -> None:
    db.execute(
        text(
            """
            INSERT INTO public.kunden_kaeufer_profil (kunden_nr, buying_group, buying_group_confidence,
                buying_group_reason, buying_group_source, buying_group_updated_at, tenant_id)
            VALUES (:k, :g, :conf, :reason, :src, now(), :t)
            ON CONFLICT (kunden_nr) DO UPDATE SET buying_group = EXCLUDED.buying_group,
                buying_group_confidence = EXCLUDED.buying_group_confidence,
                buying_group_reason = COALESCE(EXCLUDED.buying_group_reason, kunden_kaeufer_profil.buying_group_reason),
                buying_group_source = EXCLUDED.buying_group_source, buying_group_updated_at = now(), updated_at = now()
            """
        ),
        {"k": kunden_nr, "g": neu, "conf": conf, "reason": reason, "src": source, "t": tenant_id},
    )
    db.execute(
        text(
            "INSERT INTO public.kunden_kaeufer_audit (id, kunden_nr, alt_group, neu_group, source, bediener, kommentar, tenant_id) "
            "VALUES (:id, :k, :alt, :neu, :src, :bed, :kom, :t)"
        ),
        {"id": str(uuid.uuid4()), "k": kunden_nr, "alt": alt, "neu": neu, "src": source,
         "bed": bediener, "kom": kommentar, "t": tenant_id},
    )
