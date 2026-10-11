"""
Einkauf Versand-Service

Versendet Bestellungen, Anfragen und Auftragsbestätigungen via:
  - E-Mail (SMTP mit HTML-Template + PDF-Anhang)
  - Fax (Twilio-Fax oder Stub)
  - EDI (EDIFACT ORDERS D97A)
  - Post/Manuell (nur Status-Update)

Alle Methoden geben einen VersandResult-Dict zurück:
  {
    "status": "gesendet" | "fehler" | "nicht_eingerichtet" | "manuell",
    "versand_art": "email" | "fax" | "edi" | "post",
    "empfaenger": str,
    "zeitstempel": ISO-Datetime,
    "fehler": str | None,
  }

Seit 08.10.2026:

* E-Mail geht ueber das Einkaufs-Postfach des Mandanten (``mail_versand``,
  Verwendung ``einkauf``). Vorher sendete dieser Dienst ohne ``SMTP_HOST`` nichts,
  protokollierte "DEV-MODE simuliert" und meldete ``gesendet`` — die Bestellung
  stand auf "versandt", obwohl der Lieferant nie etwas bekam.
* Fax und EDI ohne Einrichtung melden ``nicht_eingerichtet`` statt ``manuell``;
  die Bestellung bleibt unversandt. ``manuell`` gibt es nur fuer die bewusst
  gewaehlte Versandart Post.
* Jeder Versand steht in ``domain_einkauf.bestellung_kommunikation`` (Reiter
  Kommunikation der Bestellmaske).
"""
from __future__ import annotations

import os
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.infrastructure.models.einkauf_models import (
    EinkaufBestellung,
    EinkaufLieferant,
)


# ─────────────────────────────────────────────────────────────────────────────
# Config (aus Umgebungsvariablen)
# ─────────────────────────────────────────────────────────────────────────────


_TWILIO_SID    = os.getenv("TWILIO_ACCOUNT_SID", "")
_TWILIO_TOKEN  = os.getenv("TWILIO_AUTH_TOKEN", "")
_TWILIO_FAX    = os.getenv("TWILIO_FAX_FROM", "+49")

_EDI_SFTP_HOST = os.getenv("EDI_SFTP_HOST", "")
_EDI_SFTP_USER = os.getenv("EDI_SFTP_USER", "")
_EDI_SFTP_KEY  = os.getenv("EDI_SFTP_KEY", "")
_EDI_SFTP_PATH = os.getenv("EDI_SFTP_PATH", "/orders/in/")

_VALEO_SENDER_NAME = os.getenv("VALEO_SENDER_NAME", "VALEO NeuroERP")
_VALEO_SENDER_ID   = os.getenv("VALEO_EDI_SENDER_ID", "4260000000001")  # GLN


# ─────────────────────────────────────────────────────────────────────────────
# E-Mail-Versand
# ─────────────────────────────────────────────────────────────────────────────

def _render_bestellung_html(bestellung: EinkaufBestellung) -> str:
    """Einfaches HTML-Template für Bestellungs-E-Mail."""
    positionen_html = "".join(
        f"<tr><td>{p.pos_nr}</td><td>{p.artikel_nr}</td><td>{p.artikel_bezeichnung}</td>"
        f"<td style='text-align:right'>{float(p.menge):,.3f}</td><td>{p.einheit}</td>"
        f"<td style='text-align:right'>{float(p.einzelpreis or 0):,.4f}</td>"
        f"<td style='text-align:right'>{p.preis_einheit}</td>"
        f"<td style='text-align:right'>{float(p.netto_betrag or 0):,.2f} €</td></tr>"
        for p in bestellung.positionen
    )

    lf = bestellung.lieferant
    return f"""
<!DOCTYPE html>
<html lang="de">
<head><meta charset="UTF-8">
<style>
  body {{ font-family: Arial, sans-serif; font-size: 12pt; color: #333; }}
  table {{ border-collapse: collapse; width: 100%; margin: 16px 0; }}
  th, td {{ border: 1px solid #ccc; padding: 4px 8px; }}
  th {{ background: #f0f0f0; text-align: left; }}
  .header {{ background: #003366; color: white; padding: 16px; }}
  .footer {{ font-size: 9pt; color: #888; margin-top: 24px; border-top: 1px solid #ccc; padding-top: 8px; }}
</style>
</head>
<body>
<div class="header">
  <h2 style="margin:0; color:white">BESTELLUNG {bestellung.bestellnummer}</h2>
  <span>Datum: {bestellung.bestelldatum.strftime('%d.%m.%Y') if bestellung.bestelldatum else ''}</span>
</div>

<p>Sehr geehrte Damen und Herren,</p>
<p>wir bestellen hiermit wie folgt:</p>

<table>
  <thead>
    <tr>
      <th>Pos</th><th>Art.-Nr.</th><th>Bezeichnung</th>
      <th>Menge</th><th>Einheit</th><th>Einzelpreis</th><th>PE</th><th>Betrag</th>
    </tr>
  </thead>
  <tbody>
    {positionen_html}
  </tbody>
  <tfoot>
    <tr>
      <td colspan="7" style="text-align:right"><strong>Netto-Summe:</strong></td>
      <td style="text-align:right"><strong>{float(bestellung.netto_summe or 0):,.2f} €</strong></td>
    </tr>
  </tfoot>
</table>

{'<p><strong>Gewünschtes Lieferdatum:</strong> ' + bestellung.lieferdatum_wunsch.strftime('%d.%m.%Y') + '</p>' if bestellung.lieferdatum_wunsch else ''}
{'<p>' + bestellung.freitext_fuss + '</p>' if bestellung.freitext_fuss else ''}

<p>Bitte bestätigen Sie diese Bestellung per E-Mail oder Fax.<br>
Bei Rückfragen stehen wir Ihnen gern zur Verfügung.</p>

<p>Mit freundlichen Grüßen<br>
<strong>{_VALEO_SENDER_NAME}</strong></p>

<div class="footer">
  Bestellnummer: {bestellung.bestellnummer} |
  Unsere Referenz: {bestellung.unsere_referenz or '—'} |
  Ihre Referenz: {bestellung.ihre_referenz or '—'}
</div>
</body>
</html>
"""


def versende_email(
    db: Session,
    bestellung: EinkaufBestellung,
    *,
    empfaenger_override: str | None = None,
    anhang_pdf: bytes | None = None,
    nutzer: dict | None = None,
) -> dict[str, Any]:
    """Versendet eine Bestellung ueber das Einkaufs-Postfach; ``gesendet`` erst nach Serverannahme."""
    from app.services.mail_versand import MailVersandFehler, MailVersandNichtEingerichtet, sende_mail

    lf = bestellung.lieferant or db.query(EinkaufLieferant).get(bestellung.lieferant_id)
    empfaenger = empfaenger_override or (lf.email_bestellung if lf else None) or (getattr(lf, "email", None) if lf else None)
    betreff = f"Bestellung {bestellung.bestellnummer}"
    ergebnis: dict[str, Any] = {"versand_art": "email", "empfaenger": empfaenger, "betreff": betreff,
                                "zeitstempel": datetime.now().isoformat(), "fehler": None}
    if not empfaenger:
        return {**ergebnis, "status": "fehler", "fehler": "Keine E-Mail-Adresse für Lieferant konfiguriert"}

    anhaenge = [(f"Bestellung_{bestellung.bestellnummer}.pdf", anhang_pdf, "application/pdf")] if anhang_pdf else None
    try:
        sende_mail(empfaenger, betreff, f"Bestellung {bestellung.bestellnummer} — Details im HTML-Teil.",
                   html=_render_bestellung_html(bestellung), db=db, tenant_id=str(bestellung.tenant_id),
                   verwendung="einkauf", nutzer=nutzer, anhaenge=anhaenge)
    except MailVersandNichtEingerichtet as fehler:
        return {**ergebnis, "status": "nicht_eingerichtet", "fehler": str(fehler)}
    except MailVersandFehler as fehler:
        return {**ergebnis, "status": "fehler", "fehler": str(fehler)}
    return {**ergebnis, "status": "gesendet"}


# ─────────────────────────────────────────────────────────────────────────────
# Fax-Versand (Twilio-Fax oder Stub)
# ─────────────────────────────────────────────────────────────────────────────

def versende_fax(
    db: Session,
    bestellung: EinkaufBestellung,
    *,
    faxnummer_override: str | None = None,
    pdf_content: bytes | None = None,
    pdf_url: str | None = None,
) -> dict[str, Any]:
    """
    Versendet eine Bestellung per Fax.
    Benötigt Twilio-Account-SID + Auth-Token + eine Fax-Nummer.
    Falls Twilio nicht konfiguriert → Stub-Modus (manuell).
    """
    lf = bestellung.lieferant or db.query(EinkaufLieferant).get(bestellung.lieferant_id)
    faxnummer = faxnummer_override or (lf.fax_bestellung if lf else None)

    if not faxnummer:
        return {
            "status": "fehler",
            "versand_art": "fax",
            "empfaenger": None,
            "zeitstempel": datetime.now().isoformat(),
            "fehler": "Keine Fax-Nummer für Lieferant konfiguriert",
        }

    if not _TWILIO_SID or not _TWILIO_TOKEN:
        # Kein Faxdienst: nichts versendet. Bis 08.10.2026 "manuell" — und die
        # Bestellung stand trotzdem auf "versandt".
        return {
            "status":      "nicht_eingerichtet",
            "versand_art": "fax",
            "empfaenger":  faxnummer,
            "zeitstempel": datetime.now().isoformat(),
            "fehler":      None,
            "hinweis":     "Twilio nicht konfiguriert — Fax muss manuell versendet werden",
        }

    try:
        from twilio.rest import Client  # type: ignore[import]
        client = Client(_TWILIO_SID, _TWILIO_TOKEN)

        fax = client.fax.v1.faxes.create(
            from_=_TWILIO_FAX,
            to=faxnummer,
            media_url=pdf_url or "",  # PDF-URL muss öffentlich zugänglich sein
        )
        return {
            "status":      "gesendet",
            "versand_art": "fax",
            "empfaenger":  faxnummer,
            "zeitstempel": datetime.now().isoformat(),
            "fehler":      None,
            "fax_sid":     fax.sid,
        }
    except ImportError:
        return {
            "status":      "nicht_eingerichtet",
            "versand_art": "fax",
            "empfaenger":  faxnummer,
            "zeitstempel": datetime.now().isoformat(),
            "fehler":      None,
            "hinweis":     "twilio-Paket nicht installiert — pip install twilio",
        }
    except Exception as e:
        return {
            "status":      "fehler",
            "versand_art": "fax",
            "empfaenger":  faxnummer,
            "zeitstempel": datetime.now().isoformat(),
            "fehler":      str(e),
        }


# ─────────────────────────────────────────────────────────────────────────────
# EDI-Versand (EDIFACT ORDERS D97A)
# ─────────────────────────────────────────────────────────────────────────────

def _generate_edifact_orders(bestellung: EinkaufBestellung, *, receiver_id: str) -> str:
    """
    Generiert eine EDIFACT ORDERS D97A Nachricht für die Bestellung.
    Vereinfachtes Format — für volle Kompatibilität muss das exakte
    Lieferanten-Format konfiguriert werden.
    """
    ts = datetime.now().strftime("%y%m%d:%H%M")
    datum = bestellung.bestelldatum.strftime("%y%m%d") if bestellung.bestelldatum else ""

    lines = [
        f"UNB+UNOC:3+{_VALEO_SENDER_ID}:14+{receiver_id}:14+{ts}+1++ORDERS'",
        f"UNH+1+ORDERS:D:97A:UN:EAN008'",
        f"BGM+220+{bestellung.bestellnummer}+9'",
        f"DTM+137:{datum}:102'",
    ]

    if bestellung.lieferdatum_wunsch:
        lf_datum = bestellung.lieferdatum_wunsch.strftime("%y%m%d")
        lines.append(f"DTM+2:{lf_datum}:102'")

    # Lieferant NAD
    if bestellung.lieferant:
        lf = bestellung.lieferant
        lines.append(f"NAD+SU+{lf.lieferantennummer}::92++{lf.firmenname}+{lf.strasse}+{lf.ort}++{lf.plz}+{lf.land}'")

    # Käufer NAD
    lines.append(f"NAD+BY+{_VALEO_SENDER_ID}::9++{_VALEO_SENDER_NAME}'")

    # Positionen
    for i, pos in enumerate(bestellung.positionen, start=1):
        # LIN-Segment
        lines.append(f"LIN+{pos.pos_nr}++'")
        # Artikel-Bezeichnung
        lines.append(f"IMD+F++:::{pos.artikel_bezeichnung[:35]}'")
        # Menge
        lines.append(f"QTY+21:{float(pos.menge):.3f}:{pos.einheit}'")
        # Preis
        if pos.einzelpreis:
            lines.append(f"PRI+AAA:{float(pos.einzelpreis):.4f}:CP'")

    # Summen
    if bestellung.netto_summe:
        lines.append(f"MOA+79:{float(bestellung.netto_summe):.2f}'")

    lines.append(f"UNS+S'")
    lines.append(f"CNT+2:{len(bestellung.positionen)}'")
    lines.append(f"UNT+{len(lines)+1}+1'")
    lines.append(f"UNZ+1+1'")

    return "\n".join(lines)


def versende_edi(
    db: Session,
    bestellung: EinkaufBestellung,
) -> dict[str, Any]:
    """
    Versendet eine Bestellung per EDI (EDIFACT ORDERS D97A).
    Überträgt die Datei per SFTP an den konfigurierten EDI-Server.
    """
    lf = bestellung.lieferant or db.query(EinkaufLieferant).get(bestellung.lieferant_id)

    if not lf or not lf.edi_kennung:
        return {
            "status": "fehler",
            "versand_art": "edi",
            "empfaenger": None,
            "zeitstempel": datetime.now().isoformat(),
            "fehler": "Kein EDI-Empfänger für Lieferant konfiguriert",
        }

    edifact_msg = _generate_edifact_orders(bestellung, receiver_id=lf.edi_kennung)
    dateiname = f"ORDERS_{bestellung.bestellnummer}_{datetime.now().strftime('%Y%m%d%H%M%S')}.edi"

    if not _EDI_SFTP_HOST:
        # Dev-Modus: EDI-Nachricht loggen, nicht senden
        import logging
        logging.getLogger("einkauf.versand").info(
            "DEV-MODE: EDI ORDERS für Bestellung %s:\n%s",
            bestellung.bestellnummer, edifact_msg[:500]
        )
        return {
            "status":      "nicht_eingerichtet",
            "versand_art": "edi",
            "empfaenger":  lf.edi_kennung,
            "zeitstempel": datetime.now().isoformat(),
            "fehler":      None,
            "edi_format":  lf.edi_format or "ORDERS05",
            "dateiname":   dateiname,
            "hinweis":     "EDI_SFTP_HOST nicht konfiguriert — EDI muss manuell übertragen werden",
        }

    try:
        import paramiko  # type: ignore[import]
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.connect(
            _EDI_SFTP_HOST,
            username=_EDI_SFTP_USER,
            key_filename=_EDI_SFTP_KEY or None,
            timeout=15,
        )
        sftp = ssh.open_sftp()
        remote_path = _EDI_SFTP_PATH.rstrip("/") + "/" + dateiname
        with sftp.open(remote_path, "w") as f:
            f.write(edifact_msg)
        sftp.close()
        ssh.close()

        return {
            "status":      "gesendet",
            "versand_art": "edi",
            "empfaenger":  lf.edi_kennung,
            "zeitstempel": datetime.now().isoformat(),
            "fehler":      None,
            "edi_format":  lf.edi_format or "ORDERS05",
            "dateiname":   dateiname,
            "remote_path": remote_path,
        }
    except ImportError:
        return {
            "status":      "nicht_eingerichtet",
            "versand_art": "edi",
            "empfaenger":  lf.edi_kennung,
            "zeitstempel": datetime.now().isoformat(),
            "fehler":      None,
            "hinweis":     "paramiko nicht installiert — pip install paramiko",
        }
    except Exception as e:
        return {
            "status":      "fehler",
            "versand_art": "edi",
            "empfaenger":  lf.edi_kennung,
            "zeitstempel": datetime.now().isoformat(),
            "fehler":      str(e),
        }


# ─────────────────────────────────────────────────────────────────────────────
# Dispatcher
# ─────────────────────────────────────────────────────────────────────────────

def versende_bestellung(
    db: Session,
    bestellung: EinkaufBestellung,
    *,
    versand_art: str = "email",
    empfaenger_override: str | None = None,
    anhang_pdf: bytes | None = None,
    pdf_url: str | None = None,
    nutzer: dict | None = None,
) -> dict[str, Any]:
    """
    Haupt-Dispatcher: wählt die richtige Versand-Methode und aktualisiert
    den Bestellungs-Status — nur bei ``gesendet`` oder bewusst gewähltem Postversand.
    """
    if versand_art == "email":
        result = versende_email(db, bestellung,
                                empfaenger_override=empfaenger_override,
                                anhang_pdf=anhang_pdf, nutzer=nutzer)
    elif versand_art == "fax":
        result = versende_fax(db, bestellung,
                              faxnummer_override=empfaenger_override,
                              pdf_content=anhang_pdf,
                              pdf_url=pdf_url)
    elif versand_art == "edi":
        result = versende_edi(db, bestellung)
    else:
        # post / manuell: bewusst gewaehlt — der Mensch versendet.
        result = {
            "status":      "manuell",
            "versand_art": versand_art,
            "empfaenger":  empfaenger_override or "—",
            "zeitstempel": datetime.now().isoformat(),
            "fehler":      None,
        }

    # Status der Bestellung aktualisieren
    if result["status"] in ("gesendet", "manuell"):
        bestellung.versand_art = versand_art
        bestellung.versandt_am = datetime.now()
        if bestellung.status == "entwurf":
            bestellung.status = "versandt"
        db.flush()
        _kommunikation_eintragen(db, bestellung, result, nutzer)

    return result


def _kommunikation_eintragen(db: Session, bestellung: EinkaufBestellung, result: dict[str, Any],
                             nutzer: dict | None) -> None:
    """Der Versand erscheint im Reiter Kommunikation der Bestellmaske."""
    import uuid

    from sqlalchemy import text

    db.execute(text(
        "INSERT INTO domain_einkauf.bestellung_kommunikation "
        "(id, tenant_id, bestellung_id, kanal, empfaenger, betreff, status, versendet_am, erfasst_von) "
        "VALUES (:id, :t, :b, :k, :e, :betreff, :s, CASE WHEN :versendet THEN NOW() END, :von)"
    ), {"id": str(uuid.uuid4()), "t": str(bestellung.tenant_id), "b": str(bestellung.id),
        "k": result.get("versand_art"), "e": result.get("empfaenger"),
        "betreff": result.get("betreff") or f"Bestellung {bestellung.bestellnummer}",
        "s": "versendet" if result["status"] == "gesendet" else "erfasst",
        "versendet": result["status"] == "gesendet", "von": (nutzer or {}).get("sub")})
