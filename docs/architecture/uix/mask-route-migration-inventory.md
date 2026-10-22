# Masken-Routen-Migrationsinventar

Stand: 2026-10-22 (Messung aus `route-inventory.gen.json` + Seitenquelltext).

> Studio-Entwuerfe in der DB sind **kein** Nachweis produktiver Ablösung.
> Nur `runtime_wired` (ScreenDefinition → RenderPlan → useUniversalMaskRuntime /
> UniversalMaskRenderer / UniversalNativeDetailPage) zaehlt als zentrale Steuerung.

## Routen (route-inventory)

| Klasse | Anzahl |
|--------|--------|
| Gesamt Routen | 941 |
| runtime_wired (UniversalMaskRuntime-Pfad) | 61 |
| legacy_mask_pattern (ObjectPage/ListReport ohne Runtime) | 115 |
| hand_built (weder Runtime noch ObjectPage/ListReport) | 764 |
| non_page_module (Layout/Redirect/sonstiges) | 1 |

## Seiten-Dateien (`src/pages/**/*.tsx`)

| Klasse | Anzahl |
|--------|--------|
| Gesamt TSX-Seiten | 700 |
| runtime_wired | 52 |
| legacy_mask_pattern | 57 |
| hand_built | 591 |

## ScreenDefinitions / Studio

- Registrierte ScreenDefinition-Builder (`_SCREEN_DEFINITIONS`): **102**
- Frontend capture/mask TS-Exports (`export const *Screen`): **31**
- Studio-Draft-Zaehlung erfordert Live-DB (`screen_definition_drafts`); ohne DB hier nicht gemessen.

### Vergleich zum frueheren Stand

| Metrik | Frueher | Jetzt (2026-10-22) |
|--------|---------|---------------------|
| handgebaute Routen | 442 | 764 |
| Routen mit alten Maskenmustern | 80 | 115 |
| Runtime-verdrahtet | — | 61 |
| Studio-Entwuerfe | 154 | (DB, nicht gemessen) |

Hinweis: Fruehere 442/80 bezogen sich vermutlich auf eine engere Routen-/Seitenbasis;
aktuell sind **941** generierte Routen inventarisiert. Die Absolute `hand_built`
ist deshalb nicht 1:1 vergleichbar, aber die Luecke zur Runtime bleibt gross.

## Dual-Pfad (Native Wrapper existiert, Primaernav oft Legacy)

Siehe UIX-057, MASK-PRIMARY-NAV-NATIVE-20261022 und MASK-BESTELLUNG-NAV-NATIVE-20261022:
Listen oeffneten teilweise `*-stamm` / Plural-Legacy, waehrend `*-native` unter der
kanonischen `/:id`-Route lag. Stammdaten (Saatgut, Duenger, Lieferant) und Bestellung-
Detailnav sind auf Native umgehaengt; Neuanlage bleibt Legacy. Paritaetsluecken Bestellung
(CaseBand, Allokation, Freigabe-Detail, Komm-Senden) und Beleg-Alt-Einstiege bleiben offen.

## Legacy ObjectPage/ListReport (erste 40)

- `agrar/biostimulanzien` ← `src/pages/agrar/biostimulanzien-liste.tsx`
- `agrar/biostimulanzien-liste` ← `src/pages/agrar/biostimulanzien-liste.tsx`
- `agrar/biostimulanzien-stamm` ← `src/pages/agrar/biostimulanzien-liste.tsx`
- `agrar/biostimulanzien-stamm/:id` ← `src/pages/agrar/biostimulanzien-liste.tsx`
- `agrar/duenger-liste` ← `src/pages/agrar/duenger-liste.tsx`
- `agrar/duenger-stamm` ← `src/pages/agrar/duenger-stamm.tsx`
- `agrar/duenger-stamm/:id` ← `src/pages/agrar/duenger-stamm.tsx`
- `agrar/duenger/stamm` ← `src/pages/agrar/duenger/stamm.tsx`
- `agrar/duenger/stamm/:id` ← `src/pages/agrar/duenger/stamm.tsx`
- `agrar/duenger/stamm/:id/edit` ← `src/pages/agrar/duenger/stamm.tsx`
- `agrar/saatgut` ← `src/pages/agrar/saatgut-liste.tsx`
- `agrar/saatgut-liste` ← `src/pages/agrar/saatgut-liste.tsx`
- `agrar/saatgut-stamm` ← `src/pages/agrar/saatgut-stamm.tsx`
- `agrar/saatgut-stamm/:id` ← `src/pages/agrar/saatgut-stamm.tsx`
- `agrar/saatgut/liste` ← `src/pages/agrar/saatgut/liste.tsx`
- `agrar/saatgut/stamm` ← `src/pages/agrar/saatgut/stamm.tsx`
- `agrar/saatgut/stamm/:id` ← `src/pages/agrar/saatgut/stamm.tsx`
- `crm/audits/neu` ← `src/pages/crm/lieferanten-liste.tsx`
- `crm/campaign-detail` ← `src/pages/crm/campaign-detail.tsx`
- `crm/campaign-template-detail` ← `src/pages/crm/campaign-template-detail.tsx`
- `crm/campaign-template/:id` ← `src/pages/crm/campaign-template-detail.tsx`
- `crm/campaign-template/new` ← `src/pages/crm/campaign-template-detail.tsx`
- `crm/campaign-templates` ← `src/pages/crm/campaign-templates.tsx`
- `crm/campaign/:id` ← `src/pages/crm/campaign-detail.tsx`
- `crm/campaign/new` ← `src/pages/crm/campaign-detail.tsx`
- `crm/campaigns` ← `src/pages/crm/campaigns.tsx`
- `crm/campaigns/new` ← `src/pages/crm/campaign-detail.tsx`
- `crm/consent-detail` ← `src/pages/crm/consent-detail.tsx`
- `crm/consent-management` ← `src/pages/crm/consent-management.tsx`
- `crm/consent/:id` ← `src/pages/crm/consent-detail.tsx`
- `crm/consent/new` ← `src/pages/crm/consent-detail.tsx`
- `crm/consents` ← `src/pages/crm/consent-management.tsx`
- `crm/customers` ← `src/pages/crm/kunden-liste.tsx`
- `crm/customers/:id` ← `src/pages/crm/kunden-stamm.tsx`
- `crm/gdpr-request-detail` ← `src/pages/crm/gdpr-request-detail.tsx`
- `crm/gdpr-request/:id` ← `src/pages/crm/gdpr-request-detail.tsx`
- `crm/gdpr-request/new` ← `src/pages/crm/gdpr-request-detail.tsx`
- `crm/gdpr-requests` ← `src/pages/crm/gdpr-requests.tsx`
- `crm/kontakt-management` ← `src/pages/crm/kontakt-management.tsx`
- `crm/kunden` ← `src/pages/crm/kunden-liste.tsx`

## Runtime-verdrahtet (alle)

- `admin/identity-budgets` ← `src/pages/admin/identity-budgets.tsx`
- `admin/postfaecher` ← `src/pages/admin/postfaecher.tsx`
- `admin/token-consumption` ← `src/pages/admin/token-consumption.tsx`
- `agrar/duenger/:id` ← `src/pages/agrar/duenger-native.tsx`
- `agrar/harvest-settlement/:id` ← `src/pages/agrar/ernte-abrechnung-native.tsx`
- `agrar/kontrakt/:id` ← `src/pages/agrar/kontrakt-native.tsx`
- `agrar/kontrakte/:id` ← `src/pages/agrar/kontrakt-native.tsx`
- `agrar/saatgut/:id` ← `src/pages/agrar/saatgut-native.tsx`
- `belege/:belegart/:id` ← `src/pages/belege/beleg.tsx`
- `crm/kunden-schnellauswahl` ← `src/pages/crm/kunden-schnellauswahl.tsx`
- `crm/opportunity/:id` ← `src/pages/crm/opportunity-native.tsx`
- `einkauf/anfrage/:id` ← `src/pages/einkauf/anfrage-native.tsx`
- `einkauf/angebot/:id` ← `src/pages/einkauf/angebot-native.tsx`
- `einkauf/anlieferavis/:id` ← `src/pages/einkauf/anlieferavis-native.tsx`
- `einkauf/auftragsbestaetigung/:id` ← `src/pages/einkauf/auftragsbestaetigung-native.tsx`
- `einkauf/bestellung/:id` ← `src/pages/einkauf/bestellung-native.tsx`
- `einkauf/lieferanten/:id` ← `src/pages/einkauf/supplier-native.tsx`
- `einkauf/supplier/:id` ← `src/pages/einkauf/supplier-native.tsx`
- `finance/ap-invoice/:id` ← `src/pages/finance/ap-invoice-native.tsx`
- `finance/ar-open-item/:id` ← `src/pages/finance/ar-open-item-native.tsx`
- `finance/bankkonto/:id` ← `src/pages/finance/bankkonto-native.tsx`
- `finance/debitor/:id` ← `src/pages/finance/debitor-native.tsx`
- `finance/kreditor/:id` ← `src/pages/finance/kreditor-native.tsx`
- `finance/payment-run/:id` ← `src/pages/finance/payment-run-native.tsx`
- `finance/steuerschluessel` ← `src/pages/finance/steuerschluessel.tsx`
- `fuhrpark/ausgehende-belege-dokumente` ← `src/pages/fuhrpark/ausgehende-belege-dokumente.tsx`
- `fuhrpark/fahrzeug-stamm` ← `src/pages/fuhrpark/fahrzeug-stamm.tsx`
- `fuhrpark/fahrzeug/:id` ← `src/pages/fuhrpark/fahrzeug-stamm.tsx`
- `fuhrpark/fahrzeug/neu` ← `src/pages/fuhrpark/fahrzeug-stamm.tsx`
- `fuhrpark/fuhrpark-rechnungen` ← `src/pages/fuhrpark/fuhrpark-rechnungen.tsx`
- `fuhrpark/fuhrpark-stammdaten` ← `src/pages/fuhrpark/fuhrpark-stammdaten.tsx`
- `futtermittel/mischfuttermittel/:id` ← `src/pages/futtermittel/mischfuttermittel-native.tsx`
- `lager/article-stock/:id` ← `src/pages/lager/article-stock-native.tsx`
- `lager/artikel/:id` ← `src/pages/lager/article-stock-native.tsx`
- `lager/stock-movement/:id` ← `src/pages/lager/lagerbewegung-native.tsx`
- `logistik/frachttabellen` ← `src/pages/logistik/frachttabellen.tsx`
- `logistik/tour-fracht-arbeitsraum` ← `src/pages/logistik/tour-fracht-arbeitsraum.tsx`
- `logistik/tourenplanung` ← `src/pages/logistik/tourenplanung.tsx`
- `logistik/versandprofile` ← `src/pages/logistik/versandprofile.tsx`
- `personal/bewerbung-einwilligung` ← `src/pages/personal/bewerbung-einwilligung.tsx`
- `personal/bewerbung/:id/einwilligung` ← `src/pages/personal/bewerbung-einwilligung.tsx`
- `personal/bewerbungen` ← `src/pages/personal/bewerbungen.tsx`
- `personal/einwilligungserklaerungen` ← `src/pages/personal/einwilligungserklaerungen.tsx`
- `personal/onboarding` ← `src/pages/personal/onboarding.tsx`
- `personal/qualifikationen` ← `src/pages/personal/qualifikationen.tsx`
- `personal/schulungen` ← `src/pages/personal/schulungen.tsx`
- `qualitaet/reklamation/:id` ← `src/pages/qualitaet/reklamation-native.tsx`
- `sales/credit-note-editor` ← `src/pages/sales/credit-note-editor.tsx`
- `sales/credit-notes` ← `src/pages/sales/credit-note-editor.tsx`
- `sales/delivery-note/:id` ← `src/pages/verkauf/lieferschein-native.tsx`
- `sales/rechnungen` ← `src/pages/verkauf/rechnungen-worklist.tsx`
- `sales/sales-order/:id` ← `src/pages/sales/sales-order-native.tsx`
- `strecke/streckengeschaeft` ← `src/pages/strecke/streckengeschaeft.tsx`
- `studio/run/:screenId` ← `src/pages/admin/studio-run.tsx`
- `transporte/fahrer` ← `src/pages/transporte/fahrer-liste.tsx`
- `transporte/fahrer-liste` ← `src/pages/transporte/fahrer-liste.tsx`
- `transporte/fahrer/:id` ← `src/pages/transporte/fahrer-liste.tsx`
- `transporte/fahrer/neu` ← `src/pages/transporte/fahrer-liste.tsx`
- `verkauf/rechnung/:id` ← `src/pages/verkauf/rechnung.tsx`
- `verkauf/rechnungen` ← `src/pages/verkauf/rechnungen-worklist.tsx`
- `versand/versand-avis` ← `src/pages/versand/versand-avis.tsx`

## Handgebaut — Migrationskandidaten (erste 60, alphabetisch)

- `/` ← `src/pages/start-dashboard.tsx`
- `abrechnung/eb-lieferschein-kontrolle` ← `src/pages/abrechnung/eb-lieferschein-kontrolle.tsx`
- `admin-suite` ← `src/pages/admin-suite/index.tsx`
- `admin-suite/compliance` ← `src/pages/admin-suite/compliance.tsx`
- `admin-suite/connectors` ← `src/pages/admin-suite/connectors.tsx`
- `admin-suite/devices` ← `src/pages/admin-suite/devices.tsx`
- `admin-suite/diagnostics` ← `src/pages/admin-suite/diagnostics.tsx`
- `admin-suite/ki-anbieter` ← `src/pages/admin-suite/ki-anbieter.tsx`
- `admin-suite/migration` ← `src/pages/admin-suite/migration.tsx`
- `admin-suite/operations` ← `src/pages/admin-suite/operations.tsx`
- `admin-suite/pos-fiscalization` ← `src/pages/admin-suite/pos-fiscalization.tsx`
- `admin-suite/security` ← `src/pages/admin-suite/security.tsx`
- `admin-suite/setup` ← `src/pages/admin-suite/setup.tsx`
- `admin-suite/system-status` ← `src/pages/admin-suite/system-status.tsx`
- `admin/GapPipelineConsole` ← `src/pages/admin/GapPipelineConsole.tsx`
- `admin/agenten-integration` ← `src/pages/admin/agenten-integration.tsx`
- `admin/ai-approvals` ← `src/pages/admin/ai-approvals.tsx`
- `admin/audit-log` ← `src/pages/admin/audit-log.tsx`
- `admin/benutzer` ← `src/pages/admin/benutzer-liste.tsx`
- `admin/benutzer-liste` ← `src/pages/admin/benutzer-liste.tsx`
- `admin/benutzer/:id` ← `src/pages/admin/benutzer-liste.tsx`
- `admin/benutzer/neu` ← `src/pages/admin/benutzer-liste.tsx`
- `admin/command-monitor` ← `src/pages/admin/command-monitor.tsx`
- `admin/compliance` ← `src/pages/admin/compliance-dashboard.tsx`
- `admin/compliance-dashboard` ← `src/pages/admin/compliance-dashboard.tsx`
- `admin/control-center` ← `src/pages/admin/control-center/index.tsx`
- `admin/control-center/agent-ops` ← `src/pages/admin/control-center/agent-ops.tsx`
- `admin/control-center/superglue` ← `src/pages/admin/control-center/superglue.tsx`
- `admin/data-quality` ← `src/pages/admin/data-quality.tsx`
- `admin/externe-gates` ← `src/pages/admin/externe-gates.tsx`
- `admin/gap-pipeline` ← `src/pages/admin/GapPipelineConsole.tsx`
- `admin/integrationen-quarantaene` ← `src/pages/admin/integrationen-quarantaene.tsx`
- `admin/monitoring/alerts` ← `src/pages/admin/monitoring/alerts.tsx`
- `admin/monitoring/regeln` ← `src/pages/admin/monitoring/regeln.tsx`
- `admin/nummernkreise` ← `src/pages/admin/nummernkreise.tsx`
- `admin/postfaecher/anmeldung-rueckruf` ← `src/pages/admin/postfaecher-anmeldung-rueckruf.tsx`
- `admin/qualitaets-cockpit` ← `src/pages/admin/qualitaets-cockpit.tsx`
- `admin/report-berechtigungen` ← `src/pages/admin/report-berechtigungen.tsx`
- `admin/rolle/:id` ← `src/pages/admin/rollen-verwaltung.tsx`
- `admin/rolle/neu` ← `src/pages/admin/rollen-verwaltung.tsx`
- `admin/rollen-verwaltung` ← `src/pages/admin/rollen-verwaltung.tsx`
- `admin/screen-studio` ← `src/pages/admin/screen-studio.tsx`
- `admin/setup` ← `src/pages/admin/setup/index.tsx`
- `admin/setup/dms-integration` ← `src/pages/admin/setup/dms-integration.tsx`
- `admin/terminologie` ← `src/pages/admin/terminologie.tsx`
- `admin/voice-channel` ← `src/pages/admin/voice-channel.tsx`
- `admin/vordruck-editor` ← `src/pages/admin/vordruck-editor.tsx`
- `admin/webhooks` ← `src/pages/admin/webhooks.tsx`
- `admin/webshop` ← `src/pages/admin/webshop.tsx`
- `agrar` ← `src/pages/agrar/aussaat/liste.tsx`
- `agrar/annahmen-qualitaet-nachtrag` ← `src/pages/agrar/annahmen-qualitaet-nachtrag.tsx`
- `agrar/aussaat` ← `src/pages/agrar/aussaat/liste.tsx`
- `agrar/aussaat/:id` ← `src/pages/agrar/aussaat/liste.tsx`
- `agrar/aussaat/liste` ← `src/pages/agrar/aussaat/liste.tsx`
- `agrar/aussaat/neu` ← `src/pages/agrar/aussaat/liste.tsx`
- `agrar/bodenprobe/:id` ← `src/pages/agrar/bodenproben/liste.tsx`
- `agrar/bodenprobe/neu` ← `src/pages/agrar/bodenproben/liste.tsx`
- `agrar/bodenproben` ← `src/pages/agrar/bodenproben/liste.tsx`
- `agrar/bodenproben/liste` ← `src/pages/agrar/bodenproben/liste.tsx`
- `agrar/duenger` ← `src/pages/agrar/duenger/liste.tsx`
