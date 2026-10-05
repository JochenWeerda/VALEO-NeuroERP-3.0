"""Produktion→Charge-Durchstich Mischfutter (FEED-CHAIN-001) — durchgängig.

Schließt den Belegbruch zwischen Produktionsauftrag und Chargen-/QS-Welt:

- ``compute_verbrauch``: reiner Verbrauchs-Snapshot (Komponentenmengen) für eine
  Produktionsmenge — wird bei Freigabe persistiert (``auftrag.verbrauch``) und ist
  die Grundlage für Mischprotokoll und exakte Bestandsrückgabe beim Storno.
- ``complete_to_charge``: erzeugt bei Status ``fertig`` idempotent die
  Fertigwaren-Charge in ``domain_ops.ops_chargen`` (Mischprotokoll in
  ``rohstoffe``/``produktionsprozess``/``digitales_mischbuch``). Fail-closed:
  eine fremde Charge mit derselben ``chargen_id`` blockiert den Abschluss.
- ``trace``: löst Auftrag oder ``chargen_id`` zur vollständigen Kette
  Auftrag ↔ Charge ↔ Komponenten (inkl. GVO-/QS-Flags) auf.
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Iterable, Optional

from sqlalchemy.orm import Session

from app.core.uuid7 import prefixed_id
from app.domains.operations.models import Charge, ChargeStatus
from app.infrastructure.models.futtermittel_models import (
    Einzelfuttermittel,
    FuttermittelRezept,
    ProduktionsAuftrag,
)


class FeedChainError(Exception):
    """Fachlicher Fehler in der Produktions-Belegkette (→ HTTP 409)."""


def compute_verbrauch(menge_t: Any, komponenten: Iterable[Any]) -> list[dict]:
    """Reiner Verbrauchs-Snapshot: benötigte Komponentenmengen für ``menge_t``.

    ``komponenten`` sind RezeptKomponente-Objekte (oder Duck-Typing-Äquivalente
    mit ``komponente_name``/``anteil``/``einzelfutter_id``/``sortierung``).
    """
    menge = Decimal(str(menge_t))
    snapshot: list[dict] = []
    for komp in sorted(komponenten, key=lambda k: getattr(k, "sortierung", 0) or 0):
        anteil = Decimal(str(komp.anteil))
        snapshot.append(
            {
                "einzelfutter_id": komp.einzelfutter_id,
                "name": komp.komponente_name,
                "anteil": float(anteil),
                "menge_t": float(menge * anteil),
            }
        )
    return snapshot


def fehlende_komponenten(
    snapshot: list[dict], bestaende: dict[str, Any]
) -> list[str]:
    """Reine Prüfung: welche Snapshot-Positionen übersteigen den Bestand?

    ``bestaende``: einzelfutter_id → verfügbare Menge (t).
    """
    fehlend: list[str] = []
    for row in snapshot:
        ef_id = row.get("einzelfutter_id")
        if not ef_id:
            continue
        verfuegbar = Decimal(str(bestaende.get(ef_id, 0) or 0))
        benoetigt = Decimal(str(row["menge_t"]))
        if verfuegbar < benoetigt:
            fehlend.append(
                f"{row['name']}: benötigt {float(benoetigt):.3f}t, "
                f"verfügbar {float(verfuegbar):.3f}t"
            )
    return fehlend


class FeedProductionChainService:
    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    # -- Bestand -----------------------------------------------------------

    def apply_verbrauch(self, snapshot: list[dict], richtung: int) -> None:
        """Bestand je Snapshot-Zeile anpassen (richtung=-1 Abzug, +1 Rückgabe).

        Sperrt die Einzelfuttermittel-Zeilen (``FOR UPDATE``); kein Commit hier —
        die Transaktion gehört dem aufrufenden Handler.
        """
        for row in snapshot:
            ef_id = row.get("einzelfutter_id")
            if not ef_id:
                continue
            ef = (
                self.db.query(Einzelfuttermittel)
                .filter(Einzelfuttermittel.id == ef_id)
                .with_for_update()
                .first()
            )
            if ef is not None:
                delta = Decimal(str(row["menge_t"])) * richtung
                ef.verfuegbar_t = (ef.verfuegbar_t or 0) + delta

    def bestaende_fuer(self, snapshot: list[dict]) -> dict[str, Any]:
        ids = [r["einzelfutter_id"] for r in snapshot if r.get("einzelfutter_id")]
        if not ids:
            return {}
        rows = (
            self.db.query(Einzelfuttermittel)
            .filter(Einzelfuttermittel.id.in_(ids))
            .all()
        )
        return {ef.id: ef.verfuegbar_t or 0 for ef in rows}

    # -- Snapshot ----------------------------------------------------------

    def snapshot_or_recipe(self, auftrag: ProduktionsAuftrag) -> list[dict]:
        """Persistierter Freigabe-Snapshot; Fallback: aktuelles Rezept (Alt-Aufträge)."""
        if auftrag.verbrauch:
            return list(auftrag.verbrauch)
        if not auftrag.rezept_id:
            return []
        rezept = (
            self.db.query(FuttermittelRezept)
            .filter(FuttermittelRezept.id == auftrag.rezept_id)
            .first()
        )
        if rezept is None:
            return []
        return compute_verbrauch(auftrag.menge_t, rezept.komponenten)

    # -- Charge ------------------------------------------------------------

    def complete_to_charge(
        self, auftrag: ProduktionsAuftrag, lagerort: str = "Mischanlage"
    ) -> Charge:
        """Fertigwaren-Charge zur Auftrags-``chargen_id`` anlegen (idempotent).

        Fail-closed: existiert die ``chargen_id`` bereits als Charge, die NICHT
        aus diesem Auftrag stammt, wird der Abschluss blockiert.
        """
        if auftrag.charge_id:
            existing = (
                self.db.query(Charge).filter(
                    Charge.id == auftrag.charge_id,
                    Charge.tenant_id == self.tenant_id,
                ).first()
            )
            if existing is not None:
                return existing

        by_chargen_id = (
            self.db.query(Charge)
            .filter(
                Charge.chargen_id == auftrag.chargen_id,
                Charge.tenant_id == self.tenant_id,
            )
            .first()
        )
        if by_chargen_id is not None:
            quelle = (by_chargen_id.produktionsprozess or {}).get(
                "produktionsauftrag_id"
            )
            if quelle == auftrag.id:
                auftrag.charge_id = by_chargen_id.id
                return by_chargen_id
            raise FeedChainError(
                f"Chargen-ID '{auftrag.chargen_id}' existiert bereits als fremde "
                "Charge — Auftrag kann nicht abgeschlossen werden."
            )

        snapshot = self.snapshot_or_recipe(auftrag)
        rohstoffe = self._rohstoffe_mit_stammdaten(snapshot)
        now = datetime.now(timezone.utc)

        charge = Charge(
            id=prefixed_id("CH"),
            tenant_id=self.tenant_id,
            chargen_id=auftrag.chargen_id,
            artikel=auftrag.rezept_name,
            artikel_id=auftrag.rezept_id or "MISCHFUTTER",
            produktbezeichnung=auftrag.rezept_name,
            menge=float(auftrag.menge_t),
            lagerort=lagerort,
            eingang=now,
            herstellungsdatum=now,
            status=ChargeStatus.ERFASST.value,
            qualitaetsstatus=ChargeStatus.IN_PRUEFUNG.value,
            herkunft="Eigenproduktion Mischfutter",
            rohstoffe=rohstoffe,
            produktionsprozess={
                "produktionsauftrag_id": auftrag.id,
                "rezept_id": auftrag.rezept_id,
                "rezept_name": auftrag.rezept_name,
                "menge_t": float(auftrag.menge_t),
                "freigegeben_von": auftrag.freigegeben_von,
                "freigegeben_am": auftrag.freigegeben_am.isoformat()
                if auftrag.freigegeben_am
                else None,
            },
            digitales_mischbuch={
                "eintraege": [
                    {
                        "zeitpunkt": now.isoformat(),
                        "aktion": "produktion_fertig",
                        "produktionsauftrag_id": auftrag.id,
                        "komponenten": len(rohstoffe),
                    }
                ]
            },
            created_by=auftrag.freigegeben_von or "produktion",
        )
        self.db.add(charge)
        self.db.flush()
        auftrag.charge_id = charge.id
        return charge

    def _rohstoffe_mit_stammdaten(self, snapshot: list[dict]) -> list[dict]:
        """Snapshot um GVO-/QS-/Lieferanten-Stammdaten der Komponenten anreichern."""
        ids = [r["einzelfutter_id"] for r in snapshot if r.get("einzelfutter_id")]
        stamm: dict[str, Einzelfuttermittel] = {}
        if ids:
            for ef in (
                self.db.query(Einzelfuttermittel)
                .filter(Einzelfuttermittel.id.in_(ids))
                .all()
            ):
                stamm[ef.id] = ef
        rohstoffe = []
        for row in snapshot:
            ef = stamm.get(row.get("einzelfutter_id") or "")
            rohstoffe.append(
                {
                    **row,
                    "einheit": "t",
                    "artikel_nummer": ef.artikel_nummer if ef else None,
                    "lieferant": ef.lieferant if ef else None,
                    "gvo_status": ef.gvo_status if ef else None,
                    "qs_milch": bool(ef.qs_milch) if ef else None,
                    "gmp_plus": bool(ef.gmp_plus) if ef else None,
                }
            )
        return rohstoffe

    # -- Trace -------------------------------------------------------------

    def trace(self, ref: str) -> Optional[dict]:
        """Kette Auftrag ↔ Charge ↔ Komponenten zu Auftrag-ID oder chargen_id."""
        auftrag = (
            self.db.query(ProduktionsAuftrag)
            .filter(
                ProduktionsAuftrag.tenant_id == self.tenant_id,
                (ProduktionsAuftrag.id == ref)
                | (ProduktionsAuftrag.chargen_id == ref),
            )
            .first()
        )
        if auftrag is None:
            return None

        charge = None
        if auftrag.charge_id:
            charge = (
                self.db.query(Charge).filter(
                    Charge.id == auftrag.charge_id,
                    Charge.tenant_id == self.tenant_id,
                ).first()
            )
        if charge is None:
            charge = (
                self.db.query(Charge)
                .filter(
                    Charge.chargen_id == auftrag.chargen_id,
                    Charge.tenant_id == self.tenant_id,
                )
                .first()
            )

        komponenten = self.snapshot_or_recipe(auftrag)
        return {
            "auftrag": {
                "id": auftrag.id,
                "chargen_id": auftrag.chargen_id,
                "rezept_id": auftrag.rezept_id,
                "rezept_name": auftrag.rezept_name,
                "menge_t": float(auftrag.menge_t),
                "status": auftrag.status,
                "freigegeben_am": auftrag.freigegeben_am.isoformat()
                if auftrag.freigegeben_am
                else None,
                "fertig_am": auftrag.fertig_am.isoformat()
                if auftrag.fertig_am
                else None,
            },
            "charge": {
                "id": charge.id,
                "chargen_id": charge.chargen_id,
                "status": charge.status,
                "qualitaetsstatus": charge.qualitaetsstatus,
                "lagerort": charge.lagerort,
                "menge": float(charge.menge),
                "rohstoffe": charge.rohstoffe or [],
            }
            if charge is not None
            else None,
            "komponenten": komponenten,
            "kette_geschlossen": charge is not None,
        }
