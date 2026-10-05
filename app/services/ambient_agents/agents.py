"""Die 4 deterministischen v1-Agenten (UIX-092).

Jeder Agent ist eine reine Regel ueber vorgeladene Read-Model-Zeilen → erklaerte
WorklistProposals. Keine DB-Zugriffe hier (die watch()-Wrapper laden die Zeilen);
so sind die Regeln isoliert testbar. confidence immer 1.0 (deterministisch).
"""
from __future__ import annotations

from typing import Any

from .base import WorklistProposal

# Toleranz Rechnungs- vs. Bestellpreis (config-ueberschreibbar).
DEFAULT_PREIS_TOLERANZ = 0.02
KONTRAKT_MIN_ANDIENUNG_PCT = 80.0
KONTRAKT_FRIST_TAGE = 21
OP_UEBERFAELLIG_TAGE = 30
OP_MAHNUNG_TAGE = 14
QS_FRIST_TAGE = 30


def _p(agent_id: str, tenant_id: str, obj_type: str, obj_id: str, **kw: Any) -> WorklistProposal:
    return WorklistProposal(
        agent_id=agent_id,
        tenant_id=tenant_id,
        dedupe_key=f"{agent_id}:{obj_id}",
        source_ref=f"{obj_type}:{obj_id}",
        confidence=1.0,
        **kw,
    )


class KontraktUntererfuellungAgent:
    agent_id = "kontrakt_untererfuellung"
    schedule = "nightly"

    def evaluate(self, rows: list[dict[str, Any]], tenant_id: str) -> list[WorklistProposal]:
        out: list[WorklistProposal] = []
        for r in rows:
            pct = r.get("angedient_pct")
            frist = r.get("andienung_frist_days")
            if pct is None or frist is None:
                continue
            if pct < KONTRAKT_MIN_ANDIENUNG_PCT and frist < KONTRAKT_FRIST_TAGE:
                cid = str(r["contract_id"])
                out.append(_p(
                    self.agent_id, tenant_id, "contract", cid,
                    title=f"Kontrakt {r.get('kontrakt_nr', cid)} untererfuellt",
                    reason=f"Erst {pct:.0f}% angedient bei Andienungsfrist in {frist} Tagen (< {KONTRAKT_MIN_ANDIENUNG_PCT:.0f}% und < {KONTRAKT_FRIST_TAGE} Tage).",
                    severity="warning",
                    target_screen_id="agrar/kontrakte",
                    target_route=f"/kontrakte/{cid}",
                    payload={"angedient_pct": pct, "andienung_frist_days": frist},
                ))
        return out


class PreisabweichungEinkaufAgent:
    agent_id = "preisabweichung_einkauf"
    schedule = "nightly"

    def __init__(self, toleranz: float = DEFAULT_PREIS_TOLERANZ) -> None:
        self.toleranz = toleranz

    def evaluate(self, rows: list[dict[str, Any]], tenant_id: str) -> list[WorklistProposal]:
        out: list[WorklistProposal] = []
        for r in rows:
            rp, bp = r.get("rechnungspreis"), r.get("bestellpreis")
            if rp is None or bp is None or bp <= 0:
                continue
            grenze = bp * (1 + self.toleranz)
            if rp > grenze:
                iid = str(r["invoice_id"])
                abw = (rp / bp - 1) * 100
                out.append(_p(
                    self.agent_id, tenant_id, "ap_invoice", iid,
                    title=f"Preisabweichung Rechnung {r.get('rechnung_nr', iid)}",
                    reason=f"Rechnungspreis {rp} > Bestellpreis {bp} + {self.toleranz * 100:.0f}% Toleranz (Abweichung {abw:.1f}%).",
                    severity="warning",
                    target_screen_id="finance/ap-invoice",
                    target_route=f"/finance/ap-invoice/{iid}",
                    payload={"rechnungspreis": rp, "bestellpreis": bp, "abweichung_pct": round(abw, 1)},
                ))
        return out


class OpEskalationAgent:
    agent_id = "op_eskalation"
    schedule = "nightly"

    def evaluate(self, rows: list[dict[str, Any]], tenant_id: str) -> list[WorklistProposal]:
        out: list[WorklistProposal] = []
        for r in rows:
            overdue = r.get("overdue_days")
            if overdue is None:
                continue
            since_mahnung = r.get("days_since_mahnung")  # None = nie gemahnt
            if overdue > OP_UEBERFAELLIG_TAGE and (since_mahnung is None or since_mahnung > OP_MAHNUNG_TAGE):
                oid = str(r["op_id"])
                mahn = "nie gemahnt" if since_mahnung is None else f"letzte Mahnung vor {since_mahnung} Tagen"
                out.append(_p(
                    self.agent_id, tenant_id, "open_item", oid,
                    title=f"OP {r.get('beleg_nr', oid)} eskaliert",
                    reason=f"Ueberfaellig seit {overdue} Tagen (> {OP_UEBERFAELLIG_TAGE}) und {mahn} (> {OP_MAHNUNG_TAGE} Tage).",
                    severity="critical",
                    target_screen_id="finance/ar-open-item",
                    target_route=f"/finance/ar-open-item/{oid}",
                    payload={"overdue_days": overdue, "days_since_mahnung": since_mahnung},
                ))
        return out


class QsFristenAgent:
    agent_id = "qs_fristen"
    schedule = "nightly"

    def evaluate(self, rows: list[dict[str, Any]], tenant_id: str) -> list[WorklistProposal]:
        out: list[WorklistProposal] = []
        for r in rows:
            days = r.get("expires_in_days")
            if days is None or days >= QS_FRIST_TAGE:
                continue
            cid = str(r["cert_id"])
            out.append(_p(
                self.agent_id, tenant_id, "certificate", cid,
                title=f"Zertifikat {r.get('bezeichnung', cid)} laeuft ab",
                reason=f"Laeuft in {days} Tagen ab (< {QS_FRIST_TAGE}).",
                severity="warning",
                target_screen_id="qualitaet/zertifikate",
                target_route=f"/zertifikate/{cid}",
                payload={"expires_in_days": days, "kind": r.get("kind")},
            ))
        return out
