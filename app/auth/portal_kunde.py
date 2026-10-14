"""Kundenkonto und Portalrechte — nur aus der geprueften Anmeldung und ihrer Zuordnung (TENANT-DOC-001,
PORTAL-CONTEXT-001).

Mandant und Kunde sind zwei getrennte Grenzen. Der Mandant kommt aus der Anmeldung (``get_tenant_id``); das
Kundenkonto aus ``domain_portal.kundenzugaenge``. Bis 14.10.2026 nahm das Portal den Kunden aus einem frei
uebergebenen Parameter oder gar nicht — jede angemeldete Person sah die Belege aller Kunden des Mandanten.

Zwei Arten von Anmeldungen:

* **Zugeordnete Anmeldung** — hat mindestens eine gueltige Zuordnung im Mandanten (Betriebsinhaber, Mitarbeiter,
  Berater, Lohndienstleister, Aussendienst …). Sie sieht nur diese Konten. Mit mehreren waehlt sie das aktive im Kopf
  ``X-Kundenkonto`` — eine Auswahl aus der zugeordneten Menge, nie ein Ueberschreiben. Ein nicht zugeordnetes Konto
  ist 403.
* **Interne Betreuung (Innendienst)** — hat eine Belegleserolle des Hauses (``BELEG_READ_ROLES``) und keine
  Zuordnung. Sie nennt den Kunden im Kopf ``X-Kundenkonto``; er muss ein Kunde dieses Mandanten sein. Schreiben
  prueft jeder Weg zusaetzlich gegen die Fachrollen des Hauses.

Was eine zugeordnete Anmeldung im Konto darf, bestimmt ihre **Portalrolle** ueber ``PORTAL_RECHTE`` — eine Tabelle,
keine zweite Rollenverwaltung: Die Rolle ist eine Vorlage, die tatsaechlichen Rechte ergeben sich zusaetzlich aus
Mandant, Kundenkonto, Objekt (zugewiesene Schlaege, zugewiesene Auftraege), Aktion und Status. Keine Portalrolle
oeffnet alle Kunden eines Mandanten.

Wer weder zugeordnet ist noch intern betreut, bekommt 403. Ein Parameter ``customer_id`` in der URL zaehlt nirgends.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Optional

from fastapi import Depends, Header, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth.beleg_roles import rollen_von
from app.auth.deps import get_current_user
from app.auth.finance_roles import BELEG_READ_ROLES
from app.core.database import get_db
from app.core.tenant import get_tenant_id

KOPF = "X-Kundenkonto"

# Portalrollen (Nutzerentscheidung PORTAL-CONTEXT-001 vom 14.10.2026). ``aussendienst`` ist der Aussendienstberater
# des Landhandels: zugeordnete Kunden, und nur im Rahmen seiner internen Berechtigungen (eine Fachrolle des Hauses).
Betriebsrolle = Literal[
    "inhaber", "betriebsleiter", "mitarbeiter", "buchhaltung", "berater", "lohndienstleister", "aussendienst",
]
BETRIEBSROLLEN: tuple[str, ...] = (
    "inhaber", "betriebsleiter", "mitarbeiter", "buchhaltung", "berater", "lohndienstleister", "aussendienst",
)

# Funktionen im Portal.
UEBERSICHT = "uebersicht"                      # Startseite
VERKAUF = "verkauf"                            # Anfragen, Bestellungen, Shop, Lieferscheine
KONTRAKTE = "kontrakte"                        # Kontrakte, Vorkaeufe
FINANZEN = "finanzen"                          # Rechnungen, Gutschriften, offene Posten, Finanzdokumente
FELDBUCH_LESEN = "feldbuch_lesen"
FELDBUCH_SCHREIBEN = "feldbuch_schreiben"      # Schlaege und Massnahmen erfassen
FELDBUCH_VERWALTEN = "feldbuch_verwalten"      # Import, Jahreswechsel, Fremdsystemuebernahme
AUSWERTUNGEN = "auswertungen"                  # Bilanzen, Nachhaltigkeit, Zertifikate
LOHNDIENST_LESEN = "lohndienst_lesen"
LOHNDIENST_BEAUFTRAGEN = "lohndienst_beauftragen"
LOHNDIENST_AUSFUEHREN = "lohndienst_ausfuehren"  # zugewiesene Auftraege abschliessen
EMPFEHLUNGEN = "empfehlungen"
ZUGAENGE_VERWALTEN = "zugaenge_verwalten"      # Benutzer des eigenen Betriebs

PORTAL_RECHTE: dict[str, frozenset[str]] = {
    "inhaber": frozenset({
        UEBERSICHT, VERKAUF, KONTRAKTE, FINANZEN, FELDBUCH_LESEN, FELDBUCH_SCHREIBEN, FELDBUCH_VERWALTEN,
        AUSWERTUNGEN, LOHNDIENST_LESEN, LOHNDIENST_BEAUFTRAGEN, EMPFEHLUNGEN, ZUGAENGE_VERWALTEN,
    }),
    "betriebsleiter": frozenset({
        UEBERSICHT, VERKAUF, KONTRAKTE, FELDBUCH_LESEN, FELDBUCH_SCHREIBEN, FELDBUCH_VERWALTEN, AUSWERTUNGEN,
        LOHNDIENST_LESEN, LOHNDIENST_BEAUFTRAGEN, EMPFEHLUNGEN,
    }),
    # Zugewiesene Schlaege (``kundenzugaenge.schlag_ids``), Arbeitsauftraege, operative Erfassung.
    "mitarbeiter": frozenset({UEBERSICHT, FELDBUCH_LESEN, FELDBUCH_SCHREIBEN, LOHNDIENST_LESEN}),
    "buchhaltung": frozenset({UEBERSICHT, FINANZEN}),
    # Externer Berater: nur ausdruecklich freigegebene Betriebe (die Zuordnung selbst), Beratungsfunktionen.
    "berater": frozenset({UEBERSICHT, FELDBUCH_LESEN, AUSWERTUNGEN, EMPFEHLUNGEN}),
    # Nur Auftraege, die ihm zugewiesen sind, mit den dafuer noetigen Schlaginformationen.
    "lohndienstleister": frozenset({LOHNDIENST_LESEN, LOHNDIENST_AUSFUEHREN}),
    "aussendienst": frozenset({
        UEBERSICHT, VERKAUF, KONTRAKTE, FELDBUCH_LESEN, AUSWERTUNGEN, LOHNDIENST_LESEN, LOHNDIENST_BEAUFTRAGEN,
        EMPFEHLUNGEN,
    }),
}
assert set(PORTAL_RECHTE) == set(BETRIEBSROLLEN)

# Interne Betreuung: alles ausser der Benutzerverwaltung eines Betriebs (die laeuft ueber die Leitung des Hauses);
# Schreibwege pruefen zusaetzlich die Fachrollen des Hauses.
INTERNE_RECHTE = frozenset().union(*PORTAL_RECHTE.values()) - {ZUGAENGE_VERWALTEN, LOHNDIENST_AUSFUEHREN}

# Rollen, die die Leitung des Hauses vergibt — ein Betriebsinhaber vergibt sie nicht.
NUR_DURCH_DAS_HAUS = frozenset({"aussendienst", "lohndienstleister"})

# Fachrollen, ohne die eine Aussendienst-Zuordnung nicht gilt ("im Rahmen seiner internen Berechtigungen").
AUSSENDIENST_FACHROLLEN = frozenset(BELEG_READ_ROLES) | {"AGRAR_LESEN", "AGRAR_BEARBEITEN", "AGRAR_ADMIN"}


@dataclass(frozen=True)
class PortalKunde:
    tenant_id: str
    customer_id: str
    subject: str
    intern: bool
    rolle: Optional[str] = None  # Portalrolle der zugeordneten Anmeldung; bei interner Betreuung None
    # Zugewiesene Schlaege (nur Mitarbeiter); None = alle Schlaege des Kontos.
    schlag_ids: Optional[tuple[str, ...]] = None
    rechte: frozenset[str] = field(default_factory=frozenset)

    def darf(self, recht: str) -> bool:
        return recht in self.rechte


@dataclass(frozen=True)
class _Zugang:
    rolle: str
    schlag_ids: Optional[tuple[str, ...]]


def _zugaenge(db: Session, tenant_id: str, subject: str, rollen: set[str]) -> dict[str, _Zugang]:
    if not tenant_id or not subject:
        return {}
    zeilen = db.execute(text("""
        SELECT z.customer_id, z.rolle, z.schlag_ids FROM domain_portal.kundenzugaenge z
        JOIN domain_crm.customers c ON c.id = z.customer_id AND c.tenant_id = z.tenant_id AND c.deleted_at IS NULL
        WHERE z.tenant_id = :t AND z.subject = :s AND z.widerrufen_am IS NULL
          AND (z.gueltig_bis IS NULL OR z.gueltig_bis > now())
        ORDER BY z.customer_id
    """), {"t": tenant_id, "s": subject}).all()
    ergebnis: dict[str, _Zugang] = {}
    for kunde, rolle, schlaege in zeilen:
        if rolle == "aussendienst" and not rollen & AUSSENDIENST_FACHROLLEN:
            continue  # Aussendienst ohne Fachrolle des Hauses: Zuordnung ruht
        ergebnis[kunde] = _Zugang(rolle, tuple(schlaege) if schlaege is not None else None)
    return ergebnis


def zugeordnete_kunden(db: Session, tenant_id: str, subject: str, rollen: Optional[set[str]] = None) -> dict[str, str]:
    """Die gueltigen Kundenkonten dieser Anmeldung im Mandanten mit Portalrolle — nur Kunden des Mandanten."""
    return {k: z.rolle for k, z in _zugaenge(db, tenant_id, subject, rollen or set()).items()}


def _kunde_des_mandanten(db: Session, tenant_id: str, customer_id: str) -> bool:
    return db.execute(text(
        "SELECT 1 FROM domain_crm.customers WHERE id = :c AND tenant_id = :t AND deleted_at IS NULL"),
        {"c": customer_id, "t": tenant_id}).first() is not None


def _zugeordnet(tenant_id: str, konto: str, subject: str, zugang: _Zugang) -> PortalKunde:
    schlaege = zugang.schlag_ids if zugang.rolle == "mitarbeiter" else None
    return PortalKunde(tenant_id, konto, subject, intern=False, rolle=zugang.rolle, schlag_ids=schlaege,
                       rechte=PORTAL_RECHTE.get(zugang.rolle, frozenset()))


def portal_kunde(
    tenant_id: str = Depends(get_tenant_id),
    nutzer: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    kundenkonto: Optional[str] = Header(None, alias=KOPF),
) -> PortalKunde:
    subject = str((nutzer or {}).get("sub") or "").strip()
    rollen = rollen_von(nutzer)
    gewaehlt = (kundenkonto or "").strip() or None
    if not tenant_id or not subject:
        raise HTTPException(status_code=403, detail="Keine gepruefte Anmeldung")

    konten = _zugaenge(db, tenant_id, subject, rollen)
    if konten:
        if gewaehlt is None:
            if len(konten) == 1:
                konto, zugang = next(iter(konten.items()))
                return _zugeordnet(tenant_id, konto, subject, zugang)
            raise HTTPException(status_code=409, detail="Mehrere Kundenkonten: bitte eines waehlen")
        if gewaehlt not in konten:
            raise HTTPException(status_code=403, detail="Dieses Kundenkonto ist der Anmeldung nicht zugeordnet")
        return _zugeordnet(tenant_id, gewaehlt, subject, konten[gewaehlt])

    if rollen & set(BELEG_READ_ROLES):
        if gewaehlt is None:
            raise HTTPException(status_code=400, detail=f"Kundenkonto im Kopf {KOPF} angeben")
        if not _kunde_des_mandanten(db, tenant_id, gewaehlt):
            raise HTTPException(status_code=404, detail="Kunde nicht gefunden")
        return PortalKunde(tenant_id, gewaehlt, subject, intern=True, rechte=INTERNE_RECHTE)

    raise HTTPException(status_code=403, detail="Kein Kundenkonto zugeordnet")


def portal_recht(*rechte: str):
    """Abhaengigkeit: Kundenkonto wie ``portal_kunde`` und zusaetzlich eines der ``rechte`` der Portalrolle (403)."""

    def _pruefen(kunde: PortalKunde = Depends(portal_kunde)) -> PortalKunde:
        if not any(kunde.darf(r) for r in rechte):
            raise HTTPException(status_code=403, detail=f"Keine Berechtigung im Portal: {' oder '.join(rechte)}")
        return kunde

    return _pruefen


def kundennummer_des_mandanten(db: Session, tenant_id: str, kunden_nr: str) -> bool:
    """Gehoert die fachliche Kundennummer zu einem Kunden dieses Mandanten? (Interne Wege, die sie nennen.)"""
    return db.execute(text(
        "SELECT 1 FROM domain_crm.customers WHERE customer_number = :n AND tenant_id = :t AND deleted_at IS NULL"),
        {"n": kunden_nr, "t": tenant_id}).first() is not None


def kunde_zur_nummer(db: Session, tenant_id: str, kunden_nr: str) -> Optional[str]:
    """Die Kunden-ID zu einer fachlichen Kundennummer dieses Mandanten, sonst None."""
    zeile = db.execute(text(
        "SELECT id FROM domain_crm.customers WHERE customer_number = :n AND tenant_id = :t AND deleted_at IS NULL"),
        {"n": kunden_nr, "t": tenant_id}).first()
    return str(zeile[0]) if zeile else None


def kundennummer(db: Session, kunde: PortalKunde) -> str:
    """Die fachliche Kundennummer des gewaehlten Kontos — Anzeige- und Suchschluessel, nicht Identitaet."""
    zeile = db.execute(text(
        "SELECT customer_number FROM domain_crm.customers WHERE id = :c AND tenant_id = :t AND deleted_at IS NULL"),
        {"c": kunde.customer_id, "t": kunde.tenant_id}).first()
    if zeile is None or not zeile[0]:
        raise HTTPException(status_code=404, detail="Kunde nicht gefunden")
    return str(zeile[0])
