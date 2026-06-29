# UIX-043 — Vollständige Masken-Migrations-Inventur

Stand: 2026-06-29

## Scope

"Maske" im Sinne des neuen Maskengenerators = entity detail screen (mode: detail),
der einem Benutzer eine Entität mit mehreren Tabs zeigt. Listenansichten, Dashboards,
Wizards, Formulare ohne Tabs sind kein Migrationsziel.

---

## Migriert (native ScreenDefinition, temporary=False, advisoryScore=1.00)

| SD-ID | Legacy-Seite | Wave |
|---|---|---|
| crm/customer-360 | kunden-stamm-modern | UIX-028 |
| sales/sales-order | — | UIX-030 |
| agrar/kontrakte | — | UIX-030 |
| einkauf/supplier | lieferanten-stamm | UIX-038 |
| crm/opportunity | opportunity-detail | UIX-039 |
| lager/article-stock | — | UIX-040 |
| sales/delivery-note | — | UIX-041 |
| einkauf/purchase-order | bestellung-stamm | UIX-041 |
| finance/ap-invoice | rechnungseingang | UIX-041 |
| finance/ar-open-item | op-debitoren (detail) | UIX-041 |
| lager/stock-movement | lagerbewegungen (detail) | UIX-041 |
| agrar/harvest-settlement | sammelabrechnung | UIX-041 |
| finance/payment-run | zahlungslauf-kreditoren (detail) | UIX-041 |
| agrar/duenger | duenger-stamm | UIX-043 |
| agrar/saatgut | saatgut-stamm | UIX-043 |
| finance/debitor | debitoren-stamm | UIX-043 |
| finance/kreditor | kreditoren-stamm | UIX-043 |
| finance/bankkonto | bankkonten-stamm | UIX-043 |
| einkauf/anfrage | anfrage-stamm | UIX-043 |
| einkauf/angebot | angebot-stamm | UIX-043 |
| einkauf/anlieferavis | anlieferavis | UIX-043 |
| einkauf/auftragsbestaetigung | auftragsbestaetigung | UIX-043 |
| qualitaet/reklamation | reklamation-detail | UIX-043 |
| futtermittel/einzelfuttermittel | einzelfuttermittel-stamm | UIX-043 |
| futtermittel/mischfuttermittel | mischfuttermittel-stamm | UIX-043 |
| crm/lead | lead-detail | UIX-043 |

**Gesamt: 26 native SDs — alle generatorReady=True, advisoryScore=1.00**

---

## Bereits durch SD abgedeckt (kein separater SD nötig)

| Legacy-Seite | Abgedeckt durch |
|---|---|
| crm/kunden-stamm.tsx | crm/customer-360 |
| crm/kunden-stamm-modern/ | crm/customer-360 |
| crm/lieferanten-stamm.tsx | einkauf/supplier |
| einkauf/bestellung-stamm.tsx | einkauf/purchase-order |
| crm/opportunity-detail.tsx | crm/opportunity |
| einkauf/rechnungseingang.tsx | finance/ap-invoice |

---

## Bewusst exempt (kein entity-detail screen)

Diese Seiten nutzen ObjectPage/MaskConfig, sind aber kein Migrationsziel weil
sie Prozessmasken, Batch-Screens, Formulare oder Listenansichten sind:

| Seite | Grund |
|---|---|
| finance/abschluss | Jahresabschluss-Wizard (Prozess, nicht Entity) |
| finance/bank-abgleich | Matching-Screen (2-Panel, kein Entity-Detail) |
| finance/buchungserfassung | Journal-Entry-Formular ohne Tabs |
| finance/dunning-editor | Mahnungs-Editor (Formular) |
| finance/kasse | POS-Kasse (Sondermaske, eigener Lebenszyklus) |
| finance/kontenplan | Kontenliste (List-Mode, kein Detail) |
| finance/lastschriften-debitoren | Batch-Lastschrift-Screen |
| finance/mahnwesen | Mahnungs-Management-Cockpit (List+Filter) |
| finance/ustva | UStVA-Formular (periodisch, kein Entity) |
| crm/campaign-detail | Campaign-Detail (Spezialmaske mit Builder-Canvas) |
| crm/campaign-template-detail | Template-Detail (Formular-Canvas) |
| crm/consent-detail | DSGVO-Consent (Spezialform) |
| crm/gdpr-request-detail | DSGVO-Antrag (Prozessmaske) |
| crm/segment-detail | Segment-Definition (Rule-Builder, kein Entity) |
| futtermittel/futtermittel-bestellung | Bestellprozess-Screen (Flow) |
| futtermittel/futtermittel-wareneingang | Wareneingangs-Flow |
| verkauf/kunde-neu | Neuanlage-Wizard |
| sales/credit-note-editor | Gutschriften-Editor (Formular) |

---

## Restliche Seiten (Listenansichten, Dashboards, Wizards)

~572 weitere .tsx-Dateien in 85 Domains sind keine Migrations-Kandidaten:
Listenansichten (ListReport), Dashboards, Wizards, Auth-Seiten, Admin-Konfiguration,
Charts, Stammdaten-Listen etc. — diese erhalten keine ScreenDefinition.
