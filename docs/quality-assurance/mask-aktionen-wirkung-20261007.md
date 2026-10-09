# Mask-Aktionen melden nur Erfolg, wenn etwas geschehen ist (Slice MASK-AKTIONEN-WIRKUNG-20261007)

Stand: 2026-10-07 · Befund aus [Die Masken zur Einwilligung](bewerbung-einwilligung-maske-20261007.md)

## Befund

Zwölf Mask-Aktionen meldeten **Erfolg ohne fachliche Wirkung**: neun in
`app/api/v1/endpoints/mask_actions.py`, je eine in `ap_invoices.py`, `open_items.py`
und `einkauf_kpis.py`. Jede baute ein Ergebnis-Dict, schrieb Audit und Outbox und
antwortete `success: true` — kein INSERT, kein UPDATE, kein Dienstaufruf.

Gegenproben, bevor etwas geändert wurde:

* Alle zwölf Pfade waren die **einzigen aktiven** Handler; kein anderer Router
  bediente sie zuerst.
* Kein Outbox-Konsument führte die Mutation nach. Im Gegenteil:
  `finance.payment_run.approved` speist die Projektion `payment_run_cockpit` — ein
  **nicht freigegebener Zahlungslauf erschien im Lesemodell als freigegeben**.
* Bestehende Tests schrieben das fest: `test_stub_returns_proposed_changes` (die
  Handler hießen dort selbst „Stub“), `test_command_endpoint_activated` und
  `test_einkauf_supplier_neue_bestellung_has_command_endpoint` verlangten genau die
  Endpunkte, die nichts taten. Ein Anlieferavis-Test lief nur grün, weil er die
  falsche Maske fand und nichts prüfte.

## Behebung

| Aktion | Maske | Jetzt |
|---|---|---|
| Zahlungslauf freigeben | finance/payment-run | **Delegation** an `approve_payment_run` |
| Lieferschein drucken | sales/delivery-note | **Delegation** an `print_delivery_note` (Nachdruck mit Begründung) |
| Reklamation abschließen | qualitaet/reklamation | **Delegation** an `transition_status` → `geschlossen`, Zustandsmaschine gilt |
| Eingangsrechnung freigeben | finance/ap-invoice | **Delegation** an `approve_ap_invoice`, Mandant vorher geprüft |
| Mahnen | finance/ar-open-item | **Delegation** an `eskaliere_mahnstufe` über die Rechnungsnummer des Postens |
| Neue Bestellung | einkauf/supplier | **Sprung** in die Bestellerfassung (`navigationRoute`) — eine Bestellung braucht Positionen |
| Lead qualifizieren | crm/lead | **nicht verfügbar** — kein Übergang Lead → Opportunity; die vorhandene Konvertierung erzeugt einen Kunden |
| Opportunity-Aktivität | crm/opportunity | **nicht verfügbar** — der Fachweg schreibt in eine Tabelle, die keine Migration anlegt |
| Angebot → Bestellung | einkauf/angebot | **nicht verfügbar** — die Umwandlung liest Spalten, die keine Migration anlegt |
| Wareneingang | einkauf/anlieferavis | **nicht verfügbar** — gebucht wird gegen die Bestellung; vom Avis aus fehlt die Verbindung |
| Lagerbewegung stornieren | lager/stock-movement | **nicht verfügbar** — kein Storno-Dienst |
| Ernte-Abrechnung drucken | agrar/harvest-settlement | **nicht verfügbar** — kein Druckdienst |

„Nicht verfügbar“ heißt nach Projektkonvention: `stubReason`, kein
`commandEndpoint`, der Handler ist entfernt. Die Maske sagt den Grund, statt
„erledigt“ zu melden.

### Die Laufzeit: `run_delegated_mask_action`

* **Prüfung in jedem Modus.** `check_fn` liest die Datenbank (Objekt im Mandanten
  da, Zustand passt). Ein Trockenlauf meldet so, was der Fachweg ablehnen würde —
  vorher meldete er „Validierung erfolgreich“ auch für Objekte, die es nicht gibt.
* **Ein Commit.** Audit- und Outbox-Zeile liegen in der Sitzung, wenn der Fachweg
  läuft; dessen eigener Commit schreibt Mutation, Audit und Ereignis zusammen.
  Scheitert er, wird alles zurückgerollt.
* **Der fachliche Grund.** Die Antwort nennt `HTTPException.detail` des Fachwegs
  („Ungueltiger Uebergang: offen -> geschlossen. Erlaubt: …“), nicht „Aktion konnte
  nicht gespeichert werden“.
* **Der Mandant kommt aus dem geprüften Kontext** und wird dem Fachweg übergeben.

`run_mask_action` (der alte Weg) hat keinen Aufrufer mehr; sein Atomaritätstest
bleibt bestehen.

## Nachweis

| Prüfung | Ergebnis |
|---|---|
| `tests/test_mask_aktionen_wirkung.py` gegen `valeo_probe` | **29 bestanden** — Freigabe ändert den Lauf und schreibt genau ein Audit und ein Ereignis; zweite Freigabe, fehlende Begründung, fremder Mandant: nichts; Trockenlauf prüft und schreibt nichts; Druck markiert, Nachdruck braucht Begründung; Reklamation schließt nur nach Zustandsmaschine; Mahnen setzt eine Stufe, fremder Posten nicht; unbekannte Eingangsrechnung wird nicht freigegeben; sechs Endpunkte entfernt, ihre Masken nennen den Grund; „neue Bestellung“ springt; **jeder `commandEndpoint` aller Screen Definitions ist montiert** (Muster-Abgleich, auch generische `{action_key}`-Wege) |
| Umgestellte UIX-Tests (`test_uix050_053`, `test_uix046_048`) | bestanden; schreiben jetzt das ehrliche Verhalten fest |
| Fach- und SD-Suiten (AP, offene Posten, Zahlungsläufe, Reklamation, Lieferscheine, Mask-SD, Meridian, Atomarität) | **1035 bestanden**, 1 rot vorbestehend (s. u.) |
| Ratschen | Pagination, Baseline-Integrität, tote Transaktionen, Godfiles, Tabellenverweise: grün (`open_items.py` bleibt unter 1000 Zeilen) |

**Vorbestehend rot, nicht Teil:** `test_actions_have_danger_level[fuhrpark/fahrzeug-stamm]`
— `loeschen` trägt `dangerLevel: "destructive"`, das der Test nicht kennt (seit
`dec0dfd1b`/`93bd71598`, 05./06.10.2026).

## Neue Befunde (eigene Slices)

1. **`approve_payment_run`** nimmt den Mandanten aus einem Query-Parameter (Vorgabe
   `"system"`) statt aus dem geprüften Kontext und prüft keine Rolle. Über die Maske
   ist das jetzt abgesichert, über den REST-Weg nicht.
2. **`approve_ap_invoice`** liest die Rechnung ohne Mandantenfilter aus dem
   Dokumentenspeicher und nimmt den Mandanten aus dem Dokument (Vorgabe `"system"`).
3. **`add_opportunity_activity`** prüft den Mandanten nicht und schreibt in
   `activities` mit `opportunity_id` — eine Tabelle, die keine Migration anlegt (500
   auf frischer Datenbank).
4. **`convert_angebot_to_order`** liest `angebots_nummer`, `artikel_name`,
   `netto_summe`, `lieferzeit_tage`; die Tabelle hat `angebotsnummer` und
   `gesamtbetrag`. Ein `except` macht daraus „Angebot nicht gefunden“ — in **beiden**
   Datenbanken; die Umwandlung hat nie gearbeitet. Außerdem committet sie die
   Bestellung, bevor der Angebotsstatus gesetzt ist.
5. **`eskaliere_mahnstufe`** prüft nicht, ob es die Rechnungsnummer gibt (über die
   Maske jetzt vorgeprüft), und setzt `mahn_stufe` am Posten nicht.
6. **Bestellerfassung** übernimmt keinen Lieferanten aus der Adresse; der Sprung aus
   der Lieferantenmaske landet in einer leeren Erfassung.

## Nachtrag 2026-10-09: kanonischer Runtime-Vertrag

Der ungenutzte run_mask_action ist entfernt. Seine Atomizitaetstests pruefen
nun run_delegated_mask_action. Eigene SAVEPOINT-Session haelt auch innere
Fachcommits mit spaeterer Ablehnung in der aeusseren Einheit; SQLAlchemy-
und HTTP-Serverfehler ohne SQL-/Personalwerte. Finale Abnahme100 Tests ohne
Skip, einschliesslich echtem PG-Zahlauf-Rueckrollvertrag. Historische Zahlen
oben bleiben datierte Nachweise. [Aktuelle QA und Grenzen](mask-runtime-legacy-retirement-20261009.md).
