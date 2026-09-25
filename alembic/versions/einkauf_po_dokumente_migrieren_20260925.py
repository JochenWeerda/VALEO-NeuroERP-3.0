"""Die Bestelldokumente ziehen in den fuehrenden Bestellbestand um.

Es gab zwei Bestellwelten: Die Compat-Schnittstelle legte Dokumente in
``public.documents`` ab (Nummernkreis ``PO-``), die fuehrende Maske schreibt
nach ``domain_einkauf.bestellungen`` (``EK-``). Entschieden ist ``EK-``.

Diese Migration holt die vorhandenen Dokumente herueber. Sie ist bewusst
vorsichtig:

- Sie laeuft nur ueber Dokumente, deren Nummer im Zielbestand noch fehlt.
  Ein zweiter Lauf tut nichts.
- Sie loescht das Dokument **nicht**, sondern vermerkt die Uebernahme darin.
  Solange niemand die alten Belege vermisst hat, ist eine Loeschung eine
  Entscheidung fuer sich; der Bestand ist klein genug, dass er niemanden
  stoert.
- Der Lieferant ist im Dokument oft nur ein Name ("Stroetmann") und hat keinen
  Stammsatz. Ohne Lieferant gibt es aber keine Bestellung — die Spalte ist zu
  Recht NOT NULL. Fehlt er, wird ein Stammsatz aus dem Namen angelegt und als
  aus der Uebernahme stammend gekennzeichnet, damit ihn jemand vervollstaendigt.

Revision ID: einkauf_po_dokumente_migrieren_20260925
Revises: mcp_tool_executions_20260921
Create Date: 2026-09-25
"""

from __future__ import annotations

import json
import uuid
from datetime import date, datetime

import sqlalchemy as sa
from alembic import op

revision = "einkauf_po_dokumente_migrieren_20260925"
down_revision = "mcp_tool_executions_20260921"
branch_labels = None
depends_on = None

#: Woran die uebernommenen Saetze spaeter erkennbar sind.
HERKUNFT = "Uebernommen aus Compat-Bestelldokument"


def _als_dict(roh) -> dict:
    if isinstance(roh, dict):
        return roh
    if isinstance(roh, (str, bytes)):
        try:
            return json.loads(roh)
        except (ValueError, TypeError):
            return {}
    return {}


def _datum(wert) -> date:
    if isinstance(wert, date):
        return wert
    if isinstance(wert, str) and wert:
        try:
            return datetime.fromisoformat(wert[:10]).date()
        except ValueError:
            pass
    return date.today()


def _status(compat: str | None) -> str:
    """Der Dokumentenspeicher schreibt gross, der Beleg klein."""
    return (compat or "entwurf").strip().lower() or "entwurf"


def upgrade() -> None:
    verbindung = op.get_bind()

    dokumente = verbindung.execute(
        sa.text(
            "SELECT id::text AS id, doc_number, data "
            "FROM public.documents WHERE doc_type = 'purchase_order'"
        )
    ).mappings().all()

    for dokument in dokumente:
        daten = _als_dict(dokument["data"])
        nummer = dokument["doc_number"] or daten.get("purchaseOrderNumber")
        mandant = daten.get("tenantId")
        if not nummer or not mandant:
            continue

        schon_da = verbindung.execute(
            sa.text(
                "SELECT 1 FROM domain_einkauf.bestellungen "
                "WHERE bestellnummer = :nr AND tenant_id = :t"
            ),
            {"nr": nummer, "t": mandant},
        ).first()
        if schon_da:
            continue

        # ── Lieferant: vorhanden, oder aus dem Namen angelegt ──────────────
        roh_lieferant = str(daten.get("supplierId") or "").strip()
        lieferant_id = None
        if roh_lieferant:
            lieferant_id = verbindung.execute(
                sa.text(
                    "SELECT id::text FROM domain_einkauf.lieferanten "
                    "WHERE tenant_id = :t AND (id::text = :s OR lieferantennummer = :s "
                    "      OR lower(firmenname) = lower(:s)) LIMIT 1"
                ),
                {"t": mandant, "s": roh_lieferant},
            ).scalar()

        if not lieferant_id:
            lieferant_id = str(uuid.uuid4())
            verbindung.execute(
                sa.text(
                    "INSERT INTO domain_einkauf.lieferanten "
                    "(id, tenant_id, lieferantennummer, firmenname, notiz) "
                    "VALUES (:id, :t, :nr, :name, :notiz)"
                ),
                {
                    "id": lieferant_id,
                    "t": mandant,
                    "nr": f"UEB-{str(uuid.uuid4())[:8].upper()}",
                    "name": roh_lieferant or "Unbekannter Lieferant",
                    "notiz": f"{HERKUNFT} {nummer}. Stammdaten bitte vervollstaendigen.",
                },
            )

        # ── Der Beleg ─────────────────────────────────────────────────────
        bestell_id = str(uuid.uuid4())
        notiz_teile = [t for t in (daten.get("notes"), daten.get("description")) if t]
        notiz_teile.append(f"{HERKUNFT} {nummer}")

        verbindung.execute(
            sa.text(
                "INSERT INTO domain_einkauf.bestellungen "
                "(id, tenant_id, bestellnummer, lieferant_id, bestelldatum, "
                " lieferdatum_wunsch, status, bestellfall, waehrung, incoterms, "
                " lieferadresse, zahlungsbedingung, ansprechpartner, "
                " unsere_referenz, netto_summe, brutto_summe, notiz) "
                "VALUES (:id, :t, :nr, :lf, :datum, :liefer, :status, "
                "        'bestand_abgleich', :waehrung, :incoterms, :adresse, "
                "        :zahlung, :kontakt, :referenz, :netto, :brutto, :notiz)"
            ),
            {
                "id": bestell_id,
                "t": mandant,
                "nr": nummer,
                "lf": lieferant_id,
                "datum": _datum(daten.get("orderDate")),
                "liefer": _datum(daten["deliveryDate"]) if daten.get("deliveryDate") else None,
                "status": _status(daten.get("status")),
                "waehrung": daten.get("currency") or "EUR",
                "incoterms": daten.get("incoterms"),
                "adresse": daten.get("shippingAddress"),
                "zahlung": daten.get("paymentTerms"),
                "kontakt": daten.get("contactPerson"),
                "referenz": daten.get("externalReference"),
                "netto": daten.get("subtotal") or 0,
                "brutto": daten.get("totalAmount") or 0,
                "notiz": "\n".join(notiz_teile),
            },
        )

        for nr, position in enumerate(daten.get("items") or [], start=1):
            menge = position.get("quantity") or 0
            preis = position.get("unitPrice") or 0
            bezeichnung = position.get("description") or f"Position {nr}"
            verbindung.execute(
                sa.text(
                    "INSERT INTO domain_einkauf.bestellung_positionen "
                    "(id, bestellung_id, pos_nr, artikel_nr, artikel_bezeichnung, "
                    " menge, einheit, einzelpreis, netto_betrag) "
                    "VALUES (:id, :b, :nr, :artnr, :bez, :menge, :einheit, "
                    "        :preis, :betrag)"
                ),
                {
                    "id": str(uuid.uuid4()),
                    "b": bestell_id,
                    "nr": nr,
                    # Das Dokument fuehrt keine Artikelnummer, nur einen Text.
                    "artnr": position.get("articleNumber") or bezeichnung[:50],
                    "bez": bezeichnung,
                    "menge": menge,
                    "einheit": position.get("unit") or "Stk",
                    "preis": preis,
                    "betrag": round(float(menge) * float(preis), 2),
                },
            )

        # Das Dokument bleibt stehen, traegt aber den Vermerk.
        daten["migratedToEinkauf"] = bestell_id
        daten["migratedAt"] = datetime.utcnow().isoformat()
        verbindung.execute(
            sa.text(
                "UPDATE public.documents SET data = CAST(:d AS jsonb), updated_at = NOW() "
                "WHERE id::text = :id"
            ),
            {"d": json.dumps(daten), "id": dokument["id"]},
        )


def downgrade() -> None:
    """Die uebernommenen Belege wieder entfernen.

    Erkennbar sind sie am Vermerk in der Notiz; die Dokumente selbst wurden
    nie geloescht, der Rueckweg ist also vollstaendig.
    """
    verbindung = op.get_bind()
    verbindung.execute(
        sa.text(
            "DELETE FROM domain_einkauf.bestellung_positionen WHERE bestellung_id IN "
            "(SELECT id FROM domain_einkauf.bestellungen WHERE notiz LIKE :muster)"
        ),
        {"muster": f"%{HERKUNFT}%"},
    )
    verbindung.execute(
        sa.text("DELETE FROM domain_einkauf.bestellungen WHERE notiz LIKE :muster"),
        {"muster": f"%{HERKUNFT}%"},
    )
    verbindung.execute(
        sa.text("DELETE FROM domain_einkauf.lieferanten WHERE notiz LIKE :muster"),
        {"muster": f"%{HERKUNFT}%"},
    )
    verbindung.execute(
        sa.text(
            "UPDATE public.documents "
            "SET data = (data - 'migratedToEinkauf' - 'migratedAt') "
            "WHERE doc_type = 'purchase_order'"
        )
    )
