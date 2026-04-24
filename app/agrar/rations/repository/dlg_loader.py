"""DLG-Futterwerttabellen: Pfadaufloesung + Loader.

Refactor-Etappe 1d (2026-04-23): aktuell enthaelt dieses Modul den
``_dlg_json_path``-Resolver. Der eigentliche Ladevorgang
(``_load_dlg_feeds_from_json``) ist stark mit Helper-Funktionen aus
der Haupt-Endpoint-Datei verzahnt und wird in einem Folge-Commit
ausgelagert, sobald die noetigen Helfer (``_v``, ``_dlg_category``,
``_estimate_price``, ``_is_structural_coproduct``, ``_max_kg_for``)
in ``feed_classification.py`` stehen.
"""

from __future__ import annotations

import os
from typing import Optional

from app.core.config import settings


def _dlg_json_path() -> Optional[str]:
    """Liefert den Pfad zur DLG-Futterwerttabellen-2025-JSON-Datei.

    Reihenfolge:
      1. ``settings.RATIONS_DLG_DATA_PATH`` (umgebungsspezifische Ueberschreibung)
      2. Gebuendelter Fallback: ``app/data/DLG_FWT_WK_2025.json`` bzw.
         ``app/data/dlg_feeds_raw.json`` (Alt-Pfad, rueckwaertskompatibel).
      3. None, falls nichts gefunden.

    Die frueher in ``rations_optimization.py`` gelebte Logik wird hier
    1:1 uebernommen; die Basis ist das ``app``-Datenverzeichnis, das
    relativ zu diesem Modul 3 Ebenen hoeher liegt
    (app/agrar/rations/repository -> app).
    """
    configured = getattr(settings, "RATIONS_DLG_DATA_PATH", None)
    if configured:
        return configured
    here = os.path.dirname(os.path.abspath(__file__))
    # app/agrar/rations/repository -> app/
    app_root = os.path.normpath(os.path.join(here, "..", "..", "..", ".."))
    for candidate in ("DLG_FWT_WK_2025.json", "dlg_feeds_raw.json"):
        bundled = os.path.normpath(os.path.join(app_root, "app", "data", candidate))
        if os.path.isfile(bundled):
            return bundled
    return None
