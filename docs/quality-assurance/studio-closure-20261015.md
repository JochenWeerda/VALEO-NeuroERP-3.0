---
title: Studio-Vertraege, Historie und gesicherte Prozesssimulation
type: reference
owner: Codex
status: in arbeit
last_reviewed: 2026-10-15
---

# Abnahme und Betriebsgrenzen

38 gezielte Backendfaelle bestanden, darunter vier echte SQL-Vertraege auf dem vorhandenen valeo_probe (Revision portal_lohndienst_persistenz_20261014), ohne neue Datenbank, Container oder Reset. Zwoelf Studio-Oberflaechenfaelle bestanden. Die real ausgefuehrte grain.v1-Kette hat dreizehn Pflichtchecks; die eigenen Daten verschwinden durch aeussere Transaktionsruecknahme. Lebenszyklustests mit kontrolliertem Nachweisdoppel gelten ausdruecklich nicht als Buchungskettennachweis.

Zwei weitere advisory POSTs verwenden gemeinsame strikte Modelle in REST und MCP. Sie verlangen ausdruecklichen Kontext und geben keine Geschaeftsfreigabe. Der bestehende Bindungsabgleich umfasst elf lesende Vertraege und sechs kanonische POST-Eingaben; kein Nachweis saemtlicher ERP-Schreibkanaele.

Historie und Diff sind native ScreenDefinitions in der bestehenden Meridian-Runtime. JSON-Differenzen unterscheiden fehlende Werte, boolesche Werte und Zahlen. Unveraenderliche Historieneintraege sind an Mandant und Entwurf gebunden. Cache-Invalidierung verhindert eine veraltete Anzeige nach dem Speichern.

Die reale Browserabnahme wies einen weiteren Revisionsbruch durch UTC-/Datenbank-Zeitzonendarstellung nach. Zeitpunkte werden fuer den Revisionshash jetzt UTC-normalisiert. Der SQL-Vertrag prueft, dass die Review-Fassung den unveraenderlichen Ausgangseintrag wirklich findet. Alte Entwicklungsereignisse mit bereits falschem Verweis werden nicht umgeschrieben oder als vollstaendig bescheinigt; deren Vergleich verweigert sich mit 409. Neue Fassungen werden mit konsistenten Revisionsverknuepfungen erzeugt.

Die zentrale Statusgrenze sperrt fehlende, gescheiterte, fremde oder veraltete Simulationen. Ein erneuter identischer Aufruf wirkt einmal; ein quittierter erneuter Simulationswunsch bekommt einen neuen Schluessel. Ein belegter Pruefstand antwortet 429 mit Retry-After und legt keinen Fehlernachweis an. Simulation und Freigabe pruefen die aktuell geladenen Schnittstellenprojektionen; nach Fach-/Vertragsaenderungen ist ein Serverneustart und ein neuer Nachweis erforderlich.

Die Annahme verwendet den bestehenden transaktionalen Nummernkreis self_billing. Er muss je Mandant eingerichtet sein; maximal zehn Zeichen lassen Platz fuer SB- und STORNO- im Journal. Standalone-Entwurfsnummern und IDs verwenden volle UUIDs. Zwei Annahmen am gleichen Tag werden in der echten Kette getrennt verbucht. Der Eingangssteuerschluessel agrar.self_billing.tax_code muss explizit konfiguriert sein. Fehlende Konfiguration scheitert vor Abschluss, ohne Zwischencommit.

Ernteannahme-Writes verlangen bestehende beleg_write-Rechte, Reads beleg_read. Der Audit-Autor stammt nur aus verifizierten Tokenclaims. Schutz gegen fremde Artikel/Lager/Wiegescheine/Kontrakte, Identitaetsfelder im Update und Neuberechnung festgeschriebener Annahmen ist getestet. Freigaben werden je Mandant transaktional serialisiert; Vertragsfehler werden nicht mehr verschluckt. Null Prozent bleibt ein ausdruecklicher Satz.

## Offen und geschuetzt

Browserabnahme am 2026-10-15 mit der bereits genehmigten synthetischen EINKAUF_BEARBEITEN-Kennung: Neuanmeldung, lesender Agrar-Entwurf, zwei gespeicherte Fassungen, sofort aktualisierte Historie, positiver /title-Vergleich, Review und reale grain.v1-Simulation bestanden. Die Freigabeschaltflaeche bleibt entsprechend der Serverrechte gesperrt. Screenshots lokal unter artifacts/studio-browser-20261015; keine Zugangsdaten im Repository. Nach Zeitnormalisierung: vier echte SQL-Vertraege und elf weitere Lebenszyklus-/Historienfaelle bestanden; acht aeltere optionale SQL-Faelle dieses Nachlaufs mangels expliziter Fixture-URL uebersprungen und nicht als Abnahme gezaehlt. Der zusaetzliche UTC/Offset-Vertrag bestand separat. Zwoelf UI-Faelle nach Staging-Formatierung erneut bestanden.

Nachlauf ohne optionale SQL-Luecke: TEST_DATABASE_URL und DATABASE_URL im isolierten Testprozess ausdruecklich auf denselben vorhandenen valeo_probe gesetzt; alle acht bisherigen SQL-Lebenszyklusfaelle bestanden mit strikter Datenbankanforderung, keine Skips. Die Vorab-Abweisung bei abweichender URL ist die beabsichtigte Testschutzgrenze. Ein in der Browserabnahme veralteter Vorschaumaskentitel wurde zentral in schemaVolatility korrigiert. Neuer Titel erzeugt bei gleicher Screen-ID einen neuen RenderPlan; alle 28 Compiler-/Studio-Oberflaechenfaelle bestanden. Die anschliessende weitere Browserbeobachtung wurde durch einen Browsersteuerungs-Timeout unterbrochen; keine zusaetzliche positive Sichtabnahme dieser letzten Titelkorrektur behauptet.

Die positive Browser-Vieraugenabnahme wartet auf die ausdrueckliche Freigabe einer temporaeren synthetischen Admin-Prueferkennung nur fuer den bestehenden Sichtpruefungsmandanten. Die bestehende EINKAUF_BEARBEITEN-Kennung wird nicht erweitert. Persoenliche Zugangsdaten werden nicht committet.

Unmodellierte Fachcommands, fachliche Regelvarianten und editierbare Agentenfelder bleiben gesperrt. Der feste Basispfad ist kein Nachweis aller ERP-Prozesse. CI-GRUEN-20261014 gehoert dem parallelen Claude-Claim; diese gezielten Ergebnisse behaupten keine gruene Gesamt-CI oder vollstaendige Testabdeckung. Fremde Arbeitskopien generierter Artefakte bleiben erhalten; eigene Projektionen werden auf aktuellen HEAD integriert.
