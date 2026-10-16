# Maskenfassung am neuen Geschaeftsbeleg

## Vertrag

Create akzeptiert optional screen_context mit screen_id und SHA-256 definition_hash. Keine weiteren Eingaben wie eine behauptete Freigabe oder eigene Variantenmetadaten sind erlaubt. Der Server liest die tatsaechlich aktive registrierte Maske im verifizierten Mandanten, prueft Belegart und exakten Definitionshash und uebernimmt ausschliesslich deren eigene documentVariant-/studioRelease-Referenzen. Fehlende oder fachfremde Definitionen werden abgewiesen, geaenderte Fassungen erzeugen Konflikt. Die Freigabepruefung selbst wird nicht veraendert.

Der Nachweis liegt im vorhandenen unveraenderlichen Create-Commandprotokoll, in derselben Transaktion wie der Beleg, und im gespeicherten Antwortsnapshot. GET liest ihn mandantengebunden aus dem Protokoll; spaetere Aenderungen des Registers veraendern ihn nicht. Altbelege und Aufrufe ohne Kontext erhalten keinen erfundenen Nachweis. Ein fehlender optionaler Kontext veraendert auch keinen alten Wiederholungshash.

## Abnahme

185 DocFlow-Familientests bestanden, inklusive realer nativer Versionsaufloesung, unveraenderlicher SQL-/HTTP-Wiederholung nach Registeraenderung, fremdem Mandanten, falschem Typ/Hash, gefaelschtem Freigabenachweis und Kompatibilitaet zuvor gespeicherter Replayhashes. Architekturindex299/299 Services,941/941 Routen,462/462 Endpunkte; C4-/Container-/Groessen-/Handbuchgates gruen. OpenAPI aus main:app erzeugt: genau vier Schemaaenderungen, kein Pfadwechsel. Physische Datenbank unveraendert, nur vorhandene valeo_probe mit eigenen Daten verwendet.

## Offener Integrationsschritt

Der Vertrag ist die serverseitige Grundlage. Eine noch nicht implementierte universelle Belegerfassung sendet ihn nicht automatisch. Vollstaendige Kopf-/Positionserfassung, weitere Fachkettenprofile und die Abnahme/Ablosung aller alten Einstiege bleiben offen; dieser Slice aktiviert keine Maske oder Agentenschreibaktion.
