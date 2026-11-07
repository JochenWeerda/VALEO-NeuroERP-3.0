# Gemeinsame Zeilencommand-Integration

Lead-Abnahme des uebernommenen Arbeitsstands: 104 Fachcommand-/Capability-/CLI-Tests sowie 69 bestehende MCP-/CLI-/Inventurvertraege bestanden (173 insgesamt), vollstaendige Frontend-Typpruefung gruen. Aktionskatalog, MCP-Maskenkarte, CLI-Register und Agent-Handbuch sind driftfrei. Die PostgreSQL-/UI-Einzelnachweise stehen in den Fachberichten und werden nicht durch diese isolierte Abnahme ersetzt.

Offen: 23 blocked_unreleased-Aktionen, vier open_high, vollstaendige neue Gesamt-CI, weitere PostgreSQL-/Kanal- und Browserabnahme sowie gesamte Studio-Migration. Ein generisches Mapping ist wieder freigegeben; das ist kein Abschluss aller bisherigen 20 generischen Aktionen. Keine neue Datenbank und keine abgesenkte Testschwelle fuer diese Lead-Abnahme.

## GitHub-Integration nach main und develop

Nutzerauftrag: geprueften Stand nach main integrieren und mit develop synchronisieren. Ausgang main f0392f7b2, develop fc93d03fa, Integrationscode 8942b5c7f. PR #115 zielt derzeit auf develop. Vor Merge ist der neue Gesamt-CI-Nachweis auszuwerten; keine Gesamtfreigabe aus den 173 isolierten Tests ableiten. Docs-Build 42401727530 meldete veraltetes Service-Inventar; alle drei Code-Inventare wurden neu erzeugt und ihr Driftcheck ist gruen. Merge- und Ziel-Commitkennungen werden nach tatsaechlicher Integration nachgetragen.

CI-Nachlauf 42401924684: vier Frontendfehler waren eine veraltete screen-registry.snapshot.json gegen die bereits aktuelle Capture-Projektion. Snapshot aus kanonischer Registry neu erzeugt; Generatorcheck und 33 zugehoerige Vitest-Vertraege gruen. Der require_db-Lauf meldet daneben test_studio_entity_channels.py::test_signed_http_cli_mcp_share_versioned_sql_command wegen fehlender Capability-Freigabe rot (687 bestanden); dieser reale Kanalvertrag ist vor Merge zu reparieren, keine Sperrpruefung abzuschwaechen. Main/develop-Merge weiterhin ausstehend.
