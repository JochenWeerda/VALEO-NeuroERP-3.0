"""E-Mail-Versand ueber SMTP — wirklich, oder mit klarer Absage.

Bis zum 08.10.2026 gab es im System keinen Weg, der eine E-Mail tatsaechlich
verschickte: ``ProductionEmailService.send_email`` protokollierte und meldete
``True``, der Newsletter meldete ``in_queue`` ohne Warteschlange, die
Bestellkommunikation ``status: "sent"``. Jeder dieser Erfolge war erfunden.

Hier gilt: Versendet wird ueber den konfigurierten SMTP-Server
(``EMAIL_SMTP_SERVER``/``EMAIL_SMTP_PORT``/``EMAIL_USERNAME``/``EMAIL_PASSWORD``,
Absender ``EMAIL_FROM`` oder der Benutzername). Fehlt die Einrichtung, wirft
:func:`sende_mail` :class:`MailVersandNichtEingerichtet`; scheitert der Server,
:class:`MailVersandFehler`. Ein Erfolg wird nur gemeldet, wenn der Server die
Nachricht angenommen hat.
"""

from __future__ import annotations

import smtplib
from dataclasses import dataclass
from email.message import EmailMessage
from email.utils import make_msgid

from app.core.config import settings


class MailVersandNichtEingerichtet(RuntimeError):
    """Kein SMTP-Server konfiguriert; es wird nichts versendet."""


class MailVersandFehler(RuntimeError):
    """Der SMTP-Server hat die Nachricht nicht angenommen."""


@dataclass(frozen=True)
class SmtpEinrichtung:
    server: str
    port: int
    benutzer: str | None
    passwort: str | None
    absender: str


def einrichtung() -> SmtpEinrichtung:
    server = (settings.EMAIL_SMTP_SERVER or "").strip()
    benutzer = (settings.EMAIL_USERNAME or "").strip() or None
    absender = (settings.EMAIL_FROM or "").strip() or benutzer
    if not server or not absender:
        raise MailVersandNichtEingerichtet(
            "E-Mail-Versand ist nicht eingerichtet (EMAIL_SMTP_SERVER und Absender fehlen)."
        )
    return SmtpEinrichtung(
        server=server,
        port=int(settings.EMAIL_SMTP_PORT or 587),
        benutzer=benutzer,
        passwort=settings.EMAIL_PASSWORD or None,
        absender=absender,
    )


def sende_mail(empfaenger: str, betreff: str, text: str, *, html: str | None = None) -> str:
    """Versendet eine Nachricht und liefert ihre Message-ID; wirft bei jedem Scheitern."""
    if not empfaenger or "@" not in empfaenger:
        raise MailVersandFehler(f"Ungueltige Empfaengeradresse: {empfaenger!r}")
    e = einrichtung()
    nachricht = EmailMessage()
    nachricht["From"] = e.absender
    nachricht["To"] = empfaenger
    nachricht["Subject"] = betreff
    nachricht["Message-ID"] = make_msgid(domain=e.absender.split("@")[-1])
    nachricht.set_content(text or "")
    if html:
        nachricht.add_alternative(html, subtype="html")
    try:
        if e.port == 465:
            verbindung: smtplib.SMTP = smtplib.SMTP_SSL(e.server, e.port, timeout=20)
        else:
            verbindung = smtplib.SMTP(e.server, e.port, timeout=20)
        with verbindung:
            if e.port != 465:
                verbindung.ehlo()
                if verbindung.has_extn("starttls"):
                    verbindung.starttls()
                    verbindung.ehlo()
            if e.benutzer and e.passwort:
                verbindung.login(e.benutzer, e.passwort)
            abgelehnt = verbindung.send_message(nachricht)
    except (smtplib.SMTPException, OSError) as fehler:
        raise MailVersandFehler(f"SMTP-Versand an {empfaenger} gescheitert: {fehler}") from fehler
    if abgelehnt:
        raise MailVersandFehler(f"SMTP-Server lehnte {empfaenger} ab: {abgelehnt}")
    return str(nachricht["Message-ID"])
