# Studio/Inbox: nativer Eingangsrechnungs-Prefill (2026-10-26)

## Befund und Umsetzung

- Der bisherige Create-Link `/einkauf/rechnung-eingang-erfassung/neu` hatte keine registrierte Route. Die Inbox verweist nun auf `/belege/purchase_invoice/neu?inbox=<ID>`. Die vorhandene Beleg-Route führt über `BelegPage`, `UniversalNativeDetailPage` und `UniversalNativeCreatePage` in den Single Mask Builder.
- Die Navigation speichert keine Prefill-Geschäftsdaten. Producer löschen einen möglicherweise vorhandenen Legacy-Sessionwert. Nur die Inbox-ID steht im Link.
- Die native Create-Maske ruft für diese ID den geschützten `POST /api/mcp/documents/inbox/{id}/prepare` auf. Das Formular bleibt bis zur frischen Antwort gesperrt. Die Antwort muss `ok=true`, `booking_allowed=false`, dieselbe Item-/Prefill-/Source-ID, `EINGANGSRECHNUNG`, `purchase_invoice`, `can_open=true`, eine aktivierte `open_mask`-Aktion und die Nichtbuchungsinvarianten erfüllen. 403/404 und unpassende Antworten übernehmen keine Werte.
- Die rohe `item.command.prefill.schema` wird vor der Normalisierung geprüft; ältere oder unbekannte Schemata werden abgewiesen.
- Nur editierbare `creation.fields` aus den bestehenden Kopffeld-Mappings werden über die `creation.defaults` gelegt. Der Nutzer kann sie ändern; erst der explizite Speichern-Klick ruft DocFlow auf. Definition-Hash, Variantenkontext, Idempotenzschlüssel und exakte Draft-Antwortprüfung der Create-Maske bleiben bestehen.
- Der Prepare-Query-Schlüssel enthält Inbox-ID, Masken-ID, angemeldetes Subjekt und die Mandantenkennung aus dem aktuellen Access-Token (`tenantFromToken`); der ungeprüfte Browser-Mandantenwert bestimmt die Isolierung nicht. Ohne lesbaren Token-Mandanten wird bei Inbox-Prefill kein Request und kein Formular freigegeben. `gcTime=0`, kein persistierter Query-Cache; bei erneutem Fetch bleibt die Form verborgen, bis die frische Antwort vorliegt. Der Server prüft Auth und Tenant verbindlich. Kein Token oder Signaturwert wird im Query-Schlüssel oder in Logs abgelegt.
- Die Forminitialisierung ist an Inbox-ID, Subjekt, Token-Mandant und Definition-Hash gebunden, nicht an den Zeitpunkt des Query-Ergebnisses. Ein Refetch derselben Identität überschreibt daher keine bearbeiteten Felder. Ein Tenantwechsel bei gleichem Subjekt sperrt sofort die alte Form und lädt neu; ein Token-Refresh im selben Tenant erhält die Eingaben.

## Abnahme

- Frontend Vitest 4.1.12 aus vorhandenen frozen `node_modules`: **10 Dateien, 91 Tests grün**, `--maxWorkers=2`. Darunter echte `UniversalNativeCreatePage`-Render-/Eingabefälle, expliziter Draft-Save, Auth- und Tenantwechsel bei gleichem Subjekt, fehlender Token-Mandant, Token-Refresh, Refetch nach Benutzereingabe, altes Prefill-Schema, falsche ID/Art/Variante, Booking-Flag, fehlende Berechtigung sowie 403/404. Die Token-Claims-Fixture ist nur ein synthetischer UI-Testwert; HTTP und Auth sind gemockt.
- Fokussierter TypeScript-Check `tsc --noEmit --project packages/frontend-web/tsconfig.typecheck.json`: **grün**.
- Keine Datenbank, Container, Installation oder Buchung ausgeführt. Der produktive HTTP-Pfad wurde hier nicht mit echtem Browser-Login geprüft; die Renderfälle ersetzen nur HTTP/Auth durch synthetische Antworten.

## Integrationshinweis

Die Inbox-Backendantwort liefert weiter `proposal.target_route` für den bestehenden Listen-Host. Die Frontendentscheidung leitet ausschließlich für die Eingangsrechnung auf den registrierten Create-Pfad um. Andere Dokumentarten behalten ihre bisherigen Übersichts-/Detailentscheidungen.
