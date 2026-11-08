# Ausgangsrechnung: Anlage ohne Überschreiben

Die bestehende Ausgangsrechnungsanlage konnte eine vorhandene Rechnung desselben Mandanten durch erneute POST-Anlage überschreiben. Auch der In-Memory-Ersatz meldete bei fehlendem Repository Erfolg ohne dauerhafte Speicherung.

Die Anlage prüft vorhandene Nummern mandantenübergreifend und verwendet `create_only=True` innerhalb der bestehenden Transaktion; ein transaktionaler Advisory-Lock serialisiert gleichzeitige Aufrufe dieses Anlagewegs für dieselbe Nummer. Ein konkurrierender Insert wird als 409 behandelt; ein fehlender Dokumentspeicher als 503. Der Aktualisierungsweg bleibt getrennt. Ein 409 ist kein idempotenter Replay-Erfolg; ein gemeinsamer sicherer Wiederholungsvertrag für UI, CLI und MCP bleibt offen.

Abnahme ohne Datenbank: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_sales_inv_dn_link_001.py --noconftest -p pytest_asyncio.plugin -p no:cacheprovider -q -o addopts=''` — 7 bestanden, darunter gleicher/fremder Mandant, konkurrierende Dublette, Sperrenreihenfolge und fehlendes Repository. Kein Datenbank-, Container- oder Schemaeingriff. Die Tests sind isolierte Vertragsprüfungen und kein realer PostgreSQL-Race-Nachweis.

Die beiden Rechnungserfassungsrouten bleiben hinsichtlich zentraler Positionsverarbeitung und CLI-/MCP-Parität offen. Der bestehende DocFlow-Create ist auf den Sichtprüfungsmandanten begrenzt; eine Gleichsetzung der Speicher oder unbedingte Routenweiterleitung ist nicht abgenommen.
