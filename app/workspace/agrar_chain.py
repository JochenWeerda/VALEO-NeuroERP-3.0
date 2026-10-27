"""Schlankes Read-Model: Kontrakt → naechster Prozessschritt.

Kein Schreiben, keine Buchung, keine Modell-Vereinheitlichung.
KonContract (source_model=kon) und AgrarContract (source_model=agrar)
bleiben getrennte Eingaben mit eigenen Statusfeldern.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Literal, Mapping

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

SourceModel = Literal["kon", "agrar"]

logger = logging.getLogger(__name__)


class NextStep(str, Enum):
    """Naechster operativer Schritt im Referenzprozess (kein UI-Label)."""

    DISPOSITION = "disposition"
    WAAGE = "waage"
    QUALITAET = "qualitaet"
    ABRECHNUNG = "abrechnung"
    DONE = "done"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class ChainHint:
    """Ergebnis je Referenz — nur Lesen."""

    contract_ref: str
    source_model: SourceModel
    next_step: NextStep
    reason: str

    def as_dict(self) -> dict[str, str]:
        return {
            "contract_ref": self.contract_ref,
            "source_model": self.source_model,
            "next_step": self.next_step.value,
            "reason": self.reason,
        }


def _norm(value: str | None) -> str:
    return (value or "").strip().lower()


def _truthy_flag(value: object | None) -> bool:
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    text = str(value).strip().lower()
    return text not in {"", "0", "false", "nein", "no", "none", "null"}


# ---------------------------------------------------------------------------
# KonContract-Pfad (domain_ops.kon_contract + Abruf-Status)
# Statusquellen (Ist):
#   contract_status: OFFEN | ERLEDIGT | STORNIERT
#   disposition_status: OFFEN | FREIGEGEBEN | GELIEFERT | STORNIERT | fehlt
#   weighing_present / weighing_status: Register-Wiegeschein vorhanden?
#   quality_is_final: QualityProtocol.is_final
#   settlement_status: draft | posted | cancelled | fehlt
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class KonChainInput:
    contract_ref: str
    contract_status: str
    disposition_status: str | None = None
    weighing_present: bool = False
    weighing_status: str | None = None
    quality_is_final: bool = False
    settlement_status: str | None = None


def resolve_kon_next_step(inp: KonChainInput) -> ChainHint:
    """Deterministisch aus Kon-Statusfeldern — ohne AgrarContract zu lesen."""
    ref = inp.contract_ref
    cstat = _norm(inp.contract_status)
    dstat = _norm(inp.disposition_status)
    sstat = _norm(inp.settlement_status)
    wstat = _norm(inp.weighing_status)
    has_waage = inp.weighing_present or wstat in {
        "open",
        "allocated",
        "posted",
        "abgeschlossen",
        "closed",
    }

    if cstat == "storniert" or dstat == "storniert":
        return ChainHint(ref, "kon", NextStep.BLOCKED, "kontrakt_oder_abruf_storniert")

    if sstat == "posted" or cstat == "erledigt":
        return ChainHint(ref, "kon", NextStep.DONE, "kontrakt_erledigt_oder_settlement_posted")

    if sstat == "cancelled":
        return ChainHint(ref, "kon", NextStep.BLOCKED, "settlement_cancelled")

    if inp.quality_is_final:
        return ChainHint(ref, "kon", NextStep.ABRECHNUNG, "qualitaet_final_settlement_offen")

    if dstat == "geliefert" or has_waage:
        return ChainHint(ref, "kon", NextStep.QUALITAET, "abruf_geliefert_oder_wiegeschein_vorhanden")

    if dstat == "freigegeben":
        return ChainHint(ref, "kon", NextStep.WAAGE, "abruf_freigegeben_waage_fehlt")

    # OFFEN / kein Abruf / unbekannter Abruf-Status → Disposition (Abruf)
    if cstat in {"", "offen"} or dstat in {"", "offen"}:
        return ChainHint(ref, "kon", NextStep.DISPOSITION, "kontrakt_offen_abruf_fehlt_oder_offen")

    return ChainHint(ref, "kon", NextStep.DISPOSITION, "kon_status_unbekannt_fallback_disposition")


# ---------------------------------------------------------------------------
# AgrarContract-Pfad (domain_inventory.agrar_contracts + Annahme/QS/Settlement)
# Statusquellen (Ist):
#   contract_status: open | partially_allocated | fulfilled | cancelled | closed
#   weighing_status / allocation: unallocated | allocated | posted | fehlt
#   harvest_release_status: draft | provisional | final | …
#   quality_status / quality_is_final
#   settlement_status: draft | posted | cancelled
# Kein kon_disposition — Allokation laeuft ueber Wiegeschein.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AgrarChainInput:
    contract_ref: str
    contract_status: str
    weighing_status: str | None = None
    allocation_status: str | None = None
    harvest_release_status: str | None = None
    quality_status: str | None = None
    quality_is_final: bool = False
    settlement_status: str | None = None


def resolve_agrar_next_step(inp: AgrarChainInput) -> ChainHint:
    """Deterministisch aus Agrar-Statusfeldern — ohne KonContract zu lesen.

    Home-Projektion (nur ``contract_status`` aus ``GET /agrar/contracts``):
      open | partially_allocated → waage
      fulfilled → qualitaet  (Menge allokiert; ohne quality_is_final nie abrechnung)
      cancelled → blocked
    Unbekannter Status → blocked (kein stilles done).
    """
    ref = inp.contract_ref
    cstat = _norm(inp.contract_status)
    wstat = _norm(inp.weighing_status)
    astat = _norm(inp.allocation_status)
    hstat = _norm(inp.harvest_release_status)
    qstat = _norm(inp.quality_status)
    sstat = _norm(inp.settlement_status)

    if cstat in {"cancelled", "storniert"}:
        return ChainHint(ref, "agrar", NextStep.BLOCKED, "agrar_kontrakt_cancelled")

    if sstat == "posted" or cstat == "closed":
        return ChainHint(ref, "agrar", NextStep.DONE, "settlement_posted_oder_kontrakt_closed")

    if sstat == "cancelled":
        return ChainHint(ref, "agrar", NextStep.BLOCKED, "settlement_cancelled")

    if hstat in {"final", "credit_note_created", "paid"} or inp.quality_is_final or qstat == "approved":
        if sstat in {"", "draft"}:
            return ChainHint(ref, "agrar", NextStep.ABRECHNUNG, "annahme_oder_qs_fertig_settlement_offen")
        return ChainHint(ref, "agrar", NextStep.DONE, "abrechnung_bereits_jenseits_draft")

    if qstat == "rejected":
        return ChainHint(ref, "agrar", NextStep.BLOCKED, "qualitaet_rejected")

    has_ticket = wstat not in {"", "none"} or astat not in {"", "none"}
    ticket_ready = astat in {"allocated", "posted"} or wstat in {
        "posted",
        "abgeschlossen",
        "closed",
        "allocated",
    }
    acceptance_started = hstat in {"draft", "provisional"} or qstat in {
        "conditional",
        "in_pruefung",
        "pending",
    }

    # fulfilled = Restmenge 0 (Allokation fertig), analog ticket_ready → Qualitaet;
    # nicht done (das ist closed) und nicht abrechnung ohne quality_is_final.
    if cstat == "fulfilled":
        return ChainHint(ref, "agrar", NextStep.QUALITAET, "agrar_kontrakt_fulfilled_ohne_qs")

    if ticket_ready or acceptance_started:
        return ChainHint(ref, "agrar", NextStep.QUALITAET, "wiegeschein_allokiert_oder_annahme_offen")

    if has_ticket or cstat == "partially_allocated" or wstat == "open" or astat == "unallocated":
        return ChainHint(ref, "agrar", NextStep.WAAGE, "allokation_oder_wiegung_offen")

    if cstat in {"", "open"}:
        # Agrar-Pfad hat keinen Kon-Abruf; Einstieg ist Waage/Allokation.
        return ChainHint(ref, "agrar", NextStep.WAAGE, "agrar_kontrakt_open_einstieg_waage")

    return ChainHint(ref, "agrar", NextStep.BLOCKED, "agrar_status_unbekannt")


def resolve_next_step(
    *,
    contract_ref: str,
    source_model: SourceModel,
    fields: Mapping[str, object],
) -> ChainHint:
    """Einheitlicher Einstieg: source_model waehlt den Resolver, Felder bleiben getrennt."""
    if source_model == "kon":
        return resolve_kon_next_step(
            KonChainInput(
                contract_ref=contract_ref,
                contract_status=str(fields.get("contract_status") or ""),
                disposition_status=(
                    str(fields["disposition_status"])
                    if fields.get("disposition_status") is not None
                    else None
                ),
                weighing_present=_truthy_flag(fields.get("weighing_present")),
                weighing_status=(
                    str(fields["weighing_status"]) if fields.get("weighing_status") is not None else None
                ),
                quality_is_final=_truthy_flag(fields.get("quality_is_final")),
                settlement_status=(
                    str(fields["settlement_status"])
                    if fields.get("settlement_status") is not None
                    else None
                ),
            )
        )
    if source_model == "agrar":
        return resolve_agrar_next_step(
            AgrarChainInput(
                contract_ref=contract_ref,
                contract_status=str(fields.get("contract_status") or ""),
                weighing_status=(
                    str(fields["weighing_status"]) if fields.get("weighing_status") is not None else None
                ),
                allocation_status=(
                    str(fields["allocation_status"])
                    if fields.get("allocation_status") is not None
                    else None
                ),
                harvest_release_status=(
                    str(fields["harvest_release_status"])
                    if fields.get("harvest_release_status") is not None
                    else None
                ),
                quality_status=(
                    str(fields["quality_status"]) if fields.get("quality_status") is not None else None
                ),
                quality_is_final=_truthy_flag(fields.get("quality_is_final")),
                settlement_status=(
                    str(fields["settlement_status"])
                    if fields.get("settlement_status") is not None
                    else None
                ),
            )
        )
    raise ValueError(f"unknown source_model: {source_model!r}")


def read_agrar_quality_is_final(
    db: Session,
    *,
    tenant_id: str,
    agrar_contract_id: str,
) -> bool | None:
    """Letztes ``QualityProtocol.is_final`` fuer eine AgrarContract-ID + Mandant.

    Join: ``HarvestAcceptance.contract_id`` → ``agrar_contracts``,
    ``QualityProtocol.harvest_acceptance_id`` → Annahme.
    Kein KonContract. Rueckgabe ``None`` wenn kein Protokoll, sonst der Bool
    (kein Fake von True).
    """
    from sqlalchemy import desc

    from app.infrastructure.models import HarvestAcceptance, QualityProtocol

    contract_id = (agrar_contract_id or "").strip()
    tid = (tenant_id or "").strip()
    if not contract_id or not tid:
        return None

    row = (
        db.query(QualityProtocol.is_final)
        .join(
            HarvestAcceptance,
            QualityProtocol.harvest_acceptance_id == HarvestAcceptance.id,
        )
        .filter(
            HarvestAcceptance.contract_id == contract_id,
            HarvestAcceptance.tenant_id == tid,
            QualityProtocol.tenant_id == tid,
        )
        .order_by(desc(QualityProtocol.version), desc(QualityProtocol.created_at))
        .first()
    )
    if row is None:
        return None
    return bool(row[0])


def hint_with_qs_unknown(hint: ChainHint) -> ChainHint:
    """Nach fehlgeschlagenem QS-Read: next_step ohne QS belassen, reason markieren."""
    return ChainHint(
        contract_ref=hint.contract_ref,
        source_model=hint.source_model,
        next_step=hint.next_step,
        reason="qs_unbekannt",
    )
