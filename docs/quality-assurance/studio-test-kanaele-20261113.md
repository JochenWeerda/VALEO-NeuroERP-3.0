# Studio-Kanalvertraege — 13.11.2026

Die neue Testgruppe `tests/test_studio_channel_outcomes.py` verwendet eine vom
Studio-Compiler generierte, ausdruecklich fuer die synthetische Testrolle
registrierte Aktion und ihr echtes Eingabeschema. Direkter HTTP-Aufruf, CLI und
MCP-Aktionsadapter erreichen denselben kontrollierten FastAPI-Zielweg.
Die Tests vergleichen Autorisierungsheader, Eingaben und Idempotenzschluessel;
sie pruefen keine Idempotenzwirkung des synthetischen Ziels.

Geprueft werden HTTP 403, eine strukturierte 409-Freigabeablehnung und eine
422-Validierungsliste sowie Erfolg und ausdruecklicher Misserfolg bei HTTP 200.
CLI-Exitcode und MCP-Ergebnis duerfen einen Misserfolg nicht als Erfolg melden.
Bereits oeffentliche fachliche Ablehnungsdetails bleiben transporttreu erhalten.

Gegenprobe vor der Korrektur: **2 failed, 3 passed**. Der MCP-Adapter ersetzte
strukturierte Objekte und Listen durch `Aktion abgelehnt`; die beiden negativen
Vertraege fanden genau diesen Unterschied. Der Fix erhaelt die strukturierten
Details des Zielwegs. Statuscode, Autorisierung und Ausfuehrungsfreigabe werden
dadurch nicht veraendert.

Nachlauf mit `--noconftest -p no:cacheprovider -o addopts=`:
`tests/test_studio_channel_outcomes.py`, `tests/test_mcp_write_capability.py`
und `tests/test_agent_autonomie_unit.py`: **62 bestanden**, Exit 0.
Eine bestehende Starlette-TestClient-Abkuendigungswarnung blieb ohne Testfehler.
Die unmittelbar betroffenen Bestandstests `test_mcp_mask_actions.py` und
`test_valeo_cli_generated_entities.py` bestanden zusaetzlich mit **33 Faellen**.

Grenzen: Der Zielweg gibt kontrollierte Geschaeftsergebnisse zurueck. Die
Identitaetspruefung und Definitionsbeschaffung sind simulierte Testgrenzen;
CLI/MCP-Adapter und Capabilitypruefung laufen echt. Der aeussere MCP-Engine-/
Protokollweg, OIDC, echte Datenbankrollen, SQL-Wirkung, RLS, Freigabepersistenz
und Browserdialoge sind damit nicht abgenommen. Dafuer bleiben insbesondere
`tests/test_studio_entity_channels.py` und die angemeldete Browserabnahme
erforderlich. Keine Datenbank und kein Container wurden angelegt oder benutzt.

Die [Teststrategie](studio-teststrategie.md) trennt Klassen-, Varianten-, Fach-
und Adapterbelege. Ein positiver Teillauf oder eine Coverage-Erhoehung ist keine
Sonar-Gesamtfreigabe.
