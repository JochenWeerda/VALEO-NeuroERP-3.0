---
title: Module & Feature-Flags
type: how-to
audience: [tenant-admin, betrieb]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-25
version: 3.0.0
---

# Module & Feature-Flags

VALEO NeuroERP ist modular: dieselbe Software, pro Mandant unterschiedlich
konfiguriert. Die Steuerung erfolgt über die Modul-Registry.

## Steuergrößen

| Schlüssel | Wirkung |
|---|---|
| `INSTALLED_MODULES` | Global verfügbare Module der Installation. |
| `TENANT_MODULE_FLAGS` | Pro-Mandant aktivierte Module/Features. |

Die Modul-Registry (`app/core/module_registry.py`) wertet diese Flags aus und
schaltet Navigation, Routen und Funktionen frei.

## Modul aktivieren

1. Sicherstellen, dass das Modul in `INSTALLED_MODULES` enthalten ist.
2. Im `TENANT_MODULE_FLAGS` des Mandanten das Modul aktivieren.
3. Anwendung/Cache aktualisieren; Nutzer:innen sehen den Bereich nach Reload.

## Auswirkungen

- **Navigation:** Nur freigeschaltete Bereiche erscheinen.
- **API:** Routen nicht aktivierter Module sind gesperrt.
- **Dokumentation:** Das Benutzerhandbuch ist modulübergreifend; nicht aktive
  Module sind für Nutzer:innen schlicht nicht sichtbar.

## Häufige Fehler

- **Feature trotz Flag nicht sichtbar:** Caching/Reload nötig oder Rolle fehlt.
- **Modul global nicht verfügbar:** fehlt in `INSTALLED_MODULES`.
