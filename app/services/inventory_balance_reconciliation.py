"""Abstimmbericht fuer das Bestandshauptbuch (DOM-INV-006).

GoBD verlangt Nachvollziehbarkeit: ein sachverstaendiger Dritter muss den
Bestand in angemessener Zeit pruefen koennen. Eine blosse Saldozahl reicht dafuer
nicht - man muss sehen, woraus sie entsteht und was bewusst *nicht* eingeht.

Der Bericht liefert deshalb drei Ebenen:

* den Saldo je Artikel und Lager,
* die Herkunft nach Belegart, damit jede Zahl auf ihre Buchungen zurueckfuehrbar
  ist,
* alles, was nicht bestandswirksam ist, getrennt ausgewiesen statt verschwiegen.

Die dritte Ebene ist die wichtigste. Reservierungen und die historischen
Absolutwerte der alten mobilen Zaehlung stehen im Hauptbuch, gehen aber nicht in
den Saldo ein. Wer sie nicht ausweist, produziert eine Zahl, die stimmt, die
aber niemand gegen die Zeilenliste nachrechnen kann.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.inventory_movement_direction import direction_sql


@dataclass
class BestandsZeile:
    """Saldo einer Artikel-/Lagerkombination."""

    article_id: str
    warehouse_id: str
    saldo: float
    buchungen: int


@dataclass
class BelegartZeile:
    """Beitrag einer Belegart zum Gesamtsaldo."""

    movement_type: str
    richtung: int
    bestandswirksam: bool
    buchungen: int
    menge_roh: float
    beitrag_saldo: float


@dataclass
class AbstimmBericht:
    """Ergebnis des Abgleichs.

    ``nicht_bestandswirksam`` ist bewusst eine eigene Liste und keine Fussnote:
    sie ist der Teil, den ein Pruefer sonst als Differenz zwischen Zeilenliste
    und Saldo wiederfinden wuerde.
    """

    tenant_id: str | None
    buchungen_gesamt: int
    saldo_gesamt: float
    bestaende: list[BestandsZeile] = field(default_factory=list)
    nach_belegart: list[BelegartZeile] = field(default_factory=list)
    nicht_bestandswirksam: list[BelegartZeile] = field(default_factory=list)
    unbekannte_belegarten: dict[str, int] = field(default_factory=dict)

    @property
    def ist_abstimmbar(self) -> bool:
        """Wahr, wenn jede Buchung einer registrierten Belegart zugeordnet ist.

        Nur dann ist der Saldo vollstaendig erklaerbar. Nicht bestandswirksame
        Zeilen stoeren das nicht - sie sind erklaert, sie zaehlen nur nicht mit.
        """
        return not self.unbekannte_belegarten

    def als_dict(self) -> dict[str, Any]:
        return {
            "tenant_id": self.tenant_id,
            "buchungen_gesamt": self.buchungen_gesamt,
            "saldo_gesamt": self.saldo_gesamt,
            "ist_abstimmbar": self.ist_abstimmbar,
            "bestaende": [vars(z) for z in self.bestaende],
            "nach_belegart": [vars(z) for z in self.nach_belegart],
            "nicht_bestandswirksam": [vars(z) for z in self.nicht_bestandswirksam],
            "unbekannte_belegarten": self.unbekannte_belegarten,
        }


def _tenant_filter(tenant_id: str | None) -> tuple[str, dict[str, Any]]:
    if tenant_id:
        return "WHERE sm.tenant_id = :tenant_id", {"tenant_id": tenant_id}
    return "", {}


def erstelle_bericht(
    db: Session,
    tenant_id: str | None = None,
    *,
    max_bestandszeilen: int = 500,
) -> AbstimmBericht:
    """Abstimmbericht ueber das Bestandshauptbuch.

    ``max_bestandszeilen`` begrenzt nur die Detailliste; Saldo und
    Belegartenherkunft werden immer ueber den vollen Bestand gerechnet, damit
    die Gesamtzahl nicht von einer Anzeigegrenze abhaengt.
    """
    where, params = _tenant_filter(tenant_id)
    richtung = direction_sql("sm.movement_type", "sm.quantity")

    gesamt = db.execute(
        text(
            f"""
            SELECT COUNT(*) AS buchungen, COALESCE(SUM({richtung}), 0) AS saldo
            FROM domain_inventory.inventory_stock_movements sm
            {where}
            """  # nosec B608 - Fragmente aus Modulkonstanten, Werte via Bind-Params
        ),
        params,
    ).first()

    belegarten = db.execute(
        text(
            f"""
            SELECT lower(sm.movement_type) AS belegart,
                   COALESCE(mt.direction, 0) AS richtung,
                   COALESCE(mt.is_delta, false) AS bestandswirksam,
                   COUNT(*) AS buchungen,
                   COALESCE(SUM(sm.quantity), 0) AS menge_roh,
                   COALESCE(SUM({richtung}), 0) AS beitrag
              FROM domain_inventory.inventory_stock_movements sm
              LEFT JOIN domain_inventory.inventory_movement_types mt
                     ON mt.movement_type = lower(sm.movement_type)
            {where}
             GROUP BY 1, 2, 3
             ORDER BY ABS(COALESCE(SUM({richtung}), 0)) DESC, 1
            """  # nosec B608 - Fragmente aus Modulkonstanten, Werte via Bind-Params
        ),
        params,
    ).all()

    nach_belegart: list[BelegartZeile] = []
    nicht_wirksam: list[BelegartZeile] = []
    for belegart, richtung_wert, wirksam, buchungen, menge_roh, beitrag in belegarten:
        zeile = BelegartZeile(
            movement_type=belegart,
            richtung=int(richtung_wert),
            bestandswirksam=bool(wirksam),
            buchungen=int(buchungen),
            menge_roh=float(menge_roh),
            beitrag_saldo=float(beitrag),
        )
        (nach_belegart if zeile.bestandswirksam else nicht_wirksam).append(zeile)

    bestaende = db.execute(
        text(
            f"""
            SELECT sm.article_id, sm.warehouse_id,
                   COALESCE(SUM({richtung}), 0) AS saldo,
                   COUNT(*) AS buchungen
              FROM domain_inventory.inventory_stock_movements sm
            {where}
             GROUP BY sm.article_id, sm.warehouse_id
             ORDER BY ABS(COALESCE(SUM({richtung}), 0)) DESC
             LIMIT :grenze
            """  # nosec B608 - Fragmente aus Modulkonstanten, Werte via Bind-Params
        ),
        {**params, "grenze": max_bestandszeilen},
    ).all()

    from app.services.inventory_movement_direction import unknown_movement_types

    return AbstimmBericht(
        tenant_id=tenant_id,
        buchungen_gesamt=int(gesamt[0]) if gesamt else 0,
        saldo_gesamt=float(gesamt[1]) if gesamt else 0.0,
        bestaende=[
            BestandsZeile(
                article_id=str(a), warehouse_id=str(w), saldo=float(s), buchungen=int(b)
            )
            for a, w, s, b in bestaende
        ],
        nach_belegart=nach_belegart,
        nicht_bestandswirksam=nicht_wirksam,
        unbekannte_belegarten=unknown_movement_types(db, tenant_id),
    )


def als_text(bericht: AbstimmBericht, *, max_zeilen: int = 20) -> str:
    """Bericht als lesbarer Block fuer Betrieb und Pruefung."""
    zeilen: list[str] = []
    zeilen.append("Abstimmbericht Bestandshauptbuch (DOM-INV-006)")
    zeilen.append(f"  Mandant:            {bericht.tenant_id or 'alle'}")
    zeilen.append(f"  Buchungen gesamt:   {bericht.buchungen_gesamt}")
    zeilen.append(f"  Saldo gesamt:       {bericht.saldo_gesamt:,.3f}")
    zeilen.append(f"  Vollstaendig erklaerbar: {'ja' if bericht.ist_abstimmbar else 'NEIN'}")

    zeilen.append("")
    zeilen.append("  Herkunft nach Belegart (bestandswirksam)")
    if not bericht.nach_belegart:
        zeilen.append("    keine")
    for z in bericht.nach_belegart[:max_zeilen]:
        zeilen.append(
            f"    {z.movement_type:<20} {z.buchungen:>6} Buchungen  "
            f"Richtung {z.richtung:+d}  Beitrag {z.beitrag_saldo:>14,.3f}"
        )

    zeilen.append("")
    zeilen.append("  Nicht bestandswirksam (im Hauptbuch, nicht im Saldo)")
    if not bericht.nicht_bestandswirksam:
        zeilen.append("    keine")
    for z in bericht.nicht_bestandswirksam[:max_zeilen]:
        zeilen.append(
            f"    {z.movement_type:<20} {z.buchungen:>6} Buchungen  "
            f"Menge roh {z.menge_roh:>14,.3f}"
        )

    if bericht.unbekannte_belegarten:
        zeilen.append("")
        zeilen.append("  UNBEKANNTE BELEGARTEN - Saldo ist nicht vollstaendig erklaerbar:")
        for belegart, anzahl in bericht.unbekannte_belegarten.items():
            zeilen.append(f"    {belegart:<20} {anzahl:>6} Buchungen")

    zeilen.append("")
    zeilen.append(f"  Bestaende (Top {min(len(bericht.bestaende), max_zeilen)} nach Betrag)")
    if not bericht.bestaende:
        zeilen.append("    keine")
    for z in bericht.bestaende[:max_zeilen]:
        zeilen.append(
            f"    {z.article_id[:20]:<20} {z.warehouse_id[:20]:<20} "
            f"{z.saldo:>14,.3f}  ({z.buchungen} Buchungen)"
        )
    return "\n".join(zeilen)
