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
