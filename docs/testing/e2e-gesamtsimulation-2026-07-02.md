# E2E-Gesamtsimulation Landhandel — 2026-07-02

Gesamtdurchlauf aller Geschäftsprozesse: Playwright-basierte **menschliche
Eingabe-Simulation** (UI) und **agentische Prozessautomatisierung** (REST-API),
jeweils mit Geschwindigkeitsprotokoll. Gefundene Fehler wurden unmittelbar
behoben; Optimierungen wurden mit Vorher/Nachher-Messung verifiziert.

## Testläufe (Geschwindigkeitsprotokoll)

| Lauf | Umfang | Ergebnis | Zeiten |
|---|---|---|---|
| All-Routes-Smoke (menschliche Navigation) | 766/767 Routen | 765 OK, 2 Bugs → gefixt | Median 944 ms, p95 1,2 s |
| UAT-Suite (UI + API-Belegketten) | 117 Tests, 8 Domänen-Spec-Dateien | 117/117 grün | 2,9 min gesamt |
| Workflow-Chains (agentisch, Szenarien A–F) | Auftrag→LS→Rechnung→Zahlung, Reklamation, Scan, Preisfindung, Getreideannahme, Einkauf | grün | einzelne API-Calls 20–120 ms |
| Qualitäts-Nachtrag Batch (agentisch) | 5 Annahmen in einem Batch | 5/5 | 179 ms für den Batch |
| **Realbeleg Auricher LI2500740 (agentisch)** | Lieferant+9 Artikel+Bestellung+ELS+Abgleich+Einbuchen+Bestandsprüfung | alle Assertions OK | **34 API-Calls in 1,5 s** |
| Realbeleg als UAT-Spec (TC-ELS-001…006) | dieselbe Kette reproduzierbar | 6/6 grün | 2,8 s |

## Durchgeführte Optimierungen (Vorher → Nachher)

| Optimierung | Messung vorher | Messung nachher |
|---|---|---|
| `CRM_CORE/SALES/SERVICE_BASE_URL` von `localhost` auf `127.0.0.1` (Windows-IPv6: httpx löst localhost zuerst nach `::1` auf) | httpx-Cold-Request 328 ms | 45 ms |
| Gepoolte `httpx.AsyncClient` je Downstream-Service statt Client-Neuaufbau pro Request (`app/integrations/crm_core_client.py`) | `/crm/customers?limit=50` kalt 1,42 s / warm ~60 ms | kalt 0,37 s / warm ~25 ms |

## Gefundene und sofort behobene Fehler

1. **UI-AGRAR-WIZARD-001** (Sammelabrechnung): kein Rendering-Bug — Frontend rief
   `/rohware/sammelabrechnung` (404) statt `/agrar/sammelabrechnung`, zudem falsches
   Payload-Schema. Seite auf echten Backend-Vertrag verdrahtet (Auswahl aus
   `harvest-acceptance`, Anlage + `/berechnen`, min-2-Validierung). TC-AGR-001 grün.
2. **UI-PERSONAL-BADGES-001** (Bewerbungen): Frontend rief `/personal/bewerbungen`
   (existiert nicht) statt `/personal/applications`; zusätzlich fehlte die Tabelle
   `domain_hr.applications` seit Wave-104 (503-Fallback) → Migration
   `hr_applications_table_20260702`. TC-PER-002 grün.
3. **Alembic Multiple Heads** (feed_qs × pricing_staffelrabatt) ließen den
   Docker-Backend-Container crash-loopen → Merge-Revision `42e0e183bd0c`.
4. **QualityProtocol-ID-Kollision**: `qp_<Sekundentimestamp>_<version>` kollidierte bei
   >1 Protokoll/Sekunde (genau der Laborbuch-Batch-Fall) → UUIDv7.
5. **Toaster-Systembug**: der shadcn-Toaster (`@/hooks/use-toast`, von ~250 Dateien
   genutzt) war nie global gemountet — sämtliches toast()-Feedback blieb unsichtbar.
   `ToastBootstrap` mountet jetzt beide Toast-Systeme.
6. **EmpfehlungsBanner /portal**: fehlender Guard auf `data.nach_typ` → TypeError.
7. **Kontraktklassen-Seite**: Frontend-Typ (klassen_code/kontrakt_typ) passte nicht zum
   Backend-Vertrag (name/variante/parität) → ErrorBoundary-Crash durch
   `undefined.toLowerCase()`. Seite auf echten Vertrag umgebaut, Create-Dialog sendet
   jetzt gültige Payloads.
8. **Fehlende Tabellen** `einkauf_lieferscheine`/`einkauf_lieferschein_positionen`
   (Migration existierte, war aber nie effektiv angewendet) → idempotent nachgezogen.
9. **Einbuchen-Kette** (`warehouse_service.book_stock_movement`):
   `Decimal("None")`-Crash bei leerem Bin, fehlende Pflichtfelder `ownership_type`,
   `storage_fee_relevant`, `previous_stock`/`new_stock` (jetzt echte
   Bestandsfortschreibung im Movement-Datensatz).
10. **Einbuchen-Artikelauflösung**: LS-Positionen tragen Artikelnummern (Realbelege!),
    die Buchung erwartete Artikel-UUIDs → Resolver article_number→articles.id.
11. **Smoke-Test-Rauschen**: externe OSM-Tile-Fehler (MapLibre, offline) wurden als
    App-Konsole-Fehler gewertet → gezielter Filter (nur maplibre/OSM-Ursprung).

## Neue Funktionen aus der Simulation heraus (User-Anforderungen)

- **Worklist „Unterbrochene Annahmen — Qualitäts-Nachtrag"**
  (`/agrar/annahmen-qualitaet-nachtrag`): Annahmescheine ohne Laborwerte; hl-Gewicht,
  Feuchte, Besatz, Protein, Fallzahl zeilenweise aus dem Laborbuch nachtragen, Batch-
  Speichern mit zeilenfehlertoleranter Verarbeitung.
  Backend: `GET /agrar/harvest-acceptance/?missing_quality=true`,
  `POST /agrar/harvest-acceptance/quality-batch`. E2E: `uat-qualitaet-nachtrag.spec.ts`.
- **Bestellabgleich für Eingangslieferscheine**
  (`POST /einkauf/lieferscheine/{id}/bestellung-abgleich`): Positionsabgleich per
  Artikelnummer (Fallback Lieferanten-Artikelnummer), Fortschreibung
  `menge_geliefert`/`menge_offen`/Positionsstatus, Bestellstatus
  teilgeliefert/geliefert, Bericht mit MATCH/UNTER-/UEBERLIEFERUNG/UNBESTELLT/
  UNGELIEFERT. E2E: `uat-eingangslieferschein-abgleich.spec.ts` (TC-ELS-001…006).

## Bekannte Restpunkte

- `/fibu/zahlungseingaenge` zeigte im Smoke-Lauf einmalig EMPTY_PAGE (30,9 s) —
  verifiziert als HMR-Artefakt (Quellcode-Edit während des Laufs, Lazy-Chunk-
  Invalidierung): gezielter Nachtest rendert die Seite in 3,6 s fehlerfrei,
  API antwortet in 22 ms.
- `/produktion/produktions-dokumente-drucken` und `/policies` laden >25 s (bestanden,
  aber langsam) — **nachgemessen 2026-07-02:** kalt 1,9 s bzw. 1,1 s, warm <1 s.
  Die Ausreißer waren Vite-Dev-Transform beim Erstaufruf unter 766-Routen-Volllast
  (Dev-Server-Artefakt, kein Produktfehler). Produktions-Build nicht betroffen.
- TC-AGR-003 (Saatzucht-Badges) flake-te einmalig unter Volllast des Gesamtlaufs,
  besteht einzeln in 6,1 s — beobachten, kein Codefehler identifiziert.

## Abschlussverifikation

- UAT-Gesamtlauf: 123/124 grün (einziger Fail = TC-AGR-003-Flake, einzeln grün).
- Backend-Tests der geänderten Bereiche: 48 passed, 1 skipped
  (einkauf_bestellungen, warehouse_transfers, 3-Way-Match).
- `tsc --noEmit`: keine Fehler in den geänderten Dateien.
