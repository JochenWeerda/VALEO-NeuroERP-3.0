# MCP-Maskenaktionen: Capability-Grenze, Zwischenstand

Generische MCP-Schreibaufrufe prüfen vor der Weiterleitung eine eindeutige Freigabe in `mask.action.execute.write_capabilities`: Screen, Aktion, versionierter Domain-Command und Endpunkt müssen exakt übereinstimmen. Die geprüfte Identität benötigt zusätzlich `masks:write` und eine explizit freigegebene Fachrolle. Das gilt auch bei einem menschlichen Bearer über MCP. Fehlende, mehrdeutige, deaktivierte oder fehlerhafte Einträge sperren den Schreibweg. Deklarierte Leseansichten bleiben getrennt; widersprüchliche Lese-/Schreibverträge werden abgewiesen.

Die vier neuen Capabilities sind vor ihrer vollständigen fachlichen Abnahme deaktiviert. Bestehende generische Schreibaktionen ohne ausdrückliche Freigabe sind ebenfalls gesperrt; dies ist eine Sicherheitszwischenstufe, keine Aussage, dass ihre fachliche MCP-Parität abgeschlossen wäre. Sie müssen anhand der kanonischen Verträge einzeln inventarisiert, geprüft und gegebenenfalls explizit wieder freigegeben werden. Die generierten Aktions-/MCP-Projektionen werden nach Integration der laufenden Maskenänderungen aktualisiert.

Gezielte lokale Tests: `tests/test_mcp_write_capability.py` und `tests/test_versandprofil_commands.py`, 25 Tests bestanden. Die Tests decken insbesondere fehlende/duplizierte/falsche Capabilities, Version, Rolle und Scope sowie menschlichen Bearer und sichere GET-/Schreibtrennung ab. PostgreSQL-, vollständige RLS-, konkurrierende Wiederholungs-, UI-/CLI- und kanalübergreifende Tests bleiben vor den jeweiligen Schreibfreigaben erforderlich.

