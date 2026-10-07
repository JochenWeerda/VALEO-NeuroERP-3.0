# Mandant in Finanz, CRM und Einkauf; echte Fachwege statt Lücken (Slice MANDANT-FINANZ-CRM-EINKAUF-20261007)

Stand: 2026-10-07 · Folgeslice zu [Mask-Aktionen-Wirkung](mask-aktionen-wirkung-20261007.md)

## Auftrag

Vier Befunde aus dem Vorslice „fertig bearbeiten“; danach die User-Vorgaben „Ein
fehlender Fachweg braucht eine echte Implementierung, keinen Platzhalter für einen
grünen Test“ und „Mask-Builder und Screen Definitions nutzen, keine handgebauten
Masken“.

## Befunde und Behebung

| Befund | Ursache | Behebung | Commit |
|---|---|---|---|
| Zahlungsläufe | alle acht Wege mit `Query("system")`, `/plan` mit Mandant im Rumpf; keine Rolle; Freigeber freier Text | Mandant aus dem Kontext, Rollenmatrix vor der Datenbank, `created_by` + Vier-Augen, Freigeber = angemeldeter Nutzer | `42f8fe6c3` |
| Eingangsrechnungen | ganzes Modul ohne Mandant, Buchen mit Dokument-Mandant; Workflow zählte Freigeber aus dem Rumpf; Workflow-SQL gegen nicht existierende Spalten; `json.loads` auf JSONB | `tenantId` im Dokument, fremd/mandantenlos = 404, kein Überschreiben (409), Rollen, Freigeber = Nutzer, SQL auf migrierte Spalten | `42f8fe6c3` |
| Opportunities | crm-sales ohne Mandant, lokale Tabelle ohne Filter, Liste mit optionalem Filter; Aktivitäten in einer Tabelle ohne Migration | eine Mandantenprüfung für jede aufgelöste Opportunity, Aktivitäten in `domain_crm.activities` (+`opportunity_id`) | `5db4b4944` |
| Angebote | alle Lesewege mit falschen Spalten, `except: return None`; Umwandlung mit erfundener Position, zwei Commits, doppelt möglich; `compat.py` las fest Mandant `default` | richtige Spalten, Positionen übernommen, ein Commit, kein zweites Mal; später in die kanonische Bestellung | `5db4b4944`, `28e6133ed` |
| Systemisch | `DocumentRepository.save` fehlte (42 Aufrufe in neun Diensten seit 15.05.2026); 50 `EntityNotFoundError` mit einem statt zwei Argumenten | `save` als Kurzform, Aufrufe korrigiert, AST-Wächter | `5db4b4944` |

## Echte Fachwege statt benannter Lücken

| Aktion | Fachweg | Commit |
|---|---|---|
| Lagerbewegung stornieren | Gegenbuchung über die Richtungstabelle (jedes Vokabular), kein Storno eines Stornos, kein negativer Bestand, idempotent | `71aecf2ae` |
| Opportunity-Aktivität | `inputFields` (Betreff, Typ, Notiz) — deklarativ, gezeichnet von `ActionInputDialog` im Mask-Builder | `54a659699` |
| Wareneingang am Anlieferavis | Avis → kanonische Bestellung, Lagerzugang im Bestandsbuch und am Artikel, Positionsmengen, Status, ein Commit; Lieferschein-Nr. und Lager als `inputFields` | `28e6133ed` |
| Angebot → Bestellung | kanonisch in `domain_einkauf.bestellungen` (dort liest die Bestellungs-Maske) | `28e6133ed` |
| Lead qualifizieren, Ernte-Abrechnung drucken | nach User-Entscheidung (Lead-Maske auf `public.crm_leads`, PDF-Inhalt in PostgreSQL) von Codex umgesetzt | `e71e0731e` |
| Logistik-Aktionen ohne `command` | von Codex deklariert | `b2a63f451` |

Das Gate `check_mask_command_endpoint_inventory` führt **0 bekannte Lücken**. Der
Vertrag `test_jede_frueher_vorgetaeuschte_aktion_hat_einen_fachweg` hält fest, dass
jede der sechs früher vorgetäuschten Aktionen einen `commandEndpoint` und keinen
`stubReason` hat.

### Plattform: Aktionen deklarieren ihre Eingaben

`ScreenActionDefinition.inputFields` (+ `optionsSource` für Auswahlen aus einem
Endpunkt). `ActionInputDialog` (mask-builder/renderers) zeichnet sie mit
`FieldRenderer` und prüft mit `useUniversalFormState`; `UniversalNativeDetailPage`
fragt sie vor Bestätigung, Vorschau und Ausführung. Governance: `inputFields` nur mit
`commandEndpoint`, Feldtypen und `optionsSource` geprüft.

## Nachweis

Je Fachweg Verträge gegen `valeo_probe`: Zahlungslauf 77, Eingangsrechnung 111,
Opportunity 12, Angebot 14, Storno 16, Wareneingang 10, Plattform 8 Vitest; die
Bereichssuiten bei jedem Schritt (zuletzt 1543 grün), alle Ratschen grün. Codex'
Lead-/PDF-Verträge (`tests/test_user_decisions_lead_pdf.py`) laufen nur mit gesetzter
`TEST_DATABASE_URL` — ohne sie werden 10 von 11 übersprungen, nicht rot.

## Weitere Befunde (benannt, nicht Teil)

* Inventar-API: 23 Stellen in sechs Dateien nehmen den Mandanten aus einem
  Query-Parameter oder dem Standardmandanten (behoben nur die Lagerliste, weil sie
  Optionsquelle ist).
* `InventoryService` schreibt `out` mit negativer Menge; die Richtungstabelle und der
  Datenbestand erwarten positive Mengen.
* `DELETE /inventory/stock-movements/{id}` löscht eine Bewegung ohne Bestandskorrektur.
* Zwei Bestellsysteme (`/purchase-orders` Dokumentspeicher, `/einkauf/bestellungen`
  kanonisch); `register_artifact` verschluckt Fehler.
* Der Lieferschein-Abgleich nimmt den Mandanten aus `Query("system")` und bucht keinen
  Lagerzugang.
