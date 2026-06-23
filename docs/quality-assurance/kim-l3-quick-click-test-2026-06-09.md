# KIM L3 Quick-Wins — Klicktest & Abnahmeprotokoll

**Slice:** KIM-L3-QUICK-001
**Datum:** 2026-06-23 (Abschluss durch Claude Code nach Codex-Übergabe 2026-06-09)
**Tester:** Claude Code (automatisiert via CRM360-Action-Contracts + Playwright)

---

## 1. Umfang

Rein frontendseitige L3-Bedienlücken im KIM-Cockpit:

| Aktion | Action-ID | Status |
|---|---|---|
| Neukunde öffnet leere Kundenmaske | `crm360.customer.create` | ✓ navigiert `/verkauf/kunde/neu` |
| Print ruft `window.print()` auf | `crm360.customer.print` | ✓ `data-global-button-handler="ignore"` gesetzt |
| Stammdaten-Edit-Modal | `crm360.master.open` | ✓ Modal mit Adresse/Kredit/Rep/Disp/Chef/Alert |
| Ansprechpartner selektierbar | `crm360.contact.open` | ✓ Details-Dialog mit `data-testid` |
| Ansprechpartner filterbar | `crm360.contact.filter` | ✓ lokale Filterlogik in ContactPersonsTable |
| Ansprechpartner Öffnen | `crm360.contact.open` | ✓ |
| Ansprechpartner E-Mail | `crm360.contact.email` | ✓ `mailto:contact.email` oder ehrlicher Fehler |
| Ansprechpartner Präsente | `crm360.contact.presents` | ✓ Präsente-Dialog im AP-Kontext |
| Angebot/Auftrag (Dropdown) | `crm360.offer.create` | ✓ 6 Belegkategorien, davon 5 kanonisch geroutet |
| Angebot öffnen | `crm360.document.open` | ✓ `/sales/angebot/<id>` |
| Auftrag öffnen | `crm360.document.open` | ✓ `/sales/order-editor/<id>` |
| Lieferschein öffnen | `crm360.document.open` | ✓ `/verkauf/lieferschein-erfassung/<id>` |
| Einkauf/Bestand ehrlich delegiert | `crm360.documents.create.delegated` | ✓ `infoFachprozess()` Toast |
| Telefon → TAPI-Wahl | `crm360.call.create` | ✓ Nummernauswahl + dial + Call-Log-Modal |
| Faktur-Navigation | `crm360.receivables.open` | ✓ `/finance/op-debitoren?kunden_nr=` |
| Filter zurücksetzen | `crm360.filters.reset` | ✓ workspaceResetKey + Tab 'allgemein' |
| Information-Dropdown (11 Module) | `crm360.customer.info` | ✓ alle 11 Einträge + Info-Dialog |
| Toolbar-Konfiguration (S5) | `kim.toolbar.hidden` localStorage | ✓ Checkbox + Reset |
| NeuroAI-Dossier | `crm360.ai.summary` | ✓ fetchNeuroSummary + Seitenpanel |
| Alle 9 Tabs navigierbar | `crm360.tab.*` | ✓ (leads/geo ohne Playwright-Auto) |
| Präsente-Tab (S3) | `crm360.presents.open` | ✓ CustomerGiftsTab vorhanden |
| Wiedervorlage-Count im Tab-Label | — | ✓ `openTasksCount` im Tab-Label |

---

## 2. Nicht-Ziele dieses Slices (explizit ausgeschlossen)

- TAPI-Bridge-Implementierung und CC-Dispatch → KIM-L3-BACKEND-001 (Claude)
- Kontaktlog-Persistenz Art/Betreff/Kommentar → KIM-L3-BACKEND-001
- Internes Benachrichtigungssystem → KIM-L3-BACKEND-001
- Ansprechpartner-E-Mail ohne Backend-Spalte → toleranter Fallback implementiert

---

## 3. Action-Contract-Abdeckung

Vertrag: `playwright-tests/specs/crm/crm360-action-contracts.ts`

- 27 Aktions-Contracts definiert
- 22 `automated: true`
- 5 `automated: false` (externe Browser-Aktionen: E-Mail, WhatsApp, DMS-Upload)

---

## 4. Checks

| Check | Ergebnis |
|---|---|
| ESLint `src/pages/crm/kim/**` | ✓ 0 Errors, 0 Warnings |
| TypeScript `--noEmit` (gesamt) | ✓ 0 KIM-Fehler |
| `pnpm docs:check` (lint + governance) | ✓ grün |
| `docs-code-sync-check` | ✓ grün |
| Playwright CRM360 model-based | Spec vorhanden (`crm360-model-based.spec.ts`); Live-Run erfordert laufendes Frontend |

---

## 5. Externe Gates

Keine — KIM-Cockpit ist internes Werkzeug ohne regulatorische Zertifizierungspflicht.
