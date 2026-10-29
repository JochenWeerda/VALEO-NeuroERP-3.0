# Studio: gemeinsamer Datenleseweg fuer Human, CLI und MCP

## Lieferung

Der bestehende Masken-REST-Router besitzt einen typisierten asynchronen
Datenquellenweg. CLI daten und MCP mask.data.read verwenden dieselbe
Datenquellenbindung und dieselben Antwort-/Fehlerregeln. Das neue MCP-Werkzeug
ist lesend und verwendet masks:read. Keine neue Rolle oder Schreibfreigabe.
Alte generische Schreibadapter bleiben unveraendert; ihre Dispatchweiche wurde
nur in den vorhandenen Maskenadapter delegiert, damit die Godfile-Ratsche sinkt.

## Echte Vertragsanahme

100 Faelle bestanden: neuer Datenadapter, bestehende generische MCP-Aktionen,
Toolregistry und bestehende CLI. Die Registry prueft jetzt konkrete erwartete
Werkzeuge und das Fehlen des unsicheren AP-Altadapters statt einer historischen
Gesamtzahl. Die Registry umfasst64 Werkzeuge.

Neue Integrationsfaelle nutzen RSA-signierte Identitaeten, echte JWKS-Pruefung,
die produktive Bearer-Middleware, install_tenant_bindings, reale Finanzrollen,
den echten AP-Domain-Endpunkt und PostgreSQL-Belege zweier Mandanten. HTTP-
Transporte bleiben ausschliesslich im Testprozess; Fachendpoint, SQL und
Autorisierung sind nicht ersetzt. Die gemeinsame Session-/Redispruefung ist in
der wiederverwendeten Identitaetsfixture ausdruecklich isoliert; ihre gesonderten
Widerrufstests werden dadurch nicht ersetzt.

Human-Domainabruf, gemeinsamer REST-Leseweg, echte CLI und echter MCP-HTTP-Aufruf
liefern denselben AP-Beleg. Ein fremder Beleg oder ein fremder aktiver Mandant
liefert404. Ohne Finanzleserolle liefern alle Wege403. Ohne masks:read verweigert
MCP zusaetzlich seinen eigenen Transport; dieses Scope verschafft keine
Finanzrolle. Wiederholte Leseaufrufe veraendern den Beleg nicht. Fremde
Mandantenselektoren, gefaelschte Header sowie fehlende/ungueltige Token scheitern.

Negativvertraege pruefen externe/protokollrelative URLs, Pfadnavigation,
POST-Quellen, fehlenden Objektkontext, Identitaetsparameter, Grenzen, Redirects,
Stubantworten, uebergrosse/ungueltige JSON-Antworten und Fehler ohne
Bewerber-/Beleg-/Tokeninhalte in der zurueckgegebenen Fehlermeldung.

Bestehender valeo_probe, aeussere Rollbacktransaktion; keine neue Datenbank,
Dockerinstanz, Migration oder pauschaler Reset. Der kanonische Tabellenkatalog
bleibt exakt erhalten. Keine pauschale neue Browser-/Livebereitstellung.

## Noch nicht durch diesen Meilenstein bewiesen

Keine globale made-by-Studio-Zertifizierung: Publikationsnachweise sind noch
unveraenderlich an Kandidaten und alle benoetigten Kanal-/Fachketten zu binden.
Die Abnahme belegt echten Zugriff auf den Human-Domainweg, keinen neuen
Pixel-/Browsernachweis. Lokale Tabellenprojektionen (Suche/Filter/Sortierung),
API-spezifisches Paging und alle weiteren nativen Quellen brauchen ihre eigenen
Dreikanalvertraege. Die allgemeine Funktionsmigration und die Ablösung der
handgebauten Seiten bleiben Bestandteil des unverkleinerten Gesamtziels.
