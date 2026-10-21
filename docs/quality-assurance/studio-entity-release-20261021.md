# Studio-Stammdaten: schreibendes Freigabeprofil (21.10.2026)

## Ziel und Profilgrenze

Gesamtziel bleibt ein funktionsfaehiges Studio und die CLI-Migration aller
Masken mit belastbarem Qualitaetsversprechen. Dieses Profil erweitert die
bisher ausschliesslich lesende grain.v1-Freigabe um registrierte generierte
CRM-/Agrar-/Lager-Stammdaten. Es ersetzt weder weitere Fachkettenprofile noch
die reale visuelle Abnahme oder die Migration aller bestehenden Masken.

Entitypakete deklarieren processSimulation mit profile=studio.entity.v1,
entity und contractHash. Der Server liest die gepruefte EntityRegistration
aus dem bestehenden Studio-Katalog und projiziert ausschliesslich deren
Schreib-/Agentenfreigabe. Die Definition muss exakt dieser Projektion
entsprechen. Auch kosmetische Abweichungen benoetigen derzeit einen passenden
registrierten Vertrag; unbekannte Regeln, Endpunkte oder Aktionsfelder werden
nicht als mitgeprueft ausgegeben. Deaktivierte Registrierung sperrt Freigabe
und Auslieferung bereits veroeffentlichter Entwuerfe. Unabgenommene
Authoringpakete bleiben unveraendert deaktiviert.

## Reale Simulation

Derselbe gemeinsame valeo_probe, keine neue DB/Container oder Ruecksetzung.
Zuvor migrierte, registrierte Tabellen muessen ihren Vertrags-/Runtime-Marker
besitzen. Die Simulation legt synthetische Mandanten und typgerechte Werte an
und verwendet dieselben Domaincommands wie der HTTP-Adapter. Geprueft werden
Schema, Anlegen, Lesen, Aendern, Deaktivieren, Versionskonflikt, Wiederholung,
Mandantenisolation, bestehende Rollenabhaengigkeit, unveraenderbarer
Vorher-/Nachher-Auditbeleg, Outbox und wirkungslose Vorschau. Rollenpruefung
erfolgt direkt am vorhandenen Authorizer; die signierte HTTP-/CLI-/MCP-Kette
bleibt durch die separaten, mitlaufenden Kanalvertraege nachgewiesen.

Geschaeftsdaten und Outbox bleiben innerhalb einer aeusseren
Rueckrolltransaktion. Der anschliessende Nachweis liest ueber eine andere
Verbindung: keine Simulationsmandanten, Datensaetze, Auditbelege oder
Outboxereignisse verbleiben. Kein externer Versand und keine Zahlung.
Eine Beratung unbekannter Fachregeln oder eine Finanzbuchungskette wird
aus diesem Stammdatenprofil nicht abgeleitet.

## Freigabe und Laufzeitbindung

Die bestehende unveraenderliche Historie bindet Evidenz an Tenant, Entwurf,
Kandidatenrevision, Definitionshash, Profil, vollstaendige Pflichtpruefungen
und den aktuellen Artefaktfingerprint. Gespeicherter Migrationsplan und
Vier-Augen-Publikation bleiben verpflichtend. Grain-Nachweise duerfen keine
Entityfreigabe und Entitynachweise keine Grainfreigabe legitimieren.
Ein Replay fuehrt die Simulation nicht noch einmal aus.

Die Artefaktbindung umfasst auch Bereichsrollen, Authorizer und Tenantgrenze.
Der Entity-Vertragsmarker bindet diese Quellen ebenfalls. Ein bereits
geladener HTTP-Router darf keine waehrend seiner Laufzeit geaenderte
Implementierung uebernehmen: bis zum konsistenten Neustart409, vor SQL.

## Paketierung

Der Compiler benoetigt docs/admin/table-catalog.json. Dockerfile.backend
kopiert diesen einen kanonischen Katalog; .dockerignore gibt ausschliesslich
diesen Dokumentationsinhalt frei. Entwicklung mountet dieselbe Datei read-only.
Identischer zweiter Konfigurations-COPY entfernt. Keine fremde physische
Dockerfile-Arbeitskopie ueberschrieben, keine laufenden Container neu gestartet.
Zwei Paketvertraege bestanden; der Image-Build im neuen CI-Lauf bleibt
erforderlich, ein lokaler Image-/Browsererfolg wird nicht behauptet.

## Abnahme

- 44 datenbankfreie Generator-/Profil-/Readinessvertraege bestanden (16,80s).
- 42 kombinierte SQL-/Freigabe-/Grain-/Kanalvertraege bestanden (74,00s),
 mit unveraendertem kanonischem Anwendungsquellbaum. Darunter drei neue reale
 Entityprofilketten, dauerhafte Evidenz, Replay, unabhaengige Publikation,
 Ruecknahme der Registrierung und belegter gemeinsamer Simulationslock.
- 2 Paketvertraege bestanden (1,37s).
- Alle Inventar-, Handbuch-, Architektur- und Ratschengates gruen;
 315/315 Services,472/472 Endpointmodule,931/931 Frontendrouten.
- Vor CLI-Uebernahme OpenAPI unveraendert; abschliessend ein neuer lesender
 Metadatenpfad, Altpfade unveraendert. Physischer Tabellenkatalog unveraendert;
 ausschliesslich neuer read_by-Verweis bei domain_shared.tenants.

Die SQL-Fixture deployt nur ihre eigenen exakt bezeichneten synthetischen
Tabellen im vorhandenen Pruefstand und entfernt genau diese Tabellen/Funktion
anschliessend. Andere Daten oder Ressourcen bleiben erhalten. Der erste
breite Lauf hatte40 Erfolge und einen veralteten Monkeypatch auf den frueher
lokalen Bereitstellungscheck; der finale Lauf prueft dessen gemeinsame Quelle.
20 bestehende Warnungen (unter anderem doppelte CRM-Operation-IDs) bleiben
separate Befunde, keine globale Fehlerfreiheit behauptet.

## Noch offen fuer das Gesamtziel

Reale Browserbedienung und Theme-/Lesbarkeitsabnahme des publizierten
Stammdatenprofils; Image-/CI-Nachlauf; danach Profile fuer Beleg-/Bestands-/
weitere Fachketten und CLI-Migration aller Altmasken. Ein bestandenes
Stammdatenprofil ist kein pauschales made-by-studio-Zertifikat fuer alle Masken.


## Vollstaendiger CLI-Lebenszyklus und Readiness-Korrektur

GET /api/v1/studio/entity-definitions/{name} liefert die registrierte,
serverseitig projizierte Maske. Bestehendes Authoringrecht und verifizierte
Identitaet, keine Datenwirkung oder Freischaltung. CLI:

```text
python -m valeo_cli studio entitaet-uebernehmen studio_KENNUNG --ausgabe entwurf.json
python -m valeo_cli studio pruefung ENTWURF --revision REVISION
python -m valeo_cli studio plan-speichern ENTWURF --revision REVISION
python -m valeo_cli studio simulieren ENTWURF --revision REVISION
python -m valeo_cli studio freigeben ENTWURF --revision REVISION
```

Kennung im Beispiel durch die echte registrierte kleingeschriebene Kennung
ersetzen. Jede Wiederholung verwendet denselben --idempotenz-Schluessel.
Die Freigabe verlangt weiterhin eine andere menschliche Adminidentitaet;
das Listing oder der CLI-Aufruf erteilt keine Berechtigung.

Der echte signierte HTTP-/CLI-Vertrag prueft diesen gesamten Weg, Replay,
gespeicherte bestandene Simulation, gesperrte Eigenfreigabe, maskengenauen
Abruf im eigenen/fremden Tenant und abschliessende Ruecknahme. Keine
rollenfreien Direktaufrufe als Ersatz fuer diesen Nachweis.

Dabei gefunden: generierte Aktionen hatten keine permission und scheiterten
am echten Readiness-Gate. Nun studio.entity.{domain}.write deklariert;
die vorhandene Aktionsrechteprojektion leitet diese Rechte aus require_roles
des tatsaechlichen Entityrouters ab. Kein zweites Rollenmodell, kein
Scope-Ersatz fuer Bereichsrechte. Neue UI-Pruefungen lehnen Leser, fremde
Bereiche, manager, blosse Scopes und unbekannte Namespaces ab.
44 Unitvertraege umfassen das echte Readiness-Gate ohne Ausnahme.
Kleine Tabellen zeigen Version und Erstellzeitpunkt; keine erfundenen
Fachspalten oder abgesenkte Mindestspaltengrenze.

30 UI-/Aktionsruntimevertraege in drei Dateien bestanden; TypeScript ohne
Fehler. Bestehende Rollenprojektion plus neue Namespaceprojektion gegen
Backend-Abhaengigkeiten erneut geprueft. Ein React-act-Hinweis aus bestehender
Aktionsruntime ist keine reale Browserabnahme und wird nicht als solche
ausgegeben. Der Pflichtschritt reale visuelle Abnahme bleibt bestehen.
