# POS-WebSocket: Bereinigung bei jedem Verbindungsende

## CI-Befund

CI/CD39255415584 meldete nach 24176 bestandenen Tests genau einen Fehler: test_two_provider_tenants_use_separate_terminal_registries fand nach Verbindungsende noch tenant-b:T-1. Der Endpoint entfernte seine Verbindung nur bei WebSocketDisconnect und teilweise bei normalen Exceptions. Ein asyncio-Abbruch wurde nicht behandelt; bei anderen Fehlern blieben leere Terminalgruppen stehen.

Der POS-Weg bereinigt nun im finally-Block genau die eigene Verbindung und entfernt eine Gruppe erst, wenn sie leer ist. CancelledError wird nicht abgefangen oder verschluckt. Authentifizierung, verifizierter Mandantenschluessel, Broadcastumfang, Rollen und HTTP-/WebSocket-Vertraege bleiben unveraendert. Kein Polling, kuenstlicher Sleep oder Abschwaechen der roten CI-Assertion.

## Nachweis

Vor Reparatur vier deterministische Regressionen rot, ein regulärer Disconnect gruen. Nach Reparatur 26 Faelle in tests/test_pos_websocket_cleanup.py und der unveraenderten tests/test_identity_transport.py gruen. Die neuen Lifecycle-Tests verwenden echte Task-Cancellation und pruefen Fehlerbereinigung sowie Erhalt anderer Teilnehmer und Mandanten. Nur diese lokalen Lifecycle-Tests injizieren einen bekannten Authkontext; die vorhandenen Integrationstests verwenden weiterhin echte signierte Provider-Tokens und dieselbe Produktionsmiddleware. Verifizierte Tokens, fremde Mandantenselektoren, Workflowcache-Isolation, Copilot-Kontext und parallele HTTP-Kontexte bleiben geprueft.

Keine neue Datenbank, Container, Migration, persistente Testkennung, Rechtevergabe oder API-Schemaaenderung. Eine bestehende Starlette-Deprecation-Warnung bleibt sichtbar. Die Reparatur betrifft die lokale Registry des vorhandenen POS-WebSocket-Endpoints; sie behauptet keine prozessuebergreifende Verbindungsregistry. Sonar, Runtime-Sweep und das gesondert dokumentierte Compliance-Testdesign bleiben offen. Der neue komplette GitHub-Nachlauf ist noch abzuwarten.
