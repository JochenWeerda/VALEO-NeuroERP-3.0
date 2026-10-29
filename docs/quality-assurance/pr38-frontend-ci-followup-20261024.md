# PR38 Frontend-CI-Folgepruefung (24.10.2026)

Quelle: `artifacts/ci38-quality-7bc7e37fa.log`, Claim `PR38-CI-FOLLOWUP-20261024`.
Der Lauf meldet 54 fehlgeschlagene Testdateien, 227 fehlgeschlagene und 1.489 bestandene Tests; eine der 54 Dateien scheitert schon beim Import.

## Ursachen nach Fehlersignatur

- 183 der 227 Testfehler vergleichen Quelltext eines duennen nativen Seitenwrappers mit frueherer seitenspezifischer Implementierung (163 `NativeListPage`, 20 Stamm-Detailwrapper). Weitere 31 sind andere Quelltext-/String-Erwartungen. Diese 214 Fehler sind **nicht** pauschal als veraltet abgenommen: Ein Teil kann einen echten Verlust von Aktionen, Feldern oder Navigation anzeigen. Die Erwartung muss jeweils gegen ScreenDefinition, zentrale Runtime und gerenderte Bedienung geprueft werden.
- 13 Testfehler liegen ausserhalb dieser String-Vergleiche: drei Start-Dashboard-Bedienfaelle, neun Workspace-Live-Signals-Faelle und ein Scheindatenbefund in `pages/annahme/lkw-registrierung-legacy.tsx`. Der Bankkonto-Formtest scheitert zusaetzlich bereits beim Import, weil sein vollstaendiger Mask-Builder-Mock den neuen Export `createStammNativeDetailPage` nicht bereitstellt. Das ist kein Beleg fuer korrektes Bankkonto-Verhalten; die Fachparitaet bleibt zu pruefen.
- Die Bestell-Navigationssuite enthielt zwei echte Integrationsfehler: Die Liste referenzierte die nicht registrierte ID `einkauf/bestellungen-liste` statt `einkauf/bestellungen`, und Anlegen/Retry/Flow-Spine-Checkpoint benutzten die Plural-Detailroute statt `/einkauf/bestellung/{id}`. Beide Wege sind im Reparatur-View korrigiert.

## Abnahme des begrenzten Bestell-Slices

`mask-bestellung-nav-native.test.ts` und `einkauf/bestellung-anlegen.test.tsx`: 2 Dateien, 16 Tests bestanden. Der bestehende Verhaltenstest prueft nun nach dem Speichern sowohl den `resume_route` im Flow-Spine-Checkpoint als auch die Navigation zur kanonischen Detailroute; beim Retry prueft er weiterhin, dass keine zweite Bestellung angelegt wird, und jetzt auch dessen Zielroute. ESLint fuer die beiden geaenderten Seiten meldet keine Fehler (Testdatei wird durch die bestehende Ignore-Regel ausgenommen).

Im ersten begrenzten Slice wurden keine anderen roten Fachfaelle durch Testlockerung oder Entfernung geschlossen. Ein vollstaendiger CI-Neulauf ist nach Integration erforderlich.

## Folgepruefung der Laufzeitfehler

- Workspace-SSE: Die neun Fehler liessen sich im Reparatur-View reproduzieren. `live-signals.ts` rief `appendSseAuthToken` aus `lib/sse-client.ts` auf, der View-Stand exportierte den bereits im Root-Stand vorhandenen Helper aber nicht. Der fehlende Helper-Export ist im View ergaenzt. Die bestehende URL-/Fallback-Semantik des allgemeinen `SSEClient` bleibt dabei unveraendert. Beide Workspace-Suiten sind jetzt mit 11/11 Tests gruen; der Null-Token-Fall verhindert weiterhin einen unautorisierten SSE-Connect.
- Scheindaten: Die aktive LKW-Registrierung lud Artikel bereits aus der API. Nur die unreferenzierte Legacy-Kopie stellte noch sieben erfundene Artikel mit dem Namen als ID bereit. Diese Liste ist entfernt, die Auswahl startet leer bis echte API-Daten eintreffen. Security- und LKW-Bedientests sind mit 5/5 gruen. Die kanonische Route wurde nicht geaendert.
- Bankkonto: `bankkonten-stamm.tsx` waehlt bei Neuanlage die Legacy-Form. Der IBAN-Lookup-Vertragstest belaesst diesen echten Route-Entrypoint und den `createStammNativeDetailPage`-Export; sein Mask-Builder-Mock ist nun partiell und ersetzt nur `ObjectPage`. Der Verhaltenstest ist gruen: Die Route laedt die Create-Form, Lookup aktualisiert nur den lokalen Entwurf und speichert nicht implizit.
- Start-Dashboard: Alle drei Bedientests bleiben im Reparatur-View rot. Die dortige Seite rendert nur den nativen Cockpit-Wrapper; das Test-DOM zeigt ein leeres `<h1>` und weder Schnellaktionen noch Anpassung oder Katalogsuche. Das ist eine echte Funktions-/Integrationsluecke und keine veraltete String-Erwartung. Die vom Lead geschuetzte Root-Seite wurde nicht bearbeitet.

Diese gezielte Folgepruefung umfasst 11 Workspace-, 5 Security/LKW- und 1 Bankkonto-Test. Die Dashboard-Abnahme sowie der volle CI-Neulauf stehen aus.
