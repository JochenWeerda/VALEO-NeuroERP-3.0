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

## Folge-Slices
- **004.2** Zusammenführen (Merge) zweier Kunden — Master wählen, Referenzen umhängen,
  append-only Audit-Eintrag; Guard gegen Belegkonflikte.
- **004.3** Ownership (Außendienst/Innendienst je Kunde) + Zuordnung/Übergabe.
- **004.4** Folgeobjektkette/Serviceabschluss + Aufgaben/Wiedervorlagen-Vollständigkeit.
- **004.5** Browser-E2E + UAT-Nachweispaket.
