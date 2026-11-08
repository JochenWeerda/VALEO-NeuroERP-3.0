# Studio-CLI-Stapel und lokale Erreichbarkeit, 20.10.2026

## Umfang und Nachweis

Vollstaendiger Quellenabruf, hashgebundener Uebernahmeplan, stabil wiederholbare
Ausgangsimporte und lokale localhost-Verbindung. Keine neue API, Datenbank,
Migration, Dockerinstanz oder Publikationsabkuerzung.

63 Vertraege bestanden: Studio-CLI, allgemeine CLI und native Studio-Uebernahme.
Der neue Integrationsfall verarbeitet den gesamten registrierten Quellbestand
(139 Definitionen) ueber die CLI, den echten HTTP-Router und den echten
PostgreSQL-Studio-Speicher. Wiederholung erzeugt keine zweite Fassung oder
Historienzeile. Fremder Mandant bleibt leer; alle Ausgangsfassungen bleiben draft
und nicht freigabefaehig. Eine aeussere Transaktion rollt eigene Daten vollstaendig
zurueck. Gemeinsamer valeo_probe, Status merge_hr_tax_20261019, kein Reset.
Testidentitaet ist in diesem Integrationsfall explizit ersetzt; dieser Test allein
ist kein Nachweis einer realen OIDC-Anmeldung.

Transport-/CLI-Negativvertraege umfassen205 Quellen ueber drei Seiten,
Speicherfehler und Wiederaufnahme, geaenderte/fehlende/zusaetzliche/doppelte Quellen,
veraenderte Plandaten, verweigerte Berechtigung und Schutz der Plandatei.
Der Massenlauf ruft weder publish noch simulate noch Geschaeftscommands auf.

## Reale lokale Erreichbarkeit

Ursache der Timeouts: localhost ueber ::1 akzeptiert Verbindungen, liefert aber
keine Antwort. 127.0.0.1 liefert /health200 und /api/v1/studio/native-sources401;
die Container-Healthpruefung ist ebenfalls200. IPv4-Quellbindung fuer den lokalen
CLI-Transport liefert dieselben Ergebnisse unter der unveraenderten localhost-URL.
Keycloak-Discovery liefert200. Keine Dienstneustarts/OS-Netzwerkaenderung.

Mit der bereits genehmigten synthetischen Testkennung wurde der regulaere
Authorization-Code-/PKCE-Weg mit State und Nonce verwendet. Kennwort/Token nur
im RAM. Der lokale Quellenabruf per CLI ist erfolgreich:117 Quellen im laufenden
Backend. CLI-Sitzung und Providerkonfiguration wurden nicht veraendert. Anschliessend wurden115 noch fehlende Ausgangsfassungen mit stabilen
CLI-Idempotenzschluesseln importiert. Zwei vorhandene Zielentwuerfe wurden erhalten,
darunter eine nicht zum aktuellen Quellhash passende Fassung. Alle117 aktuell
registrierten Quellen haben damit eine Ausgangsfassung im Testmandanten; die115
neuen Fassungen sind draft und eligible_for_release=false. Eine anschliessende neue PKCE-Anmeldung bestaetigte alle117 Fassungen erneut:
null neue Entwuerfe,117 erhalten. Die verwendete Pruefsitzung wurde beim Provider
regulaer abgemeldet (HTTP204). Keine Aktivierung,
Buchung oder Ausweitung von Benutzerrechten. Der lokale Ergebnisnachweis enthaelt
nur die Anzahlen; Zugangsdaten bleiben ausserhalb des Git-Bestands.

## Grenzen und weiteres Vorgehen

Die laufende lokale API verwendet den aelteren gemounteten Quellbestand;
der aktuelle Git-Quellbestand und dessen SQL-Vertrag sind getrennt geprueft.
Ein Quellimport ersetzt keine aktivierte, fachlich abgenommene Studio-Maske.
Handgebaute/Altmuster-Seiten und ihre fachlichen Tests bleiben erhalten, bis
Definition, Commands, fachliche Wirkung und Darstellungsabnahme gleichwertig sind.
Der parallele MASK-STUDIO-ROLLOUT-Dateibesitz bleibt unangetastet.
