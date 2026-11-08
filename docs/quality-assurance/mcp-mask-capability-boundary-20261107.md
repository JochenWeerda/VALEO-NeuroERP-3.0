# MCP-Maskenaktionen: Capability-Grenze, Zwischenstand

Generische MCP-Schreibaufrufe prüfen vor der Weiterleitung eine eindeutige Freigabe in `mask.action.execute.write_capabilities`: Screen, Aktion, versionierter Domain-Command und Endpunkt müssen exakt übereinstimmen. Die geprüfte Identität benötigt zusätzlich `masks:write` und eine explizit freigegebene Fachrolle. Das gilt auch bei einem menschlichen Bearer über MCP. Fehlende, mehrdeutige, deaktivierte oder fehlerhafte Einträge sperren den Schreibweg. Deklarierte Leseansichten bleiben getrennt; widersprüchliche Lese-/Schreibverträge werden abgewiesen.

Die vier neuen Capabilities sind vor ihrer vollständigen fachlichen Abnahme deaktiviert. Bestehende generische Schreibaktionen ohne ausdrückliche Freigabe sind ebenfalls gesperrt; dies ist eine Sicherheitszwischenstufe, keine Aussage, dass ihre fachliche MCP-Parität abgeschlossen wäre. Sie müssen anhand der kanonischen Verträge einzeln inventarisiert, geprüft und gegebenenfalls explizit wieder freigegeben werden. Die generierten Aktions-/MCP-Projektionen werden nach Integration der laufenden Maskenänderungen aktualisiert.

Gezielte lokale Tests: `tests/test_mcp_write_capability.py` und `tests/test_versandprofil_commands.py`, 25 Tests bestanden. Die Tests decken insbesondere fehlende/duplizierte/falsche Capabilities, Version, Rolle und Scope sowie menschlichen Bearer und sichere GET-/Schreibtrennung ab. PostgreSQL-, vollständige RLS-, konkurrierende Wiederholungs-, UI-/CLI- und kanalübergreifende Tests bleiben vor den jeweiligen Schreibfreigaben erforderlich.


## Auswirkungsabnahme bestehender Maskenvertraege

Leadlauf tests/test_mcp_mask_actions.py unter erforderlichen lokalen Prozessrechten: 16 bestanden, 12 fehlgeschlagen (6,82 Sekunden). Alle zwoelf Fehler entstehen, weil der bisherige Registry-basierte Positivpfad keine freigegebene Schreibaktion mehr findet. Das ist ein belegter funktionaler Zwischenstand und kein vollstaendiger Abschluss der MCP-Paritaet. Keine Tests uebersprungen oder zu erwarteten Fehlern umdeklariert. Wiederfreigabe muss echte kanonische Fachcommands samt expliziten Rollen/Versionen und Kanalnachweisen herstellen; blosse Testfixtures duerfen reale Funktionsverluste nicht verdecken.

Studio-Roundtrip: versionierte `domainCommand`-Kennungen werden im Maskenaktionskatalog erhalten und sind Teil des unveränderlichen nativen sowie Beleg-Transportvertrags. Der Draft-Validator weist Weglassen oder Austausch gegenüber der kanonischen Quelle ab. Drei gezielte Manipulationsvarianten und die bestehenden nativen Policy-Verträge ergeben 17 bestandene Tests (`tests/test_studio_native_policy_binding.py`).
