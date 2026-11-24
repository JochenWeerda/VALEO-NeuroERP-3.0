"""Buchungsschluessel: eine Bestandsbewegung je fachlichem Vorgang (Schnitt 2b-2, 24.11.2026).

Jeder Buchungsweg (Belegfluss ``docflow_lagerzugang``, Lagerplatz ``WarehouseService.book_stock_movement``) beansprucht
**vor** allen Wirkungen den Schluessel seines Vorgangs. Ist er vergeben, liefert ``beanspruche`` die Kennung der
vorhandenen Bewegung, und der Aufrufer bucht nichts:

- **Wiederholung** (gleicher Aufruf, Ereignis doppelt zugestellt): vorhandene Bewegung, keine zweite.
- **Parallel**: der Zweitversuch wartet am Primaerschluessel, bis der erste committet, und bucht dann nichts.
- **Abbruch**: rollt der erste zurueck, verschwindet sein Anspruch; der naechste Versuch bucht normal.
- **Storno**: eigener Schluessel (``storno:<bewegung>``) - ein Storno je Bewegung.

Schluessel sind fachlich, nicht zufaellig: ``<quelle>:<beleg>:<position>:<art>``.
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session


class SchluesselOhneBewegung(RuntimeError):
    """Schluessel beansprucht, aber ohne Bewegung - nur moeglich, wenn ein Aufrufer verknuepfe() vergass."""


def beanspruche(db: Session, tenant_id: str, schluessel: str) -> Optional[str]:
    """``None``: Schluessel neu beansprucht - jetzt buchen und danach ``verknuepfe``. Sonst: vorhandene Bewegung."""
    if not schluessel or len(schluessel) > 200:
        raise ValueError("Buchungsschluessel fehlt oder ist laenger als 200 Zeichen.")
    neu = db.execute(text(
        "INSERT INTO domain_inventory.bestandsbuchung_schluessel (tenant_id, schluessel) VALUES (:t, :s) "
        "ON CONFLICT (tenant_id, schluessel) DO NOTHING RETURNING schluessel"),
        {"t": tenant_id, "s": schluessel}).scalar()
    if neu is not None:
        return None
    vorhanden = db.execute(text(
        "SELECT bewegung_id FROM domain_inventory.bestandsbuchung_schluessel WHERE tenant_id = :t AND schluessel = :s"),
        {"t": tenant_id, "s": schluessel}).scalar()
    if vorhanden is None:
        raise SchluesselOhneBewegung(f"Buchungsschluessel {schluessel} ist vergeben, aber ohne Bewegung.")
    return str(vorhanden)


def verknuepfe(db: Session, tenant_id: str, schluessel: str, bewegung_id: str) -> None:
    db.execute(text(
        "UPDATE domain_inventory.bestandsbuchung_schluessel SET bewegung_id = :b "
        "WHERE tenant_id = :t AND schluessel = :s AND bewegung_id IS NULL"),
        {"b": bewegung_id, "t": tenant_id, "s": schluessel})
