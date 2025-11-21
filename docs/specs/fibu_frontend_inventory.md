# FiBu Frontend Code Inventory

Stand: aktuelle Codebasis `VALEO-NeuroERP-3.0`

Diese Übersicht dokumentiert alle identifizierten UI-Komponenten mit FiBu-Bezug, bewertet ihren Reifegrad und ordnet sie dem Zielbild der FiBu-Domain zu.

---

## 1. Navigation & Routing

- `packages/frontend-web/src/app/routes.tsx`: Enthält Routing-Einträge für diverse FiBu-Seiten (`/finance/accounts`, `/finance/journal`, `/finance/op/debitoren`, …).
- `packages/frontend-web/src/components/navigation/Sidebar.tsx` und `CommandPalette.tsx`: Referenzieren FiBu-Menüpunkte (Kontenplan, Kasse, OP-Listen, Mahnwesen, Zahlungsverkehr, UStVA).

**Bewertung:** Navigation vollständig, muss mit neuen Services synchronisiert werden (Rollen/Permissions).

---

## 2. CRUD-/Listen-Ansichten (React Query + FinanceService)

| Datei | Beschreibung | API-Abhängigkeit |
| --- | --- | --- |
| `src/pages/finance/chart-of-accounts.tsx` | Vollständige Kontenplan-UI (Filter, Dialoge, Validierung via zod) | `financeService.getAccounts` etc. (REST `/api/v1/chart-of-accounts`) |
| `src/pages/finance/op-debitoren.tsx` | OP-Listen (Debitoren) mit Filter/Statuskarten | Erwartet `/api/v1/open-items` |
| `src/pages/finance/debitoren-liste.tsx`, `kreditoren-stamm.tsx` | Stamm-Datentabellen, Inline-Aktionen | Diverse `/api/v1/...` Finance-Endpunkte |
| `src/pages/finance/bank-abgleich.tsx` | Bankabgleich-Oberfläche (Matchen, Filter) | `/api/v1/bank-reconciliation` (künftig) |
| `src/pages/finance/zahlungslauf-kreditoren.tsx`, `lastschriften-debitoren.tsx` | Zahlungs-/Lastschriftvorschläge | `/api/v1/payments/*` |

**Status:** UI-Logik solide (React Query, Mutations, Toasts). Backends fehlen – sobald neue Services stehen, können Endpoints/Query Keys angepasst werden. Reuse-Bewertung: **Refactor & Reuse** (Datenlayer neu verdrahten, mehrsprachige Labels prüfen).

---

## 3. Mask Builder / Formularbasierte Views

| Datei | Fokus | Besonderheiten |
| --- | --- | --- |
| `buchungserfassung.tsx` | Manuelle Buchung, Mehrtab-Formular via `ObjectPage` (Mask Builder), Zod-Validierung, Summenprüfung, DATEV-Export-Button | API-Placeholders `/api/finance/buchungen`. Reuse: **Refactor & Reuse** (Backend anbinden, Mask Builder stabilisieren). |
| `abschluss.tsx` | Perioden-/Jahresabschluss (Schritte, Checklisten) | Aktuell dummy states. Muss an `fibu-periodic` angebunden werden. |
| `ustva.tsx` | UStVA-Formular (Grid, Summen, ELSTER-Export) | Reuse: **Refactor & Reuse** (fibu-tax API). |
| `steuerschluessel.tsx` | Pflege von Steuerkennzeichen | Reuse: **Reuse as is** (UI reif, nur API tauschen). |
| `kasse.tsx`, `dunning-editor.tsx`, `mahnwesen.tsx` | Kassenbuch / Mahnwesen (Mask Builder + Workflow Widgets) | Reuse: **Refactor**, braucht neue Workflow-Sagas. |

---

## 4. OP-, AR-, AP-spezifische Seiten

- `op-debitoren.tsx`, `debitoren-liste.tsx`, `lastschriften-debitoren.tsx`, `mahnwesen.tsx`: Vollständige Debitoren-Workflows (OP-Historie, Mahnstufen, SEPA-Exports).
- `kreditoren-stamm.tsx`, `zahlungslauf-kreditoren.tsx`: Kreditorenverwaltung + Zahlungsverkehr, inkl. Datenträgeraustausch UI.
- `dunning-editor.tsx`: Editor für Mahnschreiben inkl. Vorschau.

**Status:** Featureumfang deckt Phase‑6-Services (`fibu-op`, `fibu-ar`, `fibu-ap`). Momentan rein clientseitig. Reuse-Priorität: **Refactor & Reuse** (API-Layer neu, Validierungen mit Backend synchronisieren).

---

## 5. Finanz-Reporting & Dashboard-Elemente

- `packages/frontend-web/src/pages/finance/kontenplan.tsx`: Visualisierung Kontenstrukturen.
- `pages/finance/abschluss.tsx`, `ustva.tsx`: Reporting/Behördenmodule.
- `packages/frontend-web/src/components/navigation/CommandPalette.tsx`: Shortcuts zu Reports (Bilanz, BWA, OP-Listen).

**Status:** UI existiert, aber kein „real data“. Reuse: **Refactor & Reuse** mit neuem Reporting-Backend.

---

## 6. API Client & Query Keys

- `src/lib/services/finance-service.ts`: zentrale REST-Client Implementierung (Accounts & Journal Entries). Muss erweitert/ersetzt werden, sobald Microservices in Phase 2+ existieren.
- `src/lib/query.ts`: `queryKeys.finance` definiert Caching-Keys (z. B. `finance.chartOfAccounts`).

**Hinweis:** Query Keys jetzt schon für Contract-Tests nutzen; künftige Middleware sollte Antworten in gewünschtem Format liefern.

---

## 7. UX-/Masken-Definitionen

- `src/config/mask-builder-valeo-modern.json`: Enthält Maskenkonfigurationen für FiBu-Objektseiten (z. B. Journal, OP-Listen, Belege).
- `packages/frontend-web/src/components/mask-builder/*`: Generische Engine für Form-basierten Aufbau (Tabs, Validierung). Bereits FiBu-spezifische Felder (Belegart, Steuer, OP-Verlinkung) vorgesehen.

**Status:** Gute Grundlage, muss mit Backend-Datenquellen synchronisiert werden.

---

## 8. Bewertung & Empfehlungen

| Bereich | Reuse-Empfehlung | Hinweise |
| --- | --- | --- |
| Kontenplan & Journal-UI | Refactor & Reuse | API-Antworten anpassen, Tenant/Permissions aus Context ziehen. |
| Mask Builder (Buchungserfassung, Abschluss, UStVA) | Refactor & Reuse | Backend-Endpunkte implementieren, Validierungsfehler vom Server zeigen. |
| AR/AP/OP Seiten | Refactor & Reuse | Abhängigkeit von OP-/Zahlungsservices, SEPA/DATEV-Exports an neues Interfaces-Hub anbinden. |
| Navigation/Routing | Reuse as is | Nur Feature Flags/Rollen konsolidieren. |
| Finance Service (Axios) | Replace | Mit GraphQL/Event-driven APIs kompatibel machen oder modularisieren (pro Microservice). |

**Cross-Cutting Needs**
1. **State & Multi-Tenancy**: UI nutzt hartcodierte Tenant-IDs; muss auf globales Session-/Auth-Modell wechseln.
2. **Permissions**: FiBu-spezifische Rollen (Sachbearbeiter, Freigeber) definieren & im Frontend auswerten.
3. **Document Links (`document_id`)**: DMS-/Doc-Capture-Integration durchgängig im UI anzeigen.
4. **Internationalisierung**: Texte sind größtenteils deutsch; falls zweisprachig, i18n vorbereiten.

---

## 9. Offene Fragen für Folge-Phasen

- Müssen Masken auf neues Design-System (z. B. ShadCN/Mask Builder 2.0) gehoben werden?
- Wie viele der existierenden Masken können wir als „Templates“ exportieren (Konfig statt hartem React-Code)?
- Welche UIs benötigen Echtzeit-Updates (WebSockets/NATS) – z. B. OP-Listen bei Zahlungseingang?

Diese Punkte fließen in Phase 0/1 Entscheidungen (Reuse-Matrix, Middleware-Mapping) ein.

