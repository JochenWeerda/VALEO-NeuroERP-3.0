from __future__ import annotations
from pydantic import BaseModel
from enum import Enum
import uuid
from datetime import date

class NaehrstoffTyp(str, Enum):
    STICKSTOFF = "N"
    PHOSPHOR = "P2O5"
    KALIUM = "K2O"

class DuengemittelEintrag(BaseModel):
    duengemittel_name: str
    naehrstoff: NaehrstoffTyp
    menge_kg_ha: float
    ausbringdatum: date
    schlag_id: str
    schema_version: int = 1

class DuengeBilanzPosition(BaseModel):
    naehrstoff: NaehrstoffTyp
    bedarf_kg_ha: float          # aus DüV-Tabelle
    zufuhr_kg_ha: float          # Summe aller Einträge für diesen Naehrstoff
    saldo_kg_ha: float           # zufuhr - bedarf (positiv = Überschuss)
    ueberschuss_warnung: bool    # True wenn saldo > 20 kg/ha N oder > 10 kg/ha P2O5
    schema_version: int = 1

class DuengeBilanz(BaseModel):
    bilanz_id: str
    tenant_id: str
    schlag_id: str
    wirtschaftsjahr: int         # z.B. 2025 für WJ 2025/26
    positionen: list[DuengeBilanzPosition]
    gesamt_n_saldo_kg_ha: float
    gobd_konform: bool           # True wenn kein Überschuss > Schwellwert
    schema_version: int = 1

    @classmethod
    def berechne(
        cls,
        tenant_id: str,
        schlag_id: str,
        wirtschaftsjahr: int,
        eintraege: list[DuengemittelEintrag],
        bedarf_n_kg_ha: float = 170.0,
        bedarf_p_kg_ha: float = 60.0,
        bedarf_k_kg_ha: float = 80.0,
    ) -> "DuengeBilanz":
        """Berechne DüV-Bilanz aus Düngemitteleintrag-Liste."""
        bedarfe = {
            NaehrstoffTyp.STICKSTOFF: bedarf_n_kg_ha,
            NaehrstoffTyp.PHOSPHOR: bedarf_p_kg_ha,
            NaehrstoffTyp.KALIUM: bedarf_k_kg_ha,
        }
        zufuhren: dict[NaehrstoffTyp, float] = {t: 0.0 for t in NaehrstoffTyp}
        for e in eintraege:
            if e.schlag_id == schlag_id:
                zufuhren[e.naehrstoff] = zufuhren.get(e.naehrstoff, 0.0) + e.menge_kg_ha

        positionen = []
        for naehrstoff, bedarf in bedarfe.items():
            zufuhr = zufuhren.get(naehrstoff, 0.0)
            saldo = zufuhr - bedarf
            ueberschuss_warnung = False
            if naehrstoff == NaehrstoffTyp.STICKSTOFF and saldo > 20.0:
                ueberschuss_warnung = True
            elif naehrstoff == NaehrstoffTyp.PHOSPHOR and saldo > 10.0:
                ueberschuss_warnung = True
            positionen.append(DuengeBilanzPosition(
                naehrstoff=naehrstoff,
                bedarf_kg_ha=bedarf,
                zufuhr_kg_ha=zufuhr,
                saldo_kg_ha=saldo,
                ueberschuss_warnung=ueberschuss_warnung,
            ))

        n_position = next(p for p in positionen if p.naehrstoff == NaehrstoffTyp.STICKSTOFF)
        gobd_konform = not any(p.ueberschuss_warnung for p in positionen)

        return cls(
            bilanz_id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            schlag_id=schlag_id,
            wirtschaftsjahr=wirtschaftsjahr,
            positionen=positionen,
            gesamt_n_saldo_kg_ha=n_position.saldo_kg_ha,
            gobd_konform=gobd_konform,
        )
