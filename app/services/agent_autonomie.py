"""Agent Trust & Autonomy Engine (ADR-086 "Risk-based Autonomous ERP", Entwurf mit gesonderter Freigabe).

Ein Agent fuehrt eine Faehigkeit (z. B. ``sales.gutschrift.buchen``) nur dann ohne menschliche Freigabe aus, wenn
**alles** zutrifft - sonst gilt der bisherige Weg (Vorschlag, Freigabe durch einen Menschen):

1. Die Autonomiepolitik (``config/agent_autonomy_policy.yaml``) ist in genau dieser Fassung (Inhaltsabdruck) fuer
   den Mandanten fachlich freigegeben - von einer Person mit Freigaberolle, die nicht Autorin ist.
2. Ein Mensch hat dem Agenten die Faehigkeit ausdruecklich delegiert (begrenzt, widerrufbar) und haelt das Recht
   selbst; der Betrag liegt unter Delegations- und Politikgrenze.
3. Das Qualitaetsmodell des Agenten ist im Rahmen (Fehler-, Befund- und Einwandquote, aktueller Testnachweis).
   Verschlechtert es sich, wird die Delegation automatisch entzogen und der Controller-Pruefkorb informiert.
4. Die deterministischen Fach- und Sicherheitspruefungen bestehen (Aufrufer reicht das Ergebnis herein).
5. Die zentrale Risiko-Engine (FIN-CONTROL-001, unveraendert) verlangt **keine** unabhaengige Freigabe.
6. Kein Pruefagent erhebt einen Einwand.

Jede Entscheidung steht unveraenderlich in ``domain_shared.agent_autonomy_decisions``. Ein Agent gibt nie frei:
Die Politik- und Delegationsfreigaben nehmen nur Personen vor (``freigabe_engine.technisches_konto``).
"""
from __future__ import annotations

import hashlib
import json
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterator, Optional
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, ValidationFailedError

POLITIK_PFAD = Path(__file__).resolve().parents[2] / "config" / "agent_autonomy_policy.yaml"
QUALITAETS_ENTZUG = "qualitaetsmodell"


# ── Wer handelt: Agentenkontext und Einzelfreigaben ──────────────────────────────────────────────────────────────

_AGENT: ContextVar[Optional[str]] = ContextVar("valeo_handelnder_agent", default=None)
_EINZELFREIGABEN: ContextVar[frozenset[str]] = ContextVar("valeo_einzelfreigaben", default=frozenset())


@contextmanager
def als_agent(agent_id: Optional[str]) -> Iterator[None]:
    """Der Block laeuft fuer einen Agenten (MCP-Werkzeugaufruf). Ohne Kennung aendert sich nichts."""
    marke = _AGENT.set(agent_id) if agent_id else None
    try:
        yield
    finally:
        if marke is not None:
            _AGENT.reset(marke)


@contextmanager
def menschlich_freigegeben(vorgang: str) -> Iterator[None]:
    """Ein Mensch hat genau diesen Vorgang im Einzelfall freigegeben (freigegebener Vorschlag): kein Autonomiefall."""
    marke = _EINZELFREIGABEN.set(_EINZELFREIGABEN.get() | {vorgang})
    try:
        yield
    finally:
        _EINZELFREIGABEN.reset(marke)


def handelnder_agent(akteur: Optional[str] = None) -> Optional[str]:
    """Die Agentenkennung, wenn ein Agent handelt - aus dem MCP-Kontext oder der geprueften Identitaet."""
    agent = _AGENT.get()
    if agent:
        return agent
    try:
        from app.core.identity_context import current_identity

        claims = dict(current_identity().claims)
    except Exception:  # noqa: BLE001 - keine gepruefte Identitaet (Hintergrundlauf, Test): kein Agent erkennbar
        return None
    if str(claims.get("identity_type") or "").lower() == "agent" or claims.get("agent_id") or claims.get("act"):
        return str(claims.get("agent_id") or claims.get("sub") or akteur or "agent")
    return None


# ── Politik ──────────────────────────────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Politik:
    inhalt: dict[str, Any]
    abdruck: str

    @property
    def policy_id(self) -> str:
        return str(self.inhalt["policy_id"])

    @property
    def version(self) -> str:
        return str(self.inhalt["version"])

    def faehigkeit(self, name: str) -> Optional[dict[str, Any]]:
        return (self.inhalt.get("faehigkeiten") or {}).get(name)


def abdruck_von(inhalt: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(inhalt, sort_keys=True, ensure_ascii=False, default=str).encode()).hexdigest()


@lru_cache(maxsize=4)
def _lade(pfad: str, stand: float) -> Politik:
    import yaml

    inhalt = yaml.safe_load(Path(pfad).read_text(encoding="utf-8"))
    return Politik(inhalt=inhalt, abdruck=abdruck_von(inhalt))


def lade_politik(pfad: Path = POLITIK_PFAD) -> Politik:
    return _lade(str(pfad), pfad.stat().st_mtime)


def _rollen(nutzer: Any) -> set[str]:
    from app.auth.beleg_roles import rollen_von

    return rollen_von(nutzer)


def _person(nutzer: Any, was: str) -> str:
    """Nur eine angemeldete Person (kein Agent, kein technisches Konto) nimmt diese Handlung vor."""
    from app.services.freigabe_engine import technisches_konto

    wer = str((nutzer or {}).get("sub") or "").strip() if isinstance(nutzer, dict) else ""
    if not wer:
        raise ValidationFailedError(f"{was} nimmt nur eine angemeldete Person vor.")
    raw = nutzer.get("raw") if isinstance(nutzer.get("raw"), dict) else {}
    if technisches_konto(nutzer) or str(raw.get("identity_type") or "").lower() == "agent":
        raise ValidationFailedError(f"{was}: Ein Agent oder technisches Konto handelt hier nicht.")
    return wer


def politik_freigabe(db: Session, tenant: str, politik: Optional[Politik] = None) -> Optional[dict[str, Any]]:
    """Die gueltige Freigabe genau dieser Fassung - oder ``None`` (dann gilt keine Autonomie)."""
    politik = politik or lade_politik()
    zeile = db.execute(text(
        "SELECT id, version, content_hash, approved_by, approved_at, note FROM domain_shared.agent_policy_approvals "
        "WHERE tenant_id = :t AND policy_id = :p AND content_hash = :h AND revoked_at IS NULL"),
        {"t": tenant, "p": politik.policy_id, "h": politik.abdruck}).mappings().first()
    return dict(zeile) if zeile else None


def gib_politik_frei(db: Session, tenant: str, nutzer: Any, notiz: str, politik: Optional[Politik] = None) -> dict:
    politik = politik or lade_politik()
    wer = _person(nutzer, "Die fachliche Freigabe der Autonomiepolitik")
    if wer == str(politik.inhalt.get("author") or ""):
        raise ValidationFailedError("Funktionstrennung: Wer die Politik verfasst hat, gibt sie nicht frei.")
    if not _rollen(nutzer) & set(politik.inhalt.get("freigaberollen") or []):
        raise ValidationFailedError("Keine Berechtigung zur fachlichen Freigabe der Autonomiepolitik.")
    if len((notiz or "").strip()) < 10:
        raise ValidationFailedError("Die Freigabe braucht eine fachliche Begruendung (mindestens 10 Zeichen).")
    if politik_freigabe(db, tenant, politik):
        raise ConflictError("Diese Fassung der Autonomiepolitik ist bereits freigegeben.")
    kennung = str(uuid4())
    db.execute(text(
        "INSERT INTO domain_shared.agent_policy_approvals (id, tenant_id, policy_id, version, content_hash, "
        "approved_by, note) VALUES (:id, :t, :p, :v, :h, :wer, :n)"),
        {"id": kennung, "t": tenant, "p": politik.policy_id, "v": politik.version, "h": politik.abdruck,
         "wer": wer, "n": notiz.strip()})
    return politik_freigabe(db, tenant, politik) or {}


def widerrufe_politik(db: Session, tenant: str, nutzer: Any, grund: str, politik: Optional[Politik] = None) -> None:
    politik = politik or lade_politik()
    wer = _person(nutzer, "Der Widerruf der Autonomiepolitik")
    if not _rollen(nutzer) & set(politik.inhalt.get("freigaberollen") or []):
        raise ValidationFailedError("Keine Berechtigung zum Widerruf der Autonomiepolitik.")
    if len((grund or "").strip()) < 3:
        raise ValidationFailedError("Der Widerruf braucht einen Grund.")
    db.execute(text(
        "UPDATE domain_shared.agent_policy_approvals SET revoked_at = clock_timestamp(), revoked_by = :wer, "
        "revoke_reason = :g WHERE tenant_id = :t AND policy_id = :p AND revoked_at IS NULL"),
        {"wer": wer, "g": grund.strip(), "t": tenant, "p": politik.policy_id})


# ── Delegation ───────────────────────────────────────────────────────────────────────────────────────────────────

def delegiere(db: Session, tenant: str, nutzer: Any, *, agent_id: str, faehigkeit: str,
              max_brutto: Optional[Decimal] = None, gueltig_bis: Optional[datetime] = None,
              politik: Optional[Politik] = None) -> dict:
    politik = politik or lade_politik()
    wer = _person(nutzer, "Die Delegation einer Agentenfaehigkeit")
    regel = politik.faehigkeit(faehigkeit)
    if regel is None:
        raise ValidationFailedError(f"Die Autonomiepolitik kennt die Faehigkeit {faehigkeit} nicht.")
    if not agent_id.strip() or agent_id == wer:
        raise ValidationFailedError("Delegiert wird an einen Agenten, nicht an sich selbst.")
    if not _rollen(nutzer) & set(regel.get("delegierbar_durch") or []):
        raise ValidationFailedError("Keine Berechtigung: Delegiert wird nur ein Recht, das die delegierende Person selbst hat.")
    grenze = Decimal(str(regel.get("hoechstbetrag_brutto") or "0"))
    if max_brutto is not None and max_brutto > grenze:
        raise ValidationFailedError(f"Die Delegation darf die Politikgrenze von {grenze} EUR nicht ueberschreiten.")
    if db.execute(text("SELECT 1 FROM domain_shared.agent_delegations WHERE tenant_id = :t AND agent_id = :a "
                       "AND capability = :c AND revoked_at IS NULL"),
                  {"t": tenant, "a": agent_id, "c": faehigkeit}).first():
        raise ConflictError("Diese Faehigkeit ist dem Agenten bereits delegiert.")
    kennung = str(uuid4())
    db.execute(text(
        "INSERT INTO domain_shared.agent_delegations (id, tenant_id, agent_id, capability, owner, max_brutto, "
        "valid_until) VALUES (:id, :t, :a, :c, :o, :m, :g)"),
        {"id": kennung, "t": tenant, "a": agent_id, "c": faehigkeit, "o": wer, "m": max_brutto, "g": gueltig_bis})
    return {"id": kennung, "agent_id": agent_id, "capability": faehigkeit, "owner": wer}


def widerrufe_delegation(db: Session, tenant: str, kennung: str, *, durch: str, grund: str) -> bool:
    return bool(db.execute(text(
        "UPDATE domain_shared.agent_delegations SET revoked_at = clock_timestamp(), revoked_by = :d, "
        "revoke_reason = :g WHERE tenant_id = :t AND id = :i AND revoked_at IS NULL"),
        {"d": durch, "g": grund, "t": tenant, "i": kennung}).rowcount)


def delegation(db: Session, tenant: str, agent_id: str, faehigkeit: str) -> Optional[dict[str, Any]]:
    zeile = db.execute(text(
        "SELECT id, owner, max_brutto, valid_until, created_at FROM domain_shared.agent_delegations "
        "WHERE tenant_id = :t AND agent_id = :a AND capability = :c AND revoked_at IS NULL"),
        {"t": tenant, "a": agent_id, "c": faehigkeit}).mappings().first()
    return dict(zeile) if zeile else None


# ── Qualitaetsmodell ─────────────────────────────────────────────────────────────────────────────────────────────

ART_VON_MENSCHEN = {"korrigiert"}  # Nur eine Person stellt fest, dass eine Agentenbuchung falsch war.
ART_TEST = {"test_bestanden", "test_fehlgeschlagen"}


def erfasse(db: Session, tenant: str, *, agent_id: str, faehigkeit: str, art: str, durch: str,
            vorgang: Optional[str] = None, detail: Optional[dict[str, Any]] = None) -> None:
    if durch == agent_id:
        raise ValidationFailedError("Ein Agent erfasst keine Qualitaetsmesspunkte ueber sich selbst.")
    db.execute(text(
        "INSERT INTO domain_shared.agent_quality_events (id, tenant_id, agent_id, capability, kind, subject_id, "
        "detail, recorded_by) VALUES (:id, :t, :a, :c, :k, :s, CAST(:d AS jsonb), :by)"),
        {"id": str(uuid4()), "t": tenant, "a": agent_id, "c": faehigkeit, "k": art, "s": vorgang,
         "d": json.dumps(detail or {}, default=str), "by": durch})


@dataclass
class Qualitaet:
    ausgefuehrt: int
    korrigiert: int
    befunde: int
    einwaende: int
    versuche: int
    letzter_test: Optional[str]
    letzter_test_am: Optional[datetime]
    verletzungen: list[str] = field(default_factory=list)

    @property
    def im_rahmen(self) -> bool:
        return not self.verletzungen

    def als_dict(self) -> dict[str, Any]:
        def quote(zaehler: int, nenner: int) -> float:
            return round(zaehler / nenner, 4) if nenner else 0.0

        return {"ausgefuehrt": self.ausgefuehrt, "korrigiert": self.korrigiert, "befunde": self.befunde,
                "einwaende": self.einwaende, "versuche": self.versuche,
                "fehlerquote": quote(self.korrigiert, self.ausgefuehrt),
                "befundquote": quote(self.befunde, self.ausgefuehrt),
                "einwandquote": quote(self.einwaende, self.versuche),
                "letzter_test": self.letzter_test,
                "letzter_test_am": self.letzter_test_am.isoformat() if self.letzter_test_am else None,
                "im_rahmen": self.im_rahmen, "verletzungen": self.verletzungen}


def qualitaet(db: Session, tenant: str, agent_id: str, faehigkeit: str, politik: Optional[Politik] = None,
              jetzt: Optional[datetime] = None) -> Qualitaet:
    politik = politik or lade_politik()
    regel = (politik.faehigkeit(faehigkeit) or {}).get("qualitaet") or {}
    jetzt = jetzt or datetime.now(timezone.utc)
    seit = jetzt - timedelta(days=int(regel.get("fenster_tage") or 90))
    zahlen = dict(db.execute(text(
        "SELECT kind, count(*) FROM domain_shared.agent_quality_events WHERE tenant_id = :t AND agent_id = :a "
        "AND capability = :c AND recorded_at >= :seit GROUP BY kind"),
        {"t": tenant, "a": agent_id, "c": faehigkeit, "seit": seit}).fetchall())
    test = db.execute(text(
        "SELECT kind, recorded_at FROM domain_shared.agent_quality_events WHERE tenant_id = :t AND agent_id = :a "
        "AND capability = :c AND kind IN ('test_bestanden', 'test_fehlgeschlagen') ORDER BY recorded_at DESC LIMIT 1"),
        {"t": tenant, "a": agent_id, "c": faehigkeit}).first()
    q = Qualitaet(ausgefuehrt=int(zahlen.get("ausgefuehrt", 0)), korrigiert=int(zahlen.get("korrigiert", 0)),
                  befunde=int(zahlen.get("befund", 0)), einwaende=int(zahlen.get("einwand", 0)),
                  versuche=int(zahlen.get("ausgefuehrt", 0)) + int(zahlen.get("einwand", 0))
                  + int(zahlen.get("abgelehnt", 0)),
                  letzter_test=test[0] if test else None, letzter_test_am=test[1] if test else None)
    if q.letzter_test is None:
        q.verletzungen.append("Kein Testnachweis fuer diese Faehigkeit.")
    elif q.letzter_test == "test_fehlgeschlagen":
        q.verletzungen.append("Der letzte Testnachweis ist fehlgeschlagen.")
    elif q.letzter_test_am < jetzt - timedelta(days=int(regel.get("testnachweis_max_alter_tage") or 30)):
        q.verletzungen.append("Der Testnachweis ist veraltet.")
    if q.ausgefuehrt < int(regel.get("mindestanzahl_fuer_quote") or 20):
        if q.korrigiert > int(regel.get("max_fehler_absolut_startphase") or 0):
            q.verletzungen.append(f"{q.korrigiert} korrigierte Buchungen in der Startphase.")
    else:
        if q.korrigiert / q.ausgefuehrt > float(regel.get("max_fehlerquote") or 0):
            q.verletzungen.append(f"Fehlerquote {q.korrigiert}/{q.ausgefuehrt} ueber der Grenze.")
        if q.befunde / q.ausgefuehrt > float(regel.get("max_befundquote") or 0):
            q.verletzungen.append(f"Befundquote {q.befunde}/{q.ausgefuehrt} ueber der Grenze.")
    if q.versuche and q.einwaende / q.versuche > float(regel.get("max_einwandquote") or 1):
        q.verletzungen.append(f"Einwandquote {q.einwaende}/{q.versuche} ueber der Grenze.")
    return q


def pruefe_qualitaet_und_entziehe(db: Session, tenant: str, agent_id: str, faehigkeit: str,
                                  politik: Optional[Politik] = None) -> Qualitaet:
    """Ausserhalb des Rahmens: Delegation entziehen, den Controller informieren. Ein Mensch muss neu delegieren."""
    q = qualitaet(db, tenant, agent_id, faehigkeit, politik)
    aktiv = delegation(db, tenant, agent_id, faehigkeit)
    if q.verletzungen and aktiv and q.letzter_test is not None:
        grund = "; ".join(q.verletzungen)
        widerrufe_delegation(db, tenant, str(aktiv["id"]), durch=QUALITAETS_ENTZUG, grund=grund)
        db.execute(text(
            "INSERT INTO domain_docflow.control_findings (id, tenant_id, subject_type, subject_id, action, code, "
            "severity, text, actor) VALUES (:id, :t, 'agent_delegation', :s, 'autonomie', 'agent_qualitaet', "
            "'warnung', :txt, :a)"),
            {"id": str(uuid4()), "t": tenant, "s": str(aktiv["id"]), "a": agent_id,
             "txt": f"Autonomie fuer {faehigkeit} entzogen ({agent_id}): {grund}"})
    return q


# ── Autonomieentscheidung ────────────────────────────────────────────────────────────────────────────────────────

@dataclass
class Entscheidung:
    ergebnis: str  # autonom | freigabe | abgelehnt
    gruende: list[str]
    risiko: Optional[str] = None
    politik_version: Optional[str] = None

    @property
    def autonom(self) -> bool:
        return self.ergebnis == "autonom"


def entscheide(db: Session, tenant: str, *, agent_id: str, faehigkeit: str, vorgang: Optional[str],
               brutto: Decimal, fachpruefung: Optional[str], risiko: Any, einwaende: list[str],
               politik: Optional[Politik] = None, protokoll: str = "einheit") -> Entscheidung:
    """``fachpruefung``: ``None`` bestanden, sonst der Pruefgrund. ``risiko``: ``Anforderung`` der Risiko-Engine."""
    politik = politik or lade_politik()
    gruende: list[str] = []
    regel = politik.faehigkeit(faehigkeit)
    stufe = getattr(risiko, "risiko", None)
    if fachpruefung:
        ergebnis, gruende = "abgelehnt", [f"Fachpruefung: {fachpruefung}"]
    elif regel is None:
        ergebnis, gruende = "freigabe", [f"Die Autonomiepolitik kennt {faehigkeit} nicht."]
    else:
        a0, a1, _q = a2_gruende(db, tenant, agent_id, faehigkeit, politik)  # Stufe A2 - dieselbe Quelle wie vertrauen
        gruende += a0 + a1
        aktiv = delegation(db, tenant, agent_id, faehigkeit)
        if aktiv is not None and aktiv["max_brutto"] is not None and brutto > Decimal(str(aktiv["max_brutto"])):
            gruende.append(f"Betrag {brutto} EUR ueber der delegierten Grenze {aktiv['max_brutto']} EUR.")
        if brutto > Decimal(str(regel.get("hoechstbetrag_brutto") or "0")):
            gruende.append(f"Betrag {brutto} EUR ueber der Politikgrenze {regel.get('hoechstbetrag_brutto')} EUR.")
        if getattr(risiko, "zweitfreigabe", True):
            gruende.append(f"Die Risiko-Engine verlangt eine unabhaengige Freigabe ({stufe}): "
                           f"{getattr(risiko, 'grund', '')}".strip())
        gruende += [f"Einwand Pruefagent: {e}" for e in einwaende]
        ergebnis = "freigabe" if gruende else "autonom"
    zeile = {"id": str(uuid4()), "t": tenant, "a": agent_id, "c": faehigkeit, "s": vorgang, "v": politik.version,
             "h": politik.abdruck, "o": ergebnis, "r": stufe, "g": json.dumps(gruende, ensure_ascii=False)}
    if protokoll == "getrennt" and ergebnis != "autonom":
        _protokolliere_getrennt(db, tenant, zeile)
    elif protokoll != "keins":
        db.execute(text(_ENTSCHEIDUNG_SQL), zeile)
    return Entscheidung(ergebnis=ergebnis, gruende=gruende, risiko=stufe, politik_version=politik.version)


_ENTSCHEIDUNG_SQL = (
    "INSERT INTO domain_shared.agent_autonomy_decisions (id, tenant_id, agent_id, capability, subject_id, "
    "policy_version, policy_hash, outcome, risk, reasons) VALUES (:id, :t, :a, :c, :s, :v, :h, :o, :r, CAST(:g AS jsonb))")


def _protokolliere_getrennt(db: Session, tenant: str, zeile: dict[str, Any]) -> None:
    """Eine Ablehnung bleibt protokolliert, auch wenn das Kommando danach zurueckrollt (eigene Verbindung, RLS)."""
    bindung = db.get_bind()
    maschine = getattr(bindung, "engine", bindung)
    try:
        with maschine.connect() as verbindung:
            with verbindung.begin():
                verbindung.execute(text("SELECT set_config('app.tenant_id', :t, true)"), {"t": tenant})
                verbindung.execute(text(_ENTSCHEIDUNG_SQL), zeile)
    except Exception:  # noqa: BLE001 - Tabelle nur in der offenen Transaktion (frische Migration im Test): dort eintragen
        db.execute(text(_ENTSCHEIDUNG_SQL), zeile)


# ── Vertrauensstufe (Agent Trust) ────────────────────────────────────────────────────────────────────────────────

STUFEN = {
    "A0": "beobachten - keine freigegebene Politik oder keine Delegation",
    "A1": "vorschlagen - delegiert, aber Qualitaet oder Testnachweis nicht im Rahmen",
    "A2": "begrenzt autonom - Routine bis zur Grenze; Risiko-Engine und Pruefagenten entscheiden mit",
    "A3": "nur mit menschlicher Freigabe - kritische Vorgaenge, unabhaengig von der Stufe des Agenten",
}


def a2_gruende(db: Session, tenant: str, agent_id: str, faehigkeit: str,
               politik: Optional[Politik] = None) -> tuple[list[str], list[str], Qualitaet]:
    """Die eine Quelle fuer Stufe A2: (Gruende fuer A0, Gruende fuer A1, Qualitaet). Leer = A2.

    ``vertrauen`` (Anzeige) und ``entscheide`` (Durchsetzung) lesen beide hier - die angezeigte Stufe und die
    durchgesetzte Entscheidung koennen nicht auseinanderlaufen.
    """
    politik = politik or lade_politik()
    a0: list[str] = []
    if politik_freigabe(db, tenant, politik) is None:
        a0.append(f"Autonomiepolitik {politik.version} ist fuer diesen Mandanten nicht fachlich freigegeben.")
    aktiv = delegation(db, tenant, agent_id, faehigkeit)
    if aktiv is None:
        a0.append("Keine gueltige Delegation dieser Faehigkeit an den Agenten.")
    elif aktiv["valid_until"] and aktiv["valid_until"] < datetime.now(timezone.utc):
        a0.append("Die Delegation ist abgelaufen.")
    q = pruefe_qualitaet_und_entziehe(db, tenant, agent_id, faehigkeit, politik)
    return a0, [f"Qualitaet: {v}" for v in q.verletzungen], q


def vertrauen(db: Session, tenant: str, agent_id: str, faehigkeit: str, politik: Optional[Politik] = None) -> dict:
    """Die Vertrauensstufe eines Agenten fuer eine Faehigkeit - abgeleitet, nie gesetzt (Agent Trust Engine).

    A3 ist keine Stufe, die ein Agent erreicht: Sie beschreibt Vorgaenge, die immer einen Menschen brauchen
    (die Risiko-Engine verlangt eine unabhaengige Freigabe). Ein Agent steht hoechstens auf A2.
    """
    politik = politik or lade_politik()
    a0, a1, q = a2_gruende(db, tenant, agent_id, faehigkeit, politik)
    stufe = "A0" if a0 else ("A1" if a1 else "A2")
    return {"agent_id": agent_id, "faehigkeit": faehigkeit, "stufe": stufe, "bedeutung": STUFEN[stufe],
            "gruende": a0 + a1, "politik_version": politik.version,
            "delegation": delegation(db, tenant, agent_id, faehigkeit), "qualitaet": q.als_dict()}


# ── Lernende Autonomie-Governance ────────────────────────────────────────────────────────────────────────────────

def lernvorschlaege(db: Session, tenant: str, politik: Optional[Politik] = None) -> list[dict[str, Any]]:
    """Vorschlaege zur Weiterentwicklung der Politik aus Bilanz und Entscheidungsprotokoll - nie selbst wirksam.

    Die Governance lernt, die Politik nicht: Jeder Vorschlag nennt seine Belege und die Aenderung. Wirksam wird er
    nur als neue Fassung von ``config/agent_autonomy_policy.yaml`` mit neuer fachlicher Freigabe (ADR-086). Es gibt
    zwei Richtungen: erweitern (lange fehlerfreie Bilanz, viele Vorgaenge knapp ueber der Grenze) und einschraenken
    (Fehler, Befunde, Einwaende gehaeuft - auch wenn der automatische Entzug schon gegriffen hat).
    """
    politik = politik or lade_politik()
    vorschlaege: list[dict[str, Any]] = []
    for name, regel in (politik.inhalt.get("faehigkeiten") or {}).items():
        qregel = regel.get("qualitaet") or {}
        mindestens = int(qregel.get("mindestanzahl_fuer_quote") or 20)
        grenze = Decimal(str(regel.get("hoechstbetrag_brutto") or "0"))
        agenten = [z[0] for z in db.execute(text(
            "SELECT DISTINCT agent_id FROM domain_shared.agent_quality_events WHERE tenant_id = :t AND capability = :c"),
            {"t": tenant, "c": name}).fetchall()]
        for agent in agenten:
            q = qualitaet(db, tenant, agent, name, politik)
            beleg = {"agent_id": agent, **q.als_dict()}
            if q.korrigiert or q.befunde > q.ausgefuehrt * float(qregel.get("max_befundquote") or 0) \
                    or (q.versuche and q.einwaende / q.versuche > float(qregel.get("max_einwandquote") or 1)):
                vorschlaege.append({
                    "faehigkeit": name, "richtung": "einschraenken", "agent_id": agent,
                    "aenderung": {"hoechstbetrag_brutto": float((grenze / 2).quantize(Decimal("0.01")))},
                    "begruendung": "Fehler, Befunde oder Einwaende im Beobachtungsfenster.", "belege": beleg})
            elif q.ausgefuehrt >= 2 * mindestens and q.im_rahmen:
                vorschlaege.append({
                    "faehigkeit": name, "richtung": "erweitern", "agent_id": agent,
                    "aenderung": {"hoechstbetrag_brutto": float((grenze * Decimal("1.5")).quantize(Decimal("0.01")))},
                    "begruendung": f"{q.ausgefuehrt} autonome Buchungen ohne Korrektur, Befund oder Einwand.",
                    "belege": beleg})
        knapp = db.execute(text(
            "SELECT count(*) FROM domain_shared.agent_autonomy_decisions WHERE tenant_id = :t AND capability = :c "
            "AND outcome = 'freigabe' AND reasons::text LIKE '%Politikgrenze%' "
            "AND decided_at >= clock_timestamp() - interval '90 days'"), {"t": tenant, "c": name}).scalar() or 0
        if knapp >= mindestens:
            vorschlaege.append({
                "faehigkeit": name, "richtung": "pruefen", "agent_id": None,
                "aenderung": {"hoechstbetrag_brutto": "fachlich bewerten"},
                "begruendung": f"{knapp} Vorgaenge in 90 Tagen nur wegen der Politikgrenze an Menschen gegangen.",
                "belege": {"vorgaenge_ueber_grenze": int(knapp)}})
    return vorschlaege



# ── Zentrales Tor in der Freigabe-Engine ─────────────────────────────────────────────────────────────────────────

class AutonomieVerweigert(ConflictError):
    """Ein Agent darf diesen Vorgang nicht autonom ausfuehren; ``gruende`` nennt warum."""

    def __init__(self, gruende: list[str], ergebnis: str = "freigabe") -> None:
        self.gruende, self.ergebnis = gruende, ergebnis
        super().__init__("Keine autonome Ausfuehrung durch einen Agenten: " + "; ".join(gruende))


def faehigkeit_fuer(belegart: str, aktion: str, politik: Optional[Politik] = None) -> Optional[str]:
    politik = politik or lade_politik()
    for name, regel in (politik.inhalt.get("faehigkeiten") or {}).items():
        if regel.get("belegart") == belegart and regel.get("aktion") == aktion:
            return name
    return None


def tor(db: Session, tenant: str, vorgang: Any, aktion: str, bedarf: Any, akteur: Optional[str],
        *, trocken: bool = False) -> None:
    """Von ``FreigabeEngine.verlange_fuer`` vor jeder freigaberelevanten Ausfuehrung gerufen - gleich ueber welchen Weg.

    * Kein Agent: nichts zu tun (FIN-CONTROL-001 unveraendert).
    * Ein Mensch hat genau diesen Vorgang freigegeben (Vorschlag, Einzelfreigabe): kein Autonomiefall.
    * Verlangt die Risiko-Engine eine unabhaengige Freigabe, prueft die Engine sie selbst (Mensch, verbraucht).
    * Sonst Routine: Ein Agent braucht Stufe A2 fuer die passende Faehigkeit, Grenzen, keinen Pruefagenten-Einwand.
      Fuer Belegart und Aktion ohne Faehigkeit in der Politik fuehrt kein Agent aus (fail-closed).
    """
    agent = handelnder_agent(akteur)
    if agent is None or str(vorgang.subject_id) in _EINZELFREIGABEN.get() or getattr(bedarf, "zweitfreigabe", False):
        return
    from app.services import agent_pruefagenten

    politik = lade_politik()
    faehigkeit = faehigkeit_fuer(str(vorgang.belegart), aktion, politik)
    if faehigkeit is None:
        gruende = [f"Die Autonomiepolitik erlaubt Agenten {vorgang.belegart}/{aktion} nicht."]
        if trocken:
            raise AutonomieVerweigert(gruende, "abgelehnt")
        _protokolliere_getrennt(db, tenant, {
            "id": str(uuid4()), "t": tenant, "a": agent, "c": f"{vorgang.belegart}.{aktion}", "s": str(vorgang.subject_id),
            "v": politik.version, "h": politik.abdruck, "o": "abgelehnt", "r": getattr(bedarf, "risiko", None),
            "g": json.dumps(gruende, ensure_ascii=False)})
        raise AutonomieVerweigert(gruende, "abgelehnt")
    regel = politik.faehigkeit(faehigkeit) or {}
    einwaende = agent_pruefagenten.pruefe(db, list(regel.get("pruefagenten") or []), agent_pruefagenten.Pruefkontext(
        tenant=tenant, faehigkeit=faehigkeit, agent_id=agent, vorgang=str(vorgang.subject_id),
        brutto=Decimal(str(vorgang.brutto)), daten=dict(vorgang.inhalt or {})))
    entscheidung = entscheide(db, tenant, agent_id=agent, faehigkeit=faehigkeit, vorgang=str(vorgang.subject_id),
                              brutto=Decimal(str(vorgang.brutto)), fachpruefung=None, risiko=bedarf,
                              einwaende=einwaende, politik=politik, protokoll="keins" if trocken else "getrennt")
    if trocken:
        if not entscheidung.autonom:
            raise AutonomieVerweigert(entscheidung.gruende)
        return
    if not entscheidung.autonom:
        if einwaende:
            _messpunkt_getrennt(db, tenant, agent, faehigkeit, "einwand", str(vorgang.subject_id), {"einwaende": einwaende})
        raise AutonomieVerweigert(entscheidung.gruende)
    erfasse(db, tenant, agent_id=agent, faehigkeit=faehigkeit, art="ausgefuehrt", durch="autonomie",
            vorgang=str(vorgang.subject_id), detail={"brutto": str(vorgang.brutto), "risk": entscheidung.risiko})
    for befund in getattr(bedarf, "warnungen", ()) or ():
        erfasse(db, tenant, agent_id=agent, faehigkeit=faehigkeit, art="befund", durch="kontroll_engine",
                vorgang=str(vorgang.subject_id), detail={"code": befund.code, "text": befund.text})


def _messpunkt_getrennt(db: Session, tenant: str, agent: str, faehigkeit: str, art: str, vorgang: str,
                        detail: dict[str, Any]) -> None:
    bindung = db.get_bind()
    maschine = getattr(bindung, "engine", bindung)
    werte = {"id": str(uuid4()), "t": tenant, "a": agent, "c": faehigkeit, "k": art, "s": vorgang,
             "d": json.dumps(detail, default=str), "by": "pruefagenten"}
    sql = ("INSERT INTO domain_shared.agent_quality_events (id, tenant_id, agent_id, capability, kind, subject_id, "
           "detail, recorded_by) VALUES (:id, :t, :a, :c, :k, :s, CAST(:d AS jsonb), :by)")
    try:
        with maschine.connect() as verbindung:
            with verbindung.begin():
                verbindung.execute(text("SELECT set_config('app.tenant_id', :t, true)"), {"t": tenant})
                verbindung.execute(text(sql), werte)
    except Exception:  # noqa: BLE001 - wie _protokolliere_getrennt
        db.execute(text(sql), werte)
