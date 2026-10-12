"""Rollen der Finanzwege — einmal definiert.

Seit 07.10.2026 pruefen Zahlungslaeufe und Eingangsrechnungen ihre Rolle vor dem
ersten Datenbankzugriff (vorher keiner). Freigeben, Ausfuehren und Buchen bewegt
Geld oder schreibt das Hauptbuch: nur ``FINANCE_ADMIN``/``admin``.

Seit 11.10.2026 gilt am Hauptbuch selbst: Die Buchhaltung (``finance_write``) erfasst, bucht und
storniert ihre Buchungen — das ist ihre taegliche Arbeit, ein Storno bleibt als Gegenbuchung sichtbar.
Der Leitung vorbehalten ist, was sich nicht durch eine Gegenbuchung zuruecknehmen laesst: loeschen,
Perioden sperren und oeffnen, ein Geschaeftsjahr anlegen, der Massenimport.
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

# Den Kontenplan liest auch der Einkauf: Der Rechnungseingang kontiert damit. Salden und Buchungen
# bleiben ``finance_read``.
kontenplan_read = require_roles(
    "FINANCE_LESEN", "FINANCE_BEARBEITEN", "FINANCE_ADMIN",
    "EINKAUF_LESEN", "EINKAUF_BEARBEITEN", "EINKAUF_ADMIN",
    "admin", "manager",
)

# Der gemeinsame Kontenrahmen (Mandant ``system``) gilt fuer alle Haeuser einer Installation. Ihn zu
# lesen ist etwas anderes als ihn zu pflegen: Aendern und deaktivieren braucht dieses eigene Recht,
# die Finanzrolle eines Hauses genuegt dafuer nicht.
KONTENRAHMEN_PFLEGE = frozenset({"KONTENRAHMEN_PFLEGE", "admin"})
