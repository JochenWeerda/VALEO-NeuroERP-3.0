"""Aufbewahrung und rechtliche Rahmenbedingungen für DSGVO-Löschanfragen (M-08/M-09)."""

# Sensible Standardfrist für Archivdaten (Steuer/Vertrag); modulspezifische Jobs können länger halten.
DEFAULT_ARCHIVE_RETENTION_YEARS = 10

LEGAL_HOLD_NOTE = (
    "Vor endgültiger Löschung ist auf Legal Hold / laufende Verfahren zu prüfen "
    "(Metadaten z. B. legal_hold)."
)


def deletion_audit_suffix() -> str:
    return f" Retention-Referenz: bis zu {DEFAULT_ARCHIVE_RETENTION_YEARS} Jahre Archiv, sofern kein Legal Hold."
