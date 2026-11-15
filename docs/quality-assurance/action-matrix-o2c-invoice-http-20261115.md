---
title: Action-Matrix O2C — Lieferschein zu Rechnungsbeleg per HTTP
status: in arbeit
last_reviewed: 2026-11-15
owner: Codex
---

# ACTION-MATRIX-O2C-INVOICE-HTTP-20261115

Der neue eigenständige Fall `o2c-003 @critical — delivery becomes one persisted invoice without double billing`
in `playwright-tests/specs/e2e-matrix/o2c-semantic-chain.spec.ts` erweitert die bereits im CI
auf Quellkopf `2e8d53caa` belegte O2C-001/002-Kette. Er legt über die vorhandene
Fachrollenkennung `VALEO_USER_POWER` einen eigenen Kunden und Auftrag an, wandelt
vier von zehn Einheiten der ersten Auftragsposition in einen Lieferschein und danach
dessen vier Einheiten in einen Rechnungsbeleg um. Die zweite Auftragsposition bleibt
unberührt. Eigene UUID-basierte Nummern und Idempotenzschlüssel trennen Wiederholungen.

Kanonische HTTP-Wege sind `GET /api/v1/docflow/{id}/conversion-options?target_doc_type=sales_invoice`,
`POST /api/v1/docflow/{id}/convert` mit `target_doc_type=sales_invoice`,
`expected_version`, `quantities_by_source_item_id` und `idempotency_key` sowie ein
frischer `GET /api/v1/docflow/{invoice_id}`. Der Test verlangt exakte Quell-ID,
Quellpositions-ID, Kunden- und Mandanten-ID, Menge 4 und Nettosumme 80. Er liest
Restmenge 0 und die unveränderten Positionen von Auftrag und Lieferschein zurück.
Wiederholung desselben Kommandos muss dieselbe Rechnungs-ID liefern.

Vor der erfolgreichen Umwandlung prüft der Fall gültige Kommandos ohne Token (401),
mit READ-Kennung (403), mit fremder Mandantenangabe in Header und Query (je 403),
mit veralteter Version (409), mit Menge 5 aus Lieferscheinmenge 4 (400) und eine
Direktrechnung aus einem Auftrag mit vorhandener Lieferung (409). Danach werden
Quellbelege und Umwandlungsoptionen erneut gelesen. Diese Gegenproben beruhen auf
`app/api/v1/endpoints/docflow.py`, `app/auth/beleg_roles.py` und
`app/services/docflow_service.py` (`delivery_to_invoice`, Rechnungsweg und
Mengen-/Versionsprüfung). Bereits vorhandene Backend-Verträge:
`tests/test_docflow_einkauf_gutschrift.py` für Doppelberechnung und
`tests/test_docflow_steuerschluessel.py` für Steuerübernahme.

Voraussetzungen sind dieselben echten signierten POWER-/READ-Kennungen, der
Testmandant und die vollständig migrierte Job-Datenbank wie beim bestehenden
O2C-HTTP-Nachweis. Die Kennungen werden nicht im Test erzeugt; ihre tatsächlich
zugewiesenen Rollen müssen `SALES_BEARBEITEN` beziehungsweise nur Leserechte
enthalten. Der Test verwendet die bestehende Kundenanlage und gefilterte
Partnerauswahl; er erfindet keine Kunden- oder Beleg-ID.

Der Zielbeleg ist nach der Umwandlung ein persistierter `sales_invoice` mit Status
`open`. Ausstellung, PDF, Finanzbuchung, offener Posten und Zahlung sind keine
Wirkung dieses Falls. Der alte Matrixeintrag `POST /verkauf/rechnungen` ist eine
deklarative, nicht kanonische API-Angabe. Der Status `partial` wird durch diesen
Quelländerungsstand nicht angehoben. Für eine Matrix-Abnahme sind ein echter
SHA-gebundener kritischer HTTP-Lauf und eine bewusste Entscheidung über den
Umfang von `o2c-003` erforderlich. Eine echte Fremdtoken-Prüfung benötigt einen
zweiten Testmandanten; Mandantenspoofing allein ersetzt sie nicht.

Lokale Prüfung: `npx tsc --noEmit --skipLibCheck --target ES2022 --module commonjs
--moduleResolution node --types node playwright-tests/specs/e2e-matrix/o2c-semantic-chain.spec.ts`
bestand. `npx playwright test --config=playwright.config.critical.ts --list
--workers=2 o2c-semantic-chain.spec.ts` sammelte genau drei `@critical`-Fälle.
Beides führt keine HTTP-Fachaktion aus. Npm meldete lediglich die bereits
bekannten Konfigurationshinweise zu `public-hoist-pattern` und `shamefully-hoist`.

Lead-Review: Neben einer widerspruechlichen zukuenftigen Version wird nach der
erfolgreichen Umwandlung auch die tatsaechlich veraltete Ursprungsversion mit
einem neuen Idempotenzschluessel abgewiesen. Das unveraenderte Auftrags-Readback
wird bereits nach den verworfenen Kommandos geprueft. Enge TypeScript-Pruefung
und Sammlung der drei Faelle wurden nach diesem Review erneut erfolgreich
ausgefuehrt; weiterhin kein lokaler HTTP-/Datenbanklauf.

## Naechste fachliche Grenze

Die Umwandlung erzeugt bereits einen offenen Beleg. `release` akzeptiert dagegen
nur `draft` (docflow_service.py, release); dieser Weg braucht deshalb keinen
zusaetzlich erfundenen Freigabeschritt. Der aktuelle Auftrag verwendet Steuer 0
ohne Steuerschluessel und belegt keine steuerlich buchbare Rechnung.

Fuer den getrennten Buchungsnachweis muss zuerst ein gueltiger mandanteneigener
Steuerschluessel ueber eine vorhandene Quelle bezogen und auf den Auftrag gesetzt
werden. Seine Uebernahme durch Lieferung und Rechnung ist zu pruefen. Danach kann
POST /api/v1/docflow/{id}/post mit expected_version und Idempotenzschluessel die
Finanzwirkung ausloesen; SalesPostingService erzeugt Journal und Debitoren-OP.
Der OP-Readback benoetigt zusaetzlich die vorhandene Finanzleserolle. Kritische
Befunde verlangen eine unabhaengige, an den Beleg gebundene Freigabe; fuer normale
R2-Vorgaenge keine pauschale zusaetzliche Freigabe anlegen.

Der ZUGFeRD-Weg unter sales/invoices liest das gesonderte Document Repository.
Die DocFlow-Umwandlung allein beweist dessen Anbindung nicht. record-print/export
sind Metadatenkommandos, keine PDF-Erzeugung. Eine PDF-/Archivabnahme muss deshalb
den tatsaechlichen kanonischen DocFlow-Druckweg gesondert nachweisen, statt die
Existenz eines Endpunkts als Wirkung auszugeben. Diese Hinweise sind Codeanalyse,
keine ausgefuehrten Buchungs- oder PDF-Nachweise.
