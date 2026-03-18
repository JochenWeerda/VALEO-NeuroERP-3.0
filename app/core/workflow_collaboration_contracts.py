from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import datetime


class AbstimmungsTyp(str, Enum):
    EINFACHE_MEHRHEIT = "EINFACHE_MEHRHEIT"     # > 50%
    QUALIFIZIERTE_MEHRHEIT = "QUALIFIZIERTE_MEHRHEIT"  # >= 66.7%
    EINSTIMMIGKEIT = "EINSTIMMIGKEIT"            # 100%
    VETO = "VETO"                                # Any NO blocks


class StimmeTyp(str, Enum):
    JA = "JA"
    NEIN = "NEIN"
    ENTHALTEN = "ENTHALTEN"


class KollaborationsStatus(str, Enum):
    OFFEN = "OFFEN"
    ANGENOMMEN = "ANGENOMMEN"
    ABGELEHNT = "ABGELEHNT"
    ABGELAUFEN = "ABGELAUFEN"


@dataclass
class Stimme:
    stimmer_id: str
    stimme: StimmeTyp
    abgegeben_am: datetime
    kommentar: str = ""


@dataclass
class KollaborationsEntscheidung:
    entscheidung_id: str
    workflow_instanz_id: str
    abstimmungs_typ: AbstimmungsTyp
    erforderliche_stimmer: list = field(default_factory=list)  # list[str] of stimmer_ids
    abgegebene_stimmen: list = field(default_factory=list)     # list[Stimme]
    status: KollaborationsStatus = KollaborationsStatus.OFFEN
    erstellt_am: datetime = field(default_factory=datetime.utcnow)
    faellig_am: Optional[datetime] = None

    def ausstehende_stimmer(self) -> list:
        """Returns stimmer_ids who haven't voted yet."""
        abgestimmt = {s.stimmer_id for s in self.abgegebene_stimmen}
        return [s for s in self.erforderliche_stimmer if s not in abgestimmt]

    def ja_stimmen(self) -> int:
        return sum(1 for s in self.abgegebene_stimmen if s.stimme == StimmeTyp.JA)

    def nein_stimmen(self) -> int:
        return sum(1 for s in self.abgegebene_stimmen if s.stimme == StimmeTyp.NEIN)

    def beteiligung_pct(self) -> float:
        """abgegebene / erforderliche * 100. 0.0 if no required voters."""
        if not self.erforderliche_stimmer:
            return 0.0
        return (len(self.abgegebene_stimmen) / len(self.erforderliche_stimmer)) * 100

    def berechne_ergebnis(self) -> KollaborationsStatus:
        """
        Calculates result based on abstimmungs_typ.
        VETO: any NEIN → ABGELEHNT; all required voted with JA/ENTHALTEN → ANGENOMMEN; else OFFEN
        EINSTIMMIGKEIT: any NEIN → ABGELEHNT; all JA no outstanding → ANGENOMMEN; else OFFEN
        EINFACHE_MEHRHEIT: if all voted — JA > 50% of votes (excl. ENTHALTEN) → ANGENOMMEN; else ABGELEHNT
                           if not all voted yet → OFFEN
        QUALIFIZIERTE_MEHRHEIT: same but threshold >= 66.7%
        Returns OFFEN if not enough votes yet (for MEHRHEIT types).
        """
        if self.abstimmungs_typ == AbstimmungsTyp.VETO:
            if self.nein_stimmen() > 0:
                return KollaborationsStatus.ABGELEHNT
            if not self.ausstehende_stimmer():
                return KollaborationsStatus.ANGENOMMEN
            return KollaborationsStatus.OFFEN

        if self.abstimmungs_typ == AbstimmungsTyp.EINSTIMMIGKEIT:
            if self.nein_stimmen() > 0:
                return KollaborationsStatus.ABGELEHNT
            if not self.ausstehende_stimmer():
                return KollaborationsStatus.ANGENOMMEN
            return KollaborationsStatus.OFFEN

        # MEHRHEIT types — only decide when all have voted
        if self.ausstehende_stimmer():
            return KollaborationsStatus.OFFEN
        entscheidende = self.ja_stimmen() + self.nein_stimmen()
        if entscheidende == 0:
            return KollaborationsStatus.OFFEN
        ja_pct = (self.ja_stimmen() / entscheidende) * 100
        schwelle = 50.0 if self.abstimmungs_typ == AbstimmungsTyp.EINFACHE_MEHRHEIT else 66.7
        return KollaborationsStatus.ANGENOMMEN if ja_pct > schwelle else KollaborationsStatus.ABGELEHNT


def get_default_entscheidungen() -> list:
    now = datetime(2026, 3, 16, 10, 0, 0)
    from datetime import timedelta

    # E-001: EINFACHE_MEHRHEIT, 3 voters, 2 voted JA → pending (1 missing)
    e1 = KollaborationsEntscheidung("E-001", "WI-K-001", AbstimmungsTyp.EINFACHE_MEHRHEIT,
                                     ["USER-A", "USER-B", "USER-C"], [], KollaborationsStatus.OFFEN,
                                     now - timedelta(hours=2), now + timedelta(hours=22))
    e1.abgegebene_stimmen = [
        Stimme("USER-A", StimmeTyp.JA, now - timedelta(hours=1)),
        Stimme("USER-B", StimmeTyp.JA, now - timedelta(minutes=30)),
    ]

    # E-002: VETO, 2 voters, one said NEIN → ABGELEHNT
    e2 = KollaborationsEntscheidung("E-002", "WI-AP-002", AbstimmungsTyp.VETO,
                                     ["USER-A", "USER-D"], [], KollaborationsStatus.ABGELEHNT,
                                     now - timedelta(hours=1), now + timedelta(hours=23))
    e2.abgegebene_stimmen = [
        Stimme("USER-A", StimmeTyp.JA, now - timedelta(minutes=50)),
        Stimme("USER-D", StimmeTyp.NEIN, now - timedelta(minutes=40), "Preis zu hoch"),
    ]

    # E-003: EINSTIMMIGKEIT, all voted JA → ANGENOMMEN
    e3 = KollaborationsEntscheidung("E-003", "WI-S-003", AbstimmungsTyp.EINSTIMMIGKEIT,
                                     ["USER-B", "USER-C"], [], KollaborationsStatus.ANGENOMMEN,
                                     now - timedelta(hours=3), now + timedelta(hours=21))
    e3.abgegebene_stimmen = [
        Stimme("USER-B", StimmeTyp.JA, now - timedelta(hours=2)),
        Stimme("USER-C", StimmeTyp.JA, now - timedelta(hours=1)),
    ]

    return [e1, e2, e3]
