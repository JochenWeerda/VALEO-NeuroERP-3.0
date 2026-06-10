# DOM-CRM-004 — Kundenstamm-Tiefe (2026-06-10)

Sprint-Ziel: CRM-Tiefe — Ownership, **Dublettenlogik**, Kundenumwandlung,
Folgeobjektkette, Serviceabschluss, Aufgaben/Wiedervorlagen. Verifizierbar an
echten Seed-Daten (462 Kunden in `public.kunden`). Erster Slice (004.1):
Dubletten-Erkennung.

## Slice 004.1 — Dubletten-Erkennung (umgesetzt, read-only)
- Service: `app/services/crm_duplicate_service.py`
  - Blocking-Schlüssel: E-Mail (lower), Telefon (Ziffern-Tail 7), Name1
    (normalisiert: Rechtsform-/Füllwörter raus, Tokens sortiert) + PLZ.
  - Union-Find → Cluster über alle Schlüssel; je Cluster Mitglieder, Treffergründe,
    Score + Konfidenz (hoch bei E-Mail/Telefon).
- API: `GET /api/v1/crm/duplicates?limit=…`.
- Frontend: `pages/crm/dubletten.tsx` (Cluster-Karten mit Mitglieder-Tabelle,
  Gründe-Badges, Konfidenz) + Hook `lib/api/crm-duplicates.ts` + Nav
  „Kunden-Dubletten" (commercial.tsx) + Route-Alias.

### Verifiziert (echte Daten, 462 Kunden)
5 Cluster erkannt, u. a. exakte Doppelanlagen sowie **namens-umgestellte GbRs**
(„Hillrich & Sandine Kleemann GbR" = „Kleemann GbR, Hillrich & Sandine",
„Enno & Etta Ohling GbR" = „Ohling GbR, Enno und Etta") — Normalisierung greift.

## Routing-Hinweis
Neue manifest-Seite: Eintrag in `src/app/route-aliases.json` + `npm run routes:generate`
(sonst weiße Seite). Siehe DOM-SUPPLY-Erfahrung.

## Slice 004.2 — Zusammenführung (Merge, umgesetzt)
- Migration `crm_merge_20260610`: `public.kunden.merged_into` + append-only `public.crm_merge_log`.
- Service: `app/services/crm_merge_service.py` — `preview()` (read-only: zeigt umzuhängende
  1:n-Historie + Guards) und `merge()` (atomar: kunden_kontakte/ansprechpartner/crm_gifts/
  capture_inbox/notifications/marketing_prefs/tapi_calls/whatsapp_bestellungen/adressen/
  email_verteiler/freitext auf Master umhängen; Verlierer `geloescht=true`+`merged_into`;
  `crm_merge_log`-Eintrag). Finanz-/Belegdaten (business_partner_id) bleiben unberührt.
- API: `POST /crm/duplicates/merge-preview` + `/merge` (422 bei Fachfehler).
- Frontend: Master-Radio + „Zusammenführen" je Cluster in `dubletten.tsx`.
- Tests: identitäts-Guard (test_crm_duplicates.py, 7 grün).

### Verifiziert (Temp-Paar, Seed unberührt)
preview zeigt umzuhängende Kontakte; merge hängt Kontakt Verlierer→Master, setzt
Verlierer geloescht+merged_into; erneuter Merge → 422; Cleanup ok.

## Slice 004.3 — Ownership / Zuordnung & Übergabe (umgesetzt)
- Migration `crm_ownership_log_20260610` (append-only Übergabe-Audit).
- Service: `app/services/crm_ownership_service.py` — get/set (Upsert kunden_crm360
  sales_rep_vb/dispatcher_disp + Log je geänderten Feld), history, `unassigned()`
  (Kunden ohne Außendienst), `by_owner()` (Workload).
- API: `GET/PUT /crm/{nr}/ownership`, `GET /crm/{nr}/ownership/history`,
  `GET /crm/ownership/unassigned`, `GET /crm/ownership/by-owner`.
- Frontend: `pages/crm/kunden-zuordnung.tsx` (Worklist „ohne Zuordnung" + Inline-
  Zuweisung) + Hooks `lib/api/crm-ownership.ts` + Nav „Kunden-Zuordnung" + Route-Alias.

### Verifiziert (echte Daten)
unassigned = 461 (nur 1 Kunde hatte Owner); Zuweisung GAP00001→AD+ID schreibt
beide Felder + 2 Audit-Einträge; by-owner findet den Kunden. Testdaten revertiert.

## Folge-Slices
- **004.4** Folgeobjektkette/Serviceabschluss + Aufgaben/Wiedervorlagen-Vollständigkeit.
- **004.5** Browser-E2E + UAT-Nachweispaket.
