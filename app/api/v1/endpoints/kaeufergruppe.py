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
from app.services.kaeufergruppe import GRUPPEN, BuyingGroup, Verhaltenssignale, klassifiziere, profil

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


@router.get("/katalog", summary="Käufergruppen-Katalog (Label/Zielanteil/Ansatz)")
def katalog() -> list[dict[str, Any]]:
    return [
        {"group": g.value, "label": p.label, "ziel_anteil_min": p.ziel_anteil_min,
         "ziel_anteil_max": p.ziel_anteil_max, "abschluss_faktor": p.abschluss_faktor,
         "grenzaufwand": p.grenzaufwand, "ansatz": p.ansatz}
        for g, p in GRUPPEN.items()
    ]


@router.get("/{kunden_nr}", summary="Käufergruppen-Profil eines Betriebs")
def get_profil(kunden_nr: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> dict[str, Any]:
    r = db.execute(
        text("SELECT * FROM public.kunden_kaeufer_profil WHERE kunden_nr = :k AND tenant_id = :t"),
        {"k": kunden_nr, "t": tenant_id},
    ).mappings().first()
    if not r:
        raise HTTPException(status_code=404, detail="Kein Käufergruppen-Profil")
    return _row(r)


@router.post("/{kunden_nr}/neu-klassifizieren", summary="Regelbasiert neu klassifizieren (aus aktuellen Signalen)")
def neu_klassifizieren(kunden_nr: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> dict[str, Any]:
    r = db.execute(
        text("SELECT * FROM public.kunden_kaeufer_profil WHERE kunden_nr = :k AND tenant_id = :t"),
        {"k": kunden_nr, "t": tenant_id},
    ).mappings().first()
    if not r:
        raise HTTPException(status_code=404, detail="Kein Käufergruppen-Profil")
    sig = Verhaltenssignale(
        angebote_12m=int(r["offer_count_12m"] or 0),
        preisabfragen_12m=int(r["price_request_count_12m"] or 0),
        abschlussquote=float(r["offer_win_rate_12m"] or 0),
        rabatt_schnitt=float(r["average_discount_rate"] or 0),
        kauffrequenz_12m=int(r["purchase_frequency_12m"] or 0),
        multi_lieferant_wahrsch=float(r["multi_supplier_prob"] or 0.5),
        saison_konzentration=float(r["season_concentration"] or 0),
    )
    kl = klassifiziere(sig)
    _set_group(db, tenant_id, kunden_nr, r["buying_group"], kl.gruppe.value, "rule_based",
               kl.confidence, kl.begruendung, None, "automatische Neuklassifikation")
    db.commit()
    return get_profil(kunden_nr, db, tenant_id)


@router.post("/{kunden_nr}/setzen", summary="Käufergruppe bestätigen/überschreiben (mit Audit)")
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
