"""Postfaecher des Mandanten: ausgehende E-Mails ueber seinen eigenen Dienst.

Ein Mandant fuehrt beliebig viele Postfaecher — ``info@``, ``dispo@``, ``fibu@``,
``zentrale@``, persoenliche Postfaecher einzelner Mitarbeiter.

Zugang je Postfach:

* ``ionos`` — smtp.ionos.de:587 STARTTLS, Benutzer = E-Mail-Adresse.
* ``google`` — smtp.gmail.com:587 STARTTLS, mit **App-Passwort** (``anmeldung =
  passwort``) oder **Google-Anmeldung** (``anmeldung = oauth2``, SMTP XOAUTH2).
* ``microsoft`` — Microsoft 365: Anmeldung ueber Microsoft (OAuth2, ``Mail.Send``),
  Versand ueber Microsoft Graph ``sendMail``. Kein SMTP AUTH noetig (das Microsoft
  abbaut); die Nachricht liegt danach in "Gesendete Elemente" des Postfachs.
* ``smtp`` — beliebiger Server (Strato, Hetzner, eigener Exchange …).
* ``alias`` — nutzt die Anmeldung eines anderen Postfachs (``zugang_von``) und
  sendet mit eigener Absenderadresse. Beim Anbieter muss die Adresse als Absender
  erlaubt sein (IONOS: Alias; Gmail: "Senden als"), sonst lehnt er ab oder
  schreibt den Absender um.

Welches Postfach (:func:`postfach_waehlen`): ausdruecklich gewaehlt (``postfach_id``)
> das erste freigegebene mit passender ``verwendung`` > das Standard-Postfach.

Wer darf (:func:`darf_senden`): ``admin`` immer; ein persoenliches Postfach nur sein
Inhaber; sonst, wenn ``rollen`` und ``benutzer_freigabe`` leer sind, jeder im
Mandanten, andernfalls nur passende Rolle oder genannter Benutzer.

Das Geheimnis wird mit :mod:`app.core.geheimnis` verschluesselt und nie
zurueckgegeben. ``geprueft`` heisst: eine Testmail wurde vom Server angenommen.
"""

from __future__ import annotations

import base64
import json
import os
import re
import secrets
import time
import uuid
from dataclasses import dataclass
from typing import Any, Iterable, Optional
from urllib.parse import urlencode

import httpx
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core import geheimnis

ZWECK = "mailkonto"
STATE_GUELTIG_SEKUNDEN = 600

#: OAuth je Anbieter. ``{tenant}`` (Microsoft) aus ``MICROSOFT_OAUTH_TENANT``, sonst
#: ``organizations`` (jedes Geschaeftskonto). Zugangsdaten des OAuth-Clients aus
#: ``<PRAEFIX>_CLIENT_ID``/``_CLIENT_SECRET``/``_REDIRECT_URI``.
OAUTH: dict[str, dict[str, Any]] = {
    "google": {
        "name": "Google",
        "praefix": "GOOGLE_OAUTH",
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",  # nosec B105 - Endpunkt, kein Geheimnis
        "scopes": "https://mail.google.com/ openid email",
        "extra": {"access_type": "offline", "prompt": "consent"},
    },
    "microsoft": {
        "name": "Microsoft",
        "praefix": "MICROSOFT_OAUTH",
        "auth_url": "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize",
        "token_url": "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token",  # nosec B105
        "scopes": "offline_access openid email https://graph.microsoft.com/Mail.Send",
        "extra": {"response_mode": "query", "prompt": "select_account"},
    },
}
GRAPH_SENDMAIL_URL = "https://graph.microsoft.com/v1.0/me/sendMail"

VORLAGEN: dict[str, dict[str, Any]] = {
    "ionos": {"smtp_host": "smtp.ionos.de", "smtp_port": 587, "sicherheit": "starttls"},
    "google": {"smtp_host": "smtp.gmail.com", "smtp_port": 587, "sicherheit": "starttls"},
    # Kein SMTP: Versand ueber Microsoft Graph (HTTPS); Host/Port nur zur Anzeige.
    "microsoft": {"smtp_host": "graph.microsoft.com", "smtp_port": 443, "sicherheit": "ssl"},
    "smtp": {},
    "alias": {},
}

#: Wofuer ein Postfach automatisch genommen wird. Schluessel = was die Fachwege angeben.
VERWENDUNGEN: dict[str, str] = {
    "einkauf": "Einkauf (Bestellungen, Anfragen)",
    "verkauf": "Verkauf (Angebote, Auftragsbestätigungen)",
    "fibu": "Finanzbuchhaltung (Rechnungen, Mahnungen)",
    "dispo": "Disposition (Lieferavise, Touren)",
    "newsletter": "Newsletter und Rundschreiben",
    "allgemein": "Allgemeine Korrespondenz",
}

_KENNUNG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,39}$")


class MailkontoFehler(ValueError):
    """Eingabe oder Zustand passt nicht; die Nachricht nennt den Grund."""


class KeinZugriff(MailkontoFehler):
    """Der Nutzer darf aus diesem Postfach nicht senden."""


@dataclass(frozen=True)
class SmtpZugang:
    server: str
    port: int
    sicherheit: str
    benutzer: Optional[str]
    passwort: Optional[str]
    absender: str
    absender_name: Optional[str] = None
    oauth_token: Optional[str] = None
    postfach_id: Optional[str] = None
    #: ``smtp`` oder ``graph`` (Microsoft 365).
    transport: str = "smtp"


# ── Lesen ─────────────────────────────────────────────────────────────────────
def _zeilen(db: Session, tenant_id: str) -> list[dict[str, Any]]:
    return [dict(z) for z in db.execute(
        text("SELECT * FROM domain_shared.mailkonten WHERE tenant_id = :t AND aktiv "
             "ORDER BY ist_standard DESC, kennung LIMIT 500"), {"t": tenant_id}
    ).mappings().all()]


def _zeile(db: Session, tenant_id: str, postfach_id: str) -> dict[str, Any]:
    z = db.execute(
        text("SELECT * FROM domain_shared.mailkonten WHERE tenant_id = :t AND id = :id AND aktiv"),
        {"t": tenant_id, "id": postfach_id},
    ).mappings().first()
    if not z:
        raise MailkontoFehler("Postfach nicht gefunden.")
    return dict(z)


def _aussen(z: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": z["id"], "kennung": z["kennung"], "bezeichnung": z["bezeichnung"],
        "anbieter": z["anbieter"], "anmeldung": z["anmeldung"],
        "smtp_host": z["smtp_host"], "smtp_port": z["smtp_port"], "sicherheit": z["sicherheit"],
        "benutzer": z["benutzer"], "absender_email": z["absender_email"], "absender_name": z["absender_name"],
        "zugang_von": z["zugang_von"], "ist_standard": bool(z["ist_standard"]),
        "verwendungen": list(z["verwendungen"] or []), "rollen": list(z["rollen"] or []),
        "benutzer_freigabe": list(z["benutzer_freigabe"] or []), "persoenlich_fuer": z["persoenlich_fuer"],
        "hat_geheimnis": bool(z["geheimnis"]), "status": z["status"],
        "geprueft_am": z["geprueft_am"].isoformat() if z.get("geprueft_am") else None,
        "letzter_fehler": z["letzter_fehler"],
        "updated_at": z["updated_at"].isoformat() if z.get("updated_at") else None,
    }


def liste(db: Session, tenant_id: str) -> list[dict[str, Any]]:
    return [_aussen(z) for z in _zeilen(db, tenant_id)]


def lesen(db: Session, tenant_id: str, postfach_id: str) -> dict[str, Any]:
    return _aussen(_zeile(db, tenant_id, postfach_id))


# ── Zugriff ───────────────────────────────────────────────────────────────────
def darf_senden(z: dict[str, Any], nutzer: Optional[dict[str, Any]]) -> bool:
    rollen = set((nutzer or {}).get("roles") or [])
    sub = str((nutzer or {}).get("sub") or "")
    if "admin" in rollen:
        return True
    if z.get("persoenlich_fuer"):
        return bool(sub) and sub == z["persoenlich_fuer"]
    freigabe_rollen = set(z.get("rollen") or [])
    freigabe_nutzer = set(z.get("benutzer_freigabe") or [])
    if not freigabe_rollen and not freigabe_nutzer:
        return True
    return bool(rollen & freigabe_rollen) or (bool(sub) and sub in freigabe_nutzer)


def verfuegbar(db: Session, tenant_id: str, nutzer: Optional[dict[str, Any]],
               verwendung: Optional[str] = None) -> list[dict[str, Any]]:
    """Die Postfaecher, aus denen dieser Nutzer senden darf (fuer die Absenderwahl)."""
    return [
        {"id": z["id"], "kennung": z["kennung"], "absender_email": z["absender_email"],
         "absender_name": z["absender_name"], "ist_standard": bool(z["ist_standard"]),
         "passt": bool(verwendung and verwendung in (z["verwendungen"] or []))}
        for z in _zeilen(db, tenant_id) if darf_senden(z, nutzer)
    ]


def postfach_waehlen(db: Session, tenant_id: str, *, verwendung: Optional[str] = None,
                     nutzer: Optional[dict[str, Any]] = None,
                     postfach_id: Optional[str] = None) -> Optional[dict[str, Any]]:
    """Das Postfach fuer einen Versand, oder ``None``, wenn der Mandant keines fuehrt."""
    if postfach_id:
        z = _zeile(db, tenant_id, postfach_id)
        if not darf_senden(z, nutzer):
            raise KeinZugriff(f"Aus {z['absender_email']} duerfen Sie nicht senden.")
        return z
    alle = _zeilen(db, tenant_id)
    if not alle:
        return None
    erlaubt = [z for z in alle if darf_senden(z, nutzer)]
    for z in erlaubt:
        if verwendung and verwendung in (z["verwendungen"] or []):
            return z
    for z in erlaubt:
        if z["ist_standard"]:
            return z
    raise KeinZugriff(
        "Kein freigegebenes Postfach fuer diesen Versand"
        + (f" (Verwendung: {verwendung})" if verwendung else "")
        + ". Bitte ein Standard-Postfach festlegen oder eines freigeben."
    )


# ── Schreiben ─────────────────────────────────────────────────────────────────
def _text(daten: dict[str, Any], schluessel: str) -> Optional[str]:
    wert = daten.get(schluessel)
    wert = str(wert).strip() if wert is not None else ""
    return wert or None


def _liste(wert: Any) -> list[str]:
    if wert is None:
        return []
    teile: Iterable[Any] = wert if isinstance(wert, (list, tuple)) else str(wert).split(",")
    return sorted({str(t).strip() for t in teile if str(t).strip()})


def speichern(db: Session, tenant_id: str, daten: dict[str, Any], *, postfach_id: Optional[str] = None,
              von: Optional[str] = None) -> dict[str, Any]:
    """Legt ein Postfach an (ohne ``postfach_id``) oder aendert es. Leeres Passwort = unveraendert."""
    kennung = (_text(daten, "kennung") or "").lower()
    if not _KENNUNG.match(kennung):
        raise MailkontoFehler("Kennung fehlt oder enthaelt unzulaessige Zeichen (a-z, 0-9, . _ -).")
    anbieter = (_text(daten, "anbieter") or "smtp").lower()
    if anbieter not in VORLAGEN:
        raise MailkontoFehler(f"Unbekannter Anbieter: {anbieter}")
    absender = _text(daten, "absender_email")
    if not absender or "@" not in absender:
        raise MailkontoFehler("Absender-Adresse fehlt oder ist ungueltig.")
    verwendungen = _liste(daten.get("verwendungen"))
    unbekannt = [v for v in verwendungen if v not in VERWENDUNGEN]
    if unbekannt:
        raise MailkontoFehler(f"Unbekannte Verwendung: {', '.join(unbekannt)}")

    bisher = _zeile(db, tenant_id, postfach_id) if postfach_id else None
    werte: dict[str, Any] = {
        "t": tenant_id, "kennung": kennung, "bez": _text(daten, "bezeichnung"), "anbieter": anbieter,
        "absender": absender, "name": _text(daten, "absender_name"),
        "standard": bool(daten.get("ist_standard")), "verwendungen": verwendungen,
        "rollen": _liste(daten.get("rollen")), "freigabe": _liste(daten.get("benutzer_freigabe")),
        "persoenlich": _text(daten, "persoenlich_fuer"), "von": von,
    }

    if anbieter == "alias":
        quelle_id = _text(daten, "zugang_von")
        if not quelle_id:
            raise MailkontoFehler("Ein Alias braucht das Postfach, dessen Anmeldung er nutzt.")
        quelle = _zeile(db, tenant_id, quelle_id)
        if quelle["anbieter"] == "alias":
            raise MailkontoFehler("Ein Alias kann nicht die Anmeldung eines anderen Alias nutzen.")
        if bisher and quelle["id"] == bisher["id"]:
            raise MailkontoFehler("Ein Postfach kann nicht seine eigene Anmeldung als Alias nutzen.")
        if _text(daten, "passwort"):
            raise MailkontoFehler("Ein Alias hat kein eigenes Passwort; er nutzt das des gewaehlten Postfachs.")
        werte.update({"anmeldung": "alias", "host": None, "port": None, "sicherheit": "starttls",
                      "benutzer": None, "geheimnis": None, "zugang_von": quelle["id"]})
    else:
        anmeldung = (_text(daten, "anmeldung") or ("oauth2" if anbieter == "microsoft" else "passwort")).lower()
        if anmeldung not in ("passwort", "oauth2"):
            raise MailkontoFehler(f"Unbekannte Anmeldung: {anmeldung}")
        if anmeldung == "oauth2" and anbieter not in OAUTH:
            raise MailkontoFehler("Die Anmeldung per OAuth gibt es fuer Google und Microsoft 365.")
        if anbieter == "microsoft" and anmeldung != "oauth2":
            raise MailkontoFehler("Microsoft 365 nur mit Anmeldung ueber Microsoft (kein Passwort-SMTP).")
        vorlage = VORLAGEN[anbieter]
        host = vorlage.get("smtp_host") or _text(daten, "smtp_host")
        if not host:
            raise MailkontoFehler("SMTP-Server fehlt.")
        try:
            port = int(vorlage.get("smtp_port") or daten.get("smtp_port") or 587)
        except (TypeError, ValueError) as fehler:
            raise MailkontoFehler("SMTP-Port ist keine Zahl.") from fehler
        if not 1 <= port <= 65535:
            raise MailkontoFehler("SMTP-Port ausserhalb 1-65535.")
        sicherheit = vorlage.get("sicherheit") or (_text(daten, "sicherheit") or ("ssl" if port == 465 else "starttls"))
        if sicherheit not in ("starttls", "ssl"):
            raise MailkontoFehler("Verbindungssicherheit muss STARTTLS oder SSL sein.")
        neues = _text(daten, "passwort")
        if neues and anmeldung == "oauth2":
            raise MailkontoFehler("Bei der Google-Anmeldung wird kein Passwort eingetragen.")
        chiffrat = geheimnis.verschluesseln(neues, tenant_id=tenant_id, zweck=ZWECK) if neues else None
        # Wechseln Anbieter oder Anmeldeart, gilt das alte Geheimnis nicht mehr.
        if bisher and not chiffrat and bisher["anmeldung"] == anmeldung and bisher["anbieter"] == anbieter:
            chiffrat = bisher["geheimnis"]
        werte.update({
            "anmeldung": anmeldung, "host": host, "port": port, "sicherheit": sicherheit,
            "benutzer": _text(daten, "benutzer") or (absender if anbieter in ("ionos", "google") else None),
            "geheimnis": chiffrat, "zugang_von": None,
        })

    if werte["standard"]:
        db.execute(text(
            "UPDATE domain_shared.mailkonten SET ist_standard = FALSE WHERE tenant_id = :t AND aktiv AND id <> :id"
        ), {"t": tenant_id, "id": postfach_id or ""})
    try:
        if bisher:
            db.execute(text(
                "UPDATE domain_shared.mailkonten SET kennung = :kennung, bezeichnung = :bez, anbieter = :anbieter, "
                "anmeldung = :anmeldung, smtp_host = :host, smtp_port = :port, sicherheit = :sicherheit, "
                "benutzer = :benutzer, absender_email = :absender, absender_name = :name, geheimnis = :geheimnis, "
                "zugang_von = :zugang_von, ist_standard = :standard, verwendungen = :verwendungen, rollen = :rollen, "
                "benutzer_freigabe = :freigabe, persoenlich_fuer = :persoenlich, status = 'neu', geprueft_am = NULL, "
                "letzter_fehler = NULL, updated_at = NOW(), geaendert_von = :von WHERE id = :id"
            ), {**werte, "id": bisher["id"]})
            neue_id = bisher["id"]
        else:
            neue_id = str(uuid.uuid4())
            db.execute(text(
                "INSERT INTO domain_shared.mailkonten (id, tenant_id, kennung, bezeichnung, anbieter, anmeldung, "
                "smtp_host, smtp_port, sicherheit, benutzer, absender_email, absender_name, geheimnis, zugang_von, "
                "ist_standard, verwendungen, rollen, benutzer_freigabe, persoenlich_fuer, geaendert_von) "
                "VALUES (:id, :t, :kennung, :bez, :anbieter, :anmeldung, :host, :port, :sicherheit, :benutzer, "
                ":absender, :name, :geheimnis, :zugang_von, :standard, :verwendungen, :rollen, :freigabe, "
                ":persoenlich, :von)"
            ), {**werte, "id": neue_id})
        db.commit()
    except Exception as fehler:
        db.rollback()
        if "ux_mailkonto_kennung" in str(fehler):
            raise MailkontoFehler(f"Die Kennung {kennung} ist schon vergeben.") from fehler
        raise
    return lesen(db, tenant_id, neue_id)


def entfernen(db: Session, tenant_id: str, postfach_id: str) -> None:
    z = _zeile(db, tenant_id, postfach_id)
    abhaengig = db.execute(text(
        "SELECT kennung FROM domain_shared.mailkonten WHERE tenant_id = :t AND aktiv AND zugang_von = :id"
    ), {"t": tenant_id, "id": z["id"]}).scalars().all()
    if abhaengig:
        raise MailkontoFehler(f"Die Aliase {', '.join(abhaengig)} nutzen die Anmeldung dieses Postfachs.")
    db.execute(text(
        "UPDATE domain_shared.mailkonten SET aktiv = FALSE, ist_standard = FALSE, updated_at = NOW() WHERE id = :id"
    ), {"id": z["id"]})
    db.commit()


# ── Versand ───────────────────────────────────────────────────────────────────
def smtp_zugang(db: Session, tenant_id: str, *, verwendung: Optional[str] = None,
                nutzer: Optional[dict[str, Any]] = None,
                postfach_id: Optional[str] = None) -> Optional[SmtpZugang]:
    """Der Zugang fuer einen Versand, oder ``None``, wenn der Mandant kein Postfach fuehrt."""
    z = postfach_waehlen(db, tenant_id, verwendung=verwendung, nutzer=nutzer, postfach_id=postfach_id)
    if z is None:
        return None
    anmeldung = _zeile(db, tenant_id, z["zugang_von"]) if z["anbieter"] == "alias" else z
    if not anmeldung["geheimnis"]:
        raise MailkontoFehler(f"Postfach {anmeldung['kennung']} ohne Passwort bzw. Anmeldung beim Anbieter.")
    klar = geheimnis.entschluesseln(anmeldung["geheimnis"], tenant_id=tenant_id, zweck=ZWECK)
    oauth = _zugriffstoken(anmeldung["anbieter"], klar) if anmeldung["anmeldung"] == "oauth2" else None
    return SmtpZugang(
        server=anmeldung["smtp_host"], port=anmeldung["smtp_port"], sicherheit=anmeldung["sicherheit"],
        benutzer=anmeldung["benutzer"], passwort=None if oauth else klar,
        absender=z["absender_email"], absender_name=z["absender_name"], oauth_token=oauth, postfach_id=z["id"],
        transport="graph" if anmeldung["anbieter"] == "microsoft" else "smtp",
    )


def pruefen(db: Session, tenant_id: str, postfach_id: str, empfaenger: Optional[str],
            nutzer: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    """Sendet eine Testmail ueber das Postfach und haelt das Ergebnis fest."""
    from app.services.mail_versand import MailVersandFehler, sende_mail

    z = _zeile(db, tenant_id, postfach_id)
    ziel = (empfaenger or "").strip() or z["absender_email"]
    try:
        sende_mail(ziel, "Testnachricht aus VALEO NeuroERP",
                   f"Diese Nachricht bestaetigt, dass der Versand ueber {z['absender_email']} funktioniert.",
                   db=db, tenant_id=tenant_id, nutzer=nutzer, postfach_id=z["id"])
    except (MailVersandFehler, MailkontoFehler, geheimnis.GeheimnisUngueltig) as fehler:
        db.execute(text(
            "UPDATE domain_shared.mailkonten SET status = 'fehler', letzter_fehler = :f, updated_at = NOW() "
            "WHERE id = :id"
        ), {"f": str(fehler)[:1000], "id": z["id"]})
        db.commit()
        raise
    db.execute(text(
        "UPDATE domain_shared.mailkonten SET status = 'geprueft', geprueft_am = NOW(), letzter_fehler = NULL, "
        "updated_at = NOW() WHERE id = :id"
    ), {"id": z["id"]})
    db.commit()
    return {**lesen(db, tenant_id, z["id"]), "testmail_an": ziel}


# ── Anmeldung beim Anbieter (Google, Microsoft) ───────────────────────────────
def _client(anbieter: str) -> tuple[str, str, str]:
    konf = OAUTH[anbieter]
    praefix = konf["praefix"]
    client_id = (os.getenv(f"{praefix}_CLIENT_ID") or "").strip()
    client_secret = (os.getenv(f"{praefix}_CLIENT_SECRET") or "").strip()
    redirect = (os.getenv(f"{praefix}_REDIRECT_URI") or "").strip()
    if not (client_id and client_secret and redirect):
        alternative = " Alternativ ein App-Passwort verwenden." if anbieter == "google" else ""
        raise MailkontoFehler(
            f"Die Anmeldung ueber {konf['name']} ist auf dieser Plattform nicht eingerichtet "
            f"({praefix}_CLIENT_ID/_SECRET/_REDIRECT_URI).{alternative}"
        )
    return client_id, client_secret, redirect


def _url(anbieter: str, schluessel: str) -> str:
    tenant = (os.getenv("MICROSOFT_OAUTH_TENANT") or "organizations").strip()
    return OAUTH[anbieter][schluessel].replace("{tenant}", tenant)


def _state(tenant_id: str, postfach_id: str, anbieter: str) -> str:
    inhalt = base64.urlsafe_b64encode(json.dumps({
        "t": tenant_id, "p": postfach_id, "a": anbieter, "n": secrets.token_urlsafe(12),
        "e": int(time.time()) + STATE_GUELTIG_SEKUNDEN,
    }).encode("utf-8")).decode("ascii")
    return f"{inhalt}.{geheimnis.signieren(inhalt)}"


def _state_pruefen(state: str, tenant_id: str) -> tuple[str, str]:
    inhalt, _, signatur = (state or "").partition(".")
    if not inhalt or not geheimnis.signatur_gueltig(inhalt, signatur):
        raise MailkontoFehler("Ungueltige Rueckmeldung des Anbieters (Signatur).")
    daten = json.loads(base64.urlsafe_b64decode(inhalt.encode("ascii")))
    if daten.get("t") != tenant_id:
        raise MailkontoFehler("Die Anmeldung gehoert zu einem anderen Mandanten.")
    if int(daten.get("e") or 0) < time.time():
        raise MailkontoFehler("Die Anmeldung ist abgelaufen; bitte erneut starten.")
    return str(daten.get("p") or ""), str(daten.get("a") or "google")


def anmeldung_starten(db: Session, tenant_id: str, postfach_id: str) -> dict[str, str]:
    """URL der Anmeldeseite des Anbieters (Google oder Microsoft) fuer dieses Postfach."""
    z = _zeile(db, tenant_id, postfach_id)
    if z["anbieter"] not in OAUTH or z["anmeldung"] != "oauth2":
        raise MailkontoFehler("Zuerst das Postfach mit Google oder Microsoft 365 und Anmeldung beim Anbieter speichern.")
    client_id, _, redirect = _client(z["anbieter"])
    parameter = {
        "client_id": client_id, "redirect_uri": redirect, "response_type": "code",
        "scope": OAUTH[z["anbieter"]]["scopes"], "state": _state(tenant_id, z["id"], z["anbieter"]),
        "login_hint": z["absender_email"], **OAUTH[z["anbieter"]]["extra"],
    }
    return {"url": f"{_url(z['anbieter'], 'auth_url')}?{urlencode(parameter)}"}


def _token_anfrage(anbieter: str, daten: dict[str, str]) -> dict[str, Any]:
    name = OAUTH[anbieter]["name"]
    try:
        antwort = httpx.post(_url(anbieter, "token_url"), data=daten, timeout=20)
    except httpx.HTTPError as fehler:
        raise MailkontoFehler(f"{name} nicht erreichbar: {fehler}") from fehler
    if antwort.status_code != 200:
        raise MailkontoFehler(f"{name} lehnte ab: {antwort.text[:300]}")
    return antwort.json()


def _email_aus_id_token(id_token: str) -> Optional[str]:
    # Direkt vom Token-Endpunkt ueber TLS erhalten; die Nutzlast genuegt fuer die Adresse.
    try:
        nutzlast = id_token.split(".")[1]
        nutzlast += "=" * (-len(nutzlast) % 4)
        daten = json.loads(base64.urlsafe_b64decode(nutzlast))
        return daten.get("email") or daten.get("preferred_username")
    except (IndexError, ValueError):
        return None


def anmeldung_abschliessen(db: Session, tenant_id: str, code: str, state: str,
                           von: Optional[str] = None) -> dict[str, Any]:
    postfach_id, anbieter = _state_pruefen(state, tenant_id)
    z = _zeile(db, tenant_id, postfach_id)
    if z["anbieter"] != anbieter or anbieter not in OAUTH:
        raise MailkontoFehler("Das Postfach passt nicht zur Anmeldung.")
    client_id, client_secret, redirect = _client(anbieter)
    daten = {"code": code, "client_id": client_id, "client_secret": client_secret,
             "redirect_uri": redirect, "grant_type": "authorization_code"}
    if anbieter == "microsoft":
        daten["scope"] = OAUTH[anbieter]["scopes"]
    token = _token_anfrage(anbieter, daten)
    refresh = token.get("refresh_token")
    if not refresh:
        raise MailkontoFehler(f"{OAUTH[anbieter]['name']} hat keinen dauerhaften Zugang erteilt (kein Refresh-Token).")
    email = _email_aus_id_token(token.get("id_token") or "") or z["benutzer"]
    db.execute(text(
        "UPDATE domain_shared.mailkonten SET anmeldung = 'oauth2', benutzer = :b, geheimnis = :g, "
        "status = 'neu', letzter_fehler = NULL, updated_at = NOW(), geaendert_von = :von WHERE id = :id"
    ), {"b": email, "g": geheimnis.verschluesseln(refresh, tenant_id=tenant_id, zweck=ZWECK),
        "von": von, "id": z["id"]})
    db.commit()
    return lesen(db, tenant_id, z["id"])


def _zugriffstoken(anbieter: str, refresh_token: str) -> str:
    client_id, client_secret, _ = _client(anbieter)
    daten = {"client_id": client_id, "client_secret": client_secret,
             "refresh_token": refresh_token, "grant_type": "refresh_token"}
    if anbieter == "microsoft":
        daten["scope"] = OAUTH[anbieter]["scopes"]
    zugriff = _token_anfrage(anbieter, daten).get("access_token")
    if not zugriff:
        raise MailkontoFehler(f"{OAUTH[anbieter]['name']} lieferte kein Zugriffstoken.")
    return zugriff


# Bisherige Namen (Google) bleiben fuer Aufrufer erhalten.
google_anmeldung_starten = anmeldung_starten
google_anmeldung_abschliessen = anmeldung_abschliessen
