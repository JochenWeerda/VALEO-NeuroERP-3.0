"""Kundenkonto im Portal — nur aus der geprueften Anmeldung und ihrer Zuordnung (TENANT-DOC-001).

Mandant und Kunde sind zwei getrennte Grenzen. Der Mandant kommt aus der Anmeldung (``get_tenant_id``); das
Kundenkonto aus ``domain_portal.kundenzugaenge``. Bis 14.10.2026 nahm das Portal den Kunden aus einem frei
uebergebenen Parameter oder gar nicht — jede angemeldete Person sah die Belege aller Kunden des Mandanten.

Zwei Arten von Anmeldungen:

* **Portalkunde** — hat mindestens eine gueltige Zuordnung im Mandanten. Er sieht nur diese Konten. Mit mehreren
  (Gemeinschaftsbetrieb) waehlt er das aktive im Kopf ``X-Kundenkonto`` — eine Auswahl aus der zugeordneten Menge,
  nie ein Ueberschreiben. Ein nicht zugeordnetes Konto ist 403.
* **Interne Betreuung** — hat eine Belegleserolle des Hauses (``BELEG_READ_ROLES``, dieselbe Liste wie fuer die
  Belege selbst; kein zweites Rechtesystem) und keine Zuordnung. Sie betreut mehrere Kunden und nennt den Kunden im
  Kopf ``X-Kundenkonto``; er muss ein Kunde dieses Mandanten sein.

Wer weder das eine noch das andere hat, bekommt 403. Ein Parameter ``customer_id`` in der URL zaehlt nirgends.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

from fastapi import Depends, Header, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user
from app.auth.finance_roles import BELEG_READ_ROLES
from app.core.database import get_db
from app.core.tenant import get_tenant_id

KOPF = "X-Kundenkonto"

# Rolle der Person im Betrieb. Welche Rolle welchen Portalweg sieht, ist noch nicht entschieden; die Rolle wird
# geprueft gespeichert und an jeden Weg weitergereicht.
Betriebsrolle = Literal["inhaber", "mitarbeiter", "buchhaltung", "berater"]


@dataclass(frozen=True)
class PortalKunde:
    tenant_id: str
    customer_id: str
    subject: str
    intern: bool
    rolle: Optional[str] = None  # Betriebsrolle des Portalkunden; bei interner Betreuung None


def zugeordnete_kunden(db: Session, tenant_id: str, subject: str) -> dict[str, str]:
    """Die gueltigen Kundenkonten dieser Anmeldung im Mandanten mit Betriebsrolle — nur Kunden des Mandanten."""
    if not tenant_id or not subject:
        return {}
    zeilen = db.execute(text("""
        SELECT z.customer_id, z.rolle FROM domain_portal.kundenzugaenge z
        JOIN domain_crm.customers c ON c.id = z.customer_id AND c.tenant_id = z.tenant_id AND c.deleted_at IS NULL
        WHERE z.tenant_id = :t AND z.subject = :s AND z.widerrufen_am IS NULL
          AND (z.gueltig_bis IS NULL OR z.gueltig_bis > now())
        ORDER BY z.customer_id
    """), {"t": tenant_id, "s": subject}).all()
    return {z[0]: z[1] for z in zeilen}


def _kunde_des_mandanten(db: Session, tenant_id: str, customer_id: str) -> bool:
    return db.execute(text(
        "SELECT 1 FROM domain_crm.customers WHERE id = :c AND tenant_id = :t AND deleted_at IS NULL"),
        {"c": customer_id, "t": tenant_id}).first() is not None


def portal_kunde(
    tenant_id: str = Depends(get_tenant_id),
    nutzer: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    kundenkonto: Optional[str] = Header(None, alias=KOPF),
) -> PortalKunde:
    subject = str((nutzer or {}).get("sub") or "").strip()
    gewaehlt = (kundenkonto or "").strip() or None
    if not tenant_id or not subject:
        raise HTTPException(status_code=403, detail="Keine gepruefte Anmeldung")

    konten = zugeordnete_kunden(db, tenant_id, subject)
    if konten:
        if gewaehlt is None:
            if len(konten) == 1:
                konto, rolle = next(iter(konten.items()))
                return PortalKunde(tenant_id, konto, subject, intern=False, rolle=rolle)
            raise HTTPException(status_code=409, detail="Mehrere Kundenkonten: bitte eines waehlen")
        if gewaehlt not in konten:
            raise HTTPException(status_code=403, detail="Dieses Kundenkonto ist der Anmeldung nicht zugeordnet")
        return PortalKunde(tenant_id, gewaehlt, subject, intern=False, rolle=konten[gewaehlt])

    if set((nutzer or {}).get("roles") or []) & set(BELEG_READ_ROLES):
        if gewaehlt is None:
            raise HTTPException(status_code=400, detail=f"Kundenkonto im Kopf {KOPF} angeben")
        if not _kunde_des_mandanten(db, tenant_id, gewaehlt):
            raise HTTPException(status_code=404, detail="Kunde nicht gefunden")
        return PortalKunde(tenant_id, gewaehlt, subject, intern=True)

    raise HTTPException(status_code=403, detail="Kein Kundenkonto zugeordnet")


def kundennummer_des_mandanten(db: Session, tenant_id: str, kunden_nr: str) -> bool:
    """Gehoert die fachliche Kundennummer zu einem Kunden dieses Mandanten? (Interne Wege, die sie nennen.)"""
    return db.execute(text(
        "SELECT 1 FROM domain_crm.customers WHERE customer_number = :n AND tenant_id = :t AND deleted_at IS NULL"),
        {"n": kunden_nr, "t": tenant_id}).first() is not None


def kundennummer(db: Session, kunde: PortalKunde) -> str:
    """Die fachliche Kundennummer des gewaehlten Kontos — Schluessel der Lohndienste und Empfehlungen."""
    zeile = db.execute(text(
        "SELECT customer_number FROM domain_crm.customers WHERE id = :c AND tenant_id = :t AND deleted_at IS NULL"),
        {"c": kunde.customer_id, "t": kunde.tenant_id}).first()
    if zeile is None or not zeile[0]:
        raise HTTPException(status_code=404, detail="Kunde nicht gefunden")
    return str(zeile[0])

