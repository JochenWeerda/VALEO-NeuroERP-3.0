# Versandwege senden wirklich oder nennen den Grund (Slice VERSANDWEGE-ECHT-20261008)

Stand: 2026-10-11 · Folgeslice zu [Postfächer mit Microsoft 365](postfach-microsoft365-20261008.md)

## Auftrag

Vier Wege meldeten Erfolg, ohne dass etwas das Haus verließ:

| Weg | Vorher | Jetzt |
|---|---|---|
| **Bestellung versenden** | Ohne `SMTP_HOST` schrieb der Dienst „DEV-MODE simuliert“ ins Protokoll und meldete `gesendet`. Fax und EDI ohne Einrichtung meldeten `manuell`, und die Bestellung stand trotzdem auf „versandt“. | E-Mail geht über das Postfach `einkauf` des Mandanten. Fax und EDI ohne Einrichtung melden `nicht_eingerichtet` (503). „Versandt“ gibt es nur nach Annahme durch den Server oder bei bewusst gewähltem Postversand. Jeder Versand steht im Reiter Kommunikation. Die PDF hängt an (SMTP und Microsoft Graph). |
| **Preisanfrage (RFQ)** | Setzte `VERSENDET` und meldete `suppliers_notified`, ohne eine Mail zu schicken. | Eine Mail je Lieferant; `VERSENDET` erst, wenn mindestens einer erreicht wurde. Die Antwort nennt je Lieferant, ob es geklappt hat und warum nicht. |
| **Anfrage (BANF) an Lieferanten** | Die Maskenbrücke antwortete `sent: true`, ohne zu senden oder zu speichern. Ein zweiter, verdeckter Weg in `app/einkauf/router.py` setzte nur `FREIGEGEBEN`. | Ein Weg: Mail je Lieferant, danach `ANGEBOTSPHASE`. Der verdeckte Weg ist entfernt. „Portal“ als Versandweg gab es nie und wird abgelehnt (422). |
| **Mahnung senden** | Setzte `sent`, ohne dass etwas hinausging. In der Maske löste schon „Speichern“ den Versand aus, und „An Inkasso übergeben“ rief denselben Weg. | E-Mail über das Postfach `fibu` an die Adresse des Debitors, oder Postversand wird festgehalten (`versand_art`, `empfaenger`). In der Maske speichert „Speichern“ nur noch; die Inkasso-Aktion ist entfernt, weil es keinen Inkassoweg gibt. |

Fehler tragen den Grund: 422 ohne Empfänger oder Adresse, 403 ohne Freigabe für das Postfach,
503 ohne eingerichtetes Postfach, 502 bei Ablehnung durch den Mailserver, 409 bei bezahlter
Mahnung. In jedem dieser Fälle bleibt der Status, wie er war.

## Dringlichkeit

`origin/main` rief in `einkauf_bestellvorschlag.py` seit dem 09.10.2026 bereits
`versende_bestellung_svc(..., nutzer=…)` auf; die Service-Seite lag nur unkommittiert im
Arbeitsbaum. `POST /einkauf/bestellungen/{id}/versenden` endete im Lieferstand mit einem
`TypeError`. Dieser Commit schließt die Lücke.

## Unterwegs gefunden

- **Mahnung ohne Fälligkeitsdatum:** `due_date` und `payment_deadline` sind in der Tabelle nullbar,
  im Antwortmodell waren sie Pflicht. Die Mail ging hinaus, der Status wurde gesetzt, die Antwort
  war 500. Beide Felder sind im Antwortmodell jetzt optional; dieselbe Zeile kippte vorher auch
  die Liste.
- **`einkauf_anfragen` ohne Mandant:** Die Tabelle wurde ohne `tenant_id` angelegt, jeder Zugriff
  filtert aber danach. Auf einer frischen Datenbank scheiterte jeder Aufruf. `get_anfrage` las
  zudem ohne Mandantenfilter – jede Anfrage jedes Mandanten.
- **Offene Posten im Mahnlauf:** Die Abfragen lasen nur die englischen Spalten (`debtor_id`,
  `open_amount`, `due_date`); Zeilen, die nur die deutschen führen (`kunde_id`, `offen`,
  `faelligkeit`), wurden nie gemahnt.
- **Postfach-Maske (aus MCP-MASK-CE-BATCH3):** Das Backend führt für „Postfach speichern“ seit dem
  09.10.2026 `commandEndpoint`, `permission` und `inputFields`, der TS-Spiegel nicht; der Vertrag
  `test_der_ts_spiegel_entspricht_dem_backend` war auf `main` rot. Der Spiegel ist nachgezogen,
  `ScreenActionDefinition` kennt `localEffect`, und die Seite gewährt `admin.postfach.write` –
  sonst hätte der Mask Builder den Speichern-Knopf ausgeblendet.

## Schema

Migration `versandwege_echt_20261008`, umgehängt hinter `fuhrpark_tenant_ce_20261009` (ein Head):

- `einkauf_anfragen.tenant_id` (`NOT NULL`; es gab nie eine Zeile ohne Mandant, weil das Anlegen
  nie gelang), Anfragenummer je Mandant eindeutig statt systemweit.
- `domain_erp.dunning_notices.versand_art` (`email` oder `post`, Prüfbedingung) und `empfaenger`.

Frisch geprüft gegen `valeo_probe` (Upgrade von `fuhrpark_tenant_ce_20261009`). In der gewachsenen
`valeo_neuro_erp` lief die Migration am 08.10.2026; beide Tabellen sind dort leer.

## Nachweis

Alles im isolierten Lieferstand (HEAD-Worktree plus die Dateien dieses Slices), gegen `valeo_probe`:

- `tests/test_versandwege_vertrag.py`: **27 Verträge grün.** SMTP ist an `smtplib` ersetzt;
  Postfachwahl, Freigaben, Statuswechsel, Kommunikationseintrag und Mandantentrennung laufen echt.
  Je Weg: Erfolg, ohne Postfach (503), ohne Adresse (422), Ablehnung durch den Server (502);
  dazu Freigabe (403), bezahlte Mahnung (409), fremder Mandant (404), Anhang, zwei Schemaverträge.
- Nachbarschaft: `test_postfaecher` 36, `test_dunning_api` 29, `test_finance_dunning_api` 3,
  `test_rfq_integration` 2, `test_compat_einkauf_anfragen` 3 – zusammen mit den Verträgen
  **100 grün**. `test_mcp_execution -k versenden` grün.
- Drei ältere Tests schrieben den Scheinerfolg fest und sind nachgezogen: RFQ ohne Lieferanten
  ist 422 statt `VERSENDET`; die beiden Mahn-Tests mit Ersatzdatenbank prüfen den Postversand und
  die Reihenfolge Archiv vor Commit.
- Gates grün: Single Head, Response-Modelle (Schwelle 0), OpenAPI-Doku, Doc-Drift, OpenAPI-Spec,
  Code-Inventare, Architektur-Index, tote Transaktionen, Tabellenverweise, Tabellenbesitz,
  Core-Kontamination, Improvement-Pipelines. Die Godfile-Baseline für `mask_frontend_bridges.py`
  sinkt von 1476 auf 1467.
- Frontend: `tsc` 0 Fehler, ESLint 0 für die geänderten Dateien, Vitest Postfächer und
  Schema-Compiler 19 grün.

## Offen

1. **Gewachsene Datenbank und Fuhrpark:** In `valeo_neuro_erp` ist `fuhrpark_tenant_ce_20261009`
   nie gelaufen. Weil diese Migration jetzt vor der Versandwege-Migration steht, ist
   `alembic_version` dort auf `postfach_microsoft_20261008` zurückgestellt; das nächste
   `alembic upgrade head` holt beide nach (die Versandwege-Migration ist idempotent). Nicht
   ausgeführt, weil der Fuhrpark-Backfill alle Bestandsfahrzeuge dem Mandanten
   `legacy-unassigned` zuordnet – das entscheidet der Fuhrpark-Owner.
2. **Tabellenkatalog:** In `valeo_probe` fehlen neun Tabellen, die CI zusätzlich über
   `create_all` anlegt. Der Katalog dieses Commits ist deshalb der CI-geprüfte Stand aus
   `8c09083df` plus die beiden neuen Spalten und die neuen Code-Verweise; er ist nicht blind aus
   dem Prüfstand erzeugt.
3. **Ein Archiveintrag im Prüfstand:** Der erste Testlauf schrieb einen Mahnungs-Archiveintrag für
   den Wegwerf-Mandanten `vw-a-92072e`. Archivierte Inhalte lassen sich nicht löschen
   (`guard_archived_content`); die Verträge ersetzen den Archiveintrag seitdem.
4. **Sichtprüfung der Masken** (Mahnwesen, Anfrage, Postfächer) im Browser steht aus.
5. **Mahnung ohne Beleg:** Die Mail nennt Beträge und Frist als Text; ein Mahnschreiben als PDF
   gibt es nicht. Der MCP-Versand kennt nur die Kennung des Akteurs, keine Rollen: Postfächer mit
   Rollenfreigabe lehnen ihn ab (403), frei gegebene funktionieren.
