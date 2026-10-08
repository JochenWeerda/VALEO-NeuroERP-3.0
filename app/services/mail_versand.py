"""E-Mail-Versand ueber SMTP — wirklich, oder mit klarer Absage.

Bis zum 08.10.2026 gab es im System keinen Weg, der eine E-Mail tatsaechlich
verschickte: ``ProductionEmailService.send_email`` protokollierte und meldete
``True``, der Newsletter meldete ``in_queue`` ohne Warteschlange, die
Bestellkommunikation ``status: "sent"``. Jeder dieser Erfolge war erfunden.

Welches Konto:

1. Ein **Postfach des Mandanten** (:mod:`app.services.mailkonto_service`; IONOS,
   Google mit App-Passwort oder Google-Anmeldung, allgemeines SMTP, Alias), wenn der
   Aufrufer ``db`` und ``tenant_id`` mitgibt und der Mandant Postfaecher fuehrt —
   gewaehlt nach ``postfach_id`` > ``verwendung`` > Standard, nur unter den
   Postfaechern, aus denen ``nutzer`` senden darf.
2. Sonst das **Plattformkonto** aus ``EMAIL_SMTP_*``/``EMAIL_FROM`` (Installationen
   mit einem Mandanten).
3. Sonst :class:`MailVersandNichtEingerichtet`.

Zugangsdaten gehen nie unverschluesselt ueber die Leitung: SSL (Port 465) oder
STARTTLS; bietet der Server kein STARTTLS, wird nicht angemeldet und nichts gesendet.
Microsoft-365-Postfaecher senden ueber Microsoft Graph (``sendMail``, HTTPS); Erfolg
heisst dort: Graph hat mit 202 angenommen.
Ein Erfolg wird nur gemeldet, wenn der Server die Nachricht angenommen hat.
"""

from __future__ import annotations

import smtplib
from dataclasses import dataclass
from email.message import EmailMessage
from email.utils import formataddr, make_msgid
from typing import Any, Optional

from app.core.config import settings


class MailVersandNichtEingerichtet(RuntimeError):
    """Kein SMTP-Zugang (weder Mandant noch Plattform); es wird nichts versendet."""


class MailVersandFehler(RuntimeError):
    """Der SMTP-Server hat die Nachricht nicht angenommen."""


class MailVersandVerweigert(MailVersandFehler):
    """Der Nutzer darf aus dem gewaehlten Postfach nicht senden (bzw. aus keinem passenden)."""


@dataclass(frozen=True)
class SmtpEinrichtung:
    server: str
    port: int
    benutzer: str | None
    passwort: str | None
    absender: str
    sicherheit: str = "starttls"
    absender_name: str | None = None
    oauth_token: str | None = None
    transport: str = "smtp"


def einrichtung() -> SmtpEinrichtung:
    """Das Plattformkonto aus den Umgebungsvariablen."""
    server = (settings.EMAIL_SMTP_SERVER or "").strip()
    benutzer = (settings.EMAIL_USERNAME or "").strip() or None
    absender = (settings.EMAIL_FROM or "").strip() or benutzer
    if not server or not absender:
        raise MailVersandNichtEingerichtet(
            "E-Mail-Versand ist nicht eingerichtet: kein Mailkonto des Mandanten und kein Plattformkonto "
            "(EMAIL_SMTP_SERVER und Absender)."
        )
    port = int(settings.EMAIL_SMTP_PORT or 587)
    return SmtpEinrichtung(
        server=server,
        port=port,
        benutzer=benutzer,
        passwort=settings.EMAIL_PASSWORD or None,
        absender=absender,
        sicherheit="ssl" if port == 465 else "starttls",
    )


def zugang(db: Any, tenant_id: Optional[str], *, verwendung: Optional[str] = None,
           nutzer: Optional[dict] = None, postfach_id: Optional[str] = None) -> SmtpEinrichtung:
    """Der Zugang fuer diesen Mandanten (eigenes Konto vor Plattformkonto); wirft, wenn keiner da ist."""
    if db is not None and tenant_id:
        from app.core.geheimnis import GeheimnisNichtEingerichtet, GeheimnisUngueltig
        from app.services.mailkonto_service import KeinZugriff, MailkontoFehler, smtp_zugang

        try:
            z = smtp_zugang(db, tenant_id, verwendung=verwendung, nutzer=nutzer, postfach_id=postfach_id)
        except KeinZugriff as fehler:
            raise MailVersandVerweigert(str(fehler)) from fehler
        except (MailkontoFehler, GeheimnisUngueltig, GeheimnisNichtEingerichtet) as fehler:
            raise MailVersandFehler(f"Postfach des Mandanten nicht nutzbar: {fehler}") from fehler
        if z is not None:
            return SmtpEinrichtung(
                server=z.server, port=z.port, benutzer=z.benutzer, passwort=z.passwort, absender=z.absender,
                sicherheit=z.sicherheit, absender_name=z.absender_name, oauth_token=z.oauth_token,
                transport=z.transport,
            )
    return einrichtung()


def sende_mail(
    empfaenger: str,
    betreff: str,
    text: str,
    *,
    html: str | None = None,
    db: Any = None,
    tenant_id: Optional[str] = None,
    verwendung: Optional[str] = None,
    nutzer: Optional[dict] = None,
    postfach_id: Optional[str] = None,
) -> str:
    """Versendet eine Nachricht und liefert ihre Message-ID; wirft bei jedem Scheitern."""
    if not empfaenger or "@" not in empfaenger:
        raise MailVersandFehler(f"Ungueltige Empfaengeradresse: {empfaenger!r}")
    e = zugang(db, tenant_id, verwendung=verwendung, nutzer=nutzer, postfach_id=postfach_id)
    if e.transport == "graph":
        return _sende_ueber_graph(e, empfaenger, betreff, text, html)
    nachricht = EmailMessage()
    nachricht["From"] = formataddr((e.absender_name, e.absender)) if e.absender_name else e.absender
    nachricht["To"] = empfaenger
    nachricht["Subject"] = betreff
    nachricht["Message-ID"] = make_msgid(domain=e.absender.split("@")[-1])
    nachricht.set_content(text or "")
    if html:
        nachricht.add_alternative(html, subtype="html")
    anmelden = bool(e.oauth_token or (e.benutzer and e.passwort))
    try:
        if e.sicherheit == "ssl":
            verbindung: smtplib.SMTP = smtplib.SMTP_SSL(e.server, e.port, timeout=20)
        else:
            verbindung = smtplib.SMTP(e.server, e.port, timeout=20)
        with verbindung:
            if e.sicherheit != "ssl":
                verbindung.ehlo()
                if verbindung.has_extn("starttls"):
                    verbindung.starttls()
                    verbindung.ehlo()
                elif anmelden:
                    raise MailVersandFehler(
                        f"{e.server} bietet kein STARTTLS; Zugangsdaten werden nicht unverschluesselt gesendet."
                    )
            if e.oauth_token:
                anmeldung = f"user={e.benutzer}\x01auth=Bearer {e.oauth_token}\x01\x01"
                verbindung.auth("XOAUTH2", lambda _herausforderung=None: anmeldung)
            elif e.benutzer and e.passwort:
                verbindung.login(e.benutzer, e.passwort)
            abgelehnt = verbindung.send_message(nachricht)
    except (smtplib.SMTPException, OSError) as fehler:
        raise MailVersandFehler(f"SMTP-Versand an {empfaenger} gescheitert: {fehler}") from fehler
    if abgelehnt:
        raise MailVersandFehler(f"SMTP-Server lehnte {empfaenger} ab: {abgelehnt}")
    return str(nachricht["Message-ID"])


def _sende_ueber_graph(e: SmtpEinrichtung, empfaenger: str, betreff: str, text: str, html: str | None) -> str:
    """Microsoft 365: ``POST /me/sendMail``. Ein abweichender Absender (Alias) braucht in
    Exchange "Senden als" fuer das angemeldete Postfach, sonst lehnt Graph ab."""
    import uuid

    import httpx

    from app.services.mailkonto_service import GRAPH_SENDMAIL_URL

    nachricht: dict[str, Any] = {
        "subject": betreff,
        "body": {"contentType": "HTML", "content": html} if html else {"contentType": "Text", "content": text or ""},
        "toRecipients": [{"emailAddress": {"address": empfaenger}}],
    }
    if e.benutzer and e.absender.lower() != e.benutzer.lower():
        nachricht["from"] = {"emailAddress": {"address": e.absender, "name": e.absender_name or e.absender}}
    try:
        antwort = httpx.post(
            GRAPH_SENDMAIL_URL,
            json={"message": nachricht, "saveToSentItems": True},
            headers={"Authorization": f"Bearer {e.oauth_token}"},
            timeout=20,
        )
    except httpx.HTTPError as fehler:
        raise MailVersandFehler(f"Microsoft Graph nicht erreichbar: {fehler}") from fehler
    if antwort.status_code != 202:
        raise MailVersandFehler(f"Microsoft Graph lehnte den Versand an {empfaenger} ab: {antwort.text[:300]}")
    # Graph liefert fuer sendMail keine Nachrichten-ID; eine eigene macht den Versand nachvollziehbar.
    return f"<{uuid.uuid4()}@graph.valeo>"
