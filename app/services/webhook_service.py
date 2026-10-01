"""Ausgehende Webhooks — die einzige Stelle, die die Anbindungen anfasst.

Bis zum 01.10.2026 gab es zwei Module unter ``/api/v1/webhooks``
(``webhook_system.py`` und ``webhooks.py``) mit zwei Tabellen, zwei
Bereichslisten und zwei Vorstellungen davon, woher der Mandant kommt. Beide
Router sind jetzt duenn und rufen hierher; damit kann es keine zweite Fassung
mehr geben.

**Eine Tabelle:** ``domain_shared.webhook_registrations`` (migriert, ORM-Modell,
``tenant_id`` mit Fremdschluessel auf ``tenants``, ``secret``). Dazu
``domain_shared.webhook_deliveries`` als Nachweis je Zustellversuch.

**Ein Vokabular:** ``BEREICHE`` unten. Es ist die Vereinigung der beiden alten
Listen, in **einer** Schreibweise. Die alten Objektnamen von ``webhooks.py``
(``auftrag``, ``bestellung`` …) werden als Aliasse weiter angenommen und auf das
zugehoerige Ereignis abgebildet; gespeichert wird immer der kanonische Name.

**Ein Mandant:** Er kommt aus dem Kopf der Anfrage. Keine Funktion hier hat
einen Vorgabewert dafuer.

Noch nicht verdrahtet ist das Senden selbst: ``trigger`` hat ausserhalb der
Tests keinen Aufrufer, weil kein Fachdienst Webhook-Ereignisse meldet. Das ist
der naechste Schritt und ein eigener Vorgang — siehe
``docs/quality-assurance/webhook-mandant-20261001.md``.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

#: Kopfzeile mit der Signatur des gesendeten Rumpfes. Ohne sie kann ein
#: Empfaenger nicht unterscheiden, ob ein Aufruf von uns kommt oder von
#: jemandem, der die URL kennt.
SIGNATUR_KOPF = "X-Valeo-Signature"

REGISTRIERUNGEN = "domain_shared.webhook_registrations"
ZUSTELLUNGEN = "domain_shared.webhook_deliveries"


#: Das kanonische Vokabular: benannte Geschaeftsereignisse, auf die ein
#: Fremdsystem hoeren kann. Die Liste ist die Vereinigung der beiden alten
#: Listen — die Ereignisse aus ``webhook_system`` und, in derselben
#: Schreibweise, je ein Ereignis fuer die Objekte, die ``webhooks.py`` anbot.
#: Niemand verliert damit eine Wahlmoeglichkeit, und es gibt nur eine Form.
BEREICHE = [
    "WIEGUNG_NEU",
    "WIEGUNG_GEAENDERT",
    "KONTRAKT_NEU",
    "KONTRAKT_FREIGEGEBEN",
    "SETTLEMENT_GEBUCHT",
    "RECHNUNG_NEU",
    "BESTELLUNG_FREIGEGEBEN",
    "LIEFERSCHEIN_ERSTELLT",
    "INVENTUR_ABGESCHLOSSEN",
    "KUNDE_NEU",
    "INTERESSENT_KONVERTIERT",
    "AUFTRAG_NEU",
    "ARTIKEL_GEAENDERT",
    "LAGERBEWEGUNG_GEBUCHT",
    "PICKLISTE_ERSTELLT",
    "NVE_ERSTELLT",
    "STAMMDATEN_GEAENDERT",
]

#: Die Objektnamen, die ``webhooks.py`` bis zum 01.10.2026 annahm, auf das
#: zugehoerige Ereignis. Bestehende Registrierungen und Aufrufer brechen damit
#: nicht; gespeichert wird aber der kanonische Name.
ALIASSE = {
    "auftrag": "AUFTRAG_NEU",
    "bestellung": "BESTELLUNG_FREIGEGEBEN",
    "kunde": "KUNDE_NEU",
    "artikel": "ARTIKEL_GEAENDERT",
    "lieferschein": "LIEFERSCHEIN_ERSTELLT",
    "rechnung": "RECHNUNG_NEU",
    "inventur": "INVENTUR_ABGESCHLOSSEN",
    "lager": "LAGERBEWEGUNG_GEBUCHT",
    "pickliste": "PICKLISTE_ERSTELLT",
    "wiegeschein": "WIEGUNG_NEU",
    "nve": "NVE_ERSTELLT",
    "stammdaten": "STAMMDATEN_GEAENDERT",
}


class UnbekannterBereich(ValueError):
    """Der Bereich ist weder kanonisch noch ein bekannter Alias."""


def kanonischer_bereich(bereich: str) -> str:
    """Bildet Alias oder Schreibweise auf den kanonischen Namen ab."""
    roh = (bereich or "").strip()
    if roh in BEREICHE:
        return roh
    klein = roh.lower()
    if klein in ALIASSE:
        return ALIASSE[klein]
    gross = roh.upper()
    if gross in BEREICHE:
        return gross
    raise UnbekannterBereich(
        f"Unbekannter Bereich '{bereich}'. Gültig: {', '.join(BEREICHE)} "
        f"(oder die alten Objektnamen: {', '.join(sorted(ALIASSE))})"
    )


@dataclass(frozen=True)
class Anbindung:
    """Eine Anbindung, wie sie nach aussen gezeigt wird — ohne Geheimnis."""

    id: str
    nr: int
    url: str
    bereich: str
    is_active: bool
    erstellt_am: Optional[str]
    letzte_auslosung_am: Optional[str]
    fehler_count: int
    signiert: bool


class NichtLesbar(RuntimeError):
    """Die Anbindungen sind derzeit nicht lesbar."""


class NichtGefunden(LookupError):
    """Es gibt keine solche Anbindung in diesem Haus."""


#: Die laufende Nummer ist keine Spalte, sondern die Stellung der Zeile **im
#: eigenen Haus**. Vorher kam sie aus ``MAX(nr) + 1`` ueber alle Haeuser.
#: ``letzte_auslosung_am`` und ``fehler_count`` kommen aus dem Zustellprotokoll
#: und sind damit belegt statt behauptet.
_ANBINDUNGEN = f"""
    SELECT r.id,
           r.url,
           r.event_area,
           r.is_active,
           r.created_at,
           (r.secret IS NOT NULL)                       AS signiert,
           ROW_NUMBER() OVER (ORDER BY r.created_at, r.id) AS nr,
           (SELECT MAX(z.versucht_am) FROM {ZUSTELLUNGEN} z
              WHERE z.webhook_id = r.id)                AS letzte_auslosung_am,
           (SELECT COUNT(*) FROM {ZUSTELLUNGEN} z
              WHERE z.webhook_id = r.id AND NOT z.erfolgreich) AS fehler_count
    FROM {REGISTRIERUNGEN} r
    WHERE r.tenant_id = :tid
"""


def _zu_anbindung(row: Any) -> Anbindung:
    return Anbindung(
        id=str(row["id"]),
        nr=int(row["nr"]),
        url=row["url"],
        bereich=row["event_area"],
        is_active=True if row["is_active"] is None else bool(row["is_active"]),
        erstellt_am=row["created_at"].isoformat() if row["created_at"] else None,
        letzte_auslosung_am=(
            row["letzte_auslosung_am"].isoformat() if row["letzte_auslosung_am"] else None
        ),
        fehler_count=int(row["fehler_count"] or 0),
        signiert=bool(row["signiert"]),
    )


def auflisten(db: Session, tenant_id: str) -> list[Anbindung]:
    """Die Anbindungen des eigenen Hauses, nach laufender Nummer."""
    try:
        rows = db.execute(
            text(_ANBINDUNGEN + " ORDER BY nr"), {"tid": tenant_id}
        ).mappings().all()
    except Exception as fehler:
        # Keine leere Liste: "keine Anbindung eingerichtet" und "die Tabelle ist
        # nicht lesbar" sahen gleich aus. Im zweiten Fall haette ein Haus eine
        # bestehende Anbindung fuer abgemeldet gehalten und doppelt registriert.
        db.rollback()
        logger.exception("Webhooks nicht lesbar (Mandant %s)", tenant_id)
        raise NichtLesbar("Webhooks sind derzeit nicht abrufbar") from fehler
    return [_zu_anbindung(r) for r in rows]


def registrieren(
    db: Session,
    tenant_id: str,
    *,
    url: str,
    bereich: str,
    secret: Optional[str] = None,
    is_active: bool = True,
) -> Anbindung:
    """Legt eine Anbindung an. ``bereich`` darf ein Alias sein."""
    from app.core.outbound_security import validate_outbound_http_target
    from app.core.uuid7 import uuid7

    kanonisch = kanonischer_bereich(bereich)
    # Eine Ziel-URL darf nicht in das eigene Netz zeigen (SSRF). ``https://``
    # allein genuegt nicht: Damit liesse sich die Anwendung als Bote an den
    # Metadatendienst der Cloud schicken.
    validate_outbound_http_target(url)

    neue_id = str(uuid7())
    jetzt = datetime.now(timezone.utc)
    db.execute(
        text(
            f"INSERT INTO {REGISTRIERUNGEN} "
            "(id, tenant_id, url, event_area, secret, is_active, created_at, updated_at) "
            "VALUES (:id, :tid, :url, :bereich, :secret, :is_active, :jetzt, :jetzt)"
        ),
        {
            "id": neue_id,
            "tid": tenant_id,
            "url": url,
            "bereich": kanonisch,
            # Das Geheimnis wurde bis zum 01.10.2026 entgegengenommen und
            # verworfen. Jetzt wird es hinterlegt, signiert jeden Aufruf und
            # wird nie wieder ausgegeben.
            "secret": secret or None,
            "is_active": is_active,
            "jetzt": jetzt,
        },
    )
    db.commit()

    nr = db.execute(
        text(f"SELECT nr FROM ({_ANBINDUNGEN}) AS m WHERE id = :id"),  # nosec B608  # reviewed-safe: _ANBINDUNGEN ist ein Code-Literal, Werte sind gebunden
        {"tid": tenant_id, "id": neue_id},
    ).scalar_one()

    return Anbindung(
        id=neue_id,
        nr=int(nr),
        url=url,
        bereich=kanonisch,
        is_active=is_active,
        erstellt_am=jetzt.isoformat(),
        letzte_auslosung_am=None,
        fehler_count=0,
        signiert=bool(secret),
    )


def abmelden_nach_nummer(db: Session, tenant_id: str, nr: int) -> None:
    """Meldet die Anbindung mit dieser laufenden Nummer im eigenen Haus ab."""
    ziel = db.execute(
        text(f"SELECT id FROM ({_ANBINDUNGEN}) AS m WHERE nr = :nr"),  # nosec B608  # reviewed-safe: _ANBINDUNGEN ist ein Code-Literal, Werte sind gebunden
        {"tid": tenant_id, "nr": nr},
    ).scalar()
    if ziel is None:
        raise NichtGefunden(f"Webhook nr={nr} nicht gefunden")
    _loeschen(db, tenant_id, str(ziel))


def abmelden_nach_kennung(db: Session, tenant_id: str, webhook_id: str) -> None:
    """Meldet die Anbindung mit dieser Kennung **im eigenen Haus** ab."""
    vorhanden = db.execute(
        text(f"SELECT 1 FROM {REGISTRIERUNGEN} WHERE id = :id AND tenant_id = :tid"),
        {"id": webhook_id, "tid": tenant_id},
    ).scalar()
    if not vorhanden:
        raise NichtGefunden("Webhook not found")
    _loeschen(db, tenant_id, webhook_id)


def _loeschen(db: Session, tenant_id: str, webhook_id: str) -> None:
    db.execute(
        text(f"DELETE FROM {REGISTRIERUNGEN} WHERE id = :id AND tenant_id = :tid"),
        {"id": webhook_id, "tid": tenant_id},
    )
    db.commit()


def signatur(secret: str, rumpf: bytes) -> str:
    """HMAC-SHA256 ueber den gesendeten Rumpf, hexadezimal."""
    return "sha256=" + hmac.new(secret.encode("utf-8"), rumpf, hashlib.sha256).hexdigest()


def _protokollieren(
    db: Session,
    tenant_id: str,
    webhook_id: str,
    bereich: str,
    *,
    erfolgreich: bool,
    status_code: Optional[int],
    dauer_ms: int,
    fehler: Optional[str],
    signiert: bool,
) -> None:
    from app.core.uuid7 import uuid7

    db.execute(
        text(
            f"INSERT INTO {ZUSTELLUNGEN} "
            "(id, tenant_id, webhook_id, event_area, versucht_am, erfolgreich, "
            " status_code, dauer_ms, fehler, signiert) "
            "VALUES (:id, :tid, :wid, :bereich, NOW(), :ok, :code, :dauer, :fehler, :signiert)"
        ),
        {
            "id": str(uuid7()),
            "tid": tenant_id,
            "wid": webhook_id,
            "bereich": bereich,
            "ok": erfolgreich,
            "code": status_code,
            "dauer": dauer_ms,
            # Der Wortlaut wird gekappt: Ein Protokoll soll sagen, was war,
            # nicht einen Stapelabzug aufbewahren.
            "fehler": (fehler or "")[:500] or None,
            "signiert": signiert,
        },
    )


async def trigger(
    db: Session,
    tenant_id: str,
    bereich: str,
    payload: dict[str, Any],
) -> int:
    """Feuert die aktiven Anbindungen **dieses Hauses** und protokolliert jeden
    Versuch. Gibt die Zahl der erfolgreichen Zustellungen zurueck.

    ``tenant_id`` ist Pflicht und ohne Vorgabewert: Vorher waehlte die Abfrage
    alle Anbindungen eines Bereichs, also haette ein Vorgang aus Haus A an die
    URL von Haus B gemeldet.
    """
    if not tenant_id:
        logger.error("webhook trigger ohne Mandant (%s) — nichts gesendet", bereich)
        return 0
    try:
        kanonisch = kanonischer_bereich(bereich)
    except UnbekannterBereich:
        logger.error("webhook trigger mit unbekanntem Bereich %r", bereich)
        return 0

    try:
        rows = db.execute(
            text(
                f"SELECT id, url, secret FROM {REGISTRIERUNGEN} "
                "WHERE tenant_id = :tid AND event_area = :b "
                "  AND COALESCE(is_active, TRUE) = TRUE"
            ),
            {"tid": tenant_id, "b": kanonisch},
        ).mappings().all()
    except Exception:  # noqa: BLE001
        db.rollback()
        logger.warning("webhook trigger: Anbindungen nicht lesbar")
        return 0

    rumpf = json.dumps(payload).encode("utf-8")
    zugestellt = 0
    for row in rows:
        url = row["url"]
        signiert = bool(row["secret"])
        kopf = {"Content-Type": "application/json"}
        if signiert:
            kopf[SIGNATUR_KOPF] = signatur(row["secret"], rumpf)
        begonnen = time.monotonic()
        status_code: Optional[int] = None
        fehlertext: Optional[str] = None
        try:
            import httpx  # optional dependency

            async with httpx.AsyncClient(timeout=5.0) as client:
                antwort = await client.post(url, content=rumpf, headers=kopf)
            status_code = getattr(antwort, "status_code", None)
            erfolgreich = status_code is not None and 200 <= int(status_code) < 300
            if not erfolgreich:
                fehlertext = f"HTTP {status_code}"
        except Exception as fehler:  # noqa: BLE001
            erfolgreich = False
            fehlertext = f"{type(fehler).__name__}: {fehler}"
            logger.warning("Webhook %s failed: %s", url, fehler)

        if erfolgreich:
            zugestellt += 1
        try:
            _protokollieren(
                db,
                tenant_id,
                str(row["id"]),
                kanonisch,
                erfolgreich=erfolgreich,
                status_code=status_code,
                dauer_ms=int((time.monotonic() - begonnen) * 1000),
                fehler=fehlertext,
                signiert=signiert,
            )
            db.commit()
        except Exception:  # noqa: BLE001
            # Der Versuch ist protokolliert, wenn es geht. Scheitert das
            # Protokoll, darf der Vorgang, der das Ereignis ausgeloest hat,
            # nicht mitgerissen werden — er ist die Buchung, nicht der Bote.
            db.rollback()
            logger.exception("Zustellprotokoll nicht schreibbar (Mandant %s)", tenant_id)
    return zugestellt


def zustellversuche(
    db: Session, tenant_id: str, webhook_id: str, grenze: int = 20
) -> list[dict[str, Any]]:
    """Die letzten Zustellversuche einer Anbindung des eigenen Hauses."""
    rows = db.execute(
        text(
            f"SELECT z.versucht_am, z.erfolgreich, z.status_code, z.dauer_ms, z.fehler "
            f"FROM {ZUSTELLUNGEN} z "
            f"JOIN {REGISTRIERUNGEN} r ON r.id = z.webhook_id AND r.tenant_id = :tid "
            "WHERE z.webhook_id = :wid "
            "ORDER BY z.versucht_am DESC LIMIT :grenze"
        ),
        {"tid": tenant_id, "wid": webhook_id, "grenze": max(1, min(grenze, 200))},
    ).mappings().all()
    return [
        {
            "versucht_am": r["versucht_am"].isoformat() if r["versucht_am"] else None,
            "erfolgreich": bool(r["erfolgreich"]),
            "status_code": r["status_code"],
            "dauer_ms": r["dauer_ms"],
            "fehler": r["fehler"],
        }
        for r in rows
    ]
