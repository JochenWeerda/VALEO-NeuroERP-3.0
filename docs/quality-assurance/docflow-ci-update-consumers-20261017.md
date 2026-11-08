# CI-Nachlauf des DocFlow-Updatevertrags

Die Laeufe38941771526 (CI/CD) und38941771683 (Quality Gate) meldeten jeweils dieselben zwei Fehler: Ein Rechte-Negativtest sendete einen leeren Updatekoerper und erreichte daher die beabsichtigte403-Pruefung nicht; ein Freigabetest sendete Positionen ohne Pflichtversion und Auftragsschluessel. Beide erhielten korrekt422.

Die Anfragen entsprechen jetzt dem produktiven Vertrag. Der Freigabetest liest die aktuelle Version zuvor per HTTP und prueft weiterhin, dass eine folgende Aenderung die bereits erteilte Freigabe entwertet und eine neue Freigabe benoetigt. Rechteverweigerung und unveraenderte Buchungszahl werden weiterhin geprueft. Keine produktive Sicherheitsregel oder Pipeline geaendert.

105 Tests im Rechte-/Freigabe-/DocFlow-Verbund bestanden. Gemeinsame valeo_probe, keine neue Datenbank oder Container und kein Reset. Der alte GitHub-Stand hatte im uebrigen24020 bzw.24135 bestandene Tests; dies ist kein Nachweis eines bereits bestandenen Gesamtnachlaufs des neuen Commits. Security Scan, Service Security, Security Agent, Docs Build/Governance, OpenAPI sowie beide E2E-Laeufe des Versionsbindungsstands2c6c4fae1 waren erfolgreich. Neuer Gesamtnachlauf nach Push erforderlich.
