"""Rollen der Finanzwege — einmal definiert.

Seit 07.10.2026 pruefen Zahlungslaeufe und Eingangsrechnungen ihre Rolle vor dem
ersten Datenbankzugriff (vorher keiner). Freigeben, Ausfuehren und Buchen bewegt
Geld oder schreibt das Hauptbuch: nur ``FINANCE_ADMIN``/``admin``.
"""

from __future__ import annotations

from app.auth.deps import require_roles

finance_read = require_roles("FINANCE_LESEN", "FINANCE_BEARBEITEN", "FINANCE_ADMIN", "admin", "manager")
finance_write = require_roles("FINANCE_BEARBEITEN", "FINANCE_ADMIN", "admin", "manager")
finance_admin = require_roles("FINANCE_ADMIN", "admin")

# Offene Posten lesen auch Verkauf, Vertrieb und Einkauf: Wer einen Auftrag annimmt oder eine
# Bestellung ausloest, muss sehen, was der Kunde schuldet und was dem Lieferanten zusteht.
# Aendern, ausgleichen und mahnen bleibt ``finance_write``; loeschen ``finance_admin``.
open_items_read = require_roles(
    "FINANCE_LESEN", "FINANCE_BEARBEITEN", "FINANCE_ADMIN",
    "SALES_LESEN", "SALES_BEARBEITEN", "SALES_ADMIN",
    "CRM_LESEN", "CRM_BEARBEITEN", "CRM_ADMIN",
    "EINKAUF_LESEN", "EINKAUF_BEARBEITEN", "EINKAUF_ADMIN",
    "admin", "manager",
)
