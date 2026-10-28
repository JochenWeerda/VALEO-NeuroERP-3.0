---
title: Masken-API-Katalog
type: reference
audience: [ki-agent, entwickler, integrator]
owner: Cursor
status: aktiv
last_reviewed: 2026-10-28
version: 3.0.0
description: ScreenDefinitions mit AgentMaskContract, REST-Endpoints und Actions.
---

# Masken-API-Katalog

> Generiert aus `app/core/screen_definitions.py` (848 Masken).

## Übersicht

| mask_id | Titel | Domäne | Risiko | Prozessketten | Agent-Contract |
|---|---|---|---|---|---|
| `abrechnung/eb-lieferschein-kontrolle` | EB-Lieferschein-Kontrolle | finance | niedrig | — | `GET /api/v1/masks/abrechnung/eb-lieferschein-kontrolle/agent-contract` |
| `admin/agenten-integration` | Agenten integration | admin | niedrig | — | `GET /api/v1/masks/admin/agenten-integration/agent-contract` |
| `admin/ai-approvals` | AI-Freigaben | admin | niedrig | — | `GET /api/v1/masks/admin/ai-approvals/agent-contract` |
| `admin/api-keys` | Api keys | admin | niedrig | — | `GET /api/v1/masks/admin/api-keys/agent-contract` |
| `admin/audit-log` | Audit log | admin | niedrig | — | `GET /api/v1/masks/admin/audit-log/agent-contract` |
| `admin/audit-log-liste` | Audit-Log | admin | niedrig | — | `GET /api/v1/masks/admin/audit-log-liste/agent-contract` |
| `admin/backup-restore` | Backup restore | admin | niedrig | — | `GET /api/v1/masks/admin/backup-restore/agent-contract` |
| `admin/belegfolgekonfig` | Belegfolgekonfig | admin | niedrig | — | `GET /api/v1/masks/admin/belegfolgekonfig/agent-contract` |
| `admin/benutzer-liste` | Benutzer | admin | niedrig | — | `GET /api/v1/masks/admin/benutzer-liste/agent-contract` |
| `admin/berechtigungen-matrix` | Berechtigungen matrix | admin | niedrig | — | `GET /api/v1/masks/admin/berechtigungen-matrix/agent-contract` |
| `admin/branches` | Branches | admin | niedrig | — | `GET /api/v1/masks/admin/branches/agent-contract` |
| `admin/command-monitor` | Command monitor | admin | niedrig | — | `GET /api/v1/masks/admin/command-monitor/agent-contract` |
| `admin/compliance-dashboard` | Compliance-Dashboard | compliance | niedrig | — | `GET /api/v1/masks/admin/compliance-dashboard/agent-contract` |
| `admin/control-center` | Control center | admin | niedrig | — | `GET /api/v1/masks/admin/control-center/agent-contract` |
| `admin/control-center/ai-approvals` | Ai approvals | admin | niedrig | — | `GET /api/v1/masks/admin/control-center/ai-approvals/agent-contract` |
| `admin/control-center/incident-response` | Incident response | admin | niedrig | — | `GET /api/v1/masks/admin/control-center/incident-response/agent-contract` |
| `admin/control-center/operations` | Operations | admin | niedrig | — | `GET /api/v1/masks/admin/control-center/operations/agent-contract` |
| `admin/control-center/security` | Security | admin | niedrig | — | `GET /api/v1/masks/admin/control-center/security/agent-contract` |
| `admin/core/audit-governance` | Audit governance | admin | niedrig | — | `GET /api/v1/masks/admin/core/audit-governance/agent-contract` |
| `admin/data-quality` | Data quality | admin | niedrig | — | `GET /api/v1/masks/admin/data-quality/agent-contract` |
| `admin/devices` | Devices | admin | niedrig | — | `GET /api/v1/masks/admin/devices/agent-contract` |
| `admin/dms-integration` | Dms integration | admin | niedrig | — | `GET /api/v1/masks/admin/dms-integration/agent-contract` |
| `admin/erntepeak-stabilitaet` | Erntepeak stabilitaet | admin | niedrig | — | `GET /api/v1/masks/admin/erntepeak-stabilitaet/agent-contract` |
| `admin/forst/kalkulation` | Kalkulation | admin | niedrig | — | `GET /api/v1/masks/admin/forst/kalkulation/agent-contract` |
| `admin/identity-budgets` | Nutzer- und Agentenkontingente | platform | mittel | — | `GET /api/v1/masks/admin/identity-budgets/agent-contract` |
| `admin/integrationen-quarantaene` | Integrationen quarantaene | admin | niedrig | — | `GET /api/v1/masks/admin/integrationen-quarantaene/agent-contract` |
| `admin/monitoring/alerting` | Alerting | admin | niedrig | — | `GET /api/v1/masks/admin/monitoring/alerting/agent-contract` |
| `admin/monitoring/historie` | Historie | admin | niedrig | — | `GET /api/v1/masks/admin/monitoring/historie/agent-contract` |
| `admin/monitoring/regeln` | Regeln | admin | niedrig | — | `GET /api/v1/masks/admin/monitoring/regeln/agent-contract` |
| `admin/omnichannel-handelskonflikt` | Omnichannel handelskonflikt | admin | niedrig | — | `GET /api/v1/masks/admin/omnichannel-handelskonflikt/agent-contract` |
| `admin/postfaecher` | Postfächer | platform | niedrig | — | `GET /api/v1/masks/admin/postfaecher/agent-contract` |
| `admin/qualitaets-cockpit` | Qualitaets-Cockpit | qualitaet | niedrig | — | `GET /api/v1/masks/admin/qualitaets-cockpit/agent-contract` |
| `admin/system-einstellungen` | System einstellungen | admin | niedrig | — | `GET /api/v1/masks/admin/system-einstellungen/agent-contract` |
| `admin/tankstelle-evb` | Tankstelle evb | admin | niedrig | — | `GET /api/v1/masks/admin/tankstelle-evb/agent-contract` |
| `admin/tenants` | Tenants | admin | niedrig | — | `GET /api/v1/masks/admin/tenants/agent-contract` |
| `admin/token-consumption` | Technisches Verbrauchsnebenbuch | platform | niedrig | — | `GET /api/v1/masks/admin/token-consumption/agent-contract` |
| `admin/users` | Users | admin | niedrig | — | `GET /api/v1/masks/admin/users/agent-contract` |
| `admin/webhooks-liste` | Webhooks | admin | niedrig | — | `GET /api/v1/masks/admin/webhooks-liste/agent-contract` |
| `admin/workflow-editor` | Workflow editor | admin | niedrig | — | `GET /api/v1/masks/admin/workflow-editor/agent-contract` |
| `admin/zeitachsen-editor` | Zeitachsen editor | admin | niedrig | — | `GET /api/v1/masks/admin/zeitachsen-editor/agent-contract` |
| `agrar/annahme-abrechnung` | Annahme abrechnung | agrar | niedrig | — | `GET /api/v1/masks/agrar/annahme-abrechnung/agent-contract` |
| `agrar/biostimulanzien-liste` | Biostimulanzien | agrar | niedrig | — | `GET /api/v1/masks/agrar/biostimulanzien-liste/agent-contract` |
| `agrar/bodenproben-liste` | Bodenproben | agrar | niedrig | — | `GET /api/v1/masks/agrar/bodenproben-liste/agent-contract` |
| `agrar/daily-prices` | Daily prices | agrar | niedrig | — | `GET /api/v1/masks/agrar/daily-prices/agent-contract` |
| `agrar/duenger` | Duenger | agrar | niedrig | — | `GET /api/v1/masks/agrar/duenger/agent-contract` |
| `agrar/duenger-liste` | Duenger | agrar | niedrig | — | `GET /api/v1/masks/agrar/duenger-liste/agent-contract` |
| `agrar/duenger-rechner` | Duenger rechner | agrar | niedrig | — | `GET /api/v1/masks/agrar/duenger-rechner/agent-contract` |
| `agrar/ernte-annahme-abrechnung` | Ernte annahme abrechnung | agrar | niedrig | — | `GET /api/v1/masks/agrar/ernte-annahme-abrechnung/agent-contract` |
| `agrar/ernte-annahme-energiemais-liste` | Ernte Annahme Energiemais | agrar | niedrig | — | `GET /api/v1/masks/agrar/ernte-annahme-energiemais-liste/agent-contract` |
| `agrar/ernte-kampagne-erfassung` | Ernte kampagne erfassung | agrar | niedrig | — | `GET /api/v1/masks/agrar/ernte-kampagne-erfassung/agent-contract` |
| `agrar/ernte-liste` | Ernte | agrar | niedrig | — | `GET /api/v1/masks/agrar/ernte-liste/agent-contract` |
| `agrar/ernte-qualitaetsfreigabe` | Ernte qualitaetsfreigabe | agrar | niedrig | — | `GET /api/v1/masks/agrar/ernte-qualitaetsfreigabe/agent-contract` |
| `agrar/ernte/kampagnenabschluss` | Kampagnenabschluss | agrar | niedrig | — | `GET /api/v1/masks/agrar/ernte/kampagnenabschluss/agent-contract` |
| `agrar/feed-advice` | Fuetterungsberatung | agrar | niedrig | — | `GET /api/v1/masks/agrar/feed-advice/agent-contract` |
| `agrar/feed-controlling` | Fuetterungscontrolling | agrar | niedrig | — | `GET /api/v1/masks/agrar/feed-controlling/agent-contract` |
| `agrar/feed-readiness` | Futterversorgung | agrar | mittel | — | `GET /api/v1/masks/agrar/feed-readiness/agent-contract` |
| `agrar/feeding-actuals` | Komponentenbezogene Ist-Fuetterung | agrar | mittel | — | `GET /api/v1/masks/agrar/feeding-actuals/agent-contract` |
| `agrar/feeding-business` | Fuetterungsbetrieb | agrar | niedrig | — | `GET /api/v1/masks/agrar/feeding-business/agent-contract` |
| `agrar/feeding-businesses` | Fuetterungsbetriebe | agrar | niedrig | — | `GET /api/v1/masks/agrar/feeding-businesses/agent-contract` |
| `agrar/feeding-group` | Tiergruppe | agrar | niedrig | — | `GET /api/v1/masks/agrar/feeding-group/agent-contract` |
| `agrar/feeding-plan` | Fuetterungsplan | agrar | niedrig | — | `GET /api/v1/masks/agrar/feeding-plan/agent-contract` |
| `agrar/feeding-reference-data` | Naehrstoffe und Einheiten | agrar | niedrig | — | `GET /api/v1/masks/agrar/feeding-reference-data/agent-contract` |
| `agrar/feldbuch-flurstueck-kataster-liste` | Flurstueck-Kataster | agrar | niedrig | — | `GET /api/v1/masks/agrar/feldbuch-flurstueck-kataster-liste/agent-contract` |
| `agrar/feldbuch-massnahmen-liste` | Feldbuch-Massnahmen | agrar | niedrig | — | `GET /api/v1/masks/agrar/feldbuch-massnahmen-liste/agent-contract` |
| `agrar/feldbuch-schlagkartei-liste` | Schlagkartei | agrar | niedrig | — | `GET /api/v1/masks/agrar/feldbuch-schlagkartei-liste/agent-contract` |
| `agrar/futter/mischfutter-optimierung` | Mischfutter optimierung | agrar | niedrig | — | `GET /api/v1/masks/agrar/futter/mischfutter-optimierung/agent-contract` |
| `agrar/harvest-controls` | Ernte-Abrechnung: Vertragsregeln und Freigaben | agrar | hoch | — | `GET /api/v1/masks/agrar/harvest-controls/agent-contract` |
| `agrar/harvest-settlement` | Ernte-Abrechnung | agrar | niedrig | `harvest-to-settlement`, `contract-to-settlement` | `GET /api/v1/masks/agrar/harvest-settlement/agent-contract` |
| `agrar/kalkulation/deckungsbeitrag` | Deckungsbeitrag | agrar | niedrig | — | `GET /api/v1/masks/agrar/kalkulation/deckungsbeitrag/agent-contract` |
| `agrar/kontrakt-detail` | Kontrakt | agrar | niedrig | — | `GET /api/v1/masks/agrar/kontrakt-detail/agent-contract` |
| `agrar/kontrakte` | Kontrakt | agrar | mittel | `contract-to-settlement`, `harvest-to-settlement` | `GET /api/v1/masks/agrar/kontrakte/agent-contract` |
| `agrar/kontrakte/formular` | Formular | agrar | niedrig | — | `GET /api/v1/masks/agrar/kontrakte/formular/agent-contract` |
| `agrar/kultur-stamm-liste` | Kulturen | agrar | niedrig | — | `GET /api/v1/masks/agrar/kultur-stamm-liste/agent-contract` |
| `agrar/kulturpflanzen-liste` | Kulturpflanzen | agrar | niedrig | — | `GET /api/v1/masks/agrar/kulturpflanzen-liste/agent-contract` |
| `agrar/lieferschein-erstellen` | Lieferschein erstellen | agrar | niedrig | — | `GET /api/v1/masks/agrar/lieferschein-erstellen/agent-contract` |
| `agrar/maschinen-auslastung-liste` | Maschinenauslastung | agrar | niedrig | — | `GET /api/v1/masks/agrar/maschinen-auslastung-liste/agent-contract` |
| `agrar/maschinen/formular` | Formular | agrar | niedrig | — | `GET /api/v1/masks/agrar/maschinen/formular/agent-contract` |
| `agrar/maschinen/wartung` | Wartung | agrar | niedrig | — | `GET /api/v1/masks/agrar/maschinen/wartung/agent-contract` |
| `agrar/nachhaltigkeit-eudr-liste` | EUDR Nachhaltigkeit | agrar | niedrig | — | `GET /api/v1/masks/agrar/nachhaltigkeit-eudr-liste/agent-contract` |
| `agrar/nawaro-erntemeldung` | Nawaro erntemeldung | agrar | niedrig | — | `GET /api/v1/masks/agrar/nawaro-erntemeldung/agent-contract` |
| `agrar/nawaro-kaskade` | Nawaro kaskade | agrar | niedrig | — | `GET /api/v1/masks/agrar/nawaro-kaskade/agent-contract` |
| `agrar/nawaro-vertraege` | Nawaro vertraege | agrar | niedrig | — | `GET /api/v1/masks/agrar/nawaro-vertraege/agent-contract` |
| `agrar/partie-historie` | Partie historie | agrar | niedrig | — | `GET /api/v1/masks/agrar/partie-historie/agent-contract` |
| `agrar/pflanzenschutz-applikationen-liste` | Pflanzenschutz-Applikationen | agrar | niedrig | — | `GET /api/v1/masks/agrar/pflanzenschutz-applikationen-liste/agent-contract` |
| `agrar/pflanzenschutz-liste` | Pflanzenschutz liste | agrar | niedrig | — | `GET /api/v1/masks/agrar/pflanzenschutz-liste/agent-contract` |
| `agrar/pflanzenschutz-rechner` | Pflanzenschutz rechner | agrar | niedrig | — | `GET /api/v1/masks/agrar/pflanzenschutz-rechner/agent-contract` |
| `agrar/planung/duengeplanung` | Duengeplanung | agrar | niedrig | — | `GET /api/v1/masks/agrar/planung/duengeplanung/agent-contract` |
| `agrar/planung/fruchtfolge` | Fruchtfolge | agrar | niedrig | — | `GET /api/v1/masks/agrar/planung/fruchtfolge/agent-contract` |
| `agrar/probenehmer-stamm` | Probenehmer stamm | agrar | niedrig | — | `GET /api/v1/masks/agrar/probenehmer-stamm/agent-contract` |
| `agrar/psm` | PSM | agrar | niedrig | — | `GET /api/v1/masks/agrar/psm/agent-contract` |
| `agrar/psm-abgabedokumentation-liste` | PSM Abgabedokumentation | agrar | niedrig | — | `GET /api/v1/masks/agrar/psm-abgabedokumentation-liste/agent-contract` |
| `agrar/psm-beratung-liste` | PSM Beratung | agrar | niedrig | — | `GET /api/v1/masks/agrar/psm-beratung-liste/agent-contract` |
| `agrar/psm-liste` | Pflanzenschutzmittel | agrar | niedrig | — | `GET /api/v1/masks/agrar/psm-liste/agent-contract` |
| `agrar/psm-sachkunde-register-liste` | PSM Sachkunde | agrar | niedrig | — | `GET /api/v1/masks/agrar/psm-sachkunde-register-liste/agent-contract` |
| `agrar/psm-wasserschutz-liste` | Wasserschutz | agrar | niedrig | — | `GET /api/v1/masks/agrar/psm-wasserschutz-liste/agent-contract` |
| `agrar/psm/anwendungsprotokoll` | Anwendungsprotokoll | agrar | niedrig | — | `GET /api/v1/masks/agrar/psm/anwendungsprotokoll/agent-contract` |
| `agrar/psm/tankmischung` | Tankmischung | agrar | niedrig | — | `GET /api/v1/masks/agrar/psm/tankmischung/agent-contract` |
| `agrar/qualitaet/ausnahmen` | Ausnahmen | agrar | niedrig | — | `GET /api/v1/masks/agrar/qualitaet/ausnahmen/agent-contract` |
| `agrar/qualitaet/laborwerte` | Laborwerte | agrar | niedrig | — | `GET /api/v1/masks/agrar/qualitaet/laborwerte/agent-contract` |
| `agrar/qualitaet/mykotoxine` | Mykotoxine | agrar | niedrig | — | `GET /api/v1/masks/agrar/qualitaet/mykotoxine/agent-contract` |
| `agrar/ration` | Rationsfreigabe | agrar | hoch | — | `GET /api/v1/masks/agrar/ration/agent-contract` |
| `agrar/rations-lifecycle` | Rationen und Freigaben | agrar | niedrig | — | `GET /api/v1/masks/agrar/rations-lifecycle/agent-contract` |
| `agrar/rechnungen-erstellen` | Rechnungen erstellen | agrar | niedrig | — | `GET /api/v1/masks/agrar/rechnungen-erstellen/agent-contract` |
| `agrar/saatgut` | Saatgut | agrar | niedrig | — | `GET /api/v1/masks/agrar/saatgut/agent-contract` |
| `agrar/saatgut-bestellungen-liste` | Saatgut-Bestellungen | agrar | niedrig | — | `GET /api/v1/masks/agrar/saatgut-bestellungen-liste/agent-contract` |
| `agrar/saatgut-liste` | Saatgut | agrar | niedrig | — | `GET /api/v1/masks/agrar/saatgut-liste/agent-contract` |
| `agrar/saatgut-sortenregister-liste` | Sortenregister | agrar | niedrig | — | `GET /api/v1/masks/agrar/saatgut-sortenregister-liste/agent-contract` |
| `agrar/saatgut/abrechnung` | Abrechnung | agrar | niedrig | — | `GET /api/v1/masks/agrar/saatgut/abrechnung/agent-contract` |
| `agrar/saatgut/formular` | Formular | agrar | niedrig | — | `GET /api/v1/masks/agrar/saatgut/formular/agent-contract` |
| `agrar/saatgut/prognose` | Prognose | agrar | niedrig | — | `GET /api/v1/masks/agrar/saatgut/prognose/agent-contract` |
| `agrar/saatgut/royalties` | Royalties | agrar | niedrig | — | `GET /api/v1/masks/agrar/saatgut/royalties/agent-contract` |
| `agrar/saatgut/vermehrung` | Vermehrung | agrar | niedrig | — | `GET /api/v1/masks/agrar/saatgut/vermehrung/agent-contract` |
| `agrar/saatzucht-partien-liste` | Saatzucht-Partien | agrar | niedrig | — | `GET /api/v1/masks/agrar/saatzucht-partien-liste/agent-contract` |
| `agrar/schlaege-karte-liste` | Schlagkarte | agrar | niedrig | — | `GET /api/v1/masks/agrar/schlaege-karte-liste/agent-contract` |
| `agrar/schlaege-kulturhistorie-liste` | Kulturhistorie | agrar | niedrig | — | `GET /api/v1/masks/agrar/schlaege-kulturhistorie-liste/agent-contract` |
| `agrar/schlaege-liste` | Schlaege | agrar | niedrig | — | `GET /api/v1/masks/agrar/schlaege-liste/agent-contract` |
| `agrar/schlaege/bodenprobe` | Bodenprobe | agrar | niedrig | — | `GET /api/v1/masks/agrar/schlaege/bodenprobe/agent-contract` |
| `agrar/schlaege/duengung` | Duengung | agrar | niedrig | — | `GET /api/v1/masks/agrar/schlaege/duengung/agent-contract` |
| `agrar/schlaege/ernte` | Ernte | agrar | niedrig | — | `GET /api/v1/masks/agrar/schlaege/ernte/agent-contract` |
| `agrar/schlaege/formular` | Formular | agrar | niedrig | — | `GET /api/v1/masks/agrar/schlaege/formular/agent-contract` |
| `agrar/schlaege/pflanzenschutz` | Pflanzenschutz | agrar | niedrig | — | `GET /api/v1/masks/agrar/schlaege/pflanzenschutz/agent-contract` |
| `agrar/schlaege/saat` | Saat | agrar | niedrig | — | `GET /api/v1/masks/agrar/schlaege/saat/agent-contract` |
| `agrar/sektion-auswahl` | Sektion auswahl | agrar | niedrig | — | `GET /api/v1/masks/agrar/sektion-auswahl/agent-contract` |
| `agrar/self-billing` | Self billing | agrar | niedrig | — | `GET /api/v1/masks/agrar/self-billing/agent-contract` |
| `agrar/silo-belegung` | Silo belegung | agrar | niedrig | — | `GET /api/v1/masks/agrar/silo-belegung/agent-contract` |
| `agrar/silo-qualitaet` | Silo qualitaet | agrar | niedrig | — | `GET /api/v1/masks/agrar/silo-qualitaet/agent-contract` |
| `agrar/silo-trocknung` | Silo trocknung | agrar | niedrig | — | `GET /api/v1/masks/agrar/silo-trocknung/agent-contract` |
| `agrar/soil-samples` | Soil samples | agrar | niedrig | — | `GET /api/v1/masks/agrar/soil-samples/agent-contract` |
| `agrar/sorten` | Sorten | agrar | niedrig | — | `GET /api/v1/masks/agrar/sorten/agent-contract` |
| `agrar/sorten-vermehrung` | Sorten vermehrung | agrar | niedrig | — | `GET /api/v1/masks/agrar/sorten-vermehrung/agent-contract` |
| `agrar/trocknungsregeln` | Trocknungsregeln | agrar | niedrig | — | `GET /api/v1/masks/agrar/trocknungsregeln/agent-contract` |
| `agrar/umwelt/nitrat` | Nitrat | agrar | niedrig | — | `GET /api/v1/masks/agrar/umwelt/nitrat/agent-contract` |
| `agrar/vermehrungsvertraege-liste` | Vermehrungsvertraege | agrar | niedrig | — | `GET /api/v1/masks/agrar/vermehrungsvertraege-liste/agent-contract` |
| `agrar/vertraege/formular` | Formular | agrar | niedrig | — | `GET /api/v1/masks/agrar/vertraege/formular/agent-contract` |
| `agrar/vertrag-kontingente-liste` | Vertrag-Kontingente | agrar | niedrig | — | `GET /api/v1/masks/agrar/vertrag-kontingente-liste/agent-contract` |
| `agrar/wetter` | Wetter | agrar | niedrig | — | `GET /api/v1/masks/agrar/wetter/agent-contract` |
| `agrar/wiegeschein-detail` | Wiegeschein detail | agrar | niedrig | — | `GET /api/v1/masks/agrar/wiegeschein-detail/agent-contract` |
| `aktien/dividenden` | Dividenden | genossenschaft | niedrig | — | `GET /api/v1/masks/aktien/dividenden/agent-contract` |
| `aktien/hauptversammlung` | Hauptversammlung | genossenschaft | niedrig | — | `GET /api/v1/masks/aktien/hauptversammlung/agent-contract` |
| `aktien/mitglieder` | Mitglieder | genossenschaft | niedrig | — | `GET /api/v1/masks/aktien/mitglieder/agent-contract` |
| `aktien/stimmrechte` | Stimmrechte | genossenschaft | niedrig | — | `GET /api/v1/masks/aktien/stimmrechte/agent-contract` |
| `aktien/zeichnungen` | Zeichnungen | genossenschaft | niedrig | — | `GET /api/v1/masks/aktien/zeichnungen/agent-contract` |
| `analysis/what-if-simulator` | What if simulator | reporting | niedrig | — | `GET /api/v1/masks/analysis/what-if-simulator/agent-contract` |
| `annahme/erfassung` | Erfassung | agrar | niedrig | — | `GET /api/v1/masks/annahme/erfassung/agent-contract` |
| `annahme/labor` | Labor | agrar | niedrig | — | `GET /api/v1/masks/annahme/labor/agent-contract` |
| `annahme/lkw-registrierung` | Lkw registrierung | agrar | niedrig | — | `GET /api/v1/masks/annahme/lkw-registrierung/agent-contract` |
| `annahme/muster` | Muster | agrar | niedrig | — | `GET /api/v1/masks/annahme/muster/agent-contract` |
| `annahme/qualitaets-check` | Qualitaets-Check | agrar | niedrig | — | `GET /api/v1/masks/annahme/qualitaets-check/agent-contract` |
| `annahme/rohwaren-annahme` | Rohwaren annahme | agrar | niedrig | — | `GET /api/v1/masks/annahme/rohwaren-annahme/agent-contract` |
| `annahme/silo-zuweisung` | Silo zuweisung | agrar | niedrig | — | `GET /api/v1/masks/annahme/silo-zuweisung/agent-contract` |
| `annahme/trocknung` | Trocknung | agrar | niedrig | — | `GET /api/v1/masks/annahme/trocknung/agent-contract` |
| `annahme/voranmeldung` | Voranmeldung | agrar | niedrig | — | `GET /api/v1/masks/annahme/voranmeldung/agent-contract` |
| `annahme/waage-1` | Waage 1 | agrar | niedrig | — | `GET /api/v1/masks/annahme/waage-1/agent-contract` |
| `annahme/waage-2` | Waage 2 | agrar | niedrig | — | `GET /api/v1/masks/annahme/waage-2/agent-contract` |
| `annahme/warteschlange` | Annahme-Warteschlange | agrar | niedrig | — | `GET /api/v1/masks/annahme/warteschlange/agent-contract` |
| `annahme/wartezeit` | Wartezeit | agrar | niedrig | — | `GET /api/v1/masks/annahme/wartezeit/agent-contract` |
| `annahme/wiegeschein` | Wiegeschein | agrar | niedrig | — | `GET /api/v1/masks/annahme/wiegeschein/agent-contract` |
| `artikel/bestandsuebersicht` | Bestandsuebersicht | lager | niedrig | — | `GET /api/v1/masks/artikel/bestandsuebersicht/agent-contract` |
| `artikel/chargen-pflicht` | Chargen pflicht | lager | niedrig | — | `GET /api/v1/masks/artikel/chargen-pflicht/agent-contract` |
| `artikel/ersatzteile` | Ersatzteile | lager | niedrig | — | `GET /api/v1/masks/artikel/ersatzteile/agent-contract` |
| `artikel/gebinde` | Gebinde | lager | niedrig | — | `GET /api/v1/masks/artikel/gebinde/agent-contract` |
| `artikel/gefahrgut` | Gefahrgut | lager | niedrig | — | `GET /api/v1/masks/artikel/gefahrgut/agent-contract` |
| `artikel/herkunft` | Herkunft | lager | niedrig | — | `GET /api/v1/masks/artikel/herkunft/agent-contract` |
| `artikel/kategorien` | Kategorien | lager | niedrig | — | `GET /api/v1/masks/artikel/kategorien/agent-contract` |
| `artikel/konditionen` | Konditionen | lager | niedrig | — | `GET /api/v1/masks/artikel/konditionen/agent-contract` |
| `artikel/lieferanten-artikel` | Lieferanten artikel | lager | niedrig | — | `GET /api/v1/masks/artikel/lieferanten-artikel/agent-contract` |
| `artikel/liste` | Artikel | lager | niedrig | — | `GET /api/v1/masks/artikel/liste/agent-contract` |
| `artikel/preisstaffeln` | Preisstaffeln | lager | niedrig | — | `GET /api/v1/masks/artikel/preisstaffeln/agent-contract` |
| `artikel/qualitaetsmerkmale` | Qualitaetsmerkmale | lager | niedrig | — | `GET /api/v1/masks/artikel/qualitaetsmerkmale/agent-contract` |
| `artikel/rabattgruppen` | Rabattgruppen | lager | niedrig | — | `GET /api/v1/masks/artikel/rabattgruppen/agent-contract` |
| `artikel/stamm` | Artikel | lager | niedrig | — | `GET /api/v1/masks/artikel/stamm/agent-contract` |
| `artikel/stuecklisten` | Stuecklisten | lager | niedrig | — | `GET /api/v1/masks/artikel/stuecklisten/agent-contract` |
| `artikel/texte-medien` | Texte medien | lager | niedrig | — | `GET /api/v1/masks/artikel/texte-medien/agent-contract` |
| `artikel/umrechnungen` | Umrechnungen | lager | niedrig | — | `GET /api/v1/masks/artikel/umrechnungen/agent-contract` |
| `artikel/verpackungen` | Verpackungen | lager | niedrig | — | `GET /api/v1/masks/artikel/verpackungen/agent-contract` |
| `artikel/zoll-intrastat` | Zoll Intrastat | lager | niedrig | — | `GET /api/v1/masks/artikel/zoll-intrastat/agent-contract` |
| `auswertungen/abfrage-center` | Abfrage-Center | reporting | mittel | — | `GET /api/v1/masks/auswertungen/abfrage-center/agent-contract` |
| `auswertungen/abfrage-generator` | Abfrage generator | reporting | niedrig | — | `GET /api/v1/masks/auswertungen/abfrage-generator/agent-contract` |
| `auswertungen/aenderungshistorie` | Aenderungshistorie | audit | niedrig | — | `GET /api/v1/masks/auswertungen/aenderungshistorie/agent-contract` |
| `auswertungen/agrarmarkt-bericht` | Agrarmarkt bericht | reporting | niedrig | — | `GET /api/v1/masks/auswertungen/agrarmarkt-bericht/agent-contract` |
| `auswertungen/auftrags-kontrolle` | Auftrags-Kontrolle | finance | niedrig | — | `GET /api/v1/masks/auswertungen/auftrags-kontrolle/agent-contract` |
| `auswertungen/beleg-kontrolle` | Beleg-Kontrolle | finance | niedrig | — | `GET /api/v1/masks/auswertungen/beleg-kontrolle/agent-contract` |
| `auswertungen/bonus-berechnung` | Bonus-Berechnung | reporting | mittel | — | `GET /api/v1/masks/auswertungen/bonus-berechnung/agent-contract` |
| `auswertungen/deckungsbeitraege` | Deckungsbeitraege | reporting | niedrig | — | `GET /api/v1/masks/auswertungen/deckungsbeitraege/agent-contract` |
| `auswertungen/dms-volltext` | Volltextsuche Dokumentenverwaltung | documents | niedrig | — | `GET /api/v1/masks/auswertungen/dms-volltext/agent-contract` |
| `auswertungen/duengemittelmengen` | Duengemittelmengen | agrar | niedrig | — | `GET /api/v1/masks/auswertungen/duengemittelmengen/agent-contract` |
| `auswertungen/erntebilanz` | Erntebilanz | reporting | niedrig | — | `GET /api/v1/masks/auswertungen/erntebilanz/agent-contract` |
| `auswertungen/kundenumsatz` | Kundenumsatz | reporting | niedrig | — | `GET /api/v1/masks/auswertungen/kundenumsatz/agent-contract` |
| `auswertungen/l3-berichtskatalog` | L3-Berichtskatalog | reporting | niedrig | — | `GET /api/v1/masks/auswertungen/l3-berichtskatalog/agent-contract` |
| `auswertungen/lagerumschlag` | Lagerumschlag | reporting | niedrig | — | `GET /api/v1/masks/auswertungen/lagerumschlag/agent-contract` |
| `auswertungen/lieferantenbewertung` | Lieferantenbewertung | reporting | niedrig | — | `GET /api/v1/masks/auswertungen/lieferantenbewertung/agent-contract` |
| `auswertungen/lieferschein-kontrolle` | Lieferschein-Kontrolle | finance | niedrig | — | `GET /api/v1/masks/auswertungen/lieferschein-kontrolle/agent-contract` |
| `auswertungen/rohertrag` | Rohertrag | reporting | niedrig | — | `GET /api/v1/masks/auswertungen/rohertrag/agent-contract` |
| `auswertungen/sanktionspruefung-kunden` | Terrorschutzpruefung Kunden | compliance | mittel | — | `GET /api/v1/masks/auswertungen/sanktionspruefung-kunden/agent-contract` |
| `auswertungen/sanktionspruefung-personal` | Terrorschutzpruefung Personal | compliance | mittel | — | `GET /api/v1/masks/auswertungen/sanktionspruefung-personal/agent-contract` |
| `auswertungen/umsatzstatistik` | Umsatzstatistik | reporting | niedrig | — | `GET /api/v1/masks/auswertungen/umsatzstatistik/agent-contract` |
| `auswertungen/vertriebstrichter` | Vertriebstrichter | reporting | niedrig | — | `GET /api/v1/masks/auswertungen/vertriebstrichter/agent-contract` |
| `auswertungen/warengruppen-analyse` | Warengruppen-Analyse | reporting | niedrig | — | `GET /api/v1/masks/auswertungen/warengruppen-analyse/agent-contract` |
| `auth/callback` | OIDC Callback | identity | niedrig | — | `GET /api/v1/masks/auth/callback/agent-contract` |
| `auth/login` | Anmeldung | identity | niedrig | — | `GET /api/v1/masks/auth/login/agent-contract` |
| `banken/konten-liste` | Bankkonten | finance | niedrig | — | `GET /api/v1/masks/banken/konten-liste/agent-contract` |
| `banken/konten-stamm` | Bankkonten-Stamm | finance | niedrig | — | `GET /api/v1/masks/banken/konten-stamm/agent-contract` |
| `banken/lastschriften` | Lastschriften | finance | niedrig | — | `GET /api/v1/masks/banken/lastschriften/agent-contract` |
| `banken/sepa-export` | SEPA-Export | finance | niedrig | — | `GET /api/v1/masks/banken/sepa-export/agent-contract` |
| `banken/ueberweisungen` | Ueberweisungen | finance | niedrig | — | `GET /api/v1/masks/banken/ueberweisungen/agent-contract` |
| `banken/zahlungsavise` | Zahlungsavise | finance | niedrig | — | `GET /api/v1/masks/banken/zahlungsavise/agent-contract` |
| `banken/zahlungsvorschlaege` | Zahlungsvorschlaege | finance | niedrig | — | `GET /api/v1/masks/banken/zahlungsvorschlaege/agent-contract` |
| `belege/belegfolge` | Belegfolge | documents | niedrig | — | `GET /api/v1/masks/belege/belegfolge/agent-contract` |
| `benachrichtigungen/liste` | Benachrichtigungen | platform | niedrig | — | `GET /api/v1/masks/benachrichtigungen/liste/agent-contract` |
| `betrieb/gefahrstoff-betriebsanweisung` | Gefahrstoff-Betriebsanweisung | operations | niedrig | — | `GET /api/v1/masks/betrieb/gefahrstoff-betriebsanweisung/agent-contract` |
| `betrieb/gefahrstoff-kataster` | Gefahrstoff-Kataster | operations | niedrig | — | `GET /api/v1/masks/betrieb/gefahrstoff-kataster/agent-contract` |
| `betrieb/maschinen-stamm` | Maschinen-Stamm | operations | niedrig | — | `GET /api/v1/masks/betrieb/maschinen-stamm/agent-contract` |
| `betrieb/prueffristen` | Prueffristen | operations | niedrig | — | `GET /api/v1/masks/betrieb/prueffristen/agent-contract` |
| `betrieb/schadensmeldung` | Schadensmeldung | operations | niedrig | — | `GET /api/v1/masks/betrieb/schadensmeldung/agent-contract` |
| `betrieb/standorte` | Standorte | operations | niedrig | — | `GET /api/v1/masks/betrieb/standorte/agent-contract` |
| `betrieb/unterweisungen` | Unterweisungen | operations | niedrig | — | `GET /api/v1/masks/betrieb/unterweisungen/agent-contract` |
| `betrieb/wartungsplan` | Wartungsplan | operations | niedrig | — | `GET /api/v1/masks/betrieb/wartungsplan/agent-contract` |
| `charge/chargen-verfolgung` | Chargen verfolgung | charge | niedrig | — | `GET /api/v1/masks/charge/chargen-verfolgung/agent-contract` |
| `charge/etiketten` | Etiketten | inventory | niedrig | — | `GET /api/v1/masks/charge/etiketten/agent-contract` |
| `charge/liste` | Chargen | lager | niedrig | — | `GET /api/v1/masks/charge/liste/agent-contract` |
| `charge/mischung` | Chargen-Mischung | inventory | niedrig | — | `GET /api/v1/masks/charge/mischung/agent-contract` |
| `charge/probenahme` | Probenahme | inventory | niedrig | — | `GET /api/v1/masks/charge/probenahme/agent-contract` |
| `charge/qualitaets-freigabe` | Qualitaets freigabe | charge | niedrig | — | `GET /api/v1/masks/charge/qualitaets-freigabe/agent-contract` |
| `charge/rueckruf` | Rueckruf | charge | niedrig | — | `GET /api/v1/masks/charge/rueckruf/agent-contract` |
| `charge/sperrlager` | Sperrlager | inventory | niedrig | — | `GET /api/v1/masks/charge/sperrlager/agent-contract` |
| `charge/stamm` | Stamm | charge | niedrig | — | `GET /api/v1/masks/charge/stamm/agent-contract` |
| `charge/teilung` | Chargenteilung | inventory | niedrig | — | `GET /api/v1/masks/charge/teilung/agent-contract` |
| `charge/wareneingang-liste` | Wareneingang Chargen | lager | niedrig | — | `GET /api/v1/masks/charge/wareneingang-liste/agent-contract` |
| `charge/zusammenfuehrung` | Chargenzusammenfuehrung | inventory | niedrig | — | `GET /api/v1/masks/charge/zusammenfuehrung/agent-contract` |
| `compliance/audit-trail` | Audit trail | compliance | niedrig | — | `GET /api/v1/masks/compliance/audit-trail/agent-contract` |
| `compliance/bvl-umsatzmeldung-liste` | BVL Umsatzmeldung | compliance | niedrig | — | `GET /api/v1/masks/compliance/bvl-umsatzmeldung-liste/agent-contract` |
| `compliance/cross-compliance` | Cross compliance | compliance | niedrig | — | `GET /api/v1/masks/compliance/cross-compliance/agent-contract` |
| `compliance/cross-compliance-liste` | Cross-Compliance | compliance | niedrig | — | `GET /api/v1/masks/compliance/cross-compliance-liste/agent-contract` |
| `compliance/duenge-bilanz` | Duenge bilanz | compliance | niedrig | — | `GET /api/v1/masks/compliance/duenge-bilanz/agent-contract` |
| `compliance/enni-meldungen-liste` | ENNI-Meldungen | compliance | niedrig | — | `GET /api/v1/masks/compliance/enni-meldungen-liste/agent-contract` |
| `compliance/eudr-compliance-liste` | EUDR Compliance | compliance | niedrig | — | `GET /api/v1/masks/compliance/eudr-compliance-liste/agent-contract` |
| `compliance/eudr-meldungen` | Eudr meldungen | compliance | niedrig | — | `GET /api/v1/masks/compliance/eudr-meldungen/agent-contract` |
| `compliance/export-pruefprotokoll` | Export-Pruefprotokoll | compliance | niedrig | — | `GET /api/v1/masks/compliance/export-pruefprotokoll/agent-contract` |
| `compliance/export-pruefung-liste` | Export-Pruefung | compliance | niedrig | — | `GET /api/v1/masks/compliance/export-pruefung-liste/agent-contract` |
| `compliance/gefahrstoff-doku-liste` | Gefahrstoff-Doku | compliance | niedrig | — | `GET /api/v1/masks/compliance/gefahrstoff-doku-liste/agent-contract` |
| `compliance/gefahrstoff-verzeichnis` | Gefahrstoff verzeichnis | compliance | niedrig | — | `GET /api/v1/masks/compliance/gefahrstoff-verzeichnis/agent-contract` |
| `compliance/gelangensbestaetigung-liste` | Gelangensbestaetigungen | compliance | niedrig | — | `GET /api/v1/masks/compliance/gelangensbestaetigung-liste/agent-contract` |
| `compliance/intrastat-liste` | Intrastat | compliance | niedrig | — | `GET /api/v1/masks/compliance/intrastat-liste/agent-contract` |
| `compliance/lksg-lieferkette` | Lksg lieferkette | compliance | niedrig | — | `GET /api/v1/masks/compliance/lksg-lieferkette/agent-contract` |
| `compliance/lksg-liste` | LKSG Lieferanten | compliance | niedrig | — | `GET /api/v1/masks/compliance/lksg-liste/agent-contract` |
| `compliance/meldewesen-konsole` | Meldewesen-Konsole | compliance | niedrig | — | `GET /api/v1/masks/compliance/meldewesen-konsole/agent-contract` |
| `compliance/pcn-liste` | PCN-Meldungen | compliance | niedrig | — | `GET /api/v1/masks/compliance/pcn-liste/agent-contract` |
| `compliance/pcn-ufi` | PCN / UFI-Meldungen | compliance | niedrig | — | `GET /api/v1/masks/compliance/pcn-ufi/agent-contract` |
| `compliance/pflanzenschutz-nachweis` | Pflanzenschutz nachweis | compliance | niedrig | — | `GET /api/v1/masks/compliance/pflanzenschutz-nachweis/agent-contract` |
| `compliance/qs-audits` | Qs audits | compliance | niedrig | — | `GET /api/v1/masks/compliance/qs-audits/agent-contract` |
| `compliance/qs-checkliste-liste` | QS-Checkliste | compliance | niedrig | — | `GET /api/v1/masks/compliance/qs-checkliste-liste/agent-contract` |
| `compliance/saatgut-nachbau-liste` | Saatgut-Nachbau | compliance | niedrig | — | `GET /api/v1/masks/compliance/saatgut-nachbau-liste/agent-contract` |
| `compliance/sachkunde-liste` | Sachkundenachweise | compliance | niedrig | — | `GET /api/v1/masks/compliance/sachkunde-liste/agent-contract` |
| `compliance/sanktionspruefung` | Sanktionspruefung | compliance | niedrig | — | `GET /api/v1/masks/compliance/sanktionspruefung/agent-contract` |
| `compliance/schadstoff-monitoring` | Schadstoff monitoring | compliance | niedrig | — | `GET /api/v1/masks/compliance/schadstoff-monitoring/agent-contract` |
| `compliance/stichtagsmeldung-bestaende` | Stichtagsmeldung bestaende | compliance | niedrig | — | `GET /api/v1/masks/compliance/stichtagsmeldung-bestaende/agent-contract` |
| `compliance/tierwohl-dokumentation` | Tierwohl dokumentation | compliance | niedrig | — | `GET /api/v1/masks/compliance/tierwohl-dokumentation/agent-contract` |
| `compliance/usp-konformitaet` | Usp konformitaet | compliance | niedrig | — | `GET /api/v1/masks/compliance/usp-konformitaet/agent-contract` |
| `compliance/vvvo-liste` | VVVO-Register | compliance | niedrig | — | `GET /api/v1/masks/compliance/vvvo-liste/agent-contract` |
| `compliance/wasserschutz-auflagen` | Wasserschutz auflagen | compliance | niedrig | — | `GET /api/v1/masks/compliance/wasserschutz-auflagen/agent-contract` |
| `compliance/zertifikate` | Zertifikate | compliance | niedrig | — | `GET /api/v1/masks/compliance/zertifikate/agent-contract` |
| `compliance/zulassungen-liste` | Zulassungsregister | compliance | niedrig | — | `GET /api/v1/masks/compliance/zulassungen-liste/agent-contract` |
| `contracts-v2` | Contracts v2 | workspace | niedrig | — | `GET /api/v1/masks/contracts-v2/agent-contract` |
| `contracts/contract` | Contract | contracts | niedrig | — | `GET /api/v1/masks/contracts/contract/agent-contract` |
| `controlling/abweichungsanalyse` | Abweichungsanalyse | controlling | niedrig | — | `GET /api/v1/masks/controlling/abweichungsanalyse/agent-contract` |
| `controlling/agrarkalkulation` | Agrarkalkulation | controlling | niedrig | — | `GET /api/v1/masks/controlling/agrarkalkulation/agent-contract` |
| `controlling/benchmark-cockpit` | Benchmark-Cockpit | controlling | niedrig | — | `GET /api/v1/masks/controlling/benchmark-cockpit/agent-contract` |
| `controlling/berichtswesen` | Berichtswesen | controlling | niedrig | — | `GET /api/v1/masks/controlling/berichtswesen/agent-contract` |
| `controlling/bwa` | Bwa | controlling | niedrig | — | `GET /api/v1/masks/controlling/bwa/agent-contract` |
| `controlling/cashflow-prognose` | Cashflow prognose | controlling | niedrig | — | `GET /api/v1/masks/controlling/cashflow-prognose/agent-contract` |
| `controlling/dashboard-verwaltung` | Dashboard-Verwaltung | controlling | niedrig | — | `GET /api/v1/masks/controlling/dashboard-verwaltung/agent-contract` |
| `controlling/deckungsbeitragsrechnung` | Deckungsbeitragsrechnung | controlling | niedrig | — | `GET /api/v1/masks/controlling/deckungsbeitragsrechnung/agent-contract` |
| `controlling/investitionsrechnung` | Investitionsrechnung | controlling | niedrig | — | `GET /api/v1/masks/controlling/investitionsrechnung/agent-contract` |
| `controlling/kampagnen-controlling` | Kampagnen controlling | controlling | niedrig | — | `GET /api/v1/masks/controlling/kampagnen-controlling/agent-contract` |
| `controlling/kennzahlen` | Kennzahlen | controlling | niedrig | — | `GET /api/v1/masks/controlling/kennzahlen/agent-contract` |
| `controlling/kostentraegerrechnung` | Kostentraegerrechnung | controlling | niedrig | — | `GET /api/v1/masks/controlling/kostentraegerrechnung/agent-contract` |
| `controlling/kpi-verwaltung` | KPI-Verwaltung | controlling | niedrig | — | `GET /api/v1/masks/controlling/kpi-verwaltung/agent-contract` |
| `controlling/liquiditaetsplanung` | Liquiditaetsplanung | controlling | niedrig | — | `GET /api/v1/masks/controlling/liquiditaetsplanung/agent-contract` |
| `controlling/massnahmen` | Controlling-Massnahmen | controlling | niedrig | — | `GET /api/v1/masks/controlling/massnahmen/agent-contract` |
| `controlling/plan-ist` | Plan-Ist-Controlling | controlling | niedrig | — | `GET /api/v1/masks/controlling/plan-ist/agent-contract` |
| `controlling/plan-ist-liste` | Plan-Ist | controlling | niedrig | — | `GET /api/v1/masks/controlling/plan-ist-liste/agent-contract` |
| `controlling/standort-vergleich` | Standort vergleich | controlling | niedrig | — | `GET /api/v1/masks/controlling/standort-vergleich/agent-contract` |
| `controlling/timeseries-erfassung` | Zeitreihen-Erfassung | controlling | niedrig | — | `GET /api/v1/masks/controlling/timeseries-erfassung/agent-contract` |
| `controlling/unternehmensplanung` | Unternehmensplanung | controlling | niedrig | — | `GET /api/v1/masks/controlling/unternehmensplanung/agent-contract` |
| `controlling/widget-verwaltung` | Widget-Verwaltung | controlling | niedrig | — | `GET /api/v1/masks/controlling/widget-verwaltung/agent-contract` |
| `crm/activities` | Aktivitaeten | crm | niedrig | — | `GET /api/v1/masks/crm/activities/agent-contract` |
| `crm/activity-detail` | Aktivitaet | crm | niedrig | — | `GET /api/v1/masks/crm/activity-detail/agent-contract` |
| `crm/aktivitaet` | Aktivitaet | crm | niedrig | — | `GET /api/v1/masks/crm/aktivitaet/agent-contract` |
| `crm/aktivitaeten-liste` | Aktivitaeten | crm | niedrig | — | `GET /api/v1/masks/crm/aktivitaeten-liste/agent-contract` |
| `crm/angebot-erstellen` | Angebot erstellen | crm | niedrig | — | `GET /api/v1/masks/crm/angebot-erstellen/agent-contract` |
| `crm/anruf-protokoll` | Anruf-Protokoll | crm | niedrig | — | `GET /api/v1/masks/crm/anruf-protokoll/agent-contract` |
| `crm/bedarfsdeckung-cockpit` | Bedarfsdeckung | crm | niedrig | — | `GET /api/v1/masks/crm/bedarfsdeckung-cockpit/agent-contract` |
| `crm/bestell-inbox` | Bestell-Inbox | crm | niedrig | — | `GET /api/v1/masks/crm/bestell-inbox/agent-contract` |
| `crm/besuchsberichte` | Besuchsberichte | crm | niedrig | — | `GET /api/v1/masks/crm/besuchsberichte/agent-contract` |
| `crm/betreuungsgebiet` | Betreuungsgebiet | crm | niedrig | — | `GET /api/v1/masks/crm/betreuungsgebiet/agent-contract` |
| `crm/betriebsprofil` | Betriebsprofil | crm | niedrig | — | `GET /api/v1/masks/crm/betriebsprofil/agent-contract` |
| `crm/betriebsprofile-liste` | Betriebsprofile | crm | niedrig | — | `GET /api/v1/masks/crm/betriebsprofile-liste/agent-contract` |
| `crm/bonus-vereinbarungen` | Bonus-Vereinbarungen | crm | niedrig | — | `GET /api/v1/masks/crm/bonus-vereinbarungen/agent-contract` |
| `crm/campaign` | Kampagne | crm | niedrig | — | `GET /api/v1/masks/crm/campaign/agent-contract` |
| `crm/campaign-performance` | Kampagnen-Performance | crm | niedrig | — | `GET /api/v1/masks/crm/campaign-performance/agent-contract` |
| `crm/campaign-template` | Kampagnenvorlage | crm | niedrig | — | `GET /api/v1/masks/crm/campaign-template/agent-contract` |
| `crm/churn-risiko` | Churn-Risiko | crm | niedrig | — | `GET /api/v1/masks/crm/churn-risiko/agent-contract` |
| `crm/consent` | Einwilligung | crm | niedrig | — | `GET /api/v1/masks/crm/consent/agent-contract` |
| `crm/contact-detail-liste` | Kontakte | crm | niedrig | — | `GET /api/v1/masks/crm/contact-detail-liste/agent-contract` |
| `crm/crm-dashboard` | CRM-Dashboard | crm | niedrig | — | `GET /api/v1/masks/crm/crm-dashboard/agent-contract` |
| `crm/cross-selling` | Cross-Selling | crm | niedrig | — | `GET /api/v1/masks/crm/cross-selling/agent-contract` |
| `crm/customer-360` | Kundenakte | crm | niedrig | `order-to-cash`, `service-to-customer` | `GET /api/v1/masks/crm/customer-360/agent-contract` |
| `crm/dokumente-kunden` | Kundendokumente | crm | niedrig | — | `GET /api/v1/masks/crm/dokumente-kunden/agent-contract` |
| `crm/dsgvo-anfragen-liste` | DSGVO-Anfragen | crm | niedrig | — | `GET /api/v1/masks/crm/dsgvo-anfragen-liste/agent-contract` |
| `crm/dubletten-pruefung` | Dubletten-Pruefung | crm | niedrig | — | `GET /api/v1/masks/crm/dubletten-pruefung/agent-contract` |
| `crm/einwilligungen-liste` | Einwilligungen | crm | niedrig | — | `GET /api/v1/masks/crm/einwilligungen-liste/agent-contract` |
| `crm/events-messen` | Events und Messen | crm | niedrig | — | `GET /api/v1/masks/crm/events-messen/agent-contract` |
| `crm/gdpr-request` | DSGVO-Anfrage | crm | niedrig | — | `GET /api/v1/masks/crm/gdpr-request/agent-contract` |
| `crm/gebietsschutz` | Gebietsschutz | crm | niedrig | — | `GET /api/v1/masks/crm/gebietsschutz/agent-contract` |
| `crm/geschenke-liste` | Geschenke | crm | niedrig | — | `GET /api/v1/masks/crm/geschenke-liste/agent-contract` |
| `crm/interaktions-historie` | Interaktions-Historie | crm | niedrig | — | `GET /api/v1/masks/crm/interaktions-historie/agent-contract` |
| `crm/kampagne-detail` | Kampagne | crm | niedrig | — | `GET /api/v1/masks/crm/kampagne-detail/agent-contract` |
| `crm/kampagne-erstellen` | Kampagne erstellen | crm | niedrig | — | `GET /api/v1/masks/crm/kampagne-erstellen/agent-contract` |
| `crm/kampagnen-liste` | Kampagnen | crm | niedrig | — | `GET /api/v1/masks/crm/kampagnen-liste/agent-contract` |
| `crm/kampagnenvorlagen-liste` | Kampagnenvorlagen | crm | niedrig | — | `GET /api/v1/masks/crm/kampagnenvorlagen-liste/agent-contract` |
| `crm/kaufverhalten` | Kaufverhalten | crm | niedrig | — | `GET /api/v1/masks/crm/kaufverhalten/agent-contract` |
| `crm/klaerfall-inbox` | Klaerfall-Inbox | crm | niedrig | — | `GET /api/v1/masks/crm/klaerfall-inbox/agent-contract` |
| `crm/kommunikation-center` | Kommunikations-Center | crm | niedrig | — | `GET /api/v1/masks/crm/kommunikation-center/agent-contract` |
| `crm/kontakt` | Kontakt | crm | niedrig | — | `GET /api/v1/masks/crm/kontakt/agent-contract` |
| `crm/kontakt-management-liste` | Kontakt-Management | crm | niedrig | — | `GET /api/v1/masks/crm/kontakt-management-liste/agent-contract` |
| `crm/kontakte-liste` | Kontakte | crm | niedrig | — | `GET /api/v1/masks/crm/kontakte-liste/agent-contract` |
| `crm/kunden-cockpit` | Kunden-Cockpit | crm | niedrig | — | `GET /api/v1/masks/crm/kunden-cockpit/agent-contract` |
| `crm/kunden-liste` | Kunden | crm | niedrig | — | `GET /api/v1/masks/crm/kunden-liste/agent-contract` |
| `crm/lead` | Kundenakte | crm | niedrig | — | `GET /api/v1/masks/crm/lead/agent-contract` |
| `crm/leads-liste` | Leads | crm | niedrig | — | `GET /api/v1/masks/crm/leads-liste/agent-contract` |
| `crm/lieferant` | Lieferant | crm | niedrig | — | `GET /api/v1/masks/crm/lieferant/agent-contract` |
| `crm/lieferanten-liste` | Lieferanten | crm | niedrig | — | `GET /api/v1/masks/crm/lieferanten-liste/agent-contract` |
| `crm/mail-arbeitsplatz` | Mail-Arbeitsplatz | crm | niedrig | — | `GET /api/v1/masks/crm/mail-arbeitsplatz/agent-contract` |
| `crm/opportunities-liste` | Verkaufschancen | crm | niedrig | — | `GET /api/v1/masks/crm/opportunities-liste/agent-contract` |
| `crm/opportunity` | Opportunity | crm | niedrig | `order-to-cash` | `GET /api/v1/masks/crm/opportunity/agent-contract` |
| `crm/segment` | Segment | crm | niedrig | — | `GET /api/v1/masks/crm/segment/agent-contract` |
| `crm/segmente-liste` | Segmente | crm | niedrig | — | `GET /api/v1/masks/crm/segmente-liste/agent-contract` |
| `crm/vertreter` | Vertreter | crm | niedrig | — | `GET /api/v1/masks/crm/vertreter/agent-contract` |
| `crm/wettbewerber` | Wettbewerber | crm | niedrig | — | `GET /api/v1/masks/crm/wettbewerber/agent-contract` |
| `crm/wiedervorlagen` | Wiedervorlagen | crm | niedrig | — | `GET /api/v1/masks/crm/wiedervorlagen/agent-contract` |
| `crm/zielgruppen` | Zielgruppen | crm | niedrig | — | `GET /api/v1/masks/crm/zielgruppen/agent-contract` |
| `dashboard/customizable` | Anpassbares Dashboard | platform | niedrig | — | `GET /api/v1/masks/dashboard/customizable/agent-contract` |
| `dashboard/customizable-dashboard` | Anpassbares Dashboard | platform | niedrig | — | `GET /api/v1/masks/dashboard/customizable-dashboard/agent-contract` |
| `dashboard/einkauf` | Einkaufs-Dashboard | einkauf | niedrig | — | `GET /api/v1/masks/dashboard/einkauf/agent-contract` |
| `dashboard/sales-dashboard` | Verkaufs-Dashboard | sales | niedrig | — | `GET /api/v1/masks/dashboard/sales-dashboard/agent-contract` |
| `dashboard/verkauf` | Verkaufs-Dashboard | sales | niedrig | — | `GET /api/v1/masks/dashboard/verkauf/agent-contract` |
| `dashboards/geschaeftsfuehrung` | Geschaeftsfuehrung | management | niedrig | — | `GET /api/v1/masks/dashboards/geschaeftsfuehrung/agent-contract` |
| `disposition/bestell-vorschlag` | Bestellvorschlag | logistics | niedrig | — | `GET /api/v1/masks/disposition/bestell-vorschlag/agent-contract` |
| `disposition/engpass-monitor` | Engpass-Monitor | logistics | niedrig | — | `GET /api/v1/masks/disposition/engpass-monitor/agent-contract` |
| `disposition/kontrakt-abruf` | Kontrakt-Abruf | logistics | niedrig | — | `GET /api/v1/masks/disposition/kontrakt-abruf/agent-contract` |
| `disposition/lager-reichweite` | Lager-Reichweite | logistics | niedrig | — | `GET /api/v1/masks/disposition/lager-reichweite/agent-contract` |
| `disposition/liste` | Disposition | lager | niedrig | — | `GET /api/v1/masks/disposition/liste/agent-contract` |
| `disposition/saison-planung` | Saison-Planung | logistics | niedrig | — | `GET /api/v1/masks/disposition/saison-planung/agent-contract` |
| `disposition/strecken-disposition` | Strecken-Disposition | logistics | niedrig | — | `GET /api/v1/masks/disposition/strecken-disposition/agent-contract` |
| `disposition/touren-disposition` | Touren-Disposition | logistics | niedrig | — | `GET /api/v1/masks/disposition/touren-disposition/agent-contract` |
| `disposition/umlagerungs-vorschlag` | Umlagerungs-Vorschlag | logistics | niedrig | — | `GET /api/v1/masks/disposition/umlagerungs-vorschlag/agent-contract` |
| `dms/archiv-suche` | Archiv-Suche | documents | niedrig | — | `GET /api/v1/masks/dms/archiv-suche/agent-contract` |
| `dms/beleg-erkennung` | Beleg-Erkennung | documents | niedrig | — | `GET /api/v1/masks/dms/beleg-erkennung/agent-contract` |
| `dms/dokument-detail` | Dokument | documents | niedrig | — | `GET /api/v1/masks/dms/dokument-detail/agent-contract` |
| `dms/dokument-upload` | Dokument-Upload | documents | niedrig | — | `GET /api/v1/masks/dms/dokument-upload/agent-contract` |
| `dms/freigabe-workflow` | Freigabe-Workflow | documents | niedrig | — | `GET /api/v1/masks/dms/freigabe-workflow/agent-contract` |
| `dms/inbox` | DMS-Eingangskorb | dms-compliance | niedrig | — | `GET /api/v1/masks/dms/inbox/agent-contract` |
| `dms/posteingang` | Posteingang | documents | niedrig | — | `GET /api/v1/masks/dms/posteingang/agent-contract` |
| `dms/verschlagwortung` | Verschlagwortung | documents | niedrig | — | `GET /api/v1/masks/dms/verschlagwortung/agent-contract` |
| `dms/vorlagen-verwaltung` | Vorlagen-Verwaltung | documents | niedrig | — | `GET /api/v1/masks/dms/vorlagen-verwaltung/agent-contract` |
| `docflow/artefakt-freigabe` | Artefakt-Freigabe | dms-compliance | niedrig | — | `GET /api/v1/masks/docflow/artefakt-freigabe/agent-contract` |
| `docflow/dokumenten-ruecklauf` | Dokumentenruecklauf | dms-compliance | niedrig | — | `GET /api/v1/masks/docflow/dokumenten-ruecklauf/agent-contract` |
| `docflow/gobd-export` | GoBD-Export | dms-compliance | niedrig | — | `GET /api/v1/masks/docflow/gobd-export/agent-contract` |
| `docflow/nachweisraum` | Nachweisraum | dms-compliance | niedrig | — | `GET /api/v1/masks/docflow/nachweisraum/agent-contract` |
| `docflow/wiedervorlagen` | Docflow-Wiedervorlagen | dms-compliance | niedrig | — | `GET /api/v1/masks/docflow/wiedervorlagen/agent-contract` |
| `dokumente/ablage-liste` | Dokumentenablage | dms | niedrig | — | `GET /api/v1/masks/dokumente/ablage-liste/agent-contract` |
| `dokumente/archiv` | Dokumentarchiv | documents | niedrig | — | `GET /api/v1/masks/dokumente/archiv/agent-contract` |
| `dokumente/eingang` | Dokumenteingang | documents | niedrig | — | `GET /api/v1/masks/dokumente/eingang/agent-contract` |
| `dokumente/suche` | Dokumentensuche | documents | niedrig | — | `GET /api/v1/masks/dokumente/suche/agent-contract` |
| `dokumente/vorlagen` | Dokumentvorlagen | documents | niedrig | — | `GET /api/v1/masks/dokumente/vorlagen/agent-contract` |
| `einkauf/anfrage` | Einkaufsanfrage | einkauf | niedrig | — | `GET /api/v1/masks/einkauf/anfrage/agent-contract` |
| `einkauf/anfrage-erstellen` | Anfrage erstellen | einkauf | niedrig | — | `GET /api/v1/masks/einkauf/anfrage-erstellen/agent-contract` |
| `einkauf/anfragen` | Anfragen | einkauf | niedrig | — | `GET /api/v1/masks/einkauf/anfragen/agent-contract` |
| `einkauf/anfragen-create-liste` | Anfragen | einkauf | niedrig | — | `GET /api/v1/masks/einkauf/anfragen-create-liste/agent-contract` |
| `einkauf/angebot` | Lieferantenangebot | einkauf | niedrig | — | `GET /api/v1/masks/einkauf/angebot/agent-contract` |
| `einkauf/angebot-erfassen` | Angebot erfassen | einkauf | niedrig | — | `GET /api/v1/masks/einkauf/angebot-erfassen/agent-contract` |
| `einkauf/angebote` | Angebote | einkauf | niedrig | — | `GET /api/v1/masks/einkauf/angebote/agent-contract` |
| `einkauf/angebote-vergleich-liste` | Angebotsvergleich | einkauf | niedrig | — | `GET /api/v1/masks/einkauf/angebote-vergleich-liste/agent-contract` |
| `einkauf/anlieferavis` | Anlieferavis | einkauf | mittel | — | `GET /api/v1/masks/einkauf/anlieferavis/agent-contract` |
| `einkauf/anlieferavis-erfassen` | Anlieferavis erfassen | einkauf | niedrig | — | `GET /api/v1/masks/einkauf/anlieferavis-erfassen/agent-contract` |
| `einkauf/anlieferavis-liste` | Anlieferavis | einkauf | niedrig | — | `GET /api/v1/masks/einkauf/anlieferavis-liste/agent-contract` |
| `einkauf/auftragsbestaetigung` | Auftragsbestaetigung | einkauf | mittel | — | `GET /api/v1/masks/einkauf/auftragsbestaetigung/agent-contract` |
| `einkauf/auftragsbestaetigung-erfassen` | Auftragsbestaetigung | einkauf | niedrig | — | `GET /api/v1/masks/einkauf/auftragsbestaetigung-erfassen/agent-contract` |
| `einkauf/auftragsbestaetigungen` | Auftragsbestaetigungen | einkauf | niedrig | — | `GET /api/v1/masks/einkauf/auftragsbestaetigungen/agent-contract` |
| `einkauf/bestellung-freigabe` | Bestellfreigabe | einkauf | niedrig | — | `GET /api/v1/masks/einkauf/bestellung-freigabe/agent-contract` |
| `einkauf/bestellungen` | Bestellungen | einkauf | niedrig | — | `GET /api/v1/masks/einkauf/bestellungen/agent-contract` |
| `einkauf/bestellvorschlaege-liste` | Bestellvorschlaege | einkauf | niedrig | — | `GET /api/v1/masks/einkauf/bestellvorschlaege-liste/agent-contract` |
| `einkauf/bestellvorschlag-kontrakt` | Bestellvorschlag Kontrakt | einkauf | niedrig | — | `GET /api/v1/masks/einkauf/bestellvorschlag-kontrakt/agent-contract` |
| `einkauf/bestellvorschlag-lager` | Bestellvorschlag Lager | einkauf | niedrig | — | `GET /api/v1/masks/einkauf/bestellvorschlag-lager/agent-contract` |
| `einkauf/bestellvorschlag-verbrauch` | Bestellvorschlag Verbrauch | einkauf | niedrig | — | `GET /api/v1/masks/einkauf/bestellvorschlag-verbrauch/agent-contract` |
| `einkauf/dienstleistungen-haltung-liste` | Dienstleistungen Haltung | einkauf | niedrig | — | `GET /api/v1/masks/einkauf/dienstleistungen-haltung-liste/agent-contract` |
| `einkauf/einkauf-vorgang-liste` | Einkaufsvorgaenge | einkauf | niedrig | — | `GET /api/v1/masks/einkauf/einkauf-vorgang-liste/agent-contract` |
| `einkauf/frachtauftraege-liste` | Frachtauftraege | einkauf | niedrig | — | `GET /api/v1/masks/einkauf/frachtauftraege-liste/agent-contract` |
| `einkauf/gutschrift-belastung` | Gutschrift/Belastung | einkauf | niedrig | — | `GET /api/v1/masks/einkauf/gutschrift-belastung/agent-contract` |
| `einkauf/kontrakt-anlage` | Kontrakt-Anlage | einkauf | niedrig | — | `GET /api/v1/masks/einkauf/kontrakt-anlage/agent-contract` |
| `einkauf/kontrakte-service-liste` | Kontrakte Service | einkauf | niedrig | — | `GET /api/v1/masks/einkauf/kontrakte-service-liste/agent-contract` |
| `einkauf/lieferanten` | Lieferanten | einkauf | niedrig | — | `GET /api/v1/masks/einkauf/lieferanten/agent-contract` |
| `einkauf/lieferanten-angebote` | Lieferanten-Angebote | einkauf | niedrig | — | `GET /api/v1/masks/einkauf/lieferanten-angebote/agent-contract` |
| `einkauf/lieferanten-dokumente` | Lieferanten-Dokumente | einkauf | niedrig | — | `GET /api/v1/masks/einkauf/lieferanten-dokumente/agent-contract` |
| `einkauf/lieferanten-konditionen` | Lieferanten-Konditionen | einkauf | niedrig | — | `GET /api/v1/masks/einkauf/lieferanten-konditionen/agent-contract` |
| `einkauf/lieferanten-reklamationen` | Lieferanten-Reklamationen | einkauf | niedrig | — | `GET /api/v1/masks/einkauf/lieferanten-reklamationen/agent-contract` |
| `einkauf/lieferschein-erfassen` | Lieferschein erfassen | einkauf | niedrig | — | `GET /api/v1/masks/einkauf/lieferschein-erfassen/agent-contract` |
| `einkauf/mahnwesen-lieferanten` | Mahnwesen Lieferanten | einkauf | niedrig | — | `GET /api/v1/masks/einkauf/mahnwesen-lieferanten/agent-contract` |
| `einkauf/purchase-order` | Bestellung | einkauf | mittel | `procure-to-pay` | `GET /api/v1/masks/einkauf/purchase-order/agent-contract` |
| `einkauf/rechnung-abgleich` | Rechnung abgleich | einkauf | niedrig | — | `GET /api/v1/masks/einkauf/rechnung-abgleich/agent-contract` |
| `einkauf/rechnung-abgleich-liste` | Rechnungsabgleich | einkauf | niedrig | — | `GET /api/v1/masks/einkauf/rechnung-abgleich-liste/agent-contract` |
| `einkauf/rechnung-eingang-erfassung` | Rechnung eingang erfassung | einkauf | niedrig | — | `GET /api/v1/masks/einkauf/rechnung-eingang-erfassung/agent-contract` |
| `einkauf/rechnungseingaenge-liste` | Rechnungseingaenge | einkauf | niedrig | — | `GET /api/v1/masks/einkauf/rechnungseingaenge-liste/agent-contract` |
| `einkauf/rechnungseingang/neu` | Vorgang | einkauf | niedrig | — | `GET /api/v1/masks/einkauf/rechnungseingang/neu/agent-contract` |
| `einkauf/reports` | Reports | einkauf | niedrig | — | `GET /api/v1/masks/einkauf/reports/agent-contract` |
| `einkauf/retouren` | Retouren | einkauf | niedrig | — | `GET /api/v1/masks/einkauf/retouren/agent-contract` |
| `einkauf/retouren-liste` | Retouren | einkauf | niedrig | — | `GET /api/v1/masks/einkauf/retouren-liste/agent-contract` |
| `einkauf/rfq-bids` | Rfq bids | einkauf | niedrig | — | `GET /api/v1/masks/einkauf/rfq-bids/agent-contract` |
| `einkauf/service-entry-sheets` | Service entry sheets | einkauf | niedrig | — | `GET /api/v1/masks/einkauf/service-entry-sheets/agent-contract` |
| `einkauf/supplier` | Lieferant | einkauf | hoch | `procure-to-pay` | `GET /api/v1/masks/einkauf/supplier/agent-contract` |
| `einkauf/wareneingang` | Wareneingang | einkauf | niedrig | — | `GET /api/v1/masks/einkauf/wareneingang/agent-contract` |
| `einkauf/wareneingangsabgleich` | Wareneingangsabgleich | einkauf | niedrig | — | `GET /api/v1/masks/einkauf/wareneingangsabgleich/agent-contract` |
| `einkauf/warengruppen` | Warengruppen | einkauf | niedrig | — | `GET /api/v1/masks/einkauf/warengruppen/agent-contract` |
| `einkauf/zahlungsbedingungen` | Zahlungsbedingungen | finance | niedrig | — | `GET /api/v1/masks/einkauf/zahlungsbedingungen/agent-contract` |
| `etiketten/druck-liste` | Etikettendruck | lager | niedrig | — | `GET /api/v1/masks/etiketten/druck-liste/agent-contract` |
| `etiketten/drucken` | Drucken | etiketten | niedrig | — | `GET /api/v1/masks/etiketten/drucken/agent-contract` |
| `export/intrastat-meldung-liste` | Intrastat-Meldung | compliance | niedrig | — | `GET /api/v1/masks/export/intrastat-meldung-liste/agent-contract` |
| `export/umsatzsteuer-voranmeldung-liste` | USt-Voranmeldung | finance | niedrig | — | `GET /api/v1/masks/export/umsatzsteuer-voranmeldung-liste/agent-contract` |
| `export/ustva` | Umsatzsteuervoranmeldung | export | niedrig | — | `GET /api/v1/masks/export/ustva/agent-contract` |
| `fibu/abschluss-checklist` | Abschluss-Checkliste | finance | niedrig | — | `GET /api/v1/masks/fibu/abschluss-checklist/agent-contract` |
| `fibu/abschluss-checklist-detail` | Abschluss checklist detail | fibu | niedrig | — | `GET /api/v1/masks/fibu/abschluss-checklist-detail/agent-contract` |
| `fibu/abschluss-cockpit` | Abschluss-Cockpit | finance | niedrig | — | `GET /api/v1/masks/fibu/abschluss-cockpit/agent-contract` |
| `fibu/anlage` | Anlage | finance | niedrig | — | `GET /api/v1/masks/fibu/anlage/agent-contract` |
| `fibu/anlagen` | Anlagen Gesamt | fibu | niedrig | — | `GET /api/v1/masks/fibu/anlagen/agent-contract` |
| `fibu/anlagen-liste` | Anlagen | finance | niedrig | — | `GET /api/v1/masks/fibu/anlagen-liste/agent-contract` |
| `fibu/anlagen-suite` | Anlagen suite | fibu | niedrig | — | `GET /api/v1/masks/fibu/anlagen-suite/agent-contract` |
| `fibu/atlas` | Atlas | fibu | niedrig | — | `GET /api/v1/masks/fibu/atlas/agent-contract` |
| `fibu/bilanz` | Bilanz | fibu | niedrig | — | `GET /api/v1/masks/fibu/bilanz/agent-contract` |
| `fibu/buchhaltungsuebersicht` | Buchhaltungsuebersicht | fibu | niedrig | — | `GET /api/v1/masks/fibu/buchhaltungsuebersicht/agent-contract` |
| `fibu/buchungsjournal-liste` | Buchungsjournal | finance | niedrig | — | `GET /api/v1/masks/fibu/buchungsjournal-liste/agent-contract` |
| `fibu/buchungsuebernahme-connectors` | Buchungsuebernahme connectors | fibu | niedrig | — | `GET /api/v1/masks/fibu/buchungsuebernahme-connectors/agent-contract` |
| `fibu/bwa` | Bwa | fibu | niedrig | — | `GET /api/v1/masks/fibu/bwa/agent-contract` |
| `fibu/debitoren` | Debitoren | fibu | niedrig | — | `GET /api/v1/masks/fibu/debitoren/agent-contract` |
| `fibu/debitoren-api` | Debitoren api | fibu | niedrig | — | `GET /api/v1/masks/fibu/debitoren-api/agent-contract` |
| `fibu/debitoren-liste` | Debitoren OP | finance | niedrig | — | `GET /api/v1/masks/fibu/debitoren-liste/agent-contract` |
| `fibu/elster-online` | Elster online | fibu | niedrig | — | `GET /api/v1/masks/fibu/elster-online/agent-contract` |
| `fibu/erloeskennziffern` | Erloeskennziffern | fibu | niedrig | — | `GET /api/v1/masks/fibu/erloeskennziffern/agent-contract` |
| `fibu/erloeskontenzuordnung` | Erloeskontenzuordnung | fibu | niedrig | — | `GET /api/v1/masks/fibu/erloeskontenzuordnung/agent-contract` |
| `fibu/forderungsgruppen` | Forderungsgruppen | fibu | niedrig | — | `GET /api/v1/masks/fibu/forderungsgruppen/agent-contract` |
| `fibu/geschaeftsjahre` | Neues Geschäftsjahr [JAHR] | fibu | niedrig | — | `GET /api/v1/masks/fibu/geschaeftsjahre/agent-contract` |
| `fibu/guv` | Guv | fibu | niedrig | — | `GET /api/v1/masks/fibu/guv/agent-contract` |
| `fibu/hauptbuch` | Hauptbuch | fibu | niedrig | — | `GET /api/v1/masks/fibu/hauptbuch/agent-contract` |
| `fibu/hauptbuch-liste` | Hauptbuch | finance | niedrig | — | `GET /api/v1/masks/fibu/hauptbuch-liste/agent-contract` |
| `fibu/kassenbuch-liste` | Kassenbuch | finance | niedrig | — | `GET /api/v1/masks/fibu/kassenbuch-liste/agent-contract` |
| `fibu/kontenplan` | Kontenplan | fibu | niedrig | — | `GET /api/v1/masks/fibu/kontenplan/agent-contract` |
| `fibu/kontenplan-liste` | Kontenplan | finance | niedrig | — | `GET /api/v1/masks/fibu/kontenplan-liste/agent-contract` |
| `fibu/kostenstellen-liste` | Kostenstellen | finance | niedrig | — | `GET /api/v1/masks/fibu/kostenstellen-liste/agent-contract` |
| `fibu/kostenstellenrechnung` | Kostenstellenrechnung | fibu | niedrig | — | `GET /api/v1/masks/fibu/kostenstellenrechnung/agent-contract` |
| `fibu/kreditlinien` | Kreditlinien | fibu | niedrig | — | `GET /api/v1/masks/fibu/kreditlinien/agent-contract` |
| `fibu/kreditoren` | Kreditoren | fibu | niedrig | — | `GET /api/v1/masks/fibu/kreditoren/agent-contract` |
| `fibu/kreditoren-liste` | Kreditoren OP | finance | niedrig | — | `GET /api/v1/masks/fibu/kreditoren-liste/agent-contract` |
| `fibu/lohn-connector` | Lohn connector | fibu | niedrig | — | `GET /api/v1/masks/fibu/lohn-connector/agent-contract` |
| `fibu/monatswerte` | Monatswerte | fibu | niedrig | — | `GET /api/v1/masks/fibu/monatswerte/agent-contract` |
| `fibu/offene-posten-liste` | Offene Posten | finance | niedrig | — | `GET /api/v1/masks/fibu/offene-posten-liste/agent-contract` |
| `fibu/op-skonto-auszifferung` | Auszifferungen | fibu | niedrig | — | `GET /api/v1/masks/fibu/op-skonto-auszifferung/agent-contract` |
| `fibu/op-verwaltung` | Op verwaltung | fibu | niedrig | — | `GET /api/v1/masks/fibu/op-verwaltung/agent-contract` |
| `fibu/periodische-buchungen` | Periodische buchungen | fibu | niedrig | — | `GET /api/v1/masks/fibu/periodische-buchungen/agent-contract` |
| `fibu/quadriga-connector` | Quadriga connector | fibu | niedrig | — | `GET /api/v1/masks/fibu/quadriga-connector/agent-contract` |
| `fibu/sachkonto` | Sachkonto | fibu | niedrig | — | `GET /api/v1/masks/fibu/sachkonto/agent-contract` |
| `fibu/schnittstelle-fibu` | Schnittstelle fibu | fibu | niedrig | — | `GET /api/v1/masks/fibu/schnittstelle-fibu/agent-contract` |
| `fibu/schnittstelle-fibu-liste` | FIBU-Schnittstelle | finance | niedrig | — | `GET /api/v1/masks/fibu/schnittstelle-fibu-liste/agent-contract` |
| `fibu/schnittstellen-center` | Schnittstellen center | fibu | niedrig | — | `GET /api/v1/masks/fibu/schnittstellen-center/agent-contract` |
| `fibu/sicherheiten` | Sicherheiten | fibu | niedrig | — | `GET /api/v1/masks/fibu/sicherheiten/agent-contract` |
| `fibu/stammdaten` | Neues Zahlungsformular [FIZAF] | fibu | niedrig | — | `GET /api/v1/masks/fibu/stammdaten/agent-contract` |
| `fibu/verbindlichkeiten` | Verbindlichkeiten | fibu | niedrig | — | `GET /api/v1/masks/fibu/verbindlichkeiten/agent-contract` |
| `fibu/verbindlichkeiten-liste` | Verbindlichkeiten | finance | niedrig | — | `GET /api/v1/masks/fibu/verbindlichkeiten-liste/agent-contract` |
| `fibu/zahlungseingaenge` | Zahlungseingaenge | fibu | niedrig | — | `GET /api/v1/masks/fibu/zahlungseingaenge/agent-contract` |
| `fibu/zahlungseingaenge-liste` | Zahlungseingaenge | finance | niedrig | — | `GET /api/v1/masks/fibu/zahlungseingaenge-liste/agent-contract` |
| `fibu/zahlungslaeufe` | Zahlungslaeufe | fibu | niedrig | — | `GET /api/v1/masks/fibu/zahlungslaeufe/agent-contract` |
| `fibu/zahlungslaeufe-liste` | Zahlungslaeufe | finance | niedrig | — | `GET /api/v1/masks/fibu/zahlungslaeufe-liste/agent-contract` |
| `fibu/zahlungsmeldungen` | Neue Zahlungsmeldung [KASSZAME] | fibu | niedrig | — | `GET /api/v1/masks/fibu/zahlungsmeldungen/agent-contract` |
| `fibu/zahlungsvorschlaege` | Zahlungsvorschlaege | fibu | niedrig | — | `GET /api/v1/masks/fibu/zahlungsvorschlaege/agent-contract` |
| `finance/abschluss` | Monats-/Jahresabschluss | finance | niedrig | — | `GET /api/v1/masks/finance/abschluss/agent-contract` |
| `finance/ap-invoice` | Eingangsrechnung | finance | mittel | `procure-to-pay` | `GET /api/v1/masks/finance/ap-invoice/agent-contract` |
| `finance/ap-invoices-liste` | AP-Rechnungen | finance | niedrig | — | `GET /api/v1/masks/finance/ap-invoices-liste/agent-contract` |
| `finance/ap/invoices` | Ap invoices list | finance | niedrig | — | `GET /api/v1/masks/finance/ap/invoices/agent-contract` |
| `finance/ap/invoices/new` | Ap invoice form | finance | niedrig | — | `GET /api/v1/masks/finance/ap/invoices/new/agent-contract` |
| `finance/ar-open-item` | Offener Posten | finance | mittel | `order-to-cash` | `GET /api/v1/masks/finance/ar-open-item/agent-contract` |
| `finance/audit-trail` | Finanz-Audit-Trail | finance | niedrig | — | `GET /api/v1/masks/finance/audit-trail/agent-contract` |
| `finance/audit-trail-liste` | Audit-Trail | finance | niedrig | — | `GET /api/v1/masks/finance/audit-trail-liste/agent-contract` |
| `finance/bank-abgleich` | Objekt | finance | niedrig | — | `GET /api/v1/masks/finance/bank-abgleich/agent-contract` |
| `finance/bank-account` | Bankkonto | finance | niedrig | — | `GET /api/v1/masks/finance/bank-account/agent-contract` |
| `finance/bank-stamm` | Bank stamm | finance | niedrig | — | `GET /api/v1/masks/finance/bank-stamm/agent-contract` |
| `finance/bankkonten-stamm` | Bankkonten stamm | finance | niedrig | — | `GET /api/v1/masks/finance/bankkonten-stamm/agent-contract` |
| `finance/bankkonto` | Bankkonto | finance | mittel | — | `GET /api/v1/masks/finance/bankkonto/agent-contract` |
| `finance/bookings/new` | Buchungsjournal | finance | niedrig | — | `GET /api/v1/masks/finance/bookings/new/agent-contract` |
| `finance/buchungserfassung` | Vorgang | finance | niedrig | — | `GET /api/v1/masks/finance/buchungserfassung/agent-contract` |
| `finance/buchungsimport` | Buchungsimport | finance | niedrig | — | `GET /api/v1/masks/finance/buchungsimport/agent-contract` |
| `finance/buchungsvorlagen` | Buchungsvorlagen | finance | niedrig | — | `GET /api/v1/masks/finance/buchungsvorlagen/agent-contract` |
| `finance/datev-export` | DATEV-Export | finance | niedrig | — | `GET /api/v1/masks/finance/datev-export/agent-contract` |
| `finance/debitor` | Debitor | finance | mittel | — | `GET /api/v1/masks/finance/debitor/agent-contract` |
| `finance/debitoren-liste` | Debitoren | finance | niedrig | — | `GET /api/v1/masks/finance/debitoren-liste/agent-contract` |
| `finance/debitoren/new` | Debitoren stamm | finance | niedrig | — | `GET /api/v1/masks/finance/debitoren/new/agent-contract` |
| `finance/dunning-editor` | Mahnvorgang | finance | niedrig | — | `GET /api/v1/masks/finance/dunning-editor/agent-contract` |
| `finance/invoices-list` | Invoices list | finance | niedrig | — | `GET /api/v1/masks/finance/invoices-list/agent-contract` |
| `finance/invoices/new` | Invoice form | finance | niedrig | — | `GET /api/v1/masks/finance/invoices/new/agent-contract` |
| `finance/kasse` | Kasse | finance | niedrig | — | `GET /api/v1/masks/finance/kasse/agent-contract` |
| `finance/kontenplan` | Chart of accounts | finance | niedrig | — | `GET /api/v1/masks/finance/kontenplan/agent-contract` |
| `finance/kreditor` | Kreditor | finance | mittel | — | `GET /api/v1/masks/finance/kreditor/agent-contract` |
| `finance/kreditoren` | Kreditoren liste | finance | niedrig | — | `GET /api/v1/masks/finance/kreditoren/agent-contract` |
| `finance/kreditoren-liste` | Kreditoren | finance | niedrig | — | `GET /api/v1/masks/finance/kreditoren-liste/agent-contract` |
| `finance/kreditoren-stamm` | Kreditoren stamm | finance | niedrig | — | `GET /api/v1/masks/finance/kreditoren-stamm/agent-contract` |
| `finance/lastschriften-debitoren` | Debitorenlauf | finance | niedrig | — | `GET /api/v1/masks/finance/lastschriften-debitoren/agent-contract` |
| `finance/nebenbuch-abstimmung` | Nebenbuch abstimmung | finance | niedrig | — | `GET /api/v1/masks/finance/nebenbuch-abstimmung/agent-contract` |
| `finance/offene-posten` | Offene posten | finance | niedrig | — | `GET /api/v1/masks/finance/offene-posten/agent-contract` |
| `finance/offene-posten-cockpit` | Offene-Posten-Cockpit | finance | niedrig | — | `GET /api/v1/masks/finance/offene-posten-cockpit/agent-contract` |
| `finance/op-debitoren` | OP-Lage | finance | niedrig | — | `GET /api/v1/masks/finance/op-debitoren/agent-contract` |
| `finance/op-kreditoren` | Op kreditoren | finance | niedrig | — | `GET /api/v1/masks/finance/op-kreditoren/agent-contract` |
| `finance/payment-matching-liste` | Zahlungsabgleich | finance | niedrig | — | `GET /api/v1/masks/finance/payment-matching-liste/agent-contract` |
| `finance/payment-run` | Zahlungslauf | finance | niedrig | `procure-to-pay`, `order-to-cash`, `finance-to-close` | `GET /api/v1/masks/finance/payment-run/agent-contract` |
| `finance/payments` | Payment matching | finance | niedrig | — | `GET /api/v1/masks/finance/payments/agent-contract` |
| `finance/periodenabschluss` | Periodenabschluss | finance | niedrig | — | `GET /api/v1/masks/finance/periodenabschluss/agent-contract` |
| `finance/periods` | Periods | finance | niedrig | — | `GET /api/v1/masks/finance/periods/agent-contract` |
| `finance/periods-liste` | Buchungsperioden | finance | niedrig | — | `GET /api/v1/masks/finance/periods-liste/agent-contract` |
| `finance/pruefkorb` | Prüfkorb | finance | niedrig | — | `GET /api/v1/masks/finance/pruefkorb/agent-contract` |
| `finance/rechnungstapel` | Rechnungstapel | finance | niedrig | — | `GET /api/v1/masks/finance/rechnungstapel/agent-contract` |
| `finance/skonto-optimizer` | Skonto optimizer | finance | niedrig | — | `GET /api/v1/masks/finance/skonto-optimizer/agent-contract` |
| `finance/skonto-optimizer-liste` | Skonto-Optimierung | finance | niedrig | — | `GET /api/v1/masks/finance/skonto-optimizer-liste/agent-contract` |
| `finance/steuerschluessel` | Steuerschlüssel | finance | mittel | — | `GET /api/v1/masks/finance/steuerschluessel/agent-contract` |
| `finance/umsatz` | Reports | finance | niedrig | — | `GET /api/v1/masks/finance/umsatz/agent-contract` |
| `finance/ustva` | Meldekontext | finance | niedrig | — | `GET /api/v1/masks/finance/ustva/agent-contract` |
| `finance/wechselkurse` | Wechselkurse | finance | niedrig | — | `GET /api/v1/masks/finance/wechselkurse/agent-contract` |
| `finance/zahlungseingang` | Zahlungseingang | finance | niedrig | — | `GET /api/v1/masks/finance/zahlungseingang/agent-contract` |
| `finance/zahlungslauf-kreditoren` | Zahlungslage | finance | niedrig | — | `GET /api/v1/masks/finance/zahlungslauf-kreditoren/agent-contract` |
| `finanzplanung/liquiditaet` | Liquiditaet | finanzplanung | niedrig | — | `GET /api/v1/masks/finanzplanung/liquiditaet/agent-contract` |
| `foerderung/antrag` | Antrag | foerderung | niedrig | — | `GET /api/v1/masks/foerderung/antrag/agent-contract` |
| `foerderung/liste` | Foerderantraege | agrar | niedrig | — | `GET /api/v1/masks/foerderung/liste/agent-contract` |
| `fuhrpark/ausgehende-belege-dokumente` | Ausgehende belege dokumente | fuhrpark | niedrig | — | `GET /api/v1/masks/fuhrpark/ausgehende-belege-dokumente/agent-contract` |
| `fuhrpark/ausgehende-dokumente` | Ausgehende Belege | logistics | niedrig | — | `GET /api/v1/masks/fuhrpark/ausgehende-dokumente/agent-contract` |
| `fuhrpark/auswertung-kosten` | Fuhrpark-Kostenauswertung | logistics | niedrig | — | `GET /api/v1/masks/fuhrpark/auswertung-kosten/agent-contract` |
| `fuhrpark/auswertungen-menu` | Fuhrpark-Auswertungen | logistics | niedrig | — | `GET /api/v1/masks/fuhrpark/auswertungen-menu/agent-contract` |
| `fuhrpark/fahrzeug-stamm` | Fahrzeug-Stamm | logistics | hoch | — | `GET /api/v1/masks/fuhrpark/fahrzeug-stamm/agent-contract` |
| `fuhrpark/fahrzeug/neu` | Fahrzeug stamm | fuhrpark | niedrig | — | `GET /api/v1/masks/fuhrpark/fahrzeug/neu/agent-contract` |
| `fuhrpark/fahrzeuge` | Fahrzeuge | logistics | niedrig | — | `GET /api/v1/masks/fuhrpark/fahrzeuge/agent-contract` |
| `fuhrpark/fahrzeuge-liste` | Fuhrpark | logistik | niedrig | — | `GET /api/v1/masks/fuhrpark/fahrzeuge-liste/agent-contract` |
| `fuhrpark/fuhrpark-auswertung-kosten-pro-fahrzeug` | Fuhrpark auswertung kosten pro fahrzeug | fuhrpark | niedrig | — | `GET /api/v1/masks/fuhrpark/fuhrpark-auswertung-kosten-pro-fahrzeug/agent-contract` |
| `fuhrpark/fuhrpark-auswertungen-menu` | Fuhrpark auswertungen menu | fuhrpark | niedrig | — | `GET /api/v1/masks/fuhrpark/fuhrpark-auswertungen-menu/agent-contract` |
| `fuhrpark/fuhrpark-klassisch` | Fuhrpark klassisch | fuhrpark | niedrig | — | `GET /api/v1/masks/fuhrpark/fuhrpark-klassisch/agent-contract` |
| `fuhrpark/fuhrpark-menue` | Fuhrpark menue | fuhrpark | niedrig | — | `GET /api/v1/masks/fuhrpark/fuhrpark-menue/agent-contract` |
| `fuhrpark/fuhrpark-rechnungen` | Fuhrpark rechnungen | fuhrpark | niedrig | — | `GET /api/v1/masks/fuhrpark/fuhrpark-rechnungen/agent-contract` |
| `fuhrpark/fuhrpark-stammdaten` | Fuhrpark stammdaten | fuhrpark | niedrig | — | `GET /api/v1/masks/fuhrpark/fuhrpark-stammdaten/agent-contract` |
| `fuhrpark/rechnungen` | Fuhrpark-Rechnungen | logistics | niedrig | — | `GET /api/v1/masks/fuhrpark/rechnungen/agent-contract` |
| `fuhrpark/rechnungen-liste` | Fuhrpark-Rechnungen | logistik | niedrig | — | `GET /api/v1/masks/fuhrpark/rechnungen-liste/agent-contract` |
| `fuhrpark/terminarten` | Terminarten | logistics | niedrig | — | `GET /api/v1/masks/fuhrpark/terminarten/agent-contract` |
| `fuhrpark/uebersicht` | Fuhrpark | logistics | niedrig | — | `GET /api/v1/masks/fuhrpark/uebersicht/agent-contract` |
| `futter/einzel` | Einzelfuttermittel | futtermittel | niedrig | — | `GET /api/v1/masks/futter/einzel/agent-contract` |
| `futter/einzel/liste` | Liste | futter | niedrig | — | `GET /api/v1/masks/futter/einzel/liste/agent-contract` |
| `futter/einzel/stamm/neu` | Stamm | futter | niedrig | — | `GET /api/v1/masks/futter/einzel/stamm/neu/agent-contract` |
| `futter/misch` | Mischfuttermittel | futtermittel | niedrig | — | `GET /api/v1/masks/futter/misch/agent-contract` |
| `futter/misch/liste` | Liste | futter | niedrig | — | `GET /api/v1/masks/futter/misch/liste/agent-contract` |
| `futter/misch/stamm/neu` | Rezeptur-Komponenten | futter | niedrig | — | `GET /api/v1/masks/futter/misch/stamm/neu/agent-contract` |
| `futtermittel/analyse` | Futteranalyse | futtermittel | hoch | — | `GET /api/v1/masks/futtermittel/analyse/agent-contract` |
| `futtermittel/analysen` | Futteranalysen | futtermittel | niedrig | — | `GET /api/v1/masks/futtermittel/analysen/agent-contract` |
| `futtermittel/beratung` | Beratung | futtermittel | niedrig | — | `GET /api/v1/masks/futtermittel/beratung/agent-contract` |
| `futtermittel/chargen/neu` | Charge-Verfolgung | futtermittel | niedrig | — | `GET /api/v1/masks/futtermittel/chargen/neu/agent-contract` |
| `futtermittel/einzelfuttermittel` | Einzelfuttermittel | futtermittel | niedrig | — | `GET /api/v1/masks/futtermittel/einzelfuttermittel/agent-contract` |
| `futtermittel/einzelfuttermittel-liste` | Einzelfuttermittel | futtermittel | niedrig | — | `GET /api/v1/masks/futtermittel/einzelfuttermittel-liste/agent-contract` |
| `futtermittel/einzelfuttermittel/liste` | Einzelfuttermittel liste | futtermittel | niedrig | — | `GET /api/v1/masks/futtermittel/einzelfuttermittel/liste/agent-contract` |
| `futtermittel/einzelfuttermittel/stamm/new` | Einzelfuttermittel-Stammdaten | futtermittel | niedrig | — | `GET /api/v1/masks/futtermittel/einzelfuttermittel/stamm/new/agent-contract` |
| `futtermittel/fuetterungsdokumentation-mobil` | Fuetterungsdokumentation mobil | futtermittel | niedrig | — | `GET /api/v1/masks/futtermittel/fuetterungsdokumentation-mobil/agent-contract` |
| `futtermittel/futtermittel-bestellung` | Futtermittel bestellung | futtermittel | niedrig | — | `GET /api/v1/masks/futtermittel/futtermittel-bestellung/agent-contract` |
| `futtermittel/futtermittel-qualitaetskontrolle` | Futtermittel-Qualitaetskontrolle | futtermittel | niedrig | — | `GET /api/v1/masks/futtermittel/futtermittel-qualitaetskontrolle/agent-contract` |
| `futtermittel/futtermittel-statistik` | Futtermittel statistik | futtermittel | niedrig | — | `GET /api/v1/masks/futtermittel/futtermittel-statistik/agent-contract` |
| `futtermittel/grundfutteranalysen` | Grundfutteranalysen native | futtermittel | niedrig | — | `GET /api/v1/masks/futtermittel/grundfutteranalysen/agent-contract` |
| `futtermittel/integrationsmonitor` | Integrationsmonitor | futtermittel | niedrig | — | `GET /api/v1/masks/futtermittel/integrationsmonitor/agent-contract` |
| `futtermittel/mischfuttermittel` | Mischfuttermittel | futtermittel | niedrig | — | `GET /api/v1/masks/futtermittel/mischfuttermittel/agent-contract` |
| `futtermittel/mischfuttermittel-liste` | Mischfuttermittel | futtermittel | niedrig | — | `GET /api/v1/masks/futtermittel/mischfuttermittel-liste/agent-contract` |
| `futtermittel/mischfuttermittel/liste` | Mischfuttermittel liste | futtermittel | niedrig | — | `GET /api/v1/masks/futtermittel/mischfuttermittel/liste/agent-contract` |
| `futtermittel/mischfuttermittel/stamm/new` | Mischfuttermittel-Stammdaten | futtermittel | niedrig | — | `GET /api/v1/masks/futtermittel/mischfuttermittel/stamm/new/agent-contract` |
| `futtermittel/rations-schnittstellen-import` | Rations schnittstellen import | futtermittel | niedrig | — | `GET /api/v1/masks/futtermittel/rations-schnittstellen-import/agent-contract` |
| `futtermittel/rations-zugang` | Rations zugang | futtermittel | niedrig | — | `GET /api/v1/masks/futtermittel/rations-zugang/agent-contract` |
| `futtermittel/rationseditor` | Rationseditor | futtermittel | niedrig | — | `GET /api/v1/masks/futtermittel/rationseditor/agent-contract` |
| `futtermittel/rationsoptimierung` | Rationsoptimierung | futtermittel | niedrig | — | `GET /api/v1/masks/futtermittel/rationsoptimierung/agent-contract` |
| `futtermittel/rationsvergleich` | Rationsvergleich | futtermittel | niedrig | — | `GET /api/v1/masks/futtermittel/rationsvergleich/agent-contract` |
| `futtermittel/wareneingang` | Futtermittel wareneingang | futtermittel | niedrig | — | `GET /api/v1/masks/futtermittel/wareneingang/agent-contract` |
| `genossenschaft/mitglieder` | Mitglieder | genossenschaft | niedrig | — | `GET /api/v1/masks/genossenschaft/mitglieder/agent-contract` |
| `genossenschaft/mitglieder-liste` | Mitglieder | genossenschaft | niedrig | — | `GET /api/v1/masks/genossenschaft/mitglieder-liste/agent-contract` |
| `inbox` | Posteingang | dms-compliance | niedrig | — | `GET /api/v1/masks/inbox/agent-contract` |
| `inventory-reports` | Inventory reports | workspace | niedrig | — | `GET /api/v1/masks/inventory-reports/agent-contract` |
| `inventory/epcis` | Index | inventory | niedrig | — | `GET /api/v1/masks/inventory/epcis/agent-contract` |
| `kasse/tagesabschluss` | Tagesabschluss | kasse | niedrig | — | `GET /api/v1/masks/kasse/tagesabschluss/agent-contract` |
| `kontrakte/FrmKontraktProtokoll` | FrmKontraktProtokoll | kontrakte | niedrig | — | `GET /api/v1/masks/kontrakte/FrmKontraktProtokoll/agent-contract` |
| `kontrakte/KontraktAlarmDashboard` | KontraktAlarmDashboard | kontrakte | niedrig | — | `GET /api/v1/masks/kontrakte/KontraktAlarmDashboard/agent-contract` |
| `kontrakte/LstKontraktUebersicht` | LstKontraktUebersicht | kontrakte | niedrig | — | `GET /api/v1/masks/kontrakte/LstKontraktUebersicht/agent-contract` |
| `kontrakte/kontraktklassen` | Kontraktklassen | kontrakte | niedrig | — | `GET /api/v1/masks/kontrakte/kontraktklassen/agent-contract` |
| `kontrakte/kontraktklassen-liste` | Kontraktklassen | agrar | niedrig | — | `GET /api/v1/masks/kontrakte/kontraktklassen-liste/agent-contract` |
| `kontrakte/liste` | Kontrakte | agrar | niedrig | — | `GET /api/v1/masks/kontrakte/liste/agent-contract` |
| `kontrakte/mengenzeitraeume` | Kontrakt wählen | kontrakte | niedrig | — | `GET /api/v1/masks/kontrakte/mengenzeitraeume/agent-contract` |
| `kontrakte/positionen` | KontraktPositionsmonitor | kontrakte | niedrig | — | `GET /api/v1/masks/kontrakte/positionen/agent-contract` |
| `labor/proben-liste` | Laborproben | qualitaet | niedrig | — | `GET /api/v1/masks/labor/proben-liste/agent-contract` |
| `lager/article-stock` | Artikelbestand | lager | niedrig | `inventory-to-settlement` | `GET /api/v1/masks/lager/article-stock/agent-contract` |
| `lager/auslagerung` | Auslagerung | lager | niedrig | — | `GET /api/v1/masks/lager/auslagerung/agent-contract` |
| `lager/bestandsbewertung` | Bestandsbewertung | lager | niedrig | — | `GET /api/v1/masks/lager/bestandsbewertung/agent-contract` |
| `lager/bestandskorrektur` | Bestandskorrektur | lager | niedrig | — | `GET /api/v1/masks/lager/bestandskorrektur/agent-contract` |
| `lager/charge` | Charge | lager | niedrig | — | `GET /api/v1/masks/lager/charge/agent-contract` |
| `lager/einlagerung` | Einlagerung | lager | niedrig | — | `GET /api/v1/masks/lager/einlagerung/agent-contract` |
| `lager/foreign-goods-queue` | Fremdware-Queue | inventory | niedrig | — | `GET /api/v1/masks/lager/foreign-goods-queue/agent-contract` |
| `lager/fremdware` | Fremdware und Fremdbestand | inventory | niedrig | — | `GET /api/v1/masks/lager/fremdware/agent-contract` |
| `lager/gs1-scanner` | Gs1 scanner | lager | niedrig | — | `GET /api/v1/masks/lager/gs1-scanner/agent-contract` |
| `lager/inventory-dashboard` | Lager-Dashboard | lager | niedrig | — | `GET /api/v1/masks/lager/inventory-dashboard/agent-contract` |
| `lager/inventur` | Inventur | lager | niedrig | — | `GET /api/v1/masks/lager/inventur/agent-contract` |
| `lager/inventur-liste` | Inventur | lager | niedrig | — | `GET /api/v1/masks/lager/inventur-liste/agent-contract` |
| `lager/inventur-nebenlaeufe` | Inventur-Nebenlaeufe | inventory | hoch | — | `GET /api/v1/masks/lager/inventur-nebenlaeufe/agent-contract` |
| `lager/kommissionierung` | Kommissionierung | lager | niedrig | — | `GET /api/v1/masks/lager/kommissionierung/agent-contract` |
| `lager/lagerbewegungen-liste` | Lagerbewegungen | lager | niedrig | — | `GET /api/v1/masks/lager/lagerbewegungen-liste/agent-contract` |
| `lager/lagerplaetze` | Lagerplaetze | lager | niedrig | — | `GET /api/v1/masks/lager/lagerplaetze/agent-contract` |
| `lager/leitstand` | Lager-Leitstand | lager | niedrig | — | `GET /api/v1/masks/lager/leitstand/agent-contract` |
| `lager/massebilanz` | Neue Massebilanz anlegen | lager | niedrig | — | `GET /api/v1/masks/lager/massebilanz/agent-contract` |
| `lager/materialfluss` | Materialfluss | lager | niedrig | — | `GET /api/v1/masks/lager/materialfluss/agent-contract` |
| `lager/materialfluss-visualisierung` | Materialfluss visualisierung | lager | niedrig | — | `GET /api/v1/masks/lager/materialfluss-visualisierung/agent-contract` |
| `lager/partiestamm` | Partiestamm | lager | niedrig | — | `GET /api/v1/masks/lager/partiestamm/agent-contract` |
| `lager/partiestamm-liste` | Partiestamm | lager | niedrig | — | `GET /api/v1/masks/lager/partiestamm-liste/agent-contract` |
| `lager/permanente-inventur` | Abschlüsse | lager | niedrig | — | `GET /api/v1/masks/lager/permanente-inventur/agent-contract` |
| `lager/qs-leitstand` | QS-Leitstand | qualitaet | niedrig | — | `GET /api/v1/masks/lager/qs-leitstand/agent-contract` |
| `lager/rueckverfolgbarkeit` | Rueckverfolgbarkeit | lager | niedrig | — | `GET /api/v1/masks/lager/rueckverfolgbarkeit/agent-contract` |
| `lager/silo-mobil` | Silo mobil | lager | niedrig | — | `GET /api/v1/masks/lager/silo-mobil/agent-contract` |
| `lager/silo-uebersicht` | Silo uebersicht | lager | niedrig | — | `GET /api/v1/masks/lager/silo-uebersicht/agent-contract` |
| `lager/silo-uebersicht-liste` | Silo-Uebersicht | lager | niedrig | — | `GET /api/v1/masks/lager/silo-uebersicht-liste/agent-contract` |
| `lager/stock-movement` | Lagerbewegung | lager | hoch | `inventory-to-settlement` | `GET /api/v1/masks/lager/stock-movement/agent-contract` |
| `lager/terminal` | Terminal | lager | niedrig | — | `GET /api/v1/masks/lager/terminal/agent-contract` |
| `lager/umlagerung` | Lagerbewegungen | lager | niedrig | — | `GET /api/v1/masks/lager/umlagerung/agent-contract` |
| `logistik/frachtbrief` | Frachtbriefe | logistics | niedrig | — | `GET /api/v1/masks/logistik/frachtbrief/agent-contract` |
| `logistik/frachtbriefe` | Frachtbriefe | logistik | niedrig | — | `GET /api/v1/masks/logistik/frachtbriefe/agent-contract` |
| `logistik/frachttabellen` | Frachttabellen | logistics | niedrig | — | `GET /api/v1/masks/logistik/frachttabellen/agent-contract` |
| `logistik/tour-fracht-arbeitsraum` | Tour & Fracht | logistics | niedrig | — | `GET /api/v1/masks/logistik/tour-fracht-arbeitsraum/agent-contract` |
| `logistik/tourenplanung` | Tourenplanung | logistics | niedrig | — | `GET /api/v1/masks/logistik/tourenplanung/agent-contract` |
| `logistik/verladung` | Verladung | logistics | niedrig | — | `GET /api/v1/masks/logistik/verladung/agent-contract` |
| `logistik/versandprofile` | Versandprofile | logistics | niedrig | — | `GET /api/v1/masks/logistik/versandprofile/agent-contract` |
| `mahnwesen/mahnlauf` | Mahnlauf | mahnwesen | niedrig | — | `GET /api/v1/masks/mahnwesen/mahnlauf/agent-contract` |
| `management/executive-dashboard` | Executive Dashboard | management | niedrig | — | `GET /api/v1/masks/management/executive-dashboard/agent-contract` |
| `marketing/kampagnen` | Kampagnen | marketing | niedrig | — | `GET /api/v1/masks/marketing/kampagnen/agent-contract` |
| `marketing/kampagnen-liste` | Marketingkampagnen | marketing | niedrig | — | `GET /api/v1/masks/marketing/kampagnen-liste/agent-contract` |
| `mobile/scanner` | Scanner | mobile | niedrig | — | `GET /api/v1/masks/mobile/scanner/agent-contract` |
| `nachhaltigkeit/eudr-compliance` | Eudr compliance | nachhaltigkeit | niedrig | — | `GET /api/v1/masks/nachhaltigkeit/eudr-compliance/agent-contract` |
| `personal/bewerbung-einwilligung` | Einwilligung zur Aufbewahrung | hr | mittel | — | `GET /api/v1/masks/personal/bewerbung-einwilligung/agent-contract` |
| `personal/bewerbungen` | Bewerbungen | hr | niedrig | — | `GET /api/v1/masks/personal/bewerbungen/agent-contract` |
| `personal/einwilligungserklaerungen` | Einwilligungserklärungen | hr | niedrig | — | `GET /api/v1/masks/personal/einwilligungserklaerungen/agent-contract` |
| `personal/hrm-operations-gates` | Hrm operations gates | personal | niedrig | — | `GET /api/v1/masks/personal/hrm-operations-gates/agent-contract` |
| `personal/mitarbeiter` | Mitarbeiter | personal | niedrig | — | `GET /api/v1/masks/personal/mitarbeiter/agent-contract` |
| `personal/mitarbeiter-liste` | Mitarbeitende | personal | niedrig | — | `GET /api/v1/masks/personal/mitarbeiter-liste/agent-contract` |
| `personal/mitarbeiter/neu` | Mitarbeiter stamm | personal | niedrig | — | `GET /api/v1/masks/personal/mitarbeiter/neu/agent-contract` |
| `personal/onboarding` | Onboarding | hr | niedrig | — | `GET /api/v1/masks/personal/onboarding/agent-contract` |
| `personal/organigramm` | Organigramm | personal | niedrig | — | `GET /api/v1/masks/personal/organigramm/agent-contract` |
| `personal/qualifikationen` | Qualifikationen | hr | niedrig | — | `GET /api/v1/masks/personal/qualifikationen/agent-contract` |
| `personal/schulung-neu` | Schulung neu | personal | niedrig | — | `GET /api/v1/masks/personal/schulung-neu/agent-contract` |
| `personal/schulungen` | Schulungen | hr | niedrig | — | `GET /api/v1/masks/personal/schulungen/agent-contract` |
| `personal/stundenzettel` | Stundenzettel | personal | niedrig | — | `GET /api/v1/masks/personal/stundenzettel/agent-contract` |
| `personal/stundenzettel-liste` | Stundenzettel | personal | niedrig | — | `GET /api/v1/masks/personal/stundenzettel-liste/agent-contract` |
| `personal/zeiterfassung` | Zeiterfassung | personal | niedrig | — | `GET /api/v1/masks/personal/zeiterfassung/agent-contract` |
| `personal/zeiterfassung-liste` | Zeiterfassung | personal | niedrig | — | `GET /api/v1/masks/personal/zeiterfassung-liste/agent-contract` |
| `planung/kalender` | Planungskalender | platform | mittel | — | `GET /api/v1/masks/planung/kalender/agent-contract` |
| `platform/analytics` | Analytics | platform | niedrig | — | `GET /api/v1/masks/platform/analytics/agent-contract` |
| `platform/studio-history` | Studio-Historie | platform | niedrig | — | `GET /api/v1/masks/platform/studio-history/agent-contract` |
| `platform/studio-history-diff` | Änderungsvergleich | platform | niedrig | — | `GET /api/v1/masks/platform/studio-history-diff/agent-contract` |
| `portal/anfragen` | Anfragen | portal | niedrig | — | `GET /api/v1/masks/portal/anfragen/agent-contract` |
| `portal/bestellungen` | Bestellungen | portal | niedrig | — | `GET /api/v1/masks/portal/bestellungen/agent-contract` |
| `portal/dokumente` | Dokumente | portal | niedrig | — | `GET /api/v1/masks/portal/dokumente/agent-contract` |
| `portal/empfehlungen` | Empfehlungen | portal | niedrig | — | `GET /api/v1/masks/portal/empfehlungen/agent-contract` |
| `portal/feldbuch` | Feldbuch | portal | niedrig | — | `GET /api/v1/masks/portal/feldbuch/agent-contract` |
| `portal/feldbuch-auswertungen` | Feldbuch-Auswertungen | agrar | niedrig | — | `GET /api/v1/masks/portal/feldbuch-auswertungen/agent-contract` |
| `portal/lohndienste/neu` | Lohndienste | portal | niedrig | — | `GET /api/v1/masks/portal/lohndienste/neu/agent-contract` |
| `portal/naehrstoffbilanzen` | Naehrstoffbilanzen | portal | niedrig | — | `GET /api/v1/masks/portal/naehrstoffbilanzen/agent-contract` |
| `portal/onboarding` | Onboarding | portal | niedrig | — | `GET /api/v1/masks/portal/onboarding/agent-contract` |
| `portal/preisspiegel` | Preisspiegel | portal | niedrig | — | `GET /api/v1/masks/portal/preisspiegel/agent-contract` |
| `portal/rationsoptimierung` | Rationsoptimierung | portal | niedrig | — | `GET /api/v1/masks/portal/rationsoptimierung/agent-contract` |
| `portal/rechnungen` | Rechnungen | portal | niedrig | — | `GET /api/v1/masks/portal/rechnungen/agent-contract` |
| `portal/shop` | Shop | portal | niedrig | — | `GET /api/v1/masks/portal/shop/agent-contract` |
| `portal/vertraege` | Vertraege | portal | niedrig | — | `GET /api/v1/masks/portal/vertraege/agent-contract` |
| `portal/whatsapp-simulator` | Whatsapp simulator | portal | niedrig | — | `GET /api/v1/masks/portal/whatsapp-simulator/agent-contract` |
| `portal/zertifikat` | Zertifikat | portal | niedrig | — | `GET /api/v1/masks/portal/zertifikat/agent-contract` |
| `portal/zertifikate` | Zertifikate | portal | niedrig | — | `GET /api/v1/masks/portal/zertifikate/agent-contract` |
| `pos/customer-display` | Customer display | pos | niedrig | — | `GET /api/v1/masks/pos/customer-display/agent-contract` |
| `pos/gift-cards` | Gift cards | pos | niedrig | — | `GET /api/v1/masks/pos/gift-cards/agent-contract` |
| `pos/promotionen` | Promotionen | pos | niedrig | — | `GET /api/v1/masks/pos/promotionen/agent-contract` |
| `pos/rabatte` | Rabatte | pos | niedrig | — | `GET /api/v1/masks/pos/rabatte/agent-contract` |
| `pos/retoure` | Retoure | pos | niedrig | — | `GET /api/v1/masks/pos/retoure/agent-contract` |
| `pos/suspended-sales` | Suspended sales | pos | niedrig | — | `GET /api/v1/masks/pos/suspended-sales/agent-contract` |
| `pos/tagesabschluss-enhanced` | Tagesabschluss enhanced | pos | niedrig | — | `GET /api/v1/masks/pos/tagesabschluss-enhanced/agent-contract` |
| `pos/terminal` | Terminal | pos | niedrig | — | `GET /api/v1/masks/pos/terminal/agent-contract` |
| `pos/tse-journal` | Tse journal | pos | niedrig | — | `GET /api/v1/masks/pos/tse-journal/agent-contract` |
| `pos/uebernahme-kasse` | Uebernahme kasse | pos | niedrig | — | `GET /api/v1/masks/pos/uebernahme-kasse/agent-contract` |
| `preise/historie` | Historie | preise | niedrig | — | `GET /api/v1/masks/preise/historie/agent-contract` |
| `preise/individualpreise` | Neuer {label} [PRI{preisTyp === 'EK' ? 'E' : ''}] | preise | niedrig | — | `GET /api/v1/masks/preise/individualpreise/agent-contract` |
| `preise/konditionen` | Konditionen | preise | niedrig | — | `GET /api/v1/masks/preise/konditionen/agent-contract` |
| `preise/rabattgruppen` | Neue Rabattgruppe [RAG] | preise | niedrig | — | `GET /api/v1/masks/preise/rabattgruppen/agent-contract` |
| `preise/zu-abschlaggruppen` | Neue Zu-/Abschlaggruppe [ZAGR] | preise | niedrig | — | `GET /api/v1/masks/preise/zu-abschlaggruppen/agent-contract` |
| `process/approval-density` | Freigabe-Dichte | platform | niedrig | — | `GET /api/v1/masks/process/approval-density/agent-contract` |
| `process/background-jobs` | Hintergrund-Jobs | platform | niedrig | — | `GET /api/v1/masks/process/background-jobs/agent-contract` |
| `produktion/chargen-bearbeiten` | Chargen-Nummern bearbeiten | inventory | niedrig | — | `GET /api/v1/masks/produktion/chargen-bearbeiten/agent-contract` |
| `produktion/mischfutter-produktion` | Mischfutter produktion | produktion | niedrig | — | `GET /api/v1/masks/produktion/mischfutter-produktion/agent-contract` |
| `produktion/produktions-dokumente-drucken` | Produktions dokumente drucken | produktion | niedrig | — | `GET /api/v1/masks/produktion/produktions-dokumente-drucken/agent-contract` |
| `produktion/produktionsleitstand` | Produktionsleitstand | agrar | mittel | — | `GET /api/v1/masks/produktion/produktionsleitstand/agent-contract` |
| `produktion/rezepturgruppe` | Rezepturgruppe | produktion | niedrig | — | `GET /api/v1/masks/produktion/rezepturgruppe/agent-contract` |
| `produktion/rezepturgruppen` | Neue Rezepturgruppe anlegen | produktion | niedrig | — | `GET /api/v1/masks/produktion/rezepturgruppen/agent-contract` |
| `projekte/liste` | Projekte | controlling | niedrig | — | `GET /api/v1/masks/projekte/liste/agent-contract` |
| `prospecting/leads` | LeadExplorer | prospecting | niedrig | — | `GET /api/v1/masks/prospecting/leads/agent-contract` |
| `qualitaet/ausnahmen` | Betriebs-Ausnahmen | operations | niedrig | — | `GET /api/v1/masks/qualitaet/ausnahmen/agent-contract` |
| `qualitaet/ausnahmen-liste` | Betriebsausnahmen | qualitaet | niedrig | — | `GET /api/v1/masks/qualitaet/ausnahmen-liste/agent-contract` |
| `qualitaet/labor-auftrag` | Labor auftrag | qualitaet | niedrig | — | `GET /api/v1/masks/qualitaet/labor-auftrag/agent-contract` |
| `qualitaet/labor-detail` | Labor detail | qualitaet | niedrig | — | `GET /api/v1/masks/qualitaet/labor-detail/agent-contract` |
| `qualitaet/labor-liste` | Laborauftraege | qualitaet | niedrig | — | `GET /api/v1/masks/qualitaet/labor-liste/agent-contract` |
| `qualitaet/reklamation` | Reklamation | qualitaet | mittel | `complaint-to-resolution` | `GET /api/v1/masks/qualitaet/reklamation/agent-contract` |
| `qualitaet/reklamation-detail` | Status geaendert | qualitaet | niedrig | — | `GET /api/v1/masks/qualitaet/reklamation-detail/agent-contract` |
| `qualitaet/reklamationen` | Reklamationen | qualitaet | niedrig | — | `GET /api/v1/masks/qualitaet/reklamationen/agent-contract` |
| `qualitaet/reklamationen-liste` | Reklamationen | qualitaet | niedrig | — | `GET /api/v1/masks/qualitaet/reklamationen-liste/agent-contract` |
| `reports` | Reports | workspace | niedrig | — | `GET /api/v1/masks/reports/agent-contract` |
| `reports/ReportsDashboardCharts` | ReportsDashboardCharts | reports | niedrig | — | `GET /api/v1/masks/reports/ReportsDashboardCharts/agent-contract` |
| `reports/deckungsbeitrag` | Deckungsbeitrag | reports | niedrig | — | `GET /api/v1/masks/reports/deckungsbeitrag/agent-contract` |
| `reports/lagerbestand` | Lagerbestand | reports | niedrig | — | `GET /api/v1/masks/reports/lagerbestand/agent-contract` |
| `reports/umsatz` | Umsatz | reports | niedrig | — | `GET /api/v1/masks/reports/umsatz/agent-contract` |
| `rezepte/editor` | Grunddaten | rezepte | niedrig | — | `GET /api/v1/masks/rezepte/editor/agent-contract` |
| `rezepte/rezept` | Rezept | produktion | niedrig | — | `GET /api/v1/masks/rezepte/rezept/agent-contract` |
| `sales/angebote-liste` | Verkaufsangebote | sales | niedrig | — | `GET /api/v1/masks/sales/angebote-liste/agent-contract` |
| `sales/angebote/neu` | Angebot erstellen | sales | niedrig | — | `GET /api/v1/masks/sales/angebote/neu/agent-contract` |
| `sales/auftraege-liste` | Verkaufsauftraege | sales | niedrig | — | `GET /api/v1/masks/sales/auftraege-liste/agent-contract` |
| `sales/auftrag-lieferschein-abgleich` | Auftrag lieferschein abgleich | sales | niedrig | — | `GET /api/v1/masks/sales/auftrag-lieferschein-abgleich/agent-contract` |
| `sales/auftragskette` | Auftragskette | sales | niedrig | — | `GET /api/v1/masks/sales/auftragskette/agent-contract` |
| `sales/credit-notes` | Credit note editor | sales | niedrig | — | `GET /api/v1/masks/sales/credit-notes/agent-contract` |
| `sales/delivery-editor` | Delivery editor | sales | niedrig | — | `GET /api/v1/masks/sales/delivery-editor/agent-contract` |
| `sales/delivery-editor-new` | Delivery editor new | sales | niedrig | — | `GET /api/v1/masks/sales/delivery-editor-new/agent-contract` |
| `sales/delivery-note` | Lieferschein | sales | niedrig | `order-to-cash` | `GET /api/v1/masks/sales/delivery-note/agent-contract` |
| `sales/gutschrift` | Gutschrift | sales | mittel | — | `GET /api/v1/masks/sales/gutschrift/agent-contract` |
| `sales/invoice` | Ausgangsrechnung | sales | niedrig | — | `GET /api/v1/masks/sales/invoice/agent-contract` |
| `sales/invoices` | Ausgangsrechnungen | sales | niedrig | — | `GET /api/v1/masks/sales/invoices/agent-contract` |
| `sales/kalkulationen/neu` | Kalkulation | sales | niedrig | — | `GET /api/v1/masks/sales/kalkulationen/neu/agent-contract` |
| `sales/kreditlimit-pruefung` | Kreditlimit-Pruefung | sales | niedrig | — | `GET /api/v1/masks/sales/kreditlimit-pruefung/agent-contract` |
| `sales/lieferung-storno` | Lieferung storno | sales | niedrig | — | `GET /api/v1/masks/sales/lieferung-storno/agent-contract` |
| `sales/lieferungen-liste` | Lieferscheine | sales | niedrig | — | `GET /api/v1/masks/sales/lieferungen-liste/agent-contract` |
| `sales/lieferungen/neu` | Lieferungen liste | sales | niedrig | — | `GET /api/v1/masks/sales/lieferungen/neu/agent-contract` |
| `sales/orders-modern` | Orders modern | sales | niedrig | — | `GET /api/v1/masks/sales/orders-modern/agent-contract` |
| `sales/rechnungen-liste` | Rechnungen liste | sales | niedrig | — | `GET /api/v1/masks/sales/rechnungen-liste/agent-contract` |
| `sales/sales-order` | Verkaufsauftrag | sales | niedrig | `order-to-cash` | `GET /api/v1/masks/sales/sales-order/agent-contract` |
| `schaeden/liste` | Schadenmeldungen | finance | niedrig | — | `GET /api/v1/masks/schaeden/liste/agent-contract` |
| `schaeden/meldung` | Meldung | schaeden | niedrig | — | `GET /api/v1/masks/schaeden/meldung/agent-contract` |
| `schnittstelle/legacy-adapter-monitor` | Standard-/Unimet-Adapter | integration | niedrig | — | `GET /api/v1/masks/schnittstelle/legacy-adapter-monitor/agent-contract` |
| `schnittstelle/mde-inbox` | MDE-Eingangskorb | platform | mittel | — | `GET /api/v1/masks/schnittstelle/mde-inbox/agent-contract` |
| `service/abschluss` | Abschluss | service | niedrig | — | `GET /api/v1/masks/service/abschluss/agent-contract` |
| `service/anfrage` | Serviceanfrage | service | niedrig | — | `GET /api/v1/masks/service/anfrage/agent-contract` |
| `service/anfrage-detail` | Anfrage detail | service | niedrig | — | `GET /api/v1/masks/service/anfrage-detail/agent-contract` |
| `service/anfrage/neu` | Anfrage erstellt | service | niedrig | — | `GET /api/v1/masks/service/anfrage/neu/agent-contract` |
| `service/anfragen` | Anfragen | service | niedrig | — | `GET /api/v1/masks/service/anfragen/agent-contract` |
| `service/anfragen-liste` | Serviceanfragen | service | niedrig | — | `GET /api/v1/masks/service/anfragen-liste/agent-contract` |
| `service/rueckmeldung` | Rueckmeldung | service | niedrig | — | `GET /api/v1/masks/service/rueckmeldung/agent-contract` |
| `setup/firma` | Firma | setup | niedrig | — | `GET /api/v1/masks/setup/firma/agent-contract` |
| `silo/kapazitaeten` | Silos Gesamt | silo | niedrig | — | `GET /api/v1/masks/silo/kapazitaeten/agent-contract` |
| `silo/silo` | Silo | lager | niedrig | — | `GET /api/v1/masks/silo/silo/agent-contract` |
| `stammdaten/artikel-stoffstrom` | Stoffstrom-Datensätze | stammdaten | niedrig | — | `GET /api/v1/masks/stammdaten/artikel-stoffstrom/agent-contract` |
| `stammdaten/artikelbestandteile` | Neuen Bestandteil anlegen | stammdaten | niedrig | — | `GET /api/v1/masks/stammdaten/artikelbestandteile/agent-contract` |
| `stammdaten/artikelverpackung` | Neue Verpackung anlegen | stammdaten | niedrig | — | `GET /api/v1/masks/stammdaten/artikelverpackung/agent-contract` |
| `stammdaten/betriebsstaetten` | Neue Betriebsstätte | stammdaten | niedrig | — | `GET /api/v1/masks/stammdaten/betriebsstaetten/agent-contract` |
| `stammdaten/hausbank` | Hausbank | finance | niedrig | — | `GET /api/v1/masks/stammdaten/hausbank/agent-contract` |
| `stammdaten/hausbanken` | Neue Hausbank anlegen | stammdaten | niedrig | — | `GET /api/v1/masks/stammdaten/hausbanken/agent-contract` |
| `stammdaten/individuelle-artikelnummer` | Individuelle Artikelnummer | lager | niedrig | — | `GET /api/v1/masks/stammdaten/individuelle-artikelnummer/agent-contract` |
| `stammdaten/individuelle-artikelnummern` | Neue Zuordnung anlegen | stammdaten | niedrig | — | `GET /api/v1/masks/stammdaten/individuelle-artikelnummern/agent-contract` |
| `stammdaten/mengeneinheit` | Mengeneinheit | lager | niedrig | — | `GET /api/v1/masks/stammdaten/mengeneinheit/agent-contract` |
| `stammdaten/mengeneinheiten` | Neue Mengeneinheit | stammdaten | niedrig | — | `GET /api/v1/masks/stammdaten/mengeneinheiten/agent-contract` |
| `start-dashboard` | Start dashboard | workspace | niedrig | — | `GET /api/v1/masks/start-dashboard/agent-contract` |
| `strecke/disposition` | Strecken-Disposition | logistics | niedrig | — | `GET /api/v1/masks/strecke/disposition/agent-contract` |
| `strecke/dokumente-drucken` | Strecken-Dokumente drucken | logistics | niedrig | — | `GET /api/v1/masks/strecke/dokumente-drucken/agent-contract` |
| `strecke/menu` | Menu | strecke | niedrig | — | `GET /api/v1/masks/strecke/menu/agent-contract` |
| `strecke/nawaro-ernterklaerung-drucken` | NaWaRo-Ernterklärung drucken | agrar | niedrig | — | `GET /api/v1/masks/strecke/nawaro-ernterklaerung-drucken/agent-contract` |
| `strecke/nawaro-lieferungen` | NaWaRo-Lieferungen | agrar | niedrig | — | `GET /api/v1/masks/strecke/nawaro-lieferungen/agent-contract` |
| `strecke/nawaro-uebersicht` | Nawaro uebersicht | strecke | niedrig | — | `GET /api/v1/masks/strecke/nawaro-uebersicht/agent-contract` |
| `strecke/nawaro-uebersicht-drucken` | Nawaro uebersicht drucken | strecke | niedrig | — | `GET /api/v1/masks/strecke/nawaro-uebersicht-drucken/agent-contract` |
| `strecke/nawaro-vertraege-pruefen` | NaWaRo-Vertraege pruefen | agrar | niedrig | — | `GET /api/v1/masks/strecke/nawaro-vertraege-pruefen/agent-contract` |
| `strecke/qualitaets-abweichung` | Qualitätsabweichung | qualitaet | niedrig | — | `GET /api/v1/masks/strecke/qualitaets-abweichung/agent-contract` |
| `strecke/speditionen-fracht-preise` | Speditionen fracht preise | strecke | niedrig | — | `GET /api/v1/masks/strecke/speditionen-fracht-preise/agent-contract` |
| `strecke/streckengeschaeft` | Streckengeschäft | logistics | niedrig | — | `GET /api/v1/masks/strecke/streckengeschaeft/agent-contract` |
| `strecke/vorlaeufig` | Vorläufige Streckengeschäfte | logistics | niedrig | — | `GET /api/v1/masks/strecke/vorlaeufig/agent-contract` |
| `strecke/vorlaeufige-streckengeschaefte` | Vorlaeufige streckengeschaefte | strecke | niedrig | — | `GET /api/v1/masks/strecke/vorlaeufige-streckengeschaefte/agent-contract` |
| `subventionen/dashboard` | Foerder-Dashboard | foerderung | niedrig | — | `GET /api/v1/masks/subventionen/dashboard/agent-contract` |
| `system/live-monitor` | Live monitor | system | niedrig | — | `GET /api/v1/masks/system/live-monitor/agent-contract` |
| `tankstelle/adapter-inbox` | Tankanlagen-Eingang | agrar | niedrig | — | `GET /api/v1/masks/tankstelle/adapter-inbox/agent-contract` |
| `tankstelle/zapfungen` | Zapfungen | tankstelle | niedrig | — | `GET /api/v1/masks/tankstelle/zapfungen/agent-contract` |
| `tankstelle/zapfungen-liste` | Zapfungen | logistik | niedrig | — | `GET /api/v1/masks/tankstelle/zapfungen-liste/agent-contract` |
| `transporte/fahrer` | Fahrer | logistics | niedrig | — | `GET /api/v1/masks/transporte/fahrer/agent-contract` |
| `transporte/fahrer-liste` | Fahrer | logistik | niedrig | — | `GET /api/v1/masks/transporte/fahrer-liste/agent-contract` |
| `transporte/fahrer/neu` | Fahrer liste | transporte | niedrig | — | `GET /api/v1/masks/transporte/fahrer/neu/agent-contract` |
| `verkauf/auftraege` | Auftraege liste | verkauf | niedrig | — | `GET /api/v1/masks/verkauf/auftraege/agent-contract` |
| `verkauf/auftraege/neu` | Order editor | verkauf | niedrig | — | `GET /api/v1/masks/verkauf/auftraege/neu/agent-contract` |
| `verkauf/betriebs-auftraege` | Betriebs auftraege | verkauf | niedrig | — | `GET /api/v1/masks/verkauf/betriebs-auftraege/agent-contract` |
| `verkauf/betriebsauftrag` | Betriebsauftrag drucken | sales | niedrig | — | `GET /api/v1/masks/verkauf/betriebsauftrag/agent-contract` |
| `verkauf/dauerauftraege` | Neuen Dauerauftrag anlegen | verkauf | niedrig | — | `GET /api/v1/masks/verkauf/dauerauftraege/agent-contract` |
| `verkauf/kommissions-auftraege` | Kommissions auftraege | verkauf | niedrig | — | `GET /api/v1/masks/verkauf/kommissions-auftraege/agent-contract` |
| `verkauf/kunde` | Kunde | verkauf | niedrig | — | `GET /api/v1/masks/verkauf/kunde/agent-contract` |
| `verkauf/kunde-neu` | Kunde neu | verkauf | niedrig | — | `GET /api/v1/masks/verkauf/kunde-neu/agent-contract` |
| `verkauf/kunden-liste` | Kunden liste | verkauf | niedrig | — | `GET /api/v1/masks/verkauf/kunden-liste/agent-contract` |
| `verkauf/kunden-stamm` | Vorlage übernommen | verkauf | niedrig | — | `GET /api/v1/masks/verkauf/kunden-stamm/agent-contract` |
| `verkauf/kunden-stamm-enhanced` | Kunden stamm enhanced | verkauf | niedrig | — | `GET /api/v1/masks/verkauf/kunden-stamm-enhanced/agent-contract` |
| `verkauf/lieferschein-erfassung` | Lieferschein erfassung | verkauf | niedrig | — | `GET /api/v1/masks/verkauf/lieferschein-erfassung/agent-contract` |
| `verkauf/rechnungen` | Rechnungen worklist | verkauf | niedrig | — | `GET /api/v1/masks/verkauf/rechnungen/agent-contract` |
| `verkauf/rechnungen/neu` | Invoice editor | verkauf | niedrig | — | `GET /api/v1/masks/verkauf/rechnungen/neu/agent-contract` |
| `verkauf/unerledigte-auftrags-positionen` | Unerledigte auftrags positionen | verkauf | niedrig | — | `GET /api/v1/masks/verkauf/unerledigte-auftrags-positionen/agent-contract` |
| `verladung/liste` | Verladungen | logistik | niedrig | — | `GET /api/v1/masks/verladung/liste/agent-contract` |
| `verladung/lkw-beladung` | Lkw beladung | verladung | niedrig | — | `GET /api/v1/masks/verladung/lkw-beladung/agent-contract` |
| `versand/versand-avis` | Versand-Avis | logistics | niedrig | — | `GET /api/v1/masks/versand/versand-avis/agent-contract` |
| `versicherungen/liste` | Versicherungen | finance | niedrig | — | `GET /api/v1/masks/versicherungen/liste/agent-contract` |
| `vertrag/neu` | Gespeichert | vertrag | niedrig | — | `GET /api/v1/masks/vertrag/neu/agent-contract` |
| `vertrag/rahmenvertraege` | Rahmenvertraege | vertrag | niedrig | — | `GET /api/v1/masks/vertrag/rahmenvertraege/agent-contract` |
| `vertrag/rahmenvertraege-liste` | Rahmenvertraege | agrar | niedrig | — | `GET /api/v1/masks/vertrag/rahmenvertraege-liste/agent-contract` |
| `vertrieb/kundenumsatz` | Kundenumsatz | vertrieb | niedrig | — | `GET /api/v1/masks/vertrieb/kundenumsatz/agent-contract` |
| `waage/hofliste` | Hofliste Waage | agrar | niedrig | — | `GET /api/v1/masks/waage/hofliste/agent-contract` |
| `waage/liste` | Waagen | logistik | niedrig | — | `GET /api/v1/masks/waage/liste/agent-contract` |
| `waage/neu` | Liste | waage | niedrig | — | `GET /api/v1/masks/waage/neu/agent-contract` |
| `waage/vorlagen` | Vorlagen | waage | niedrig | — | `GET /api/v1/masks/waage/vorlagen/agent-contract` |
| `waage/waagen-liste` | Waagen | agrar | niedrig | — | `GET /api/v1/masks/waage/waagen-liste/agent-contract` |
| `waage/wiegeschein` | Wiegeschein | waage | niedrig | — | `GET /api/v1/masks/waage/wiegeschein/agent-contract` |
| `waage/wiegeschein-detail` | Wiegeschein detail | waage | niedrig | — | `GET /api/v1/masks/waage/wiegeschein-detail/agent-contract` |
| `waage/wiegungen` | Wiegungen | waage | niedrig | — | `GET /api/v1/masks/waage/wiegungen/agent-contract` |
| `waage/wiegungen-liste` | Wiegescheine | agrar | niedrig | — | `GET /api/v1/masks/waage/wiegungen-liste/agent-contract` |
| `wartung/anlagen-liste` | Wartung | lager | niedrig | — | `GET /api/v1/masks/wartung/anlagen-liste/agent-contract` |
| `workflow/flow-spine-complaint-to-resolution` | Flow spine complaint to resolution | workflow | niedrig | — | `GET /api/v1/masks/workflow/flow-spine-complaint-to-resolution/agent-contract` |
| `workflow/flow-spine-compliance-to-report` | Flow spine compliance to report | workflow | niedrig | — | `GET /api/v1/masks/workflow/flow-spine-compliance-to-report/agent-contract` |
| `workflow/flow-spine-contract-to-settlement` | Flow spine contract to settlement | workflow | niedrig | — | `GET /api/v1/masks/workflow/flow-spine-contract-to-settlement/agent-contract` |
| `workflow/flow-spine-finance-to-close` | Flow spine finance to close | workflow | niedrig | — | `GET /api/v1/masks/workflow/flow-spine-finance-to-close/agent-contract` |
| `workflow/flow-spine-harvest-to-settlement` | Flow spine harvest to settlement | workflow | niedrig | — | `GET /api/v1/masks/workflow/flow-spine-harvest-to-settlement/agent-contract` |
| `workflow/flow-spine-inventory-to-settlement` | Flow spine inventory to settlement | workflow | niedrig | — | `GET /api/v1/masks/workflow/flow-spine-inventory-to-settlement/agent-contract` |
| `workflow/flow-spine-order-to-cash` | Flow spine order to cash | workflow | niedrig | — | `GET /api/v1/masks/workflow/flow-spine-order-to-cash/agent-contract` |
| `workflow/flow-spine-procure-to-pay` | Flow spine procure to pay | workflow | niedrig | — | `GET /api/v1/masks/workflow/flow-spine-procure-to-pay/agent-contract` |
| `workflow/flow-spine-service-to-customer` | Flow spine service to customer | workflow | niedrig | — | `GET /api/v1/masks/workflow/flow-spine-service-to-customer/agent-contract` |
| `workflow/flow-spine-studio` | Flow spine studio | workflow | niedrig | — | `GET /api/v1/masks/workflow/flow-spine-studio/agent-contract` |
| `workflow/leitstand` | Workflow-Leitstand | workflow | niedrig | — | `GET /api/v1/masks/workflow/leitstand/agent-contract` |
| `workflow/process-mining` | Process Mining | workflow | niedrig | — | `GET /api/v1/masks/workflow/process-mining/agent-contract` |
| `workflow/process-mining-analytics` | Process mining analytics | workflow | niedrig | — | `GET /api/v1/masks/workflow/process-mining-analytics/agent-contract` |
| `workflow/workflow-monitoring` | Workflow-Monitoring | platform | niedrig | — | `GET /api/v1/masks/workflow/workflow-monitoring/agent-contract` |
| `workflow/workflow-regeln` | Workflow regeln | workflow | niedrig | — | `GET /api/v1/masks/workflow/workflow-regeln/agent-contract` |
| `workflow/workflow-sandbox` | Workflow sandbox | workflow | niedrig | — | `GET /api/v1/masks/workflow/workflow-sandbox/agent-contract` |
| `workflows/history` | Workflow monitoring | workflows | niedrig | — | `GET /api/v1/masks/workflows/history/agent-contract` |
| `workflows/supervisor` | Supervisor | workflows | niedrig | — | `GET /api/v1/masks/workflows/supervisor/agent-contract` |
| `workspace/einkauf` | Einkauf-Cockpit | einkauf | niedrig | — | `GET /api/v1/masks/workspace/einkauf/agent-contract` |
| `workspace/fibu` | FiBu-Cockpit | finance | niedrig | — | `GET /api/v1/masks/workspace/fibu/agent-contract` |
| `workspace/lager` | Lager-Cockpit | lager | niedrig | — | `GET /api/v1/masks/workspace/lager/agent-contract` |
| `workspace/leitung` | Leitung-Cockpit | management | niedrig | — | `GET /api/v1/masks/workspace/leitung/agent-contract` |
| `workspace/letzte-dokumente` | Letzte Dokumente | workspace | niedrig | — | `GET /api/v1/masks/workspace/letzte-dokumente/agent-contract` |
| `workspace/start-dashboard` | Start-Dashboard | workspace | niedrig | — | `GET /api/v1/masks/workspace/start-dashboard/agent-contract` |
| `workspace/verkauf` | Verkauf-Cockpit | sales | niedrig | — | `GET /api/v1/masks/workspace/verkauf/agent-contract` |
| `zertifikate/liste` | Zertifikate | qualitaet | niedrig | — | `GET /api/v1/masks/zertifikate/liste/agent-contract` |
| `zertifikate/neu` | Liste | zertifikate | niedrig | — | `GET /api/v1/masks/zertifikate/neu/agent-contract` |

---

## Domäne: admin

### `admin/agenten-integration` — Agenten integration

**Zweck:** Stamm- und Fachmaske fuer Agenten integration (admin/agenten-integration).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/admin/agenten-integration/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/admin/agenten-integration/agent-contract` |
| Readiness | `GET /api/v1/masks/admin/agenten-integration/readiness` |
| Rollout-Route | `/mask-rollout/admin__agenten-integration/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agent/integrations/providers/superglue/tenants/{entity_id}/admin-state`

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Agenten integration {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `admin/ai-approvals` — AI-Freigaben

**Zweck:** AI-/Agent-Vorschlaege fuer Einkaufsrechnungen freigeben.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/admin/ai-approvals/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/admin/ai-approvals/agent-contract` |
| Readiness | `GET /api/v1/masks/admin/ai-approvals/readiness` |
| Rollout-Route | `/mask-rollout/admin__ai-approvals/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `items` → `/api/v1/finance/ap/invoices/?status=ZUR_FREIGABE`

**Beispiel-Prompts:**

- Welche Rechnungen warten auf Freigabe?

---

### `admin/api-keys` — Api keys

**Zweck:** Stamm- und Fachmaske fuer Api keys (admin/api-keys).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/admin/api-keys/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/admin/api-keys/agent-contract` |
| Readiness | `GET /api/v1/masks/admin/api-keys/readiness` |
| Rollout-Route | `/mask-rollout/admin__api-keys/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/admin/benutzer/{entity_id}`

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Api keys {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `admin/audit-log` — Audit log

**Zweck:** Audit log mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/admin/audit-log/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/admin/audit-log/agent-contract` |
| Readiness | `GET /api/v1/masks/admin/audit-log/readiness` |
| Rollout-Route | `/mask-rollout/admin__audit-log/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/admin/audit-log`
- `items` → `/api/v1/admin/audit-log`

**Beispiel-Prompts:**

- Zeige offene Audit log.
- Was ist in Audit log faellig?

---

### `admin/audit-log-liste` — Audit-Log

**Zweck:** Audit-Ereignisse nachvollziehen und exportieren.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/admin/audit-log-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/admin/audit-log-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/admin/audit-log-liste/readiness` |
| Rollout-Route | `/mask-rollout/admin__audit-log-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/admin/audit-log`

**Beispiel-Prompts:**

- Welche Aenderungen gab es heute?
- Wer hat den Datensatz geaendert?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `admin/backup-restore` — Backup restore

**Zweck:** Stamm- und Fachmaske fuer Backup restore (admin/backup-restore).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/admin/backup-restore/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/admin/backup-restore/agent-contract` |
| Readiness | `GET /api/v1/masks/admin/backup-restore/readiness` |
| Rollout-Route | `/mask-rollout/admin__backup-restore/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/admin/benutzer/{entity_id}`

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Backup restore {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `admin/belegfolgekonfig` — Belegfolgekonfig

**Zweck:** Belegfolgekonfig mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/admin/belegfolgekonfig/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/admin/belegfolgekonfig/agent-contract` |
| Readiness | `GET /api/v1/masks/admin/belegfolgekonfig/readiness` |
| Rollout-Route | `/mask-rollout/admin__belegfolgekonfig/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/admin/number-ranges/`
- `items` → `/api/v1/admin/number-ranges/`

**Beispiel-Prompts:**

- Zeige offene Belegfolgekonfig.
- Was ist in Belegfolgekonfig faellig?

---

### `admin/benutzer-liste` — Benutzer

**Zweck:** Benutzer mit Rolle und letzter Anmeldung pruefen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/admin/benutzer-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/admin/benutzer-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/admin/benutzer-liste/readiness` |
| Rollout-Route | `/mask-rollout/admin__benutzer-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/admin/benutzer`

**Beispiel-Prompts:**

- Wer hat sich seit drei Monaten nicht angemeldet?
- Welche Benutzer sind Administratoren?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `admin/berechtigungen-matrix` — Berechtigungen matrix

**Zweck:** Stamm- und Fachmaske fuer Berechtigungen matrix (admin/berechtigungen-matrix).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/admin/berechtigungen-matrix/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/admin/berechtigungen-matrix/agent-contract` |
| Readiness | `GET /api/v1/masks/admin/berechtigungen-matrix/readiness` |
| Rollout-Route | `/mask-rollout/admin__berechtigungen-matrix/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/admin/report-permissions/{entity_id}`

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Berechtigungen matrix {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `admin/branches` — Branches

**Zweck:** Stamm- und Fachmaske fuer Branches (admin/branches).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/admin/branches/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/admin/branches/agent-contract` |
| Readiness | `GET /api/v1/masks/admin/branches/readiness` |
| Rollout-Route | `/mask-rollout/admin__branches/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/admin/branches/{entity_id}`

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Branches {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `admin/command-monitor` — Command monitor

**Zweck:** Stamm- und Fachmaske fuer Command monitor (admin/command-monitor).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/admin/command-monitor/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/admin/command-monitor/agent-contract` |
| Readiness | `GET /api/v1/masks/admin/command-monitor/readiness` |
| Rollout-Route | `/mask-rollout/admin__command-monitor/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/articles/{entity_id}`

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Command monitor {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `admin/control-center` — Control center

**Zweck:** Control center mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/admin/control-center/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/admin/control-center/agent-contract` |
| Readiness | `GET /api/v1/masks/admin/control-center/readiness` |
| Rollout-Route | `/mask-rollout/admin__control-center/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agents/neuroassist/ops/control-center`
- `items` → `/api/v1/agents/neuroassist/ops/control-center`

**Beispiel-Prompts:**

- Zeige offene Control center.
- Was ist in Control center faellig?

---

### `admin/control-center/ai-approvals` — Ai approvals

**Zweck:** Ai approvals mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/admin/control-center/ai-approvals/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/admin/control-center/ai-approvals/agent-contract` |
| Readiness | `GET /api/v1/masks/admin/control-center/ai-approvals/readiness` |
| Rollout-Route | `/mask-rollout/admin__control-center__ai-approvals/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/finance/ap/invoices/`
- `items` → `/api/v1/finance/ap/invoices/`

**Beispiel-Prompts:**

- Zeige offene Ai approvals.
- Was ist in Ai approvals faellig?

---

### `admin/control-center/incident-response` — Incident response

**Zweck:** Incident response mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/admin/control-center/incident-response/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/admin/control-center/incident-response/agent-contract` |
| Readiness | `GET /api/v1/masks/admin/control-center/incident-response/readiness` |
| Rollout-Route | `/mask-rollout/admin__control-center__incident-response/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agents/neuroassist/ops/incidents`
- `items` → `/api/v1/agents/neuroassist/ops/incidents`

**Beispiel-Prompts:**

- Zeige offene Incident response.
- Was ist in Incident response faellig?

---

### `admin/control-center/operations` — Operations

**Zweck:** Operations mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/admin/control-center/operations/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/admin/control-center/operations/agent-contract` |
| Readiness | `GET /api/v1/masks/admin/control-center/operations/readiness` |
| Rollout-Route | `/mask-rollout/admin__control-center__operations/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/admin-suite/operations`
- `items` → `/api/v1/admin-suite/operations`

**Beispiel-Prompts:**

- Zeige offene Operations.
- Was ist in Operations faellig?

---

### `admin/control-center/security` — Security

**Zweck:** Security mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/admin/control-center/security/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/admin/control-center/security/agent-contract` |
| Readiness | `GET /api/v1/masks/admin/control-center/security/readiness` |
| Rollout-Route | `/mask-rollout/admin__control-center__security/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/admin-suite/security`
- `items` → `/api/v1/admin-suite/security`

**Beispiel-Prompts:**

- Zeige offene Security.
- Was ist in Security faellig?

---

### `admin/core/audit-governance` — Audit governance

**Zweck:** Audit governance mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/admin/core/audit-governance/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/admin/core/audit-governance/agent-contract` |
| Readiness | `GET /api/v1/masks/admin/core/audit-governance/readiness` |
| Rollout-Route | `/mask-rollout/admin__core__audit-governance/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/governance/audit-trail`
- `items` → `/api/v1/governance/audit-trail`

**Beispiel-Prompts:**

- Zeige offene Audit governance.
- Was ist in Audit governance faellig?

---

### `admin/data-quality` — Data quality

**Zweck:** Data quality mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/admin/data-quality/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/admin/data-quality/agent-contract` |
| Readiness | `GET /api/v1/masks/admin/data-quality/readiness` |
| Rollout-Route | `/mask-rollout/admin__data-quality/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/admin/data-quality/rules`
- `items` → `/api/v1/admin/data-quality/rules`

**Beispiel-Prompts:**

- Zeige offene Data quality.
- Was ist in Data quality faellig?

---

### `admin/devices` — Devices

**Zweck:** Devices mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/admin/devices/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/admin/devices/agent-contract` |
| Readiness | `GET /api/v1/masks/admin/devices/readiness` |
| Rollout-Route | `/mask-rollout/admin__devices/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/admin/devices`
- `items` → `/api/v1/admin/devices`

**Beispiel-Prompts:**

- Zeige offene Devices.
- Was ist in Devices faellig?

---

### `admin/dms-integration` — Dms integration

**Zweck:** Dms integration mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/admin/dms-integration/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/admin/dms-integration/agent-contract` |
| Readiness | `GET /api/v1/masks/admin/dms-integration/readiness` |
| Rollout-Route | `/mask-rollout/admin__dms-integration/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/admin/dms/status`
- `items` → `/api/v1/admin/dms/status`

**Beispiel-Prompts:**

- Zeige offene Dms integration.
- Was ist in Dms integration faellig?

---

### `admin/erntepeak-stabilitaet` — Erntepeak stabilitaet

**Zweck:** Erntepeak stabilitaet mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/admin/erntepeak-stabilitaet/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/admin/erntepeak-stabilitaet/agent-contract` |
| Readiness | `GET /api/v1/masks/admin/erntepeak-stabilitaet/readiness` |
| Rollout-Route | `/mask-rollout/admin__erntepeak-stabilitaet/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/admin/erntefenster-campaigns`
- `items` → `/api/v1/admin/erntefenster-campaigns`

**Beispiel-Prompts:**

- Zeige offene Erntepeak stabilitaet.
- Was ist in Erntepeak stabilitaet faellig?

---

### `admin/forst/kalkulation` — Kalkulation

**Zweck:** Kalkulation mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/admin/forst/kalkulation/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/admin/forst/kalkulation/agent-contract` |
| Readiness | `GET /api/v1/masks/admin/forst/kalkulation/readiness` |
| Rollout-Route | `/mask-rollout/admin__forst__kalkulation/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/contracts/`
- `items` → `/api/v1/agrar/contracts/`

**Beispiel-Prompts:**

- Zeige offene Kalkulation.
- Was ist in Kalkulation faellig?

---

### `admin/integrationen-quarantaene` — Integrationen quarantaene

**Zweck:** Integrationen quarantaene mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/admin/integrationen-quarantaene/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/admin/integrationen-quarantaene/agent-contract` |
| Readiness | `GET /api/v1/masks/admin/integrationen-quarantaene/readiness` |
| Rollout-Route | `/mask-rollout/admin__integrationen-quarantaene/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/admin/mobile/connector-events/quarantine`
- `items` → `/api/v1/admin/mobile/connector-events/quarantine`

**Beispiel-Prompts:**

- Zeige offene Integrationen quarantaene.
- Was ist in Integrationen quarantaene faellig?

---

### `admin/monitoring/alerting` — Alerting

**Zweck:** Alerting mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/admin/monitoring/alerting/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/admin/monitoring/alerting/agent-contract` |
| Readiness | `GET /api/v1/masks/admin/monitoring/alerting/readiness` |
| Rollout-Route | `/mask-rollout/admin__monitoring__alerting/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/admin/monitoring/alerts`
- `items` → `/api/v1/admin/monitoring/alerts`

**Beispiel-Prompts:**

- Zeige offene Alerting.
- Was ist in Alerting faellig?

---

### `admin/monitoring/historie` — Historie

**Zweck:** Historie mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/admin/monitoring/historie/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/admin/monitoring/historie/agent-contract` |
| Readiness | `GET /api/v1/masks/admin/monitoring/historie/readiness` |
| Rollout-Route | `/mask-rollout/admin__monitoring__historie/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/admin/monitoring/scheduler-jobs`
- `items` → `/api/v1/admin/monitoring/scheduler-jobs`

**Beispiel-Prompts:**

- Zeige offene Historie.
- Was ist in Historie faellig?

---

### `admin/monitoring/regeln` — Regeln

**Zweck:** Regeln mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/admin/monitoring/regeln/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/admin/monitoring/regeln/agent-contract` |
| Readiness | `GET /api/v1/masks/admin/monitoring/regeln/readiness` |
| Rollout-Route | `/mask-rollout/admin__monitoring__regeln/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/admin/monitoring/rules`
- `items` → `/api/v1/admin/monitoring/rules`

**Beispiel-Prompts:**

- Zeige offene Regeln.
- Was ist in Regeln faellig?

---

### `admin/omnichannel-handelskonflikt` — Omnichannel handelskonflikt

**Zweck:** Omnichannel handelskonflikt mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/admin/omnichannel-handelskonflikt/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/admin/omnichannel-handelskonflikt/agent-contract` |
| Readiness | `GET /api/v1/masks/admin/omnichannel-handelskonflikt/readiness` |
| Rollout-Route | `/mask-rollout/admin__omnichannel-handelskonflikt/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/channels/livechat/sessions`
- `items` → `/api/v1/channels/livechat/sessions`

**Beispiel-Prompts:**

- Zeige offene Omnichannel handelskonflikt.
- Was ist in Omnichannel handelskonflikt faellig?

---

### `admin/system-einstellungen` — System einstellungen

**Zweck:** Stamm- und Fachmaske fuer System einstellungen (admin/system-einstellungen).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/admin/system-einstellungen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/admin/system-einstellungen/agent-contract` |
| Readiness | `GET /api/v1/masks/admin/system-einstellungen/readiness` |
| Rollout-Route | `/mask-rollout/admin__system-einstellungen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/articles/{entity_id}`

**Beispiel-Prompts:**

- Zeige Stammdaten fuer System einstellungen {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `admin/tankstelle-evb` — Tankstelle evb

**Zweck:** Stamm- und Fachmaske fuer Tankstelle evb (admin/tankstelle-evb).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/admin/tankstelle-evb/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/admin/tankstelle-evb/agent-contract` |
| Readiness | `GET /api/v1/masks/admin/tankstelle-evb/readiness` |
| Rollout-Route | `/mask-rollout/admin__tankstelle-evb/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/tankstelle/zapfungen/{entity_id}`

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Tankstelle evb {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `admin/tenants` — Tenants

**Zweck:** Stamm- und Fachmaske fuer Tenants (admin/tenants).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/admin/tenants/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/admin/tenants/agent-contract` |
| Readiness | `GET /api/v1/masks/admin/tenants/readiness` |
| Rollout-Route | `/mask-rollout/admin__tenants/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/tenants/{entity_id}`

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Tenants {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `admin/users` — Users

**Zweck:** Stamm- und Fachmaske fuer Users (admin/users).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/admin/users/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/admin/users/agent-contract` |
| Readiness | `GET /api/v1/masks/admin/users/readiness` |
| Rollout-Route | `/mask-rollout/admin__users/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/admin/benutzer/{entity_id}`

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Users {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `admin/webhooks-liste` — Webhooks

**Zweck:** Webhooks: Eintraege finden und Details oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/admin/webhooks-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/admin/webhooks-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/admin/webhooks-liste/readiness` |
| Rollout-Route | `/mask-rollout/admin__webhooks-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/webhooks`

**Beispiel-Prompts:**

- Welche offenen Webhooks?
- Zeige aktuelle Webhooks.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `admin/workflow-editor` — Workflow editor

**Zweck:** Stamm- und Fachmaske fuer Workflow editor (admin/workflow-editor).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/admin/workflow-editor/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/admin/workflow-editor/agent-contract` |
| Readiness | `GET /api/v1/masks/admin/workflow-editor/readiness` |
| Rollout-Route | `/mask-rollout/admin__workflow-editor/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/workflow/runtime/instances/{entity_id}`

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Workflow editor {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `admin/zeitachsen-editor` — Zeitachsen editor

**Zweck:** Stamm- und Fachmaske fuer Zeitachsen editor (admin/zeitachsen-editor).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/admin/zeitachsen-editor/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/admin/zeitachsen-editor/agent-contract` |
| Readiness | `GET /api/v1/masks/admin/zeitachsen-editor/readiness` |
| Rollout-Route | `/mask-rollout/admin__zeitachsen-editor/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/workflow/cockpit/processes/{entity_id}`

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Zeitachsen editor {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

## Domäne: agrar

### `agrar/annahme-abrechnung` — Annahme abrechnung

**Zweck:** Stamm- und Fachmaske fuer Annahme abrechnung (agrar/annahme-abrechnung).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/annahme-abrechnung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/annahme-abrechnung/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/annahme-abrechnung/readiness` |
| Rollout-Route | `/mask-rollout/agrar__annahme-abrechnung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/self-billing/harvest-acceptance/{entity_id}`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Annahme abrechnung {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `agrar/biostimulanzien-liste` — Biostimulanzien

**Zweck:** Biostimulanzien und Agrarprodukte mit Zulassung und Verfuegbarkeit finden.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/biostimulanzien-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/biostimulanzien-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/biostimulanzien-liste/readiness` |
| Rollout-Route | `/mask-rollout/agrar__biostimulanzien-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/agrar/biostimulanzien`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Biostimulanzien sind aktiv?
- Welche Zulassungen laufen ab?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `agrar/bodenproben-liste` — Bodenproben

**Zweck:** Bodenproben finden und Ergebnisse oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/bodenproben-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/bodenproben-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/bodenproben-liste/readiness` |
| Rollout-Route | `/mask-rollout/agrar__bodenproben-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/labor/proben`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Proben warten auf Labor?
- Zeige Proben fuer Schlag X.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `agrar/daily-prices` — Daily prices

**Zweck:** Daily prices mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/daily-prices/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/daily-prices/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/daily-prices/readiness` |
| Rollout-Route | `/mask-rollout/agrar__daily-prices/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/daily-prices`
- `items` → `/api/v1/agrar/daily-prices`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige offene Daily prices.
- Was ist in Daily prices faellig?

---

### `agrar/duenger` — Duenger

**Zweck:** Duenger-Stammdaten: Naehrstoffgehalte, Verwendungshistorie und Preise fuer Duengungsplanung.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/duenger/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/duenger/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/duenger/readiness` |
| Rollout-Route | `/mask-rollout/agrar__duenger/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/duenger/{entity_id}`
- `verwendung` → `/api/v1/masks/agrar/duenger/entity/{entity_id}/tabs/verwendung`
- `preise` → `/api/v1/masks/agrar/duenger/entity/{entity_id}/tabs/preise`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Naehrstoffgehalte hat Duenger {entity_id}?
- Zeige die Preisentwicklung von Duenger {entity_id}.

**Sensible Felder:** `vk_preis`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `agrar/duenger-liste` — Duenger

**Zweck:** Duengemittel mit Naehrstoffgehalten finden, oeffnen und nicht mehr gefuehrte deaktivieren.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/duenger-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/duenger-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/duenger-liste/readiness` |
| Rollout-Route | `/mask-rollout/agrar__duenger-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/agrar/duenger/`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Stickstoffduenger fuehren wir?
- Welche Duenger sind wassergefaehrdend?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `neu` | Neuer Duenger | safe | nein | `Oeffnet die Anlage; Rechte prueft deren Anlageweg.` |
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `agrar/duenger-rechner` — Duenger rechner

**Zweck:** Duenger rechner mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/duenger-rechner/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/duenger-rechner/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/duenger-rechner/readiness` |
| Rollout-Route | `/mask-rollout/agrar__duenger-rechner/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/duenger/stats/overview`
- `items` → `/api/v1/agrar/duenger/stats/overview`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige offene Duenger rechner.
- Was ist in Duenger rechner faellig?

---

### `agrar/ernte-annahme-abrechnung` — Ernte annahme abrechnung

**Zweck:** Stamm- und Fachmaske fuer Ernte annahme abrechnung (agrar/ernte-annahme-abrechnung).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/ernte-annahme-abrechnung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/ernte-annahme-abrechnung/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/ernte-annahme-abrechnung/readiness` |
| Rollout-Route | `/mask-rollout/agrar__ernte-annahme-abrechnung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/harvest-acceptance/{entity_id}`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Ernte annahme abrechnung {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `agrar/ernte-annahme-energiemais-liste` — Ernte Annahme Energiemais

**Zweck:** Energiemais-Ernten in der Annahme verfolgen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/ernte-annahme-energiemais-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/ernte-annahme-energiemais-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/ernte-annahme-energiemais-liste/readiness` |
| Rollout-Route | `/mask-rollout/agrar__ernte-annahme-energiemais-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/agrar/ernte`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Energiemais-Lieferungen sind offen?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `agrar/ernte-kampagne-erfassung` — Ernte kampagne erfassung

**Zweck:** Ernte kampagne erfassung mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/ernte-kampagne-erfassung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/ernte-kampagne-erfassung/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/ernte-kampagne-erfassung/readiness` |
| Rollout-Route | `/mask-rollout/agrar__ernte-kampagne-erfassung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/ernte-kampagnen/tenant/{tenant_id}`
- `items` → `/api/v1/ernte-kampagnen/tenant/{tenant_id}`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige offene Ernte kampagne erfassung.
- Was ist in Ernte kampagne erfassung faellig?

---

### `agrar/ernte-liste` — Ernte

**Zweck:** Ernten nach Schlag und Kultur verfolgen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/ernte-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/ernte-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/ernte-liste/readiness` |
| Rollout-Route | `/mask-rollout/agrar__ernte-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/agrar/ernte`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Ernten laufen heute?
- Welche Schlaege sind abgeschlossen?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `neu` | Ernte erfassen | safe | nein | `Oeffnet die Anlage; Rechte prueft deren Anlageweg.` |
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `agrar/ernte-qualitaetsfreigabe` — Ernte qualitaetsfreigabe

**Zweck:** Ernte qualitaetsfreigabe mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/ernte-qualitaetsfreigabe/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/ernte-qualitaetsfreigabe/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/ernte-qualitaetsfreigabe/readiness` |
| Rollout-Route | `/mask-rollout/agrar__ernte-qualitaetsfreigabe/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/harvest-acceptance/`
- `items` → `/api/v1/agrar/harvest-acceptance/`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige offene Ernte qualitaetsfreigabe.
- Was ist in Ernte qualitaetsfreigabe faellig?

---

### `agrar/ernte/kampagnenabschluss` — Kampagnenabschluss

**Zweck:** Kampagnenabschluss mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/ernte/kampagnenabschluss/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/ernte/kampagnenabschluss/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/ernte/kampagnenabschluss/readiness` |
| Rollout-Route | `/mask-rollout/agrar__ernte__kampagnenabschluss/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/ernte-kampagnen/tenant/{tenant_id}`
- `items` → `/api/v1/ernte-kampagnen/tenant/{tenant_id}`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige offene Kampagnenabschluss.
- Was ist in Kampagnenabschluss faellig?

---

### `agrar/feed-advice` — Fuetterungsberatung

**Zweck:** Aufgabenorientierter Einstieg in Planung, Freigabe, Stallausfuehrung und Controlling der Fuetterung.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/feed-advice/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/feed-advice/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/feed-advice/readiness` |
| Rollout-Route | `/mask-rollout/agrar__feed-advice/:entityId` |
| Adapter | `native` (temporary=nein) |

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Ration braucht heute Aufmerksamkeit?
- Wo fehlen aktuelle Analysen oder ausreichend Bestand?
- Zeige mir den schnellsten Weg zur heutigen Fuetterung.

**Sensible Felder:** `futterkosten, milchleistung`

---

### `agrar/feed-controlling` — Fuetterungscontrolling

**Zweck:** Aufnahme, Kosten, Milch/ECM, Stickstoff und Methan je Tiergruppe im Zeitverlauf vergleichen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/feed-controlling/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/feed-controlling/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/feed-controlling/readiness` |
| Rollout-Route | `/mask-rollout/agrar__feed-controlling/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `series` → `/api/v1/agrar/rations-optimization/controlling/series`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Gruppe weicht bei der Aufnahme ab?
- Wie entwickeln sich ECM und Futterkosten?

**Sensible Felder:** `actual_cost_eur_cow`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `record_observation` | Tageswerte erfassen | safe | nein | `—` |

---

### `agrar/feed-readiness` — Futterversorgung

**Zweck:** Planbedarf, Sicherheitsreserve und Bestandsreichweite erklaerbar vergleichen und Unterdeckungen kontrolliert an den Einkauf geben.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/feed-readiness/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/feed-readiness/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/feed-readiness/readiness` |
| Rollout-Route | `/mask-rollout/agrar__feed-readiness/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `materials` → `/api/v1/agrar/rations-optimization/feeding/supply`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Futtermittel reichen weniger als 14 Tage?
- Welche Unterdeckungen sind wegen unbekannter Handelseinheiten noch nicht uebergabefaehig?

**Sensible Felder:** `stock_kg`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `create_handoff` | An Einkauf uebergeben | moderate | nein | `—` |
| `open_inventory` | Bestaende pflegen | safe | nein | `—` |

---

### `agrar/feeding-actuals` — Komponentenbezogene Ist-Fuetterung

**Zweck:** Komponentenabweichungen und ihre Kosten-/Naehrstofffolgen planversionsgebunden erklaeren.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/feeding-actuals/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/feeding-actuals/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/feeding-actuals/readiness` |
| Rollout-Route | `/mask-rollout/agrar__feeding-actuals/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `actuals` → `/api/v1/agrar/rations-optimization/feeding/actuals/components`
- `findings` → `/api/v1/agrar/rations-optimization/feeding/actuals/findings`
- `measures` → `/api/v1/agrar/rations-optimization/feeding/actuals/measures`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Komponenten wurden heute ueberdosiert?
- Bei welchen Ist-Fuetterungen fehlen Preise oder Naehrstoffwerte?

**Sensible Felder:** `comment, value_consequences`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export_csv` | CSV exportieren | safe | nein | `—` |
| `create_measure` | Massnahme aus Abweichung | moderate | nein | `—` |
| `configure_threshold` | Schwellen konfigurieren | moderate | nein | `—` |
| `open_mobile` | Ist-Fuetterung erfassen | safe | nein | `—` |

---

### `agrar/feeding-business` — Fuetterungsbetrieb

**Zweck:** Die naechste fachliche Fuetterungsentscheidung aus belastbarer Datenlage ableiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/feeding-business/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/feeding-business/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/feeding-business/readiness` |
| Rollout-Route | `/mask-rollout/agrar__feeding-business/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/rations-optimization/feeding/businesses/{entity_id}/overview`
- `groups` → `/api/v1/agrar/rations-optimization/feeding/businesses/{entity_id}/groups`
- `rations` → `/api/v1/agrar/rations-optimization/feeding/businesses/{entity_id}/rations`
- `findings` → `/api/v1/agrar/rations-optimization/feeding/businesses/{entity_id}/findings`
- `templates` → `/api/v1/agrar/rations-optimization/feeding/businesses/{entity_id}/ration-templates`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Ration ist blockiert?
- Wo fehlt eine belastbare Analyse?
- Welche Befunde sind kritisch?

**Sensible Felder:** `business_partner_id, preferences, snapshot_checksum`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `create_template` | Vorlage anlegen | safe | nein | `—` |
| `apply_template` | Vorlage anwenden | safe | nein | `—` |

---

### `agrar/feeding-businesses` — Fuetterungsbetriebe

**Zweck:** Autorisierte Fuetterungsbetriebe und ihre Beratungsreife steuern.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/feeding-businesses/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/feeding-businesses/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/feeding-businesses/readiness` |
| Rollout-Route | `/mask-rollout/agrar__feeding-businesses/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `businesses` → `/api/v1/agrar/rations-optimization/feeding/businesses`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Betriebe betreue ich?
- Wo fehlen Herden oder Tiergruppen?

**Sensible Felder:** `business_partner_id, preferences`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `create_business` | Betrieb anlegen | safe | nein | `—` |

---

### `agrar/feeding-group` — Tiergruppe

**Zweck:** Tiergruppenparameter und ihre zeitliche Herkunft sicher pflegen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/feeding-group/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/feeding-group/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/feeding-group/readiness` |
| Rollout-Route | `/mask-rollout/agrar__feeding-group/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/rations-optimization/lifecycle/groups/{entity_id}`
- `history` → `/api/v1/agrar/rations-optimization/lifecycle/groups/{entity_id}/history`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige die aktuelle Leistung der Tiergruppe.
- Welche Parameter wurden zuletzt geaendert?

**Sensible Felder:** `business_id, herd_id, external_ref`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit_group` | Tiergruppe bearbeiten | safe | nein | `—` |

---

### `agrar/feeding-plan` — Fuetterungsplan

**Zweck:** Eine publizierte Mischanweisung sicher ausfuehren und ihre Herkunft nachweisen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/feeding-plan/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/feeding-plan/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/feeding-plan/readiness` |
| Rollout-Route | `/mask-rollout/agrar__feeding-plan/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/rations-optimization/feeding/plans/{entity_id}`
- `instructions` → `/api/v1/agrar/rations-optimization/feeding/plans/{entity_id}/instructions`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Menge kommt als Naechstes?
- Ist dieser Plan noch aktuell?
- Warum wurde gerundet?

**Sensible Felder:** `source_ration_version_id, published_by`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `print_plan` | Drucken / als PDF speichern | safe | nein | `—` |
| `open_mobile` | Mobile Stallansicht | safe | nein | `—` |

---

### `agrar/feeding-reference-data` — Naehrstoffe und Einheiten

**Zweck:** Einheiten, Bezugsbasen und Naehrstoffherkunft fuer Berechnung und Beratung erklaerbar machen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/feeding-reference-data/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/feeding-reference-data/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/feeding-reference-data/readiness` |
| Rollout-Route | `/mask-rollout/agrar__feeding-reference-data/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `nutrients` → `/api/v1/agrar/rations-optimization/reference-data/nutrients`
- `units` → `/api/v1/agrar/rations-optimization/reference-data/units`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- In welcher Einheit wird Rohprotein bewertet?
- Welche Naehrstoffe sind auf TM bezogen?

---

### `agrar/feldbuch-flurstueck-kataster-liste` — Flurstueck-Kataster

**Zweck:** Flurstuecke im Kataster finden.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/feldbuch-flurstueck-kataster-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/feldbuch-flurstueck-kataster-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/feldbuch-flurstueck-kataster-liste/readiness` |
| Rollout-Route | `/mask-rollout/agrar__feldbuch-flurstueck-kataster-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/agrar/schlaege`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Flurstuecke gehoeren zu Schlag X?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `agrar/feldbuch-massnahmen-liste` — Feldbuch-Massnahmen

**Zweck:** Feldbuch-Massnahmen: Eintraege finden und Details oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/feldbuch-massnahmen-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/feldbuch-massnahmen-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/feldbuch-massnahmen-liste/readiness` |
| Rollout-Route | `/mask-rollout/agrar__feldbuch-massnahmen-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/agrar/feldbuch/massnahmen`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche offenen Feldbuch-Massnahmen?
- Zeige aktuelle Feldbuch-Massnahmen.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `agrar/feldbuch-schlagkartei-liste` — Schlagkartei

**Zweck:** Schlagkartei: Eintraege finden und Details oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/feldbuch-schlagkartei-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/feldbuch-schlagkartei-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/feldbuch-schlagkartei-liste/readiness` |
| Rollout-Route | `/mask-rollout/agrar__feldbuch-schlagkartei-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/agrar/schlaege`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche offenen Schlagkartei?
- Zeige aktuelle Schlagkartei.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `agrar/futter/mischfutter-optimierung` — Mischfutter optimierung

**Zweck:** Mischfutter optimierung mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/futter/mischfutter-optimierung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/futter/mischfutter-optimierung/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/futter/mischfutter-optimierung/readiness` |
| Rollout-Route | `/mask-rollout/agrar__futter__mischfutter-optimierung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/rations-optimization/controlling/series`
- `items` → `/api/v1/agrar/rations-optimization/controlling/series`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige offene Mischfutter optimierung.
- Was ist in Mischfutter optimierung faellig?

---

### `agrar/harvest-controls` — Ernte-Abrechnung: Vertragsregeln und Freigaben

**Zweck:** Vertragsregeln und konkrete Ernte-Abrechnungsfassungen nachvollziehbar prüfen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/harvest-controls/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/harvest-controls/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/harvest-controls/readiness` |
| Rollout-Route | `/mask-rollout/agrar__harvest-controls/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `rules` → `/api/v1/agrar/harvest-acceptance/settlement-controls/rules`
- `acceptances` → `/api/v1/agrar/harvest-acceptance/settlement-controls/choices/acceptance`
- `customers` → `/api/v1/agrar/harvest-acceptance/settlement-controls/choices/customer`
- `articles` → `/api/v1/agrar/harvest-acceptance/settlement-controls/choices/article`
- `contracts` → `/api/v1/agrar/harvest-acceptance/settlement-controls/choices/contract`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Sensible Felder:** `customer_id, source_reference`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Annahme und Nachweise laden | safe | nein | `—` |
| `create_rule` | Regelversion erstellen | moderate | nein | `/api/v1/agrar/harvest-acceptance/settlement-controls/rules` |
| `approve_rule` | Regel genehmigen | high | ja | `/api/v1/agrar/harvest-acceptance/settlement-controls/rules/{version_id}/approve` |
| `revoke_rule` | Regelgenehmigung widerrufen | high | ja | `/api/v1/agrar/harvest-acceptance/settlement-controls/rules/{version_id}/revoke` |
| `bind_rule` | Regel an Annahme binden | moderate | nein | `/api/v1/agrar/harvest-acceptance/settlement-controls/acceptances/{acceptance_id}/bind-rule` |
| `attest` | Messnachweis bestätigen | moderate | nein | `/api/v1/agrar/harvest-acceptance/settlement-controls/acceptances/{acceptance_id}/attest-measurement` |
| `calculate` | Verbindlich berechnen | moderate | nein | `/api/v1/agrar/harvest-acceptance/{acceptance_id}/calculate` |
| `approve_calculation` | Berechnungsfassung genehmigen | high | ja | `/api/v1/agrar/harvest-acceptance/settlement-controls/acceptances/{acceptance_id}/approve-calculation` |
| `release` | Gutschrift und Wareneingang erzeugen | high | ja | `/api/v1/agrar/harvest-acceptance/{acceptance_id}/release?release_status=final&create_stock_movement=true&create_credit_note=true` |

---

### `agrar/harvest-settlement` — Ernte-Abrechnung

**Zweck:** Ernte-Abrechnung: Erzeuger-Abrechnung mit Lieferschein-Positionen, Qualitaets-Abzuegen und Gesamtbetrag fuer Agrar-Buchhalter.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/harvest-settlement/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/harvest-settlement/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/harvest-settlement/readiness` |
| Rollout-Route | `/mask-rollout/agrar__harvest-settlement/:entityId` |
| Adapter | `native` (temporary=nein) |

**Summary:** `/api/v1/mask-rollouts/agrar/harvest-settlement/{entity_id}/screen-summary`

**Data Sources:**

- `entity` → `/api/v1/agrar/settlements/{entity_id}`
- `positionen` → `/api/v1/mask-rollouts/agrar/harvest-settlement/{entity_id}/tabs/positionen`
- `abzuege` → `/api/v1/mask-rollouts/agrar/harvest-settlement/{entity_id}/tabs/abzuege`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Was ist der Gesamtbetrag und Status der Ernte-Abrechnung {entity_id}?
- Zeige alle Lieferschein-Positionen und Qualitaets-Abzuege von Abrechnung {entity_id}.

**Sensible Felder:** `gesamtbetrag`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `drucken` | Abrechnung drucken | safe | nein | `/api/v1/agrar/settlements/{entity_id}/actions/drucken` |

---

### `agrar/kalkulation/deckungsbeitrag` — Deckungsbeitrag

**Zweck:** Deckungsbeitrag mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/kalkulation/deckungsbeitrag/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/kalkulation/deckungsbeitrag/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/kalkulation/deckungsbeitrag/readiness` |
| Rollout-Route | `/mask-rollout/agrar__kalkulation__deckungsbeitrag/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/rations-optimization/controlling/series`
- `items` → `/api/v1/agrar/rations-optimization/controlling/series`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige offene Deckungsbeitrag.
- Was ist in Deckungsbeitrag faellig?

---

### `agrar/kontrakt-detail` — Kontrakt

**Zweck:** Kontraktdetail Agrar.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/kontrakt-detail/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/kontrakt-detail/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/kontrakt-detail/readiness` |
| Rollout-Route | `/mask-rollout/agrar__kontrakt-detail/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/kontrakte/{entity_id}`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Restmenge hat Kontrakt {entity_id}?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `agrar/kontrakte` — Kontrakt

**Zweck:** Agrar-Kontrakt-Cockpit: Positionen (Sorte, Menge, Preis) und Umsaetze fuer Erzeuger-Vertragsmanagement.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/kontrakte/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/kontrakte/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/kontrakte/readiness` |
| Rollout-Route | `/mask-rollout/agrar__kontrakte/:entityId` |
| Adapter | `native` (temporary=nein) |

**Summary:** `/api/v1/kontrakte/{contract_id}/screen-summary`

**Data Sources:**

- `entity` → `/api/v1/kontrakte/{entity_id}`
- `positionen` → `/api/v1/kontrakte/{entity_id}/tabs/positionen`
- `umsaetze` → `/api/v1/kontrakte/{entity_id}/tabs/umsaetze`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Was ist der Erfuellungsstand von Kontrakt {entity_id}?
- Zeige alle Lieferschein-Umsaetze fuer Kontrakt {entity_id}.
- Welche Sorten und Mengen sind in Kontrakt {entity_id} vereinbart?

**Sensible Felder:** `preis`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | moderate | nein | `/api/v1/kontrakte/{entity_id}/actions/bearbeiten` |

---

### `agrar/kontrakte/formular` — Formular

**Zweck:** Stamm- und Fachmaske fuer Formular (agrar/kontrakte/formular).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/kontrakte/formular/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/kontrakte/formular/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/kontrakte/formular/readiness` |
| Rollout-Route | `/mask-rollout/agrar__kontrakte__formular/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/kontrakte/{entity_id}`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Formular {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `/api/v1/kontrakte/{entity_id}/actions/bearbeiten` |

---

### `agrar/kultur-stamm-liste` — Kulturen

**Zweck:** Kulturen im Stamm finden.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/kultur-stamm-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/kultur-stamm-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/kultur-stamm-liste/readiness` |
| Rollout-Route | `/mask-rollout/agrar__kultur-stamm-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/agrar/kulturen`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Kulturen sind aktiv?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `agrar/kulturpflanzen-liste` — Kulturpflanzen

**Zweck:** Kulturen nach Flaeche und Deckungsbeitrag vergleichen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/kulturpflanzen-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/kulturpflanzen-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/kulturpflanzen-liste/readiness` |
| Rollout-Route | `/mask-rollout/agrar__kulturpflanzen-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/agrar/kulturen`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Kulturen haben den hoechsten Deckungsbeitrag?
- Wie viel Flaeche ist Weizen?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `agrar/lieferschein-erstellen` — Lieferschein erstellen

**Zweck:** Stamm- und Fachmaske fuer Lieferschein erstellen (agrar/lieferschein-erstellen).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/lieferschein-erstellen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/lieferschein-erstellen/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/lieferschein-erstellen/readiness` |
| Rollout-Route | `/mask-rollout/agrar__lieferschein-erstellen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/einkauf/lieferscheine/{entity_id}`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Lieferschein erstellen {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `agrar/maschinen-auslastung-liste` — Maschinenauslastung

**Zweck:** Maschinenauslastung im Blick behalten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/maschinen-auslastung-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/maschinen-auslastung-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/maschinen-auslastung-liste/readiness` |
| Rollout-Route | `/mask-rollout/agrar__maschinen-auslastung-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/agrar/maschinen`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Maschinen sind in Wartung?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `agrar/maschinen/formular` — Formular

**Zweck:** Stamm- und Fachmaske fuer Formular (agrar/maschinen/formular).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/maschinen/formular/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/maschinen/formular/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/maschinen/formular/readiness` |
| Rollout-Route | `/mask-rollout/agrar__maschinen__formular/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/maschinen/{entity_id}`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Formular {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `agrar/maschinen/wartung` — Wartung

**Zweck:** Wartung mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/maschinen/wartung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/maschinen/wartung/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/maschinen/wartung/readiness` |
| Rollout-Route | `/mask-rollout/agrar__maschinen__wartung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/maschinen`
- `items` → `/api/v1/agrar/maschinen`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige offene Wartung.
- Was ist in Wartung faellig?

---

### `agrar/nachhaltigkeit-eudr-liste` — EUDR Nachhaltigkeit

**Zweck:** EUDR-Sorgfaltserklaerungen verfolgen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/nachhaltigkeit-eudr-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/nachhaltigkeit-eudr-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/nachhaltigkeit-eudr-liste/readiness` |
| Rollout-Route | `/mask-rollout/agrar__nachhaltigkeit-eudr-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/eudr/sorgfaltserklaerungen`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Erklaerungen sind offen?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `agrar/nawaro-erntemeldung` — Nawaro erntemeldung

**Zweck:** Nawaro erntemeldung mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/nawaro-erntemeldung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/nawaro-erntemeldung/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/nawaro-erntemeldung/readiness` |
| Rollout-Route | `/mask-rollout/agrar__nawaro-erntemeldung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/nawaro/print-notifications`
- `items` → `/api/v1/agrar/nawaro/print-notifications`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige offene Nawaro erntemeldung.
- Was ist in Nawaro erntemeldung faellig?

---

### `agrar/nawaro-kaskade` — Nawaro kaskade

**Zweck:** Nawaro kaskade mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/nawaro-kaskade/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/nawaro-kaskade/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/nawaro-kaskade/readiness` |
| Rollout-Route | `/mask-rollout/agrar__nawaro-kaskade/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/nawaro/area-sheets`
- `items` → `/api/v1/agrar/nawaro/area-sheets`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige offene Nawaro kaskade.
- Was ist in Nawaro kaskade faellig?

---

### `agrar/nawaro-vertraege` — Nawaro vertraege

**Zweck:** Nawaro vertraege mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/nawaro-vertraege/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/nawaro-vertraege/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/nawaro-vertraege/readiness` |
| Rollout-Route | `/mask-rollout/agrar__nawaro-vertraege/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/nawaro/contract-sheets`
- `items` → `/api/v1/agrar/nawaro/contract-sheets`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige offene Nawaro vertraege.
- Was ist in Nawaro vertraege faellig?

---

### `agrar/partie-historie` — Partie historie

**Zweck:** Stamm- und Fachmaske fuer Partie historie (agrar/partie-historie).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/partie-historie/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/partie-historie/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/partie-historie/readiness` |
| Rollout-Route | `/mask-rollout/agrar__partie-historie/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/saatzucht/partien/{entity_id}`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Partie historie {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `agrar/pflanzenschutz-applikationen-liste` — Pflanzenschutz-Applikationen

**Zweck:** Pflanzenschutz-Applikationen dokumentieren und finden.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/pflanzenschutz-applikationen-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/pflanzenschutz-applikationen-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/pflanzenschutz-applikationen-liste/readiness` |
| Rollout-Route | `/mask-rollout/agrar__pflanzenschutz-applikationen-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/agrar/feldbuch/massnahmen`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Applikationen diese Woche?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `agrar/pflanzenschutz-liste` — Pflanzenschutz liste

**Zweck:** Pflanzenschutz liste mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/pflanzenschutz-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/pflanzenschutz-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/pflanzenschutz-liste/readiness` |
| Rollout-Route | `/mask-rollout/agrar__pflanzenschutz-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/psm/`
- `items` → `/api/v1/agrar/psm/`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige offene Pflanzenschutz liste.
- Was ist in Pflanzenschutz liste faellig?

---

### `agrar/pflanzenschutz-rechner` — Pflanzenschutz rechner

**Zweck:** Stamm- und Fachmaske fuer Pflanzenschutz rechner (agrar/pflanzenschutz-rechner).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/pflanzenschutz-rechner/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/pflanzenschutz-rechner/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/pflanzenschutz-rechner/readiness` |
| Rollout-Route | `/mask-rollout/agrar__pflanzenschutz-rechner/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/schlaege/{entity_id}`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Pflanzenschutz rechner {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `agrar/planung/duengeplanung` — Duengeplanung

**Zweck:** Duengeplanung mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/planung/duengeplanung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/planung/duengeplanung/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/planung/duengeplanung/readiness` |
| Rollout-Route | `/mask-rollout/agrar__planung__duengeplanung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/feldbuch/duengemittelmengen`
- `items` → `/api/v1/agrar/feldbuch/duengemittelmengen`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige offene Duengeplanung.
- Was ist in Duengeplanung faellig?

---

### `agrar/planung/fruchtfolge` — Fruchtfolge

**Zweck:** Fruchtfolge mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/planung/fruchtfolge/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/planung/fruchtfolge/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/planung/fruchtfolge/readiness` |
| Rollout-Route | `/mask-rollout/agrar__planung__fruchtfolge/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/kulturen`
- `items` → `/api/v1/agrar/kulturen`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige offene Fruchtfolge.
- Was ist in Fruchtfolge faellig?

---

### `agrar/probenehmer-stamm` — Probenehmer stamm

**Zweck:** Stamm- und Fachmaske fuer Probenehmer stamm (agrar/probenehmer-stamm).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/probenehmer-stamm/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/probenehmer-stamm/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/probenehmer-stamm/readiness` |
| Rollout-Route | `/mask-rollout/agrar__probenehmer-stamm/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/articles/{entity_id}`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Probenehmer stamm {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `/api/v1/articles/{entity_id}/actions/bearbeiten` |

---

### `agrar/psm` — PSM

**Zweck:** PSM-Stammdaten fuer Agrar.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/psm/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/psm/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/psm/readiness` |
| Rollout-Route | `/mask-rollout/agrar__psm/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/psm/{entity_id}`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Zulassung hat PSM {entity_id}?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `agrar/psm-abgabedokumentation-liste` — PSM Abgabedokumentation

**Zweck:** PSM-Abgabedokumentation finden.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/psm-abgabedokumentation-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/psm-abgabedokumentation-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/psm-abgabedokumentation-liste/readiness` |
| Rollout-Route | `/mask-rollout/agrar__psm-abgabedokumentation-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/agrar/psm/`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Abgaben fehlen noch?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `agrar/psm-beratung-liste` — PSM Beratung

**Zweck:** PSM-Beratung mit Sortimentsdaten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/psm-beratung-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/psm-beratung-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/psm-beratung-liste/readiness` |
| Rollout-Route | `/mask-rollout/agrar__psm-beratung-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/agrar/psm/`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Mittel fuer Weizen?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `agrar/psm-liste` — Pflanzenschutzmittel

**Zweck:** Pflanzenschutzmittel mit Zulassung und Wirkstoff finden und oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/psm-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/psm-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/psm-liste/readiness` |
| Rollout-Route | `/mask-rollout/agrar__psm-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/agrar/psm/?source=bvl`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Mittel laufen dieses Jahr aus?
- Welche Mittel enthalten Glyphosat?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `neu` | Neues Mittel | safe | nein | `Oeffnet die Anlage; Rechte prueft deren Anlageweg.` |
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `agrar/psm-sachkunde-register-liste` — PSM Sachkunde

**Zweck:** Sachkundenachweise fuer PSM-Abgabe pruefen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/psm-sachkunde-register-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/psm-sachkunde-register-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/psm-sachkunde-register-liste/readiness` |
| Rollout-Route | `/mask-rollout/agrar__psm-sachkunde-register-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/compliance/sachkunde-register`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Nachweise laufen ab?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `agrar/psm-wasserschutz-liste` — Wasserschutz

**Zweck:** Wasserschutzzonen und PSM-Auflagen pruefen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/psm-wasserschutz-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/psm-wasserschutz-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/psm-wasserschutz-liste/readiness` |
| Rollout-Route | `/mask-rollout/agrar__psm-wasserschutz-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/agrar/psm/wasserschutz-zonen`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Zonen sind betroffen?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `agrar/psm/anwendungsprotokoll` — Anwendungsprotokoll

**Zweck:** Anwendungsprotokoll mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/psm/anwendungsprotokoll/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/psm/anwendungsprotokoll/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/psm/anwendungsprotokoll/readiness` |
| Rollout-Route | `/mask-rollout/agrar__psm__anwendungsprotokoll/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/psm/`
- `items` → `/api/v1/agrar/psm/`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige offene Anwendungsprotokoll.
- Was ist in Anwendungsprotokoll faellig?

---

### `agrar/psm/tankmischung` — Tankmischung

**Zweck:** Tankmischung mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/psm/tankmischung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/psm/tankmischung/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/psm/tankmischung/readiness` |
| Rollout-Route | `/mask-rollout/agrar__psm__tankmischung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/psm/monitoring`
- `items` → `/api/v1/agrar/psm/monitoring`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige offene Tankmischung.
- Was ist in Tankmischung faellig?

---

### `agrar/qualitaet/ausnahmen` — Ausnahmen

**Zweck:** Ausnahmen mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/qualitaet/ausnahmen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/qualitaet/ausnahmen/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/qualitaet/ausnahmen/readiness` |
| Rollout-Route | `/mask-rollout/agrar__qualitaet__ausnahmen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/quality-lots`
- `items` → `/api/v1/agrar/quality-lots`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige offene Ausnahmen.
- Was ist in Ausnahmen faellig?

---

### `agrar/qualitaet/laborwerte` — Laborwerte

**Zweck:** Laborwerte mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/qualitaet/laborwerte/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/qualitaet/laborwerte/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/qualitaet/laborwerte/readiness` |
| Rollout-Route | `/mask-rollout/agrar__qualitaet__laborwerte/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/quality-lots`
- `items` → `/api/v1/agrar/quality-lots`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige offene Laborwerte.
- Was ist in Laborwerte faellig?

---

### `agrar/qualitaet/mykotoxine` — Mykotoxine

**Zweck:** Mykotoxine mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/qualitaet/mykotoxine/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/qualitaet/mykotoxine/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/qualitaet/mykotoxine/readiness` |
| Rollout-Route | `/mask-rollout/agrar__qualitaet__mykotoxine/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/labor/proben`
- `items` → `/api/v1/labor/proben`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige offene Mykotoxine.
- Was ist in Mykotoxine faellig?

---

### `agrar/ration` — Rationsfreigabe

**Zweck:** Eine Rationsversion pruefen, freigeben, terminieren, aktivieren oder revisionssicher beenden.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/ration/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/ration/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/ration/readiness` |
| Rollout-Route | `/mask-rollout/agrar__ration/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/rations-optimization/lifecycle/rations/{entity_id}`
- `versions` → `/api/v1/agrar/rations-optimization/lifecycle/rations/{entity_id}/versions`
- `audit` → `/api/v1/agrar/rations-optimization/lifecycle/rations/{entity_id}/audit`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Warum wurde diese Ration freigegeben?
- Wann beginnt die Fuetterung dieser Version?

**Sensible Felder:** `snapshot, snapshot_checksum`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `submit_review` | Zur Pruefung | safe | nein | `/api/v1/agrar/rations-optimization/lifecycle/rations/{entity_id}/actions/submit_review` |
| `approve` | Freigeben | moderate | ja | `/api/v1/agrar/rations-optimization/lifecycle/rations/{entity_id}/actions/approve` |
| `schedule` | Fuetterungsbeginn planen | moderate | nein | `/api/v1/agrar/rations-optimization/lifecycle/rations/{entity_id}/actions/schedule` |
| `activate` | Jetzt aktivieren | moderate | ja | `/api/v1/agrar/rations-optimization/lifecycle/rations/{entity_id}/actions/activate` |
| `retire` | Fuetterung beenden | high | ja | `/api/v1/agrar/rations-optimization/lifecycle/rations/{entity_id}/actions/retire` |
| `archive` | Archivieren | high | ja | `/api/v1/agrar/rations-optimization/lifecycle/rations/{entity_id}/actions/archive` |

---

### `agrar/rations-lifecycle` — Rationen und Freigaben

**Zweck:** Rationsversionen nach Tiergruppe, Status und Fuetterungsbeginn steuern.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/rations-lifecycle/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/rations-lifecycle/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/rations-lifecycle/readiness` |
| Rollout-Route | `/mask-rollout/agrar__rations-lifecycle/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `rations` → `/api/v1/agrar/rations-optimization/lifecycle/rations`
- `groups` → `/api/v1/agrar/rations-optimization/lifecycle/groups`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Rationen warten auf Freigabe?
- Welche Ration ist je Tiergruppe aktiv?

**Sensible Felder:** `snapshot_checksum`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `plan_ration` | Neue Ration planen | safe | nein | `—` |
| `create_group` | Tiergruppe anlegen | safe | nein | `—` |

---

### `agrar/rechnungen-erstellen` — Rechnungen erstellen

**Zweck:** Stamm- und Fachmaske fuer Rechnungen erstellen (agrar/rechnungen-erstellen).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/rechnungen-erstellen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/rechnungen-erstellen/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/rechnungen-erstellen/readiness` |
| Rollout-Route | `/mask-rollout/agrar__rechnungen-erstellen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/self-billing/{entity_id}`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Rechnungen erstellen {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `agrar/saatgut` — Saatgut

**Zweck:** Saatgut-Stammdaten: Sorteninfo, Lagerbestaende und Anbauvertraege fuer Saatgutplanung.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/saatgut/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/saatgut/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/saatgut/readiness` |
| Rollout-Route | `/mask-rollout/agrar__saatgut/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/saatgut/{entity_id}`
- `lagerbestaende` → `/api/v1/masks/agrar/saatgut/entity/{entity_id}/tabs/lagerbestaende`
- `vertraege` → `/api/v1/masks/agrar/saatgut/entity/{entity_id}/tabs/vertraege`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Lagerbestaende hat Saatgut {entity_id}?
- Zeige alle Anbauvertraege fuer Saatgut {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `agrar/saatgut-bestellungen-liste` — Saatgut-Bestellungen

**Zweck:** Saatgut-Bestellungen verfolgen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/saatgut-bestellungen-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/saatgut-bestellungen-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/saatgut-bestellungen-liste/readiness` |
| Rollout-Route | `/mask-rollout/agrar__saatgut-bestellungen-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/agrar/saatgut/`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Bestellungen sind offen?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `agrar/saatgut-liste` — Saatgut

**Zweck:** Saatgut-Sorten mit Zulassung, Preis und verfuegbarem Bestand finden.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/saatgut-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/saatgut-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/saatgut-liste/readiness` |
| Rollout-Route | `/mask-rollout/agrar__saatgut-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/agrar/saatgut/`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Weizensorten haben BSA-Zulassung?
- Welches Saatgut ist knapp?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `neu` | Neues Saatgut | safe | nein | `Oeffnet die Anlage; Rechte prueft deren Anlageweg.` |
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `agrar/saatgut-sortenregister-liste` — Sortenregister

**Zweck:** Sortenregister durchsuchen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/saatgut-sortenregister-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/saatgut-sortenregister-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/saatgut-sortenregister-liste/readiness` |
| Rollout-Route | `/mask-rollout/agrar__saatgut-sortenregister-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/agrar/varieties/`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Sorten sind aktiv?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `agrar/saatgut/abrechnung` — Abrechnung

**Zweck:** Stamm- und Fachmaske fuer Abrechnung (agrar/saatgut/abrechnung).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/saatgut/abrechnung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/saatgut/abrechnung/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/saatgut/abrechnung/readiness` |
| Rollout-Route | `/mask-rollout/agrar__saatgut__abrechnung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/saatgut/{entity_id}`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Abrechnung {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `agrar/saatgut/formular` — Formular

**Zweck:** Stamm- und Fachmaske fuer Formular (agrar/saatgut/formular).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/saatgut/formular/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/saatgut/formular/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/saatgut/formular/readiness` |
| Rollout-Route | `/mask-rollout/agrar__saatgut__formular/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/saatgut/{entity_id}`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Formular {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `agrar/saatgut/prognose` — Prognose

**Zweck:** Prognose mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/saatgut/prognose/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/saatgut/prognose/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/saatgut/prognose/readiness` |
| Rollout-Route | `/mask-rollout/agrar__saatgut__prognose/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/saatgut/stats/overview`
- `items` → `/api/v1/agrar/saatgut/stats/overview`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige offene Prognose.
- Was ist in Prognose faellig?

---

### `agrar/saatgut/royalties` — Royalties

**Zweck:** Stamm- und Fachmaske fuer Royalties (agrar/saatgut/royalties).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/saatgut/royalties/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/saatgut/royalties/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/saatgut/royalties/readiness` |
| Rollout-Route | `/mask-rollout/agrar__saatgut__royalties/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/saatgut/{entity_id}`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Royalties {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `agrar/saatgut/vermehrung` — Vermehrung

**Zweck:** Vermehrung mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/saatgut/vermehrung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/saatgut/vermehrung/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/saatgut/vermehrung/readiness` |
| Rollout-Route | `/mask-rollout/agrar__saatgut__vermehrung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/saatzucht/vermehrungsvertraege`
- `items` → `/api/v1/saatzucht/vermehrungsvertraege`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige offene Vermehrung.
- Was ist in Vermehrung faellig?

---

### `agrar/saatzucht-partien-liste` — Saatzucht-Partien

**Zweck:** Saatzucht-Partien: Eintraege finden und Details oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/saatzucht-partien-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/saatzucht-partien-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/saatzucht-partien-liste/readiness` |
| Rollout-Route | `/mask-rollout/agrar__saatzucht-partien-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/saatzucht/partien`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche offenen Saatzucht-Partien?
- Zeige aktuelle Saatzucht-Partien.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `agrar/schlaege-karte-liste` — Schlagkarte

**Zweck:** Schlaege fuer die Kartenansicht laden.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/schlaege-karte-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/schlaege-karte-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/schlaege-karte-liste/readiness` |
| Rollout-Route | `/mask-rollout/agrar__schlaege-karte-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/agrar/schlaege`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige alle Schlaege mit Geometrie.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `agrar/schlaege-kulturhistorie-liste` — Kulturhistorie

**Zweck:** Kulturhistorie der Schlaege einsehen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/schlaege-kulturhistorie-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/schlaege-kulturhistorie-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/schlaege-kulturhistorie-liste/readiness` |
| Rollout-Route | `/mask-rollout/agrar__schlaege-kulturhistorie-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/agrar/schlaege`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Kultur war letztes Jahr auf Schlag X?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `agrar/schlaege-liste` — Schlaege

**Zweck:** Schlaege finden und oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/schlaege-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/schlaege-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/schlaege-liste/readiness` |
| Rollout-Route | `/mask-rollout/agrar__schlaege-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/agrar/schlaege`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Schlaege haben Weizen?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `agrar/schlaege/bodenprobe` — Bodenprobe

**Zweck:** Stamm- und Fachmaske fuer Bodenprobe (agrar/schlaege/bodenprobe).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/schlaege/bodenprobe/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/schlaege/bodenprobe/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/schlaege/bodenprobe/readiness` |
| Rollout-Route | `/mask-rollout/agrar__schlaege__bodenprobe/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/schlaege/{entity_id}`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Bodenprobe {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `agrar/schlaege/duengung` — Duengung

**Zweck:** Stamm- und Fachmaske fuer Duengung (agrar/schlaege/duengung).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/schlaege/duengung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/schlaege/duengung/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/schlaege/duengung/readiness` |
| Rollout-Route | `/mask-rollout/agrar__schlaege__duengung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/schlaege/{entity_id}`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Duengung {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `agrar/schlaege/ernte` — Ernte

**Zweck:** Stamm- und Fachmaske fuer Ernte (agrar/schlaege/ernte).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/schlaege/ernte/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/schlaege/ernte/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/schlaege/ernte/readiness` |
| Rollout-Route | `/mask-rollout/agrar__schlaege__ernte/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/ernte/{entity_id}`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Ernte {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `agrar/schlaege/formular` — Formular

**Zweck:** Stamm- und Fachmaske fuer Formular (agrar/schlaege/formular).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/schlaege/formular/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/schlaege/formular/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/schlaege/formular/readiness` |
| Rollout-Route | `/mask-rollout/agrar__schlaege__formular/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/schlaege/{entity_id}`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Formular {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `agrar/schlaege/pflanzenschutz` — Pflanzenschutz

**Zweck:** Stamm- und Fachmaske fuer Pflanzenschutz (agrar/schlaege/pflanzenschutz).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/schlaege/pflanzenschutz/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/schlaege/pflanzenschutz/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/schlaege/pflanzenschutz/readiness` |
| Rollout-Route | `/mask-rollout/agrar__schlaege__pflanzenschutz/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/schlaege/{entity_id}`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Pflanzenschutz {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `agrar/schlaege/saat` — Saat

**Zweck:** Stamm- und Fachmaske fuer Saat (agrar/schlaege/saat).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/schlaege/saat/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/schlaege/saat/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/schlaege/saat/readiness` |
| Rollout-Route | `/mask-rollout/agrar__schlaege__saat/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/saatgut/{entity_id}`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Saat {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `agrar/sektion-auswahl` — Sektion auswahl

**Zweck:** Sektion auswahl mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/sektion-auswahl/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/sektion-auswahl/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/sektion-auswahl/readiness` |
| Rollout-Route | `/mask-rollout/agrar__sektion-auswahl/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/kunden`
- `items` → `/api/v1/agrar/kunden`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige offene Sektion auswahl.
- Was ist in Sektion auswahl faellig?

---

### `agrar/self-billing` — Self billing

**Zweck:** Stamm- und Fachmaske fuer Self billing (agrar/self-billing).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/self-billing/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/self-billing/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/self-billing/readiness` |
| Rollout-Route | `/mask-rollout/agrar__self-billing/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/self-billing/{entity_id}`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Self billing {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `agrar/silo-belegung` — Silo belegung

**Zweck:** Silo belegung mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/silo-belegung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/silo-belegung/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/silo-belegung/readiness` |
| Rollout-Route | `/mask-rollout/agrar__silo-belegung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/silo/silos`
- `items` → `/api/v1/silo/silos`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige offene Silo belegung.
- Was ist in Silo belegung faellig?

---

### `agrar/silo-qualitaet` — Silo qualitaet

**Zweck:** Silo qualitaet mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/silo-qualitaet/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/silo-qualitaet/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/silo-qualitaet/readiness` |
| Rollout-Route | `/mask-rollout/agrar__silo-qualitaet/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/quality-lots`
- `items` → `/api/v1/agrar/quality-lots`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige offene Silo qualitaet.
- Was ist in Silo qualitaet faellig?

---

### `agrar/silo-trocknung` — Silo trocknung

**Zweck:** Silo trocknung mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/silo-trocknung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/silo-trocknung/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/silo-trocknung/readiness` |
| Rollout-Route | `/mask-rollout/agrar__silo-trocknung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/settlements/drying-rules`
- `items` → `/api/v1/agrar/settlements/drying-rules`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige offene Silo trocknung.
- Was ist in Silo trocknung faellig?

---

### `agrar/soil-samples` — Soil samples

**Zweck:** Soil samples mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/soil-samples/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/soil-samples/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/soil-samples/readiness` |
| Rollout-Route | `/mask-rollout/agrar__soil-samples/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/labor/proben`
- `items` → `/api/v1/labor/proben`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige offene Soil samples.
- Was ist in Soil samples faellig?

---

### `agrar/sorten` — Sorten

**Zweck:** Sorten mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/sorten/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/sorten/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/sorten/readiness` |
| Rollout-Route | `/mask-rollout/agrar__sorten/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/kulturen`
- `items` → `/api/v1/agrar/kulturen`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige offene Sorten.
- Was ist in Sorten faellig?

---

### `agrar/sorten-vermehrung` — Sorten vermehrung

**Zweck:** Stamm- und Fachmaske fuer Sorten vermehrung (agrar/sorten-vermehrung).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/sorten-vermehrung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/sorten-vermehrung/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/sorten-vermehrung/readiness` |
| Rollout-Route | `/mask-rollout/agrar__sorten-vermehrung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/saatzucht/vermehrungsvertraege/{entity_id}`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Sorten vermehrung {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `agrar/trocknungsregeln` — Trocknungsregeln

**Zweck:** Trocknungsregeln mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/trocknungsregeln/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/trocknungsregeln/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/trocknungsregeln/readiness` |
| Rollout-Route | `/mask-rollout/agrar__trocknungsregeln/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/settlements/drying-rules`
- `items` → `/api/v1/agrar/settlements/drying-rules`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige offene Trocknungsregeln.
- Was ist in Trocknungsregeln faellig?

---

### `agrar/umwelt/nitrat` — Nitrat

**Zweck:** Nitrat mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/umwelt/nitrat/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/umwelt/nitrat/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/umwelt/nitrat/readiness` |
| Rollout-Route | `/mask-rollout/agrar__umwelt__nitrat/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/feldbuch/duengebilanz`
- `items` → `/api/v1/agrar/feldbuch/duengebilanz`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige offene Nitrat.
- Was ist in Nitrat faellig?

---

### `agrar/vermehrungsvertraege-liste` — Vermehrungsvertraege

**Zweck:** Vermehrungsvertraege: Eintraege finden und Details oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/vermehrungsvertraege-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/vermehrungsvertraege-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/vermehrungsvertraege-liste/readiness` |
| Rollout-Route | `/mask-rollout/agrar__vermehrungsvertraege-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/saatzucht/vermehrungsvertraege`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche offenen Vermehrungsvertraege?
- Zeige aktuelle Vermehrungsvertraege.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `agrar/vertraege/formular` — Formular

**Zweck:** Stamm- und Fachmaske fuer Formular (agrar/vertraege/formular).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/vertraege/formular/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/vertraege/formular/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/vertraege/formular/readiness` |
| Rollout-Route | `/mask-rollout/agrar__vertraege__formular/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/kontrakte/{entity_id}`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Formular {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `/api/v1/kontrakte/{entity_id}/actions/bearbeiten` |

---

### `agrar/vertrag-kontingente-liste` — Vertrag-Kontingente

**Zweck:** Kontrakt-Kontingente und Restmengen pruefen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/vertrag-kontingente-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/vertrag-kontingente-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/vertrag-kontingente-liste/readiness` |
| Rollout-Route | `/mask-rollout/agrar__vertrag-kontingente-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/kontrakte`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Kontingente sind ausgeschoepft?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `agrar/wetter` — Wetter

**Zweck:** Wetter mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/wetter/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/wetter/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/wetter/readiness` |
| Rollout-Route | `/mask-rollout/agrar__wetter/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/wetter/boden`
- `items` → `/api/v1/agrar/wetter/boden`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige offene Wetter.
- Was ist in Wetter faellig?

---

### `agrar/wiegeschein-detail` — Wiegeschein detail

**Zweck:** Stamm- und Fachmaske fuer Wiegeschein detail (agrar/wiegeschein-detail).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/wiegeschein-detail/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/wiegeschein-detail/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/wiegeschein-detail/readiness` |
| Rollout-Route | `/mask-rollout/agrar__wiegeschein-detail/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/waage/wiegungen/{entity_id}/extended`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Wiegeschein detail {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `annahme/erfassung` — Erfassung

**Zweck:** Stamm- und Fachmaske fuer Erfassung (annahme/erfassung).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/annahme/erfassung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/annahme/erfassung/agent-contract` |
| Readiness | `GET /api/v1/masks/annahme/erfassung/readiness` |
| Rollout-Route | `/mask-rollout/annahme__erfassung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/annahme/warteschlange/{entity_id}`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Erfassung {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `annahme/labor` — Labor

**Zweck:** Stamm- und Fachmaske fuer Labor (annahme/labor).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/annahme/labor/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/annahme/labor/agent-contract` |
| Readiness | `GET /api/v1/masks/annahme/labor/readiness` |
| Rollout-Route | `/mask-rollout/annahme__labor/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/labor/labor-auftraege/{entity_id}`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Labor {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `annahme/lkw-registrierung` — Lkw registrierung

**Zweck:** Stamm- und Fachmaske fuer Lkw registrierung (annahme/lkw-registrierung).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/annahme/lkw-registrierung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/annahme/lkw-registrierung/agent-contract` |
| Readiness | `GET /api/v1/masks/annahme/lkw-registrierung/readiness` |
| Rollout-Route | `/mask-rollout/annahme__lkw-registrierung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/annahme/warteschlange/{entity_id}`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Lkw registrierung {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `annahme/muster` — Muster

**Zweck:** Stamm- und Fachmaske fuer Muster (annahme/muster).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/annahme/muster/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/annahme/muster/agent-contract` |
| Readiness | `GET /api/v1/masks/annahme/muster/readiness` |
| Rollout-Route | `/mask-rollout/annahme__muster/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/annahme/warteschlange/{entity_id}`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Muster {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `annahme/qualitaets-check` — Qualitaets-Check

**Zweck:** Qualitaetsprotokolle vor Freigabe sichten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/annahme/qualitaets-check/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/annahme/qualitaets-check/agent-contract` |
| Readiness | `GET /api/v1/masks/annahme/qualitaets-check/readiness` |
| Rollout-Route | `/mask-rollout/annahme__qualitaets-check/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `protocols` → `/api/v1/agrar/quality-protocols`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Protokolle sind noch offen?

---

### `annahme/rohwaren-annahme` — Rohwaren annahme

**Zweck:** Stamm- und Fachmaske fuer Rohwaren annahme (annahme/rohwaren-annahme).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/annahme/rohwaren-annahme/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/annahme/rohwaren-annahme/agent-contract` |
| Readiness | `GET /api/v1/masks/annahme/rohwaren-annahme/readiness` |
| Rollout-Route | `/mask-rollout/annahme__rohwaren-annahme/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/annahme/warteschlange/{entity_id}`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Rohwaren annahme {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `annahme/silo-zuweisung` — Silo zuweisung

**Zweck:** Stamm- und Fachmaske fuer Silo zuweisung (annahme/silo-zuweisung).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/annahme/silo-zuweisung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/annahme/silo-zuweisung/agent-contract` |
| Readiness | `GET /api/v1/masks/annahme/silo-zuweisung/readiness` |
| Rollout-Route | `/mask-rollout/annahme__silo-zuweisung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/silo/zielzellen-vorschlag/lot/{entity_id}`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Silo zuweisung {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `annahme/trocknung` — Trocknung

**Zweck:** Stamm- und Fachmaske fuer Trocknung (annahme/trocknung).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/annahme/trocknung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/annahme/trocknung/agent-contract` |
| Readiness | `GET /api/v1/masks/annahme/trocknung/readiness` |
| Rollout-Route | `/mask-rollout/annahme__trocknung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/process/trocknungs-abrechnung/preview/{entity_id}`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Trocknung {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `annahme/voranmeldung` — Voranmeldung

**Zweck:** Stamm- und Fachmaske fuer Voranmeldung (annahme/voranmeldung).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/annahme/voranmeldung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/annahme/voranmeldung/agent-contract` |
| Readiness | `GET /api/v1/masks/annahme/voranmeldung/readiness` |
| Rollout-Route | `/mask-rollout/annahme__voranmeldung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/annahme/warteschlange/{entity_id}`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Voranmeldung {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `annahme/waage-1` — Waage 1

**Zweck:** Stamm- und Fachmaske fuer Waage 1 (annahme/waage-1).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/annahme/waage-1/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/annahme/waage-1/agent-contract` |
| Readiness | `GET /api/v1/masks/annahme/waage-1/readiness` |
| Rollout-Route | `/mask-rollout/annahme__waage-1/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/waage/waagen/{entity_id}`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Waage 1 {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `annahme/waage-2` — Waage 2

**Zweck:** Stamm- und Fachmaske fuer Waage 2 (annahme/waage-2).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/annahme/waage-2/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/annahme/waage-2/agent-contract` |
| Readiness | `GET /api/v1/masks/annahme/waage-2/readiness` |
| Rollout-Route | `/mask-rollout/annahme__waage-2/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/waage/waagen/{entity_id}`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Waage 2 {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `annahme/warteschlange` — Annahme-Warteschlange

**Zweck:** Warteschlange an der Waage priorisieren.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/annahme/warteschlange/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/annahme/warteschlange/agent-contract` |
| Readiness | `GET /api/v1/masks/annahme/warteschlange/readiness` |
| Rollout-Route | `/mask-rollout/annahme__warteschlange/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `items` → `/api/v1/annahme/warteschlange`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche LKW warten laenger als 30 Minuten?

---

### `annahme/wartezeit` — Wartezeit

**Zweck:** Stamm- und Fachmaske fuer Wartezeit (annahme/wartezeit).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/annahme/wartezeit/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/annahme/wartezeit/agent-contract` |
| Readiness | `GET /api/v1/masks/annahme/wartezeit/readiness` |
| Rollout-Route | `/mask-rollout/annahme__wartezeit/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/annahme/warteschlange/{entity_id}`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Wartezeit {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `annahme/wiegeschein` — Wiegeschein

**Zweck:** Stamm- und Fachmaske fuer Wiegeschein (annahme/wiegeschein).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/annahme/wiegeschein/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/annahme/wiegeschein/agent-contract` |
| Readiness | `GET /api/v1/masks/annahme/wiegeschein/readiness` |
| Rollout-Route | `/mask-rollout/annahme__wiegeschein/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/waage/wiegungen/{entity_id}/extended`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Wiegeschein {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `auswertungen/duengemittelmengen` — Duengemittelmengen

**Zweck:** Duengemittelmengen aus kanonischen Feldbuchdaten L3-vertraut auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/auswertungen/duengemittelmengen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/auswertungen/duengemittelmengen/agent-contract` |
| Readiness | `GET /api/v1/masks/auswertungen/duengemittelmengen/readiness` |
| Rollout-Route | `/mask-rollout/auswertungen__duengemittelmengen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/feldbuch/duengemittelmengen`
- `amounts` → `/api/v1/agrar/feldbuch/duengemittelmengen`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Duengemittelmengen dieses Jahres.
- Summiere N, P2O5 und K2O je Schlag.

**Sensible Felder:** `customer_id, schlag_name, lieferschein_id`

---

### `foerderung/liste` — Foerderantraege

**Zweck:** Foerderantraege nach Programm und Stand verfolgen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/foerderung/liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/foerderung/liste/agent-contract` |
| Readiness | `GET /api/v1/masks/foerderung/liste/readiness` |
| Rollout-Route | `/mask-rollout/foerderung__liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/foerderung/antraege`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Antraege sind eingereicht?
- Welche Foerdersumme ist bewilligt?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `neu` | Neuer Antrag | safe | nein | `Oeffnet die Anlage; Rechte prueft deren Anlageweg.` |
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `kontrakte/kontraktklassen-liste` — Kontraktklassen

**Zweck:** Kontraktklassen: Eintraege finden und Details oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/kontrakte/kontraktklassen-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/kontrakte/kontraktklassen-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/kontrakte/kontraktklassen-liste/readiness` |
| Rollout-Route | `/mask-rollout/kontrakte__kontraktklassen-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/kontrakt-klassen`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche offenen Kontraktklassen?
- Zeige aktuelle Kontraktklassen.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `kontrakte/liste` — Kontrakte

**Zweck:** Kontrakte: Eintraege finden und Details oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/kontrakte/liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/kontrakte/liste/agent-contract` |
| Readiness | `GET /api/v1/masks/kontrakte/liste/readiness` |
| Rollout-Route | `/mask-rollout/kontrakte__liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/kontrakte`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche offenen Kontrakte?
- Zeige aktuelle Kontrakte.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `neu` | Neuer Kontrakt | safe | nein | `Oeffnet die Anlage; Rechte prueft deren Anlageweg.` |
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `portal/feldbuch-auswertungen` — Feldbuch-Auswertungen

**Zweck:** Feldbuch-Massnahmen fuer Auswertung und Nachweis.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/portal/feldbuch-auswertungen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/portal/feldbuch-auswertungen/agent-contract` |
| Readiness | `GET /api/v1/masks/portal/feldbuch-auswertungen/readiness` |
| Rollout-Route | `/mask-rollout/portal__feldbuch-auswertungen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/feldbuch/massnahmen`
- `massnahmen` → `/api/v1/agrar/feldbuch/massnahmen`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Feldbuch-Massnahmen wurden erfasst?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `produktion/produktionsleitstand` — Produktionsleitstand

**Zweck:** Produktionsvorgaenge aus kanonischen Auftraegen und Bewegungen steuern.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/produktion/produktionsleitstand/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/produktion/produktionsleitstand/agent-contract` |
| Readiness | `GET /api/v1/masks/produktion/produktionsleitstand/readiness` |
| Rollout-Route | `/mask-rollout/produktion__produktionsleitstand/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/production-control/summary`
- `operations` → `/api/v1/production-control/operations`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige laufende Muehlenauftraege.
- Welche Vorgaenge brauchen Nachbearbeitung?

**Sensible Felder:** `assigned_user, notes`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `sync` | Auftraege synchronisieren | moderate | nein | `/api/v1/production-control/sync` |

---

### `strecke/nawaro-ernterklaerung-drucken` — NaWaRo-Ernterklärung drucken

**Zweck:** Die Ernterklaerung ueber den NaWaRo-Mitteilungsdruck ausgeben.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/strecke/nawaro-ernterklaerung-drucken/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/strecke/nawaro-ernterklaerung-drucken/agent-contract` |
| Readiness | `GET /api/v1/masks/strecke/nawaro-ernterklaerung-drucken/readiness` |
| Rollout-Route | `/mask-rollout/strecke__nawaro-ernterklaerung-drucken/:entityId` |
| Adapter | `native` (temporary=nein) |

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Oeffne NaWaRo-Ernterklärung drucken.

---

### `strecke/nawaro-lieferungen` — NaWaRo-Lieferungen

**Zweck:** NaWaRo-Lieferungen nach Streckennummer, Datum, Typ und Status suchen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/strecke/nawaro-lieferungen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/strecke/nawaro-lieferungen/agent-contract` |
| Readiness | `GET /api/v1/masks/strecke/nawaro-lieferungen/readiness` |
| Rollout-Route | `/mask-rollout/strecke__nawaro-lieferungen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/tours`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche NaWaRo-Lieferungen sind noch geplant?

---

### `strecke/nawaro-vertraege-pruefen` — NaWaRo-Vertraege pruefen

**Zweck:** NaWaRo-Vertragssheets vor Druck validieren.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/strecke/nawaro-vertraege-pruefen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/strecke/nawaro-vertraege-pruefen/agent-contract` |
| Readiness | `GET /api/v1/masks/strecke/nawaro-vertraege-pruefen/readiness` |
| Rollout-Route | `/mask-rollout/strecke__nawaro-vertraege-pruefen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `sheets` → `/api/v1/agrar/nawaro/contract-sheets`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Sheets haben fehlende Vertragsnummern?

---

### `tankstelle/adapter-inbox` — Tankanlagen-Eingang

**Zweck:** Tankanlagen-Eingaenge genau einmal und nachvollziehbar uebernehmen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/tankstelle/adapter-inbox/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/tankstelle/adapter-inbox/agent-contract` |
| Readiness | `GET /api/v1/masks/tankstelle/adapter-inbox/readiness` |
| Rollout-Route | `/mask-rollout/tankstelle__adapter-inbox/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/tank-adapter/summary`
- `intake` → `/api/v1/tank-adapter/intake`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Fehler im Tankadapter.
- Welche Zapfungen erzeugen einen Lieferschein-Handover?

**Sensible Felder:** `external_id, payload_hash, validation_errors`

---

### `vertrag/rahmenvertraege-liste` — Rahmenvertraege

**Zweck:** Rahmenvertraege mit Restmenge und Laufzeit verfolgen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/vertrag/rahmenvertraege-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/vertrag/rahmenvertraege-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/vertrag/rahmenvertraege-liste/readiness` |
| Rollout-Route | `/mask-rollout/vertrag__rahmenvertraege-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/vertrag/rahmenvertraege`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Rahmenvertraege laufen aus?
- Welche Restmengen sind kritisch?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `waage/hofliste` — Hofliste Waage

**Zweck:** Hofliste Waage: Eintraege finden und Details oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/waage/hofliste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/waage/hofliste/agent-contract` |
| Readiness | `GET /api/v1/masks/waage/hofliste/readiness` |
| Rollout-Route | `/mask-rollout/waage__hofliste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/waage/hofliste`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche offenen Hofliste Waage?
- Zeige aktuelle Hofliste Waage.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `waage/waagen-liste` — Waagen

**Zweck:** Waagen: Eintraege finden und Details oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/waage/waagen-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/waage/waagen-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/waage/waagen-liste/readiness` |
| Rollout-Route | `/mask-rollout/waage__waagen-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/waage/waagen`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche offenen Waagen?
- Zeige aktuelle Waagen.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `waage/wiegungen-liste` — Wiegescheine

**Zweck:** Wiegescheine: Eintraege finden und Details oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/waage/wiegungen-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/waage/wiegungen-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/waage/wiegungen-liste/readiness` |
| Rollout-Route | `/mask-rollout/waage__wiegungen-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/weighing-tickets/`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig
- `agrar.ration.transition` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.supply_handoff` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.actual_measure` — scope `agrar:write`, Risiko mittel
- `agrar.feeding.configure_threshold` — scope `agrar:write`, Risiko mittel
- `agrar.feed_analysis.transition` — scope `agrar:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche offenen Wiegescheine?
- Zeige aktuelle Wiegescheine.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

## Domäne: audit

### `auswertungen/aenderungshistorie` — Aenderungshistorie

**Zweck:** Aenderungen an Stammdaten und Belegen bereichsuebergreifend nachvollziehen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/auswertungen/aenderungshistorie/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/auswertungen/aenderungshistorie/agent-contract` |
| Readiness | `GET /api/v1/masks/auswertungen/aenderungshistorie/readiness` |
| Rollout-Route | `/mask-rollout/auswertungen__aenderungshistorie/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `trail` → `/api/v1/audit/trail`

**Beispiel-Prompts:**

- Wer hat dieses Feld geaendert?
- Zeige Aenderungen an diesem Beleg.

**Sensible Felder:** `user_email, changes, entity_id`

---

## Domäne: charge

### `charge/chargen-verfolgung` — Chargen verfolgung

**Zweck:** Chargen verfolgung mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/charge/chargen-verfolgung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/charge/chargen-verfolgung/agent-contract` |
| Readiness | `GET /api/v1/masks/charge/chargen-verfolgung/readiness` |
| Rollout-Route | `/mask-rollout/charge__chargen-verfolgung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/chargen/stats/summary`
- `items` → `/api/v1/chargen/stats/summary`

**Beispiel-Prompts:**

- Zeige offene Chargen verfolgung.
- Was ist in Chargen verfolgung faellig?

---

### `charge/qualitaets-freigabe` — Qualitaets freigabe

**Zweck:** Qualitaets freigabe mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/charge/qualitaets-freigabe/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/charge/qualitaets-freigabe/agent-contract` |
| Readiness | `GET /api/v1/masks/charge/qualitaets-freigabe/readiness` |
| Rollout-Route | `/mask-rollout/charge__qualitaets-freigabe/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/chargen`
- `items` → `/api/v1/chargen`

**Beispiel-Prompts:**

- Zeige offene Qualitaets freigabe.
- Was ist in Qualitaets freigabe faellig?

---

### `charge/rueckruf` — Rueckruf

**Zweck:** Rueckruf mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/charge/rueckruf/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/charge/rueckruf/agent-contract` |
| Readiness | `GET /api/v1/masks/charge/rueckruf/readiness` |
| Rollout-Route | `/mask-rollout/charge__rueckruf/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/chargen`
- `items` → `/api/v1/chargen`

**Beispiel-Prompts:**

- Zeige offene Rueckruf.
- Was ist in Rueckruf faellig?

---

### `charge/stamm` — Stamm

**Zweck:** Stamm mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/charge/stamm/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/charge/stamm/agent-contract` |
| Readiness | `GET /api/v1/masks/charge/stamm/readiness` |
| Rollout-Route | `/mask-rollout/charge__stamm/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/chargen`
- `items` → `/api/v1/chargen`

**Beispiel-Prompts:**

- Zeige offene Stamm.
- Was ist in Stamm faellig?

---

## Domäne: compliance

### `admin/compliance-dashboard` — Compliance-Dashboard

**Zweck:** Compliance-Quote und offene Meldungen mandantensicher ueberblicken.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/admin/compliance-dashboard/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/admin/compliance-dashboard/agent-contract` |
| Readiness | `GET /api/v1/masks/admin/compliance-dashboard/readiness` |
| Rollout-Route | `/mask-rollout/admin__compliance-dashboard/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/compliance/stats`

**MCP-Tools (Domäne):**

- `compliance.gate.status` — scope `compliance:read`, Risiko niedrig
- `compliance.sanctions.check` — scope `compliance:write`, Risiko mittel

**Beispiel-Prompts:**

- Wie ist die Compliance-Quote?
- Welche ENNI-Meldungen sind offen?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `auswertungen/sanktionspruefung-kunden` — Terrorschutzpruefung Kunden

**Zweck:** Terrorschutzpruefungen fuer Kunden getrennt und mandantensicher nachweisen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/auswertungen/sanktionspruefung-kunden/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/auswertungen/sanktionspruefung-kunden/agent-contract` |
| Readiness | `GET /api/v1/masks/auswertungen/sanktionspruefung-kunden/readiness` |
| Rollout-Route | `/mask-rollout/auswertungen__sanktionspruefung-kunden/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `checks` → `/api/v1/compliance/sanctions/pruefprotokoll?scope=customers`

**MCP-Tools (Domäne):**

- `compliance.gate.status` — scope `compliance:read`, Risiko niedrig
- `compliance.sanctions.check` — scope `compliance:write`, Risiko mittel

**Beispiel-Prompts:**

- Pruefe Kunden gegen die Sanktionsliste.
- Zeige verdaechtige Treffer.

**Sensible Felder:** `geprueft_name, entity_ref, checked_by`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `check` | Kunden pruefen | moderate | nein | `/api/v1/compliance/sanctions/actions/pruefen/customers` |

---

### `auswertungen/sanktionspruefung-personal` — Terrorschutzpruefung Personal

**Zweck:** Terrorschutzpruefungen fuer Personal getrennt und mandantensicher nachweisen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/auswertungen/sanktionspruefung-personal/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/auswertungen/sanktionspruefung-personal/agent-contract` |
| Readiness | `GET /api/v1/masks/auswertungen/sanktionspruefung-personal/readiness` |
| Rollout-Route | `/mask-rollout/auswertungen__sanktionspruefung-personal/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `checks` → `/api/v1/compliance/sanctions/pruefprotokoll?scope=personal`

**MCP-Tools (Domäne):**

- `compliance.gate.status` — scope `compliance:read`, Risiko niedrig
- `compliance.sanctions.check` — scope `compliance:write`, Risiko mittel

**Beispiel-Prompts:**

- Pruefe Personal gegen die Sanktionsliste.
- Zeige verdaechtige Treffer.

**Sensible Felder:** `geprueft_name, entity_ref, checked_by`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `check` | Personal pruefen | moderate | nein | `/api/v1/compliance/sanctions/actions/pruefen/personal` |

---

### `compliance/audit-trail` — Audit trail

**Zweck:** Audit trail mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/compliance/audit-trail/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/compliance/audit-trail/agent-contract` |
| Readiness | `GET /api/v1/masks/compliance/audit-trail/readiness` |
| Rollout-Route | `/mask-rollout/compliance__audit-trail/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/audit/logs`
- `items` → `/api/v1/audit/logs`

**MCP-Tools (Domäne):**

- `compliance.gate.status` — scope `compliance:read`, Risiko niedrig
- `compliance.sanctions.check` — scope `compliance:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige offene Audit trail.
- Was ist in Audit trail faellig?

---

### `compliance/bvl-umsatzmeldung-liste` — BVL Umsatzmeldung

**Zweck:** BVL-Umsatzmeldungen verfolgen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/compliance/bvl-umsatzmeldung-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/compliance/bvl-umsatzmeldung-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/compliance/bvl-umsatzmeldung-liste/readiness` |
| Rollout-Route | `/mask-rollout/compliance__bvl-umsatzmeldung-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/compliance/bvl-umsaetze`

**MCP-Tools (Domäne):**

- `compliance.gate.status` — scope `compliance:read`, Risiko niedrig
- `compliance.sanctions.check` — scope `compliance:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Meldungen sind faellig?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `compliance/cross-compliance` — Cross compliance

**Zweck:** Cross compliance mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/compliance/cross-compliance/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/compliance/cross-compliance/agent-contract` |
| Readiness | `GET /api/v1/masks/compliance/cross-compliance/readiness` |
| Rollout-Route | `/mask-rollout/compliance__cross-compliance/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/compliance/cross-compliance`
- `items` → `/api/v1/compliance/cross-compliance`

**MCP-Tools (Domäne):**

- `compliance.gate.status` — scope `compliance:read`, Risiko niedrig
- `compliance.sanctions.check` — scope `compliance:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige offene Cross compliance.
- Was ist in Cross compliance faellig?

---

### `compliance/cross-compliance-liste` — Cross-Compliance

**Zweck:** Cross-Compliance-Anforderungen und offene Nachweise pruefen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/compliance/cross-compliance-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/compliance/cross-compliance-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/compliance/cross-compliance-liste/readiness` |
| Rollout-Route | `/mask-rollout/compliance__cross-compliance-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/compliance/cross-compliance`

**MCP-Tools (Domäne):**

- `compliance.gate.status` — scope `compliance:read`, Risiko niedrig
- `compliance.sanctions.check` — scope `compliance:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Anforderungen sind nicht erfuellt?
- Was ist diese Woche faellig?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `compliance/duenge-bilanz` — Duenge bilanz

**Zweck:** Duenge bilanz mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/compliance/duenge-bilanz/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/compliance/duenge-bilanz/agent-contract` |
| Readiness | `GET /api/v1/masks/compliance/duenge-bilanz/readiness` |
| Rollout-Route | `/mask-rollout/compliance__duenge-bilanz/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/feldbuch/duengebilanz`
- `items` → `/api/v1/agrar/feldbuch/duengebilanz`

**MCP-Tools (Domäne):**

- `compliance.gate.status` — scope `compliance:read`, Risiko niedrig
- `compliance.sanctions.check` — scope `compliance:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige offene Duenge bilanz.
- Was ist in Duenge bilanz faellig?

---

### `compliance/enni-meldungen-liste` — ENNI-Meldungen

**Zweck:** ENNI-Meldungen und offene Entwuerfe verfolgen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/compliance/enni-meldungen-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/compliance/enni-meldungen-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/compliance/enni-meldungen-liste/readiness` |
| Rollout-Route | `/mask-rollout/compliance__enni-meldungen-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/compliance/enni-meldungen`

**MCP-Tools (Domäne):**

- `compliance.gate.status` — scope `compliance:read`, Risiko niedrig
- `compliance.sanctions.check` — scope `compliance:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Meldungen sind noch Entwurf?
- Welche VVVO-Meldungen sind faellig?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `neu` | Neue Meldung | safe | nein | `Oeffnet die Anlage; Rechte prueft deren Anlageweg.` |
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `compliance/eudr-compliance-liste` — EUDR Compliance

**Zweck:** EUDR-Compliance-Faelle finden.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/compliance/eudr-compliance-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/compliance/eudr-compliance-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/compliance/eudr-compliance-liste/readiness` |
| Rollout-Route | `/mask-rollout/compliance__eudr-compliance-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/eudr/sorgfaltserklaerungen`

**MCP-Tools (Domäne):**

- `compliance.gate.status` — scope `compliance:read`, Risiko niedrig
- `compliance.sanctions.check` — scope `compliance:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Lieferketten sind ungeprueft?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `compliance/eudr-meldungen` — Eudr meldungen

**Zweck:** Eudr meldungen mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/compliance/eudr-meldungen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/compliance/eudr-meldungen/agent-contract` |
| Readiness | `GET /api/v1/masks/compliance/eudr-meldungen/readiness` |
| Rollout-Route | `/mask-rollout/compliance__eudr-meldungen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/compliance/eudr`
- `items` → `/api/v1/compliance/eudr`

**MCP-Tools (Domäne):**

- `compliance.gate.status` — scope `compliance:read`, Risiko niedrig
- `compliance.sanctions.check` — scope `compliance:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige offene Eudr meldungen.
- Was ist in Eudr meldungen faellig?

---

### `compliance/export-pruefprotokoll` — Export-Pruefprotokoll

**Zweck:** Compliance-Exporte vor Abgabe stichprobenartig pruefen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/compliance/export-pruefprotokoll/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/compliance/export-pruefprotokoll/agent-contract` |
| Readiness | `GET /api/v1/masks/compliance/export-pruefprotokoll/readiness` |
| Rollout-Route | `/mask-rollout/compliance__export-pruefprotokoll/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `rows` → `/api/v1/compliance/exports/gefahrstoffdoku`

**MCP-Tools (Domäne):**

- `compliance.gate.status` — scope `compliance:read`, Risiko niedrig
- `compliance.sanctions.check` — scope `compliance:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Lieferungen sind nicht compliant?

---

### `compliance/export-pruefung-liste` — Export-Pruefung

**Zweck:** Export-Pruefungen nachvollziehen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/compliance/export-pruefung-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/compliance/export-pruefung-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/compliance/export-pruefung-liste/readiness` |
| Rollout-Route | `/mask-rollout/compliance__export-pruefung-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/export/entities`

**MCP-Tools (Domäne):**

- `compliance.gate.status` — scope `compliance:read`, Risiko niedrig
- `compliance.sanctions.check` — scope `compliance:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Exporte sind blockiert?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `compliance/gefahrstoff-doku-liste` — Gefahrstoff-Doku

**Zweck:** Gefahrstoffdokumentation einsehen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/compliance/gefahrstoff-doku-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/compliance/gefahrstoff-doku-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/compliance/gefahrstoff-doku-liste/readiness` |
| Rollout-Route | `/mask-rollout/compliance__gefahrstoff-doku-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/compliance/exports/gefahrstoffdoku`

**MCP-Tools (Domäne):**

- `compliance.gate.status` — scope `compliance:read`, Risiko niedrig
- `compliance.sanctions.check` — scope `compliance:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Produkte brauchen Update?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `compliance/gefahrstoff-verzeichnis` — Gefahrstoff verzeichnis

**Zweck:** Gefahrstoff verzeichnis mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/compliance/gefahrstoff-verzeichnis/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/compliance/gefahrstoff-verzeichnis/agent-contract` |
| Readiness | `GET /api/v1/masks/compliance/gefahrstoff-verzeichnis/readiness` |
| Rollout-Route | `/mask-rollout/compliance__gefahrstoff-verzeichnis/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/compliance/exports/gefahrstoffdoku`
- `items` → `/api/v1/compliance/exports/gefahrstoffdoku`

**MCP-Tools (Domäne):**

- `compliance.gate.status` — scope `compliance:read`, Risiko niedrig
- `compliance.sanctions.check` — scope `compliance:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige offene Gefahrstoff verzeichnis.
- Was ist in Gefahrstoff verzeichnis faellig?

---

### `compliance/gelangensbestaetigung-liste` — Gelangensbestaetigungen

**Zweck:** Gelangensbestaetigungen: Eintraege finden und Details oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/compliance/gelangensbestaetigung-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/compliance/gelangensbestaetigung-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/compliance/gelangensbestaetigung-liste/readiness` |
| Rollout-Route | `/mask-rollout/compliance__gelangensbestaetigung-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/gelangensbestaetigung`

**MCP-Tools (Domäne):**

- `compliance.gate.status` — scope `compliance:read`, Risiko niedrig
- `compliance.sanctions.check` — scope `compliance:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche offenen Gelangensbestaetigungen?
- Zeige aktuelle Gelangensbestaetigungen.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `compliance/intrastat-liste` — Intrastat

**Zweck:** Intrastat: Eintraege finden und Details oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/compliance/intrastat-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/compliance/intrastat-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/compliance/intrastat-liste/readiness` |
| Rollout-Route | `/mask-rollout/compliance__intrastat-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/intrastat/meldungen`

**MCP-Tools (Domäne):**

- `compliance.gate.status` — scope `compliance:read`, Risiko niedrig
- `compliance.sanctions.check` — scope `compliance:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche offenen Intrastat?
- Zeige aktuelle Intrastat.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `compliance/lksg-lieferkette` — Lksg lieferkette

**Zweck:** Lksg lieferkette mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/compliance/lksg-lieferkette/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/compliance/lksg-lieferkette/agent-contract` |
| Readiness | `GET /api/v1/masks/compliance/lksg-lieferkette/readiness` |
| Rollout-Route | `/mask-rollout/compliance__lksg-lieferkette/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/compliance/lksg/supplier-risk-assessments`
- `items` → `/api/v1/compliance/lksg/supplier-risk-assessments`

**MCP-Tools (Domäne):**

- `compliance.gate.status` — scope `compliance:read`, Risiko niedrig
- `compliance.sanctions.check` — scope `compliance:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige offene Lksg lieferkette.
- Was ist in Lksg lieferkette faellig?

---

### `compliance/lksg-liste` — LKSG Lieferanten

**Zweck:** LKSG Lieferanten: Eintraege finden und Details oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/compliance/lksg-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/compliance/lksg-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/compliance/lksg-liste/readiness` |
| Rollout-Route | `/mask-rollout/compliance__lksg-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/compliance/lksg/supplier-risk-assessments`

**MCP-Tools (Domäne):**

- `compliance.gate.status` — scope `compliance:read`, Risiko niedrig
- `compliance.sanctions.check` — scope `compliance:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche offenen LKSG Lieferanten?
- Zeige aktuelle LKSG Lieferanten.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `compliance/meldewesen-konsole` — Meldewesen-Konsole

**Zweck:** Meldewesen-Jobs und Konnektoren im Blick behalten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/compliance/meldewesen-konsole/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/compliance/meldewesen-konsole/agent-contract` |
| Readiness | `GET /api/v1/masks/compliance/meldewesen-konsole/readiness` |
| Rollout-Route | `/mask-rollout/compliance__meldewesen-konsole/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/config/connectors`
- `jobs` → `/api/v1/jobs`

**MCP-Tools (Domäne):**

- `compliance.gate.status` — scope `compliance:read`, Risiko niedrig
- `compliance.sanctions.check` — scope `compliance:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Melde-Jobs sind fehlgeschlagen?

---

### `compliance/pcn-liste` — PCN-Meldungen

**Zweck:** PCN-Meldungen mit UFI und Uebermittlungsstand nachweisen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/compliance/pcn-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/compliance/pcn-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/compliance/pcn-liste/readiness` |
| Rollout-Route | `/mask-rollout/compliance__pcn-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/compliance/pcn-meldungen`

**MCP-Tools (Domäne):**

- `compliance.gate.status` — scope `compliance:read`, Risiko niedrig
- `compliance.sanctions.check` — scope `compliance:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche PCN-Meldungen sind noch Entwurf?
- Welche UFI hat Produkt X?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `neu` | Neue PCN-Meldung | safe | nein | `Oeffnet die Anlage; Rechte prueft deren Anlageweg.` |
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `compliance/pcn-ufi` — PCN / UFI-Meldungen

**Zweck:** PCN/UFI-Pflichten ohne Medienbruch nachverfolgen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/compliance/pcn-ufi/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/compliance/pcn-ufi/agent-contract` |
| Readiness | `GET /api/v1/masks/compliance/pcn-ufi/readiness` |
| Rollout-Route | `/mask-rollout/compliance__pcn-ufi/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `items` → `/api/v1/compliance/pcn-meldungen`

**MCP-Tools (Domäne):**

- `compliance.gate.status` — scope `compliance:read`, Risiko niedrig
- `compliance.sanctions.check` — scope `compliance:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche PCN-Meldungen sind faellig?

---

### `compliance/pflanzenschutz-nachweis` — Pflanzenschutz nachweis

**Zweck:** Pflanzenschutz nachweis mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/compliance/pflanzenschutz-nachweis/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/compliance/pflanzenschutz-nachweis/agent-contract` |
| Readiness | `GET /api/v1/masks/compliance/pflanzenschutz-nachweis/readiness` |
| Rollout-Route | `/mask-rollout/compliance__pflanzenschutz-nachweis/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/compliance/bvl-umsaetze`
- `items` → `/api/v1/compliance/bvl-umsaetze`

**MCP-Tools (Domäne):**

- `compliance.gate.status` — scope `compliance:read`, Risiko niedrig
- `compliance.sanctions.check` — scope `compliance:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige offene Pflanzenschutz nachweis.
- Was ist in Pflanzenschutz nachweis faellig?

---

### `compliance/qs-audits` — Qs audits

**Zweck:** Qs audits mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/compliance/qs-audits/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/compliance/qs-audits/agent-contract` |
| Readiness | `GET /api/v1/masks/compliance/qs-audits/readiness` |
| Rollout-Route | `/mask-rollout/compliance__qs-audits/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/admin/quality-evidence/`
- `items` → `/api/v1/admin/quality-evidence/`

**MCP-Tools (Domäne):**

- `compliance.gate.status` — scope `compliance:read`, Risiko niedrig
- `compliance.sanctions.check` — scope `compliance:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige offene Qs audits.
- Was ist in Qs audits faellig?

---

### `compliance/qs-checkliste-liste` — QS-Checkliste

**Zweck:** QS-Checkliste: Eintraege finden und Details oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/compliance/qs-checkliste-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/compliance/qs-checkliste-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/compliance/qs-checkliste-liste/readiness` |
| Rollout-Route | `/mask-rollout/compliance__qs-checkliste-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/compliance/qs-checkliste`

**MCP-Tools (Domäne):**

- `compliance.gate.status` — scope `compliance:read`, Risiko niedrig
- `compliance.sanctions.check` — scope `compliance:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche offenen QS-Checkliste?
- Zeige aktuelle QS-Checkliste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `compliance/saatgut-nachbau-liste` — Saatgut-Nachbau

**Zweck:** Saatgut-Nachbauflaechen und offene Gebuehren verfolgen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/compliance/saatgut-nachbau-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/compliance/saatgut-nachbau-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/compliance/saatgut-nachbau-liste/readiness` |
| Rollout-Route | `/mask-rollout/compliance__saatgut-nachbau-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/compliance/saatgut-nachbau`

**MCP-Tools (Domäne):**

- `compliance.gate.status` — scope `compliance:read`, Risiko niedrig
- `compliance.sanctions.check` — scope `compliance:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Nachbaugebuehren sind offen?
- Welche Sorten wurden nachgebaut?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `compliance/sachkunde-liste` — Sachkundenachweise

**Zweck:** Sachkundenachweise und Ablaufdaten verfolgen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/compliance/sachkunde-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/compliance/sachkunde-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/compliance/sachkunde-liste/readiness` |
| Rollout-Route | `/mask-rollout/compliance__sachkunde-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/compliance/sachkunde-register`

**MCP-Tools (Domäne):**

- `compliance.gate.status` — scope `compliance:read`, Risiko niedrig
- `compliance.sanctions.check` — scope `compliance:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Nachweise laufen ab?
- Welche Kunden haben gueltige Sachkunde?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `compliance/sanktionspruefung` — Sanktionspruefung

**Zweck:** Sanktionstreffer getrennt vom Auswertungs-Cockpit nachverfolgen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/compliance/sanktionspruefung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/compliance/sanktionspruefung/agent-contract` |
| Readiness | `GET /api/v1/masks/compliance/sanktionspruefung/readiness` |
| Rollout-Route | `/mask-rollout/compliance__sanktionspruefung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `eintraege` → `/api/v1/compliance/sanctions/eintraege`

**MCP-Tools (Domäne):**

- `compliance.gate.status` — scope `compliance:read`, Risiko niedrig
- `compliance.sanctions.check` — scope `compliance:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Sanktionstreffer sind offen?

---

### `compliance/schadstoff-monitoring` — Schadstoff monitoring

**Zweck:** Schadstoff monitoring mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/compliance/schadstoff-monitoring/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/compliance/schadstoff-monitoring/agent-contract` |
| Readiness | `GET /api/v1/masks/compliance/schadstoff-monitoring/readiness` |
| Rollout-Route | `/mask-rollout/compliance__schadstoff-monitoring/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/psm/monitoring`
- `items` → `/api/v1/agrar/psm/monitoring`

**MCP-Tools (Domäne):**

- `compliance.gate.status` — scope `compliance:read`, Risiko niedrig
- `compliance.sanctions.check` — scope `compliance:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige offene Schadstoff monitoring.
- Was ist in Schadstoff monitoring faellig?

---

### `compliance/stichtagsmeldung-bestaende` — Stichtagsmeldung bestaende

**Zweck:** Stichtagsmeldung bestaende mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/compliance/stichtagsmeldung-bestaende/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/compliance/stichtagsmeldung-bestaende/agent-contract` |
| Readiness | `GET /api/v1/masks/compliance/stichtagsmeldung-bestaende/readiness` |
| Rollout-Route | `/mask-rollout/compliance__stichtagsmeldung-bestaende/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/intrastat/meldungen`
- `items` → `/api/v1/intrastat/meldungen`

**MCP-Tools (Domäne):**

- `compliance.gate.status` — scope `compliance:read`, Risiko niedrig
- `compliance.sanctions.check` — scope `compliance:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige offene Stichtagsmeldung bestaende.
- Was ist in Stichtagsmeldung bestaende faellig?

---

### `compliance/tierwohl-dokumentation` — Tierwohl dokumentation

**Zweck:** Tierwohl dokumentation mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/compliance/tierwohl-dokumentation/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/compliance/tierwohl-dokumentation/agent-contract` |
| Readiness | `GET /api/v1/masks/compliance/tierwohl-dokumentation/readiness` |
| Rollout-Route | `/mask-rollout/compliance__tierwohl-dokumentation/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/compliance/vvvo-register`
- `items` → `/api/v1/compliance/vvvo-register`

**MCP-Tools (Domäne):**

- `compliance.gate.status` — scope `compliance:read`, Risiko niedrig
- `compliance.sanctions.check` — scope `compliance:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige offene Tierwohl dokumentation.
- Was ist in Tierwohl dokumentation faellig?

---

### `compliance/usp-konformitaet` — Usp konformitaet

**Zweck:** Usp konformitaet mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/compliance/usp-konformitaet/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/compliance/usp-konformitaet/agent-contract` |
| Readiness | `GET /api/v1/masks/compliance/usp-konformitaet/readiness` |
| Rollout-Route | `/mask-rollout/compliance__usp-konformitaet/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/compliance/zulassungen-register`
- `items` → `/api/v1/compliance/zulassungen-register`

**MCP-Tools (Domäne):**

- `compliance.gate.status` — scope `compliance:read`, Risiko niedrig
- `compliance.sanctions.check` — scope `compliance:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige offene Usp konformitaet.
- Was ist in Usp konformitaet faellig?

---

### `compliance/vvvo-liste` — VVVO-Register

**Zweck:** VVVO-registrierte Betriebe finden und pruefen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/compliance/vvvo-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/compliance/vvvo-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/compliance/vvvo-liste/readiness` |
| Rollout-Route | `/mask-rollout/compliance__vvvo-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/compliance/vvvo-register`

**MCP-Tools (Domäne):**

- `compliance.gate.status` — scope `compliance:read`, Risiko niedrig
- `compliance.sanctions.check` — scope `compliance:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Betriebe sind inaktiv?
- Zeige Betriebe in Niedersachsen.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `compliance/wasserschutz-auflagen` — Wasserschutz auflagen

**Zweck:** Wasserschutz auflagen mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/compliance/wasserschutz-auflagen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/compliance/wasserschutz-auflagen/agent-contract` |
| Readiness | `GET /api/v1/masks/compliance/wasserschutz-auflagen/readiness` |
| Rollout-Route | `/mask-rollout/compliance__wasserschutz-auflagen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/psm/wasserschutz-zonen`
- `items` → `/api/v1/agrar/psm/wasserschutz-zonen`

**MCP-Tools (Domäne):**

- `compliance.gate.status` — scope `compliance:read`, Risiko niedrig
- `compliance.sanctions.check` — scope `compliance:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige offene Wasserschutz auflagen.
- Was ist in Wasserschutz auflagen faellig?

---

### `compliance/zertifikate` — Zertifikate

**Zweck:** Zertifikate mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/compliance/zertifikate/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/compliance/zertifikate/agent-contract` |
| Readiness | `GET /api/v1/masks/compliance/zertifikate/readiness` |
| Rollout-Route | `/mask-rollout/compliance__zertifikate/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/zertifikate`
- `items` → `/api/v1/zertifikate`

**MCP-Tools (Domäne):**

- `compliance.gate.status` — scope `compliance:read`, Risiko niedrig
- `compliance.sanctions.check` — scope `compliance:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige offene Zertifikate.
- Was ist in Zertifikate faellig?

---

### `compliance/zulassungen-liste` — Zulassungsregister

**Zweck:** Produktzulassungen und Ablaufdaten im Blick behalten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/compliance/zulassungen-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/compliance/zulassungen-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/compliance/zulassungen-liste/readiness` |
| Rollout-Route | `/mask-rollout/compliance__zulassungen-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/compliance/zulassungen-register`

**MCP-Tools (Domäne):**

- `compliance.gate.status` — scope `compliance:read`, Risiko niedrig
- `compliance.sanctions.check` — scope `compliance:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Zulassungen laufen ab?
- Welche Produkte sind widerrufen?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `export/intrastat-meldung-liste` — Intrastat-Meldung

**Zweck:** Intrastat-Meldungen verfolgen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/export/intrastat-meldung-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/export/intrastat-meldung-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/export/intrastat-meldung-liste/readiness` |
| Rollout-Route | `/mask-rollout/export__intrastat-meldung-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/intrastat/meldungen`

**MCP-Tools (Domäne):**

- `compliance.gate.status` — scope `compliance:read`, Risiko niedrig
- `compliance.sanctions.check` — scope `compliance:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Meldungen sind faellig?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

## Domäne: contracts

### `contracts/contract` — Contract

**Zweck:** Contract mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/contracts/contract/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/contracts/contract/agent-contract` |
| Readiness | `GET /api/v1/masks/contracts/contract/readiness` |
| Rollout-Route | `/mask-rollout/contracts__contract/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/contracts/`
- `items` → `/api/v1/agrar/contracts/`

**Beispiel-Prompts:**

- Zeige offene Contract.
- Was ist in Contract faellig?

---

## Domäne: controlling

### `controlling/abweichungsanalyse` — Abweichungsanalyse

**Zweck:** Abweichungsanalyse mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/controlling/abweichungsanalyse/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/controlling/abweichungsanalyse/agent-contract` |
| Readiness | `GET /api/v1/masks/controlling/abweichungsanalyse/readiness` |
| Rollout-Route | `/mask-rollout/controlling__abweichungsanalyse/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/controlling/abweichung`
- `items` → `/api/v1/controlling/abweichung`

**Beispiel-Prompts:**

- Zeige offene Abweichungsanalyse.
- Was ist in Abweichungsanalyse faellig?

---

### `controlling/agrarkalkulation` — Agrarkalkulation

**Zweck:** Agrarkalkulation mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/controlling/agrarkalkulation/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/controlling/agrarkalkulation/agent-contract` |
| Readiness | `GET /api/v1/masks/controlling/agrarkalkulation/readiness` |
| Rollout-Route | `/mask-rollout/controlling__agrarkalkulation/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/controlling/kpis`
- `items` → `/api/v1/controlling/kpis`

**Beispiel-Prompts:**

- Zeige offene Agrarkalkulation.
- Was ist in Agrarkalkulation faellig?

---

### `controlling/benchmark-cockpit` — Benchmark-Cockpit

**Zweck:** Eigene KPIs gegen Branchenbenchmark und Read-Model spiegeln.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/controlling/benchmark-cockpit/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/controlling/benchmark-cockpit/agent-contract` |
| Readiness | `GET /api/v1/masks/controlling/benchmark-cockpit/readiness` |
| Rollout-Route | `/mask-rollout/controlling__benchmark-cockpit/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/benchmark/read-model`

**Beispiel-Prompts:**

- Wie stehen unsere KPIs zum Branchendurchschnitt?
- Zeige das Benchmark-Read-Model.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `controlling/berichtswesen` — Berichtswesen

**Zweck:** Berichtswesen mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/controlling/berichtswesen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/controlling/berichtswesen/agent-contract` |
| Readiness | `GET /api/v1/masks/controlling/berichtswesen/readiness` |
| Rollout-Route | `/mask-rollout/controlling__berichtswesen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/controlling/dashboards`
- `items` → `/api/v1/controlling/dashboards`

**Beispiel-Prompts:**

- Zeige offene Berichtswesen.
- Was ist in Berichtswesen faellig?

---

### `controlling/bwa` — Bwa

**Zweck:** Bwa mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/controlling/bwa/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/controlling/bwa/agent-contract` |
| Readiness | `GET /api/v1/masks/controlling/bwa/readiness` |
| Rollout-Route | `/mask-rollout/controlling__bwa/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/finance/financial-reports/bwa`
- `items` → `/api/v1/finance/financial-reports/bwa`

**Beispiel-Prompts:**

- Zeige offene Bwa.
- Was ist in Bwa faellig?

---

### `controlling/cashflow-prognose` — Cashflow prognose

**Zweck:** Cashflow prognose mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/controlling/cashflow-prognose/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/controlling/cashflow-prognose/agent-contract` |
| Readiness | `GET /api/v1/masks/controlling/cashflow-prognose/readiness` |
| Rollout-Route | `/mask-rollout/controlling__cashflow-prognose/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/finance/liquidity/forecast`
- `items` → `/api/v1/finance/liquidity/forecast`

**Beispiel-Prompts:**

- Zeige offene Cashflow prognose.
- Was ist in Cashflow prognose faellig?

---

### `controlling/dashboard-verwaltung` — Dashboard-Verwaltung

**Zweck:** Controlling-Dashboards mandantensicher verwalten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/controlling/dashboard-verwaltung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/controlling/dashboard-verwaltung/agent-contract` |
| Readiness | `GET /api/v1/masks/controlling/dashboard-verwaltung/readiness` |
| Rollout-Route | `/mask-rollout/controlling__dashboard-verwaltung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/controlling/dashboards`
- `dashboards` → `/api/v1/controlling/dashboards`

**Beispiel-Prompts:**

- Welche Dashboards sind aktiv?
- Zeige alle Cockpit-Layouts.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `controlling/deckungsbeitragsrechnung` — Deckungsbeitragsrechnung

**Zweck:** Deckungsbeitragsrechnung mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/controlling/deckungsbeitragsrechnung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/controlling/deckungsbeitragsrechnung/agent-contract` |
| Readiness | `GET /api/v1/masks/controlling/deckungsbeitragsrechnung/readiness` |
| Rollout-Route | `/mask-rollout/controlling__deckungsbeitragsrechnung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/controlling/abweichung/drill-down`
- `items` → `/api/v1/controlling/abweichung/drill-down`

**Beispiel-Prompts:**

- Zeige offene Deckungsbeitragsrechnung.
- Was ist in Deckungsbeitragsrechnung faellig?

---

### `controlling/investitionsrechnung` — Investitionsrechnung

**Zweck:** Investitionsrechnung mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/controlling/investitionsrechnung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/controlling/investitionsrechnung/agent-contract` |
| Readiness | `GET /api/v1/masks/controlling/investitionsrechnung/readiness` |
| Rollout-Route | `/mask-rollout/controlling__investitionsrechnung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/controlling/dashboards`
- `items` → `/api/v1/controlling/dashboards`

**Beispiel-Prompts:**

- Zeige offene Investitionsrechnung.
- Was ist in Investitionsrechnung faellig?

---

### `controlling/kampagnen-controlling` — Kampagnen controlling

**Zweck:** Kampagnen controlling mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/controlling/kampagnen-controlling/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/controlling/kampagnen-controlling/agent-contract` |
| Readiness | `GET /api/v1/masks/controlling/kampagnen-controlling/readiness` |
| Rollout-Route | `/mask-rollout/controlling__kampagnen-controlling/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/ernte-kampagnen/tenant/{tenant_id}`
- `items` → `/api/v1/ernte-kampagnen/tenant/{tenant_id}`

**Beispiel-Prompts:**

- Zeige offene Kampagnen controlling.
- Was ist in Kampagnen controlling faellig?

---

### `controlling/kennzahlen` — Kennzahlen

**Zweck:** Kennzahlen mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/controlling/kennzahlen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/controlling/kennzahlen/agent-contract` |
| Readiness | `GET /api/v1/masks/controlling/kennzahlen/readiness` |
| Rollout-Route | `/mask-rollout/controlling__kennzahlen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/controlling/kpis`
- `items` → `/api/v1/controlling/kpis`

**Beispiel-Prompts:**

- Zeige offene Kennzahlen.
- Was ist in Kennzahlen faellig?

---

### `controlling/kostentraegerrechnung` — Kostentraegerrechnung

**Zweck:** Kostentraegerrechnung mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/controlling/kostentraegerrechnung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/controlling/kostentraegerrechnung/agent-contract` |
| Readiness | `GET /api/v1/masks/controlling/kostentraegerrechnung/readiness` |
| Rollout-Route | `/mask-rollout/controlling__kostentraegerrechnung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/controlling/timeseries`
- `items` → `/api/v1/controlling/timeseries`

**Beispiel-Prompts:**

- Zeige offene Kostentraegerrechnung.
- Was ist in Kostentraegerrechnung faellig?

---

### `controlling/kpi-verwaltung` — KPI-Verwaltung

**Zweck:** KPI-Stamm fuer Controlling-Cockpits pflegen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/controlling/kpi-verwaltung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/controlling/kpi-verwaltung/agent-contract` |
| Readiness | `GET /api/v1/masks/controlling/kpi-verwaltung/readiness` |
| Rollout-Route | `/mask-rollout/controlling__kpi-verwaltung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/controlling/kpis`
- `kpis` → `/api/v1/controlling/kpis`

**Beispiel-Prompts:**

- Welche KPIs sind aktiv?
- Zeige KPI-Definitionen mit Zielwerten.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `controlling/liquiditaetsplanung` — Liquiditaetsplanung

**Zweck:** Liquiditaetsplanung mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/controlling/liquiditaetsplanung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/controlling/liquiditaetsplanung/agent-contract` |
| Readiness | `GET /api/v1/masks/controlling/liquiditaetsplanung/readiness` |
| Rollout-Route | `/mask-rollout/controlling__liquiditaetsplanung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/finance/liquidity/overview`
- `items` → `/api/v1/finance/liquidity/overview`

**Beispiel-Prompts:**

- Zeige offene Liquiditaetsplanung.
- Was ist in Liquiditaetsplanung faellig?

---

### `controlling/massnahmen` — Controlling-Massnahmen

**Zweck:** Massnahmen aus Plan-Ist-Abweichungen nachverfolgen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/controlling/massnahmen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/controlling/massnahmen/agent-contract` |
| Readiness | `GET /api/v1/masks/controlling/massnahmen/readiness` |
| Rollout-Route | `/mask-rollout/controlling__massnahmen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/controlling/actions`
- `actions` → `/api/v1/controlling/actions`

**Beispiel-Prompts:**

- Welche Massnahmen sind offen?
- Zeige ueberfaellige Massnahmen.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `controlling/plan-ist` — Plan-Ist-Controlling

**Zweck:** Plan-Ist-Abweichungen fuer Kostenstellen und KPIs sichtbar machen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/controlling/plan-ist/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/controlling/plan-ist/agent-contract` |
| Readiness | `GET /api/v1/masks/controlling/plan-ist/readiness` |
| Rollout-Route | `/mask-rollout/controlling__plan-ist/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/controlling/abweichung`

**Beispiel-Prompts:**

- Wo weichen Ist-Werte vom Plan ab?
- Zeige die groessten Abweichungen.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `controlling/plan-ist-liste` — Plan-Ist

**Zweck:** Plan-Ist-KPIs vergleichen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/controlling/plan-ist-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/controlling/plan-ist-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/controlling/plan-ist-liste/readiness` |
| Rollout-Route | `/mask-rollout/controlling__plan-ist-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/controlling/kpis`

**Beispiel-Prompts:**

- Wo weicht Ist vom Plan ab?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `controlling/standort-vergleich` — Standort vergleich

**Zweck:** Standort vergleich mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/controlling/standort-vergleich/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/controlling/standort-vergleich/agent-contract` |
| Readiness | `GET /api/v1/masks/controlling/standort-vergleich/readiness` |
| Rollout-Route | `/mask-rollout/controlling__standort-vergleich/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/benchmark/read-model`
- `items` → `/api/v1/benchmark/read-model`

**Beispiel-Prompts:**

- Zeige offene Standort vergleich.
- Was ist in Standort vergleich faellig?

---

### `controlling/timeseries-erfassung` — Zeitreihen-Erfassung

**Zweck:** Zeitreihen fuer Controlling-KPIs erfassen und pruefen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/controlling/timeseries-erfassung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/controlling/timeseries-erfassung/agent-contract` |
| Readiness | `GET /api/v1/masks/controlling/timeseries-erfassung/readiness` |
| Rollout-Route | `/mask-rollout/controlling__timeseries-erfassung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/controlling/timeseries`
- `timeseries` → `/api/v1/controlling/timeseries`

**Beispiel-Prompts:**

- Welche Zeitreihen fehlen?
- Zeige Ist-Werte der letzten Periode.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `controlling/unternehmensplanung` — Unternehmensplanung

**Zweck:** Unternehmensplanung mandantensicher als Kontroll-Worklist abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/controlling/unternehmensplanung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/controlling/unternehmensplanung/agent-contract` |
| Readiness | `GET /api/v1/masks/controlling/unternehmensplanung/readiness` |
| Rollout-Route | `/mask-rollout/controlling__unternehmensplanung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/controlling/kpis`
- `items` → `/api/v1/controlling/kpis`

**Beispiel-Prompts:**

- Zeige offene Unternehmensplanung.
- Was ist in Unternehmensplanung faellig?

---

### `controlling/widget-verwaltung` — Widget-Verwaltung

**Zweck:** Widgets den Controlling-Dashboards zuordnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/controlling/widget-verwaltung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/controlling/widget-verwaltung/agent-contract` |
| Readiness | `GET /api/v1/masks/controlling/widget-verwaltung/readiness` |
| Rollout-Route | `/mask-rollout/controlling__widget-verwaltung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/controlling/dashboards`
- `widgets` → `/api/v1/controlling/dashboards`

**Beispiel-Prompts:**

- Welche Widgets sind aktiv?
- Zeige Widget-Zuordnungen.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `projekte/liste` — Projekte

**Zweck:** Projekte nach Fortschritt, Budget und Ausgaben steuern.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/projekte/liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/projekte/liste/agent-contract` |
| Readiness | `GET /api/v1/masks/projekte/liste/readiness` |
| Rollout-Route | `/mask-rollout/projekte__liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/projekte`

**Beispiel-Prompts:**

- Welche Projekte liegen ueber Budget?
- Welche Projekte enden diesen Monat?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

## Domäne: crm

### `crm/activities` — Aktivitaeten

**Zweck:** Aktivitaeten als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/activities/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/activities/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/activities/readiness` |
| Rollout-Route | `/mask-rollout/crm__activities/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/crm/activities`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Aktivitaeten.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `crm/activity-detail` — Aktivitaet

**Zweck:** Aktivitaet als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/activity-detail/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/activity-detail/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/activity-detail/readiness` |
| Rollout-Route | `/mask-rollout/crm__activity-detail/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/crm/activities/{activity_id}`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Aktivitaet.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `crm/aktivitaet` — Aktivitaet

**Zweck:** Aktivitaetsdetail im CRM.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/aktivitaet/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/aktivitaet/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/aktivitaet/readiness` |
| Rollout-Route | `/mask-rollout/crm__aktivitaet/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/crm/activities/{entity_id}`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Wann ist Aktivitaet {entity_id} faellig?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `crm/aktivitaeten-liste` — Aktivitaeten

**Zweck:** Aktivitaeten: Eintraege finden und Details oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/aktivitaeten-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/aktivitaeten-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/aktivitaeten-liste/readiness` |
| Rollout-Route | `/mask-rollout/crm__aktivitaeten-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/crm/activities`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche offenen Aktivitaeten?
- Zeige aktuelle Aktivitaeten.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `crm/angebot-erstellen` — Angebot erstellen

**Zweck:** Angebot erstellen als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/angebot-erstellen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/angebot-erstellen/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/angebot-erstellen/readiness` |
| Rollout-Route | `/mask-rollout/crm__angebot-erstellen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/einkauf/angebote`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Angebot erstellen.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `crm/anruf-protokoll` — Anruf-Protokoll

**Zweck:** Anruf-Protokoll als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/anruf-protokoll/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/anruf-protokoll/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/anruf-protokoll/readiness` |
| Rollout-Route | `/mask-rollout/crm__anruf-protokoll/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/crm/activities`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Anruf-Protokoll.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `crm/bedarfsdeckung-cockpit` — Bedarfsdeckung

**Zweck:** Bedarfsdeckung und Pipeline je Kunde fuer Vertrieb und Agrar.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/bedarfsdeckung-cockpit/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/bedarfsdeckung-cockpit/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/bedarfsdeckung-cockpit/readiness` |
| Rollout-Route | `/mask-rollout/crm__bedarfsdeckung-cockpit/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/crm/bedarfsdeckung/pipeline`
- `pipeline` → `/api/v1/crm/bedarfsdeckung/pipeline`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Kunden haben ungedeckten Bedarf?
- Zeige die Bedarfsdeckungs-Pipeline.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `crm/bestell-inbox` — Bestell-Inbox

**Zweck:** Medienbruch zwischen Messenger und ERP reduzieren.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/bestell-inbox/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/bestell-inbox/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/bestell-inbox/readiness` |
| Rollout-Route | `/mask-rollout/crm__bestell-inbox/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `items` → `/api/v1/crm/bestell-inbox`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Bestellungen warten auf Bestaetigung?

---

### `crm/besuchsberichte` — Besuchsberichte

**Zweck:** Besuchsberichte als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/besuchsberichte/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/besuchsberichte/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/besuchsberichte/readiness` |
| Rollout-Route | `/mask-rollout/crm__besuchsberichte/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/crm/activities`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Besuchsberichte.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `crm/betreuungsgebiet` — Betreuungsgebiet

**Zweck:** Betreuungsgebiet als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/betreuungsgebiet/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/betreuungsgebiet/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/betreuungsgebiet/readiness` |
| Rollout-Route | `/mask-rollout/crm__betreuungsgebiet/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/crm/segments`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Betreuungsgebiet.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `crm/betriebsprofil` — Betriebsprofil

**Zweck:** Betriebsprofil fuer Agrarkunden.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/betriebsprofil/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/betriebsprofil/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/betriebsprofil/readiness` |
| Rollout-Route | `/mask-rollout/crm__betriebsprofil/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/crm/betriebsprofile/{entity_id}`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche VVVO hat Betrieb {entity_id}?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `crm/betriebsprofile-liste` — Betriebsprofile

**Zweck:** Betriebsprofile fuer Agrarberatung und CRM finden.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/betriebsprofile-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/betriebsprofile-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/betriebsprofile-liste/readiness` |
| Rollout-Route | `/mask-rollout/crm__betriebsprofile-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/crm/betriebsprofile`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Betriebe haben mehr als 200 ha?
- Zeige Betriebe mit Bio-Zertifikat.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `neu` | Neues Betriebsprofil | safe | nein | `Oeffnet die Anlage; Rechte prueft deren Anlageweg.` |
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `crm/bonus-vereinbarungen` — Bonus-Vereinbarungen

**Zweck:** Bonus-Vereinbarungen als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/bonus-vereinbarungen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/bonus-vereinbarungen/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/bonus-vereinbarungen/readiness` |
| Rollout-Route | `/mask-rollout/crm__bonus-vereinbarungen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/l3-report-catalog/bonus-runs`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Bonus-Vereinbarungen.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `crm/campaign` — Kampagne

**Zweck:** Kampagnendetail.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/campaign/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/campaign/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/campaign/readiness` |
| Rollout-Route | `/mask-rollout/crm__campaign/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/crm/campaigns/{entity_id}`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Welchen Status hat Kampagne {entity_id}?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `crm/campaign-performance` — Kampagnen-Performance

**Zweck:** Marketing-Kampagnenleistung gegen Ziele auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/campaign-performance/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/campaign-performance/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/campaign-performance/readiness` |
| Rollout-Route | `/mask-rollout/crm__campaign-performance/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/crm/dashboard`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Kampagne performt am besten?
- Zeige Conversion je Kampagne.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `crm/campaign-template` — Kampagnenvorlage

**Zweck:** Wiederverwendbare Kampagnenvorlage.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/campaign-template/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/campaign-template/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/campaign-template/readiness` |
| Rollout-Route | `/mask-rollout/crm__campaign-template/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/crm/campaigns/templates/{entity_id}`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Welchen Kanal nutzt Vorlage {entity_id}?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `crm/churn-risiko` — Churn-Risiko

**Zweck:** Churn-Risiko als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/churn-risiko/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/churn-risiko/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/churn-risiko/readiness` |
| Rollout-Route | `/mask-rollout/crm__churn-risiko/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/crm/dashboard`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Churn-Risiko.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `crm/consent` — Einwilligung

**Zweck:** Einwilligungsnachweis.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/consent/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/consent/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/consent/readiness` |
| Rollout-Route | `/mask-rollout/crm__consent/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/crm/consents/{entity_id}`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Ist Einwilligung {entity_id} aktiv?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `crm/contact-detail-liste` — Kontakte

**Zweck:** Kontakte finden und Detail oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/contact-detail-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/contact-detail-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/contact-detail-liste/readiness` |
| Rollout-Route | `/mask-rollout/crm__contact-detail-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/crm/contacts`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Kontakte haben offene Aufgaben?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `crm/crm-dashboard` — CRM-Dashboard

**Zweck:** CRM-KPIs und naechste Aktionen auf einen Blick.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/crm-dashboard/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/crm-dashboard/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/crm-dashboard/readiness` |
| Rollout-Route | `/mask-rollout/crm__crm-dashboard/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/crm/dashboard`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Wie steht die Pipeline?
- Welche Kunden brauchen Aufmerksamkeit?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `crm/cross-selling` — Cross-Selling

**Zweck:** Cross-Selling als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/cross-selling/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/cross-selling/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/cross-selling/readiness` |
| Rollout-Route | `/mask-rollout/crm__cross-selling/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/milchvieh-crosssell/summary`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Cross-Selling.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `crm/customer-360` — Kundenakte

**Zweck:** 360-Grad-Kundenakte fuer Vertrieb und CRM — Stammdaten, Aktivitaeten, Belege und Dokumente in einer Ansicht.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/customer-360/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/customer-360/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/customer-360/readiness` |
| Rollout-Route | `/mask-rollout/crm__customer-360/:entityId` |
| Adapter | `native` (temporary=nein) |

**Summary:** `/api/v1/crm/customers/{customer_id}/screen-summary`

**Data Sources:**

- `entity` → `/api/v1/crm/customers/{entity_id}`
- `contacts` → `/api/v1/crm/customers/{entity_id}/tabs/contacts`
- `auftraege` → `/api/v1/crm/customers/{entity_id}/tabs/auftraege`
- `aktivitaeten` → `/api/v1/crm/customers/{entity_id}/tabs/aktivitaeten`
- `dokumente` → `/api/v1/crm/customers/{entity_id}/tabs/dokumente`
- `aufgaben` → `/api/v1/crm/customers/{entity_id}/tabs/aufgaben`
- `kontrakte` → `/api/v1/crm/customers/{entity_id}/tabs/kontrakte`
- `angebote` → `/api/v1/crm/customers/{entity_id}/tabs/angebote`
- `historie` → `/api/v1/crm/customers/{entity_id}/tabs/historie`
- `praesente` → `/api/v1/crm/customers/{entity_id}/tabs/praesente`
- `chefanweisungen` → `/api/v1/crm/customers/{entity_id}/tabs/chefanweisungen`
- `anschriften` → `/api/v1/crm/customers/{entity_id}/tabs/anschriften`
- `cpd` → `/api/v1/crm/customers/{entity_id}/tabs/cpd`
- `rabatte` → `/api/v1/crm/customers/{entity_id}/tabs/rabatte`
- `preise` → `/api/v1/crm/customers/{entity_id}/tabs/preise`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Analysiere Kunde {entity_id}: offene Posten, letzte Aktivitaeten, Umsatz 12M.
- Lege eine Aktivitaet fuer Kunde {entity_id} an — Betreff: {betreff}, Typ: Anruf.
- Zeige alle offenen Auftraege von Kunde {entity_id} mit Status 'offen'.

**Sensible Felder:** `iban, bic, kreditlimit, zahlungsbedingungen, notizen`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `/api/v1/crm/customers/{entity_id}/actions/bearbeiten` |
| `edit` | Erweiterte Pflege | safe | nein | `—` |
| `create_activity` | Aktivitaet anlegen | safe | nein | `/api/v1/crm/customers/{entity_id}/actions/create_activity` |

---

### `crm/dokumente-kunden` — Kundendokumente

**Zweck:** Kundendokumente als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/dokumente-kunden/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/dokumente-kunden/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/dokumente-kunden/readiness` |
| Rollout-Route | `/mask-rollout/crm__dokumente-kunden/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/dokumente`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Kundendokumente.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `crm/dsgvo-anfragen-liste` — DSGVO-Anfragen

**Zweck:** Betroffenenanfragen fristgerecht pruefen, beantworten, loeschen oder begruendet ablehnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/dsgvo-anfragen-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/dsgvo-anfragen-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/dsgvo-anfragen-liste/readiness` |
| Rollout-Route | `/mask-rollout/crm__dsgvo-anfragen-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/gdpr/requests`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche DSGVO-Anfragen sind noch offen?
- Welche Loeschanfragen sind geprueft?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `neu` | Anfrage erfassen | safe | nein | `Oeffnet die Anlage; Rechte prueft deren Anlageweg.` |

---

### `crm/dubletten-pruefung` — Dubletten-Pruefung

**Zweck:** Dubletten-Pruefung als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/dubletten-pruefung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/dubletten-pruefung/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/dubletten-pruefung/readiness` |
| Rollout-Route | `/mask-rollout/crm__dubletten-pruefung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/crm/duplicates`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Dubletten-Pruefung.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `crm/einwilligungen-liste` — Einwilligungen

**Zweck:** Einwilligungen je Kontakt und Kanal nachweisen und auf Wunsch widerrufen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/einwilligungen-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/einwilligungen-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/einwilligungen-liste/readiness` |
| Rollout-Route | `/mask-rollout/crm__einwilligungen-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/crm/consents`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Einwilligungen warten auf Double-Opt-in?
- Welche Einwilligungen wurden widerrufen?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `neu` | Einwilligung erfassen | safe | nein | `Oeffnet die Anlage; Rechte prueft deren Anlageweg.` |
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `crm/events-messen` — Events und Messen

**Zweck:** Events und Messen als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/events-messen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/events-messen/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/events-messen/readiness` |
| Rollout-Route | `/mask-rollout/crm__events-messen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/marketing/kampagnen`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Events und Messen.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `crm/gdpr-request` — DSGVO-Anfrage

**Zweck:** DSGVO-Anfrage bearbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/gdpr-request/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/gdpr-request/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/gdpr-request/readiness` |
| Rollout-Route | `/mask-rollout/crm__gdpr-request/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/gdpr/requests/{entity_id}`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Welchen Status hat Anfrage {entity_id}?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `crm/gebietsschutz` — Gebietsschutz

**Zweck:** Gebietsschutz als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/gebietsschutz/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/gebietsschutz/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/gebietsschutz/readiness` |
| Rollout-Route | `/mask-rollout/crm__gebietsschutz/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/crm/ownership/unassigned`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Gebietsschutz.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `crm/geschenke-liste` — Geschenke

**Zweck:** Geschenke als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/geschenke-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/geschenke-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/geschenke-liste/readiness` |
| Rollout-Route | `/mask-rollout/crm__geschenke-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/crm/kim/customers/{kunden_nr}/gifts`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Geschenke.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `crm/interaktions-historie` — Interaktions-Historie

**Zweck:** Interaktions-Historie als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/interaktions-historie/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/interaktions-historie/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/interaktions-historie/readiness` |
| Rollout-Route | `/mask-rollout/crm__interaktions-historie/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/crm/customers/{customer_id}/tabs/historie`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Interaktions-Historie.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `crm/kampagne-detail` — Kampagne

**Zweck:** Kampagne als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/kampagne-detail/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/kampagne-detail/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/kampagne-detail/readiness` |
| Rollout-Route | `/mask-rollout/crm__kampagne-detail/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/marketing/kampagnen`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Kampagne.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `crm/kampagne-erstellen` — Kampagne erstellen

**Zweck:** Kampagne erstellen als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/kampagne-erstellen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/kampagne-erstellen/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/kampagne-erstellen/readiness` |
| Rollout-Route | `/mask-rollout/crm__kampagne-erstellen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/marketing/kampagnen`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Kampagne erstellen.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `crm/kampagnen-liste` — Kampagnen

**Zweck:** Kampagnen mit Versand-, Oeffnungs- und Klickzahlen finden und oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/kampagnen-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/kampagnen-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/kampagnen-liste/readiness` |
| Rollout-Route | `/mask-rollout/crm__kampagnen-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/crm/campaigns`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Kampagnen sind noch im Entwurf?
- Welche Kampagne hat die meisten Klicks?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `neu` | Neue Kampagne | safe | nein | `Oeffnet die Anlage; Rechte prueft deren Anlageweg.` |
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `crm/kampagnenvorlagen-liste` — Kampagnenvorlagen

**Zweck:** Kampagnenvorlagen pflegen: aktivieren, deaktivieren, duplizieren.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/kampagnenvorlagen-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/kampagnenvorlagen-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/kampagnenvorlagen-liste/readiness` |
| Rollout-Route | `/mask-rollout/crm__kampagnenvorlagen-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/crm/campaigns/templates`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Vorlagen sind aktiv?
- Welche Vorlage wird am haeufigsten verwendet?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `neu` | Neue Vorlage | safe | nein | `Oeffnet die Anlage; Rechte prueft deren Anlageweg.` |
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `crm/kaufverhalten` — Kaufverhalten

**Zweck:** Kaufverhalten als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/kaufverhalten/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/kaufverhalten/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/kaufverhalten/readiness` |
| Rollout-Route | `/mask-rollout/crm__kaufverhalten/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/sales/reports/top-customers`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Kaufverhalten.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `crm/klaerfall-inbox` — Klaerfall-Inbox

**Zweck:** KIM-Erfassungen ohne Kundenmatch sichtbar machen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/klaerfall-inbox/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/klaerfall-inbox/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/klaerfall-inbox/readiness` |
| Rollout-Route | `/mask-rollout/crm__klaerfall-inbox/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `items` → `/api/v1/crm/kim/capture-inbox`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Klaerfaelle sind offen?

---

### `crm/kommunikation-center` — Kommunikations-Center

**Zweck:** Kommunikations-Center als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/kommunikation-center/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/kommunikation-center/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/kommunikation-center/readiness` |
| Rollout-Route | `/mask-rollout/crm__kommunikation-center/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/query-center/catalog`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Kommunikations-Center.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `crm/kontakt` — Kontakt

**Zweck:** Kontaktstammdaten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/kontakt/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/kontakt/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/kontakt/readiness` |
| Rollout-Route | `/mask-rollout/crm__kontakt/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/crm/contacts/{entity_id}`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche E-Mail hat Kontakt {entity_id}?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `crm/kontakt-management-liste` — Kontakt-Management

**Zweck:** Kontakte im Management finden.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/kontakt-management-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/kontakt-management-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/kontakt-management-liste/readiness` |
| Rollout-Route | `/mask-rollout/crm__kontakt-management-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/crm/contacts`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Kontakte sind ueberfaellig?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `crm/kontakte-liste` — Kontakte

**Zweck:** Kontakte finden und die Kontaktakte oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/kontakte-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/kontakte-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/kontakte-liste/readiness` |
| Rollout-Route | `/mask-rollout/crm__kontakte-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/crm/contacts`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Kontakte gehoeren zu diesem Kunden?
- Zeige Lieferanten-Kontakte.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `neu` | Neuer Kontakt | safe | nein | `Oeffnet die Anlage; Rechte prueft deren Anlageweg.` |
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `crm/kunden-cockpit` — Kunden-Cockpit

**Zweck:** Vom Kunden-Cockpit in Akte, Offene Posten und Kontrakte springen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/kunden-cockpit/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/kunden-cockpit/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/kunden-cockpit/readiness` |
| Rollout-Route | `/mask-rollout/crm__kunden-cockpit/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/crm/dashboard`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Oeffne die Kundenakte.
- Zeige offene CRM-Aufgaben.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `crm/kunden-liste` — Kunden

**Zweck:** Kunden im operativen Stamm finden und die Kundenakte oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/kunden-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/kunden-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/kunden-liste/readiness` |
| Rollout-Route | `/mask-rollout/crm__kunden-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/crm/customers/lookup?q=&limit=1000`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Kunden sind in Hamburg?
- Zeige gesperrte Kunden.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `neu` | Neuer Kunde | safe | nein | `Oeffnet die Anlage; Rechte prueft deren Anlageweg.` |
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `crm/lead` — Kundenakte

**Zweck:** Lead-Akte: Kundenpotenzial mit Aktivitaeten und Aufgaben fuer Vertriebssteuerung.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/lead/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/lead/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/lead/readiness` |
| Rollout-Route | `/mask-rollout/crm__lead/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/crm/leads/{entity_id}`
- `aktivitaeten` → `/api/v1/masks/crm/leads/entity/{entity_id}/tabs/aktivitaeten`
- `aufgaben` → `/api/v1/masks/crm/leads/entity/{entity_id}/tabs/aufgaben`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Was ist der Status von Lead {entity_id}?
- Zeige alle offenen Aufgaben fuer Lead {entity_id}.
- Welche Aktivitaeten wurden fuer Lead {entity_id} erfasst?

**Sensible Felder:** `wert`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `/api/v1/crm/leads/{entity_id}/actions/bearbeiten` |
| `qualifizieren` | Als Opportunity qualifizieren | safe | nein | `/api/v1/crm/leads/{entity_id}/actions/qualifizieren` |

---

### `crm/leads-liste` — Leads

**Zweck:** Leads: Eintraege finden und Details oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/leads-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/leads-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/leads-liste/readiness` |
| Rollout-Route | `/mask-rollout/crm__leads-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/crm/leads`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche offenen Leads?
- Zeige aktuelle Leads.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `neu` | Neu | safe | nein | `Oeffnet die Anlage; Rechte prueft deren Anlageweg.` |
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `crm/lieferant` — Lieferant

**Zweck:** Lieferantenstamm CRM.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/lieferant/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/lieferant/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/lieferant/readiness` |
| Rollout-Route | `/mask-rollout/crm__lieferant/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/crm/business-partners/{entity_id}`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Ist Lieferant {entity_id} aktiv?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `crm/lieferanten-liste` — Lieferanten

**Zweck:** Lieferanten finden und Stammdaten oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/lieferanten-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/lieferanten-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/lieferanten-liste/readiness` |
| Rollout-Route | `/mask-rollout/crm__lieferanten-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/crm/suppliers`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Lieferanten sind aktiv?
- Zeige Lieferanten mit Skonto.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `neu` | Neuer Lieferant | safe | nein | `Oeffnet die Anlage; Rechte prueft deren Anlageweg.` |
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `crm/mail-arbeitsplatz` — Mail-Arbeitsplatz

**Zweck:** Rollenpostfaecher revisionssicher mit Kontakten und Belegen verbinden.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/mail-arbeitsplatz/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/mail-arbeitsplatz/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/mail-arbeitsplatz/readiness` |
| Rollout-Route | `/mask-rollout/crm__mail-arbeitsplatz/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `messages` → `/api/v1/mail-workspace`
- `attachments` → `/api/v1/mail-workspace/attachments`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige unzugeordnete CRM-Mails.
- Welche Anlagen warten auf DMS-Uebernahme?

**Sensible Felder:** `from_address, to_addresses, subject, body_text, contact_id`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `draft` | Neue Mail | safe | nein | `—` |

---

### `crm/opportunities-liste` — Verkaufschancen

**Zweck:** Verkaufschancen nach Phase und Betrag steuern, Angebote erstellen und abschliessen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/opportunities-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/opportunities-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/opportunities-liste/readiness` |
| Rollout-Route | `/mask-rollout/crm__opportunities-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/crm/opportunities/`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Chancen schliessen diesen Monat?
- Welche Chancen haben ueber 70 % Wahrscheinlichkeit?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `neu` | Neue Chance | safe | nein | `Oeffnet die Anlage; Rechte prueft deren Anlageweg.` |
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |
| `kanban` | Pipeline-Ansicht | safe | nein | `Oeffnet die Pipeline als Kanban.` |

---

### `crm/opportunity` — Opportunity

**Zweck:** CRM-Verkaufschance: Phase, Wert, Wahrscheinlichkeit, Aktivitaeten und Angebote in einer Ansicht fuer Vertriebssteuerung.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/opportunity/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/opportunity/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/opportunity/readiness` |
| Rollout-Route | `/mask-rollout/crm__opportunity/:entityId` |
| Adapter | `native` (temporary=nein) |

**Summary:** `/api/v1/mask-rollouts/crm/opportunity/{entity_id}/screen-summary`

**Data Sources:**

- `entity` → `/api/v1/crm/opportunities/{entity_id}`
- `aktivitaeten` → `/api/v1/mask-rollouts/crm/opportunity/{entity_id}/tabs/aktivitaeten`
- `angebote` → `/api/v1/mask-rollouts/crm/opportunity/{entity_id}/tabs/angebote`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Was ist der aktuelle Status und die Wahrscheinlichkeit von Opportunity {entity_id}?
- Zeige alle Aktivitaeten der letzten 30 Tage fuer Opportunity {entity_id}.
- Welche Angebote sind mit Opportunity {entity_id} verknuepft?

**Sensible Felder:** `wert, wahrscheinlichkeit`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `/api/v1/crm/opportunities/{entity_id}/actions/bearbeiten` |
| `create_activity` | Aktivitaet anlegen | safe | nein | `/api/v1/crm/opportunities/{entity_id}/actions/create_activity` |

---

### `crm/segment` — Segment

**Zweck:** Segmentdefinition.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/segment/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/segment/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/segment/readiness` |
| Rollout-Route | `/mask-rollout/crm__segment/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/crm/segments/{entity_id}`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Wie viele Mitglieder hat Segment {entity_id}?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `crm/segmente-liste` — Segmente

**Zweck:** Kundensegmente finden, Mitglieder neu berechnen und nicht mehr genutzte entfernen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/segmente-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/segmente-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/segmente-liste/readiness` |
| Rollout-Route | `/mask-rollout/crm__segmente-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/crm/segments`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Wie viele Mitglieder hat jedes Segment?
- Welche Segmente sind lange nicht berechnet?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `neu` | Neues Segment | safe | nein | `Oeffnet die Anlage; Rechte prueft deren Anlageweg.` |
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `crm/vertreter` — Vertreter

**Zweck:** Vertreterstammdaten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/vertreter/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/vertreter/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/vertreter/readiness` |
| Rollout-Route | `/mask-rollout/crm__vertreter/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/crm/vertreter/{entity_id}`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Gruppe hat Vertreter {entity_id}?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `crm/wettbewerber` — Wettbewerber

**Zweck:** Wettbewerber als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/wettbewerber/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/wettbewerber/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/wettbewerber/readiness` |
| Rollout-Route | `/mask-rollout/crm__wettbewerber/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/crm/dashboard`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Wettbewerber.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `crm/wiedervorlagen` — Wiedervorlagen

**Zweck:** Faellige Rueckrufe und Aufgaben abarbeiten; das Ergebnis wird an die Kontaktnotiz angehaengt.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/wiedervorlagen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/wiedervorlagen/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/wiedervorlagen/readiness` |
| Rollout-Route | `/mask-rollout/crm__wiedervorlagen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/crm/kunden-kontakte/wiedervorlagen?tage=365`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Wiedervorlagen sind ueberfaellig?
- Was steht diese Woche fuer Kunde X an?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `crm/zielgruppen` — Zielgruppen

**Zweck:** Zielgruppen als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/zielgruppen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/zielgruppen/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/zielgruppen/readiness` |
| Rollout-Route | `/mask-rollout/crm__zielgruppen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/crm/segments`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.customer.open` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel
- `crm.activity.create` — scope `crm:write`, Risiko mittel
- `crm.lead.qualify` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Zielgruppen.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

## Domäne: dms

### `dokumente/ablage-liste` — Dokumentenablage

**Zweck:** Dokumente in der Ablage finden und herunterladen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/dokumente/ablage-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/dokumente/ablage-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/dokumente/ablage-liste/readiness` |
| Rollout-Route | `/mask-rollout/dokumente__ablage-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/dokumente`

**Beispiel-Prompts:**

- Welche Dokumente wurden heute hochgeladen?
- Zeige Vertraege in der Ablage.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

## Domäne: dms-compliance

### `dms/inbox` — DMS-Eingangskorb

**Zweck:** Eingescannte Belege priorisieren und in den Belegfluss ueberfuehren.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/dms/inbox/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/dms/inbox/agent-contract` |
| Readiness | `GET /api/v1/masks/dms/inbox/readiness` |
| Rollout-Route | `/mask-rollout/dms__inbox/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `items` → `/api/v1/dms/inbox`

**Beispiel-Prompts:**

- Welche Inbox-Dokumente haben niedrige OCR-Konfidenz?

---

### `docflow/artefakt-freigabe` — Artefakt-Freigabe

**Zweck:** Artefakt-Lebenszyklus entwurf→freigegeben→archiviert steuern.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/docflow/artefakt-freigabe/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/docflow/artefakt-freigabe/agent-contract` |
| Readiness | `GET /api/v1/masks/docflow/artefakt-freigabe/readiness` |
| Rollout-Route | `/mask-rollout/docflow__artefakt-freigabe/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `artifacts` → `/api/v1/docflow/evidence/artifacts`

**Beispiel-Prompts:**

- Welche Artefakte warten auf Freigabe?

---

### `docflow/dokumenten-ruecklauf` — Dokumentenruecklauf

**Zweck:** Dokumentenversand und erwartete Ruecklaeufe mandantensicher bearbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/docflow/dokumenten-ruecklauf/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/docflow/dokumenten-ruecklauf/agent-contract` |
| Readiness | `GET /api/v1/masks/docflow/dokumenten-ruecklauf/readiness` |
| Rollout-Route | `/mask-rollout/docflow__dokumenten-ruecklauf/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/docflow/returns/summary`
- `returns` → `/api/v1/docflow/returns`

**Beispiel-Prompts:**

- Zeige ueberfaellige Ruecklaeufe.
- Welche Dokumente wurden noch nicht versendet?

**Sensible Felder:** `contact_ref, subject_ref, storage_key`

---

### `docflow/gobd-export` — GoBD-Export

**Zweck:** GoBD-Exporte aus dem Nachweisraum anstossen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/docflow/gobd-export/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/docflow/gobd-export/agent-contract` |
| Readiness | `GET /api/v1/masks/docflow/gobd-export/readiness` |
| Rollout-Route | `/mask-rollout/docflow__gobd-export/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `documents` → `/api/v1/docflow/evidence/documents`

**Beispiel-Prompts:**

- Welche Vorgaenge haben offene Artefakte?

---

### `docflow/nachweisraum` — Nachweisraum

**Zweck:** Nachweisraum-Worklist fuer Audit und GoBD.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/docflow/nachweisraum/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/docflow/nachweisraum/agent-contract` |
| Readiness | `GET /api/v1/masks/docflow/nachweisraum/readiness` |
| Rollout-Route | `/mask-rollout/docflow__nachweisraum/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `documents` → `/api/v1/docflow/evidence/documents`

**Beispiel-Prompts:**

- Zeige Vorgaenge ohne freigegebene Artefakte.

---

### `docflow/wiedervorlagen` — Docflow-Wiedervorlagen

**Zweck:** Follow-ups im Nachweisraum nicht verlieren.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/docflow/wiedervorlagen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/docflow/wiedervorlagen/agent-contract` |
| Readiness | `GET /api/v1/masks/docflow/wiedervorlagen/readiness` |
| Rollout-Route | `/mask-rollout/docflow__wiedervorlagen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `items` → `/api/v1/docflow/evidence/wiedervorlagen`

**Beispiel-Prompts:**

- Welche Wiedervorlagen sind ueberfaellig?

---

### `inbox` — Posteingang

**Zweck:** Kurzroute /inbox auf dieselbe DMS-Inbox-Queue.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/inbox/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/inbox/agent-contract` |
| Readiness | `GET /api/v1/masks/inbox/readiness` |
| Rollout-Route | `/mask-rollout/inbox/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `items` → `/api/v1/dms/inbox`

**Beispiel-Prompts:**

- Was liegt im Posteingang?

---

## Domäne: documents

### `auswertungen/dms-volltext` — Volltextsuche Dokumentenverwaltung

**Zweck:** Tenant-sicher Dokumente wiederfinden und zum Quellobjekt springen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/auswertungen/dms-volltext/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/auswertungen/dms-volltext/agent-contract` |
| Readiness | `GET /api/v1/masks/auswertungen/dms-volltext/readiness` |
| Rollout-Route | `/mask-rollout/auswertungen__dms-volltext/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/dms/search`
- `documents` → `/api/v1/dms/search`

**Beispiel-Prompts:**

- Suche Dokumente mit dieser Belegnummer.
- Zeige Zertifikate zu diesem Artikel.

**Sensible Felder:** `description, document_name, article_name`

---

### `belege/belegfolge` — Belegfolge

**Zweck:** Belegfolge als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/belege/belegfolge/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/belege/belegfolge/agent-contract` |
| Readiness | `GET /api/v1/masks/belege/belegfolge/readiness` |
| Rollout-Route | `/mask-rollout/belege__belegfolge/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/docflow/`

**Beispiel-Prompts:**

- Zeige Belegfolge.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `dms/archiv-suche` — Archiv-Suche

**Zweck:** Archiv-Suche als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/dms/archiv-suche/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/dms/archiv-suche/agent-contract` |
| Readiness | `GET /api/v1/masks/dms/archiv-suche/readiness` |
| Rollout-Route | `/mask-rollout/dms__archiv-suche/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/dms/search`

**Beispiel-Prompts:**

- Zeige Archiv-Suche.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `dms/beleg-erkennung` — Beleg-Erkennung

**Zweck:** Beleg-Erkennung als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/dms/beleg-erkennung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/dms/beleg-erkennung/agent-contract` |
| Readiness | `GET /api/v1/masks/dms/beleg-erkennung/readiness` |
| Rollout-Route | `/mask-rollout/dms__beleg-erkennung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/process/dms/erkennungsregeln`

**Beispiel-Prompts:**

- Zeige Beleg-Erkennung.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `dms/dokument-detail` — Dokument

**Zweck:** Dokument als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/dms/dokument-detail/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/dms/dokument-detail/agent-contract` |
| Readiness | `GET /api/v1/masks/dms/dokument-detail/readiness` |
| Rollout-Route | `/mask-rollout/dms__dokument-detail/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/dms/documents`

**Beispiel-Prompts:**

- Zeige Dokument.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `dms/dokument-upload` — Dokument-Upload

**Zweck:** Dokument-Upload als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/dms/dokument-upload/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/dms/dokument-upload/agent-contract` |
| Readiness | `GET /api/v1/masks/dms/dokument-upload/readiness` |
| Rollout-Route | `/mask-rollout/dms__dokument-upload/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/dms/documents`

**Beispiel-Prompts:**

- Zeige Dokument-Upload.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `dms/freigabe-workflow` — Freigabe-Workflow

**Zweck:** Freigabe-Workflow als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/dms/freigabe-workflow/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/dms/freigabe-workflow/agent-contract` |
| Readiness | `GET /api/v1/masks/dms/freigabe-workflow/readiness` |
| Rollout-Route | `/mask-rollout/dms__freigabe-workflow/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/docflow/evidence/artifacts`

**Beispiel-Prompts:**

- Zeige Freigabe-Workflow.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `dms/posteingang` — Posteingang

**Zweck:** Posteingang als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/dms/posteingang/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/dms/posteingang/agent-contract` |
| Readiness | `GET /api/v1/masks/dms/posteingang/readiness` |
| Rollout-Route | `/mask-rollout/dms__posteingang/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/dms/inbox`

**Beispiel-Prompts:**

- Zeige Posteingang.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `dms/verschlagwortung` — Verschlagwortung

**Zweck:** Verschlagwortung als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/dms/verschlagwortung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/dms/verschlagwortung/agent-contract` |
| Readiness | `GET /api/v1/masks/dms/verschlagwortung/readiness` |
| Rollout-Route | `/mask-rollout/dms__verschlagwortung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/dms/documents`

**Beispiel-Prompts:**

- Zeige Verschlagwortung.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `dms/vorlagen-verwaltung` — Vorlagen-Verwaltung

**Zweck:** Vorlagen-Verwaltung als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/dms/vorlagen-verwaltung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/dms/vorlagen-verwaltung/agent-contract` |
| Readiness | `GET /api/v1/masks/dms/vorlagen-verwaltung/readiness` |
| Rollout-Route | `/mask-rollout/dms__vorlagen-verwaltung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/process/template/vorlagen`

**Beispiel-Prompts:**

- Zeige Vorlagen-Verwaltung.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `dokumente/archiv` — Dokumentarchiv

**Zweck:** Dokumentarchiv als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/dokumente/archiv/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/dokumente/archiv/agent-contract` |
| Readiness | `GET /api/v1/masks/dokumente/archiv/readiness` |
| Rollout-Route | `/mask-rollout/dokumente__archiv/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/process/archiv/eintraege`

**Beispiel-Prompts:**

- Zeige Dokumentarchiv.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `dokumente/eingang` — Dokumenteingang

**Zweck:** Dokumenteingang als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/dokumente/eingang/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/dokumente/eingang/agent-contract` |
| Readiness | `GET /api/v1/masks/dokumente/eingang/readiness` |
| Rollout-Route | `/mask-rollout/dokumente__eingang/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/dms/inbox`

**Beispiel-Prompts:**

- Zeige Dokumenteingang.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `dokumente/suche` — Dokumentensuche

**Zweck:** Dokumentensuche als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/dokumente/suche/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/dokumente/suche/agent-contract` |
| Readiness | `GET /api/v1/masks/dokumente/suche/readiness` |
| Rollout-Route | `/mask-rollout/dokumente__suche/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/dms/search`

**Beispiel-Prompts:**

- Zeige Dokumentensuche.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `dokumente/vorlagen` — Dokumentvorlagen

**Zweck:** Dokumentvorlagen als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/dokumente/vorlagen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/dokumente/vorlagen/agent-contract` |
| Readiness | `GET /api/v1/masks/dokumente/vorlagen/readiness` |
| Rollout-Route | `/mask-rollout/dokumente__vorlagen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/process/template/vorlagen`

**Beispiel-Prompts:**

- Zeige Dokumentvorlagen.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

## Domäne: einkauf

### `dashboard/einkauf` — Einkaufs-Dashboard

**Zweck:** Einkaufslage mit KPIs und Sprung in Bestell- und Avis-Masken.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/dashboard/einkauf/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/dashboard/einkauf/agent-contract` |
| Readiness | `GET /api/v1/masks/dashboard/einkauf/readiness` |
| Rollout-Route | `/mask-rollout/dashboard__einkauf/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/purchase-orders/statistics`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Wie viele offene Bestellungen gibt es?
- Zeige ueberfaellige Lieferungen.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `einkauf/anfrage` — Einkaufsanfrage

**Zweck:** Einkaufsanfrage: Kopfdaten und Positionen fuer Beschaffungsanfragen an Lieferanten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/anfrage/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/anfrage/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/anfrage/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__anfrage/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/einkauf/anfragen/{entity_id}`
- `positionen` → `/api/v1/masks/einkauf/anfragen/entity/{entity_id}/tabs/positionen`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Was ist der Status von Anfrage {entity_id}?
- Zeige alle Positionen von Anfrage {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `/api/v1/einkauf/anfragen/{entity_id}/actions/bearbeiten` |

---

### `einkauf/anfrage-erstellen` — Anfrage erstellen

**Zweck:** Anfrage erstellen als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/anfrage-erstellen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/anfrage-erstellen/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/anfrage-erstellen/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__anfrage-erstellen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/einkauf/anfragen`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Anfrage erstellen.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `einkauf/anfragen` — Anfragen

**Zweck:** Bedarfsanforderungen des Einkaufs finden, an Lieferanten senden und in Bestellungen ueberfuehren.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/anfragen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/anfragen/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/anfragen/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__anfragen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/einkauf/anfragen`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Anfragen sind noch im Entwurf?
- Zeige dringende Anfragen.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `neu` | Neue Anfrage | safe | nein | `Oeffnet die Anlage; Rechte prueft deren Anlageweg.` |
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `einkauf/anfragen-create-liste` — Anfragen

**Zweck:** Anfragen vor Anlage finden.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/anfragen-create-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/anfragen-create-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/anfragen-create-liste/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__anfragen-create-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/einkauf/anfragen`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Anfragen sind Entwurf?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `einkauf/angebot` — Lieferantenangebot

**Zweck:** Lieferantenangebot: Preise und Positionen fuer Angebotsvergleich und Bestellentscheidung.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/angebot/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/angebot/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/angebot/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__angebot/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/einkauf/angebote/{entity_id}`
- `positionen` → `/api/v1/masks/einkauf/angebote/entity/{entity_id}/tabs/positionen`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Wie lange ist Angebot {entity_id} gueltig?
- Zeige alle Positionen und Preise von Angebot {entity_id}.

**Sensible Felder:** `gesamtbetrag, einzelpreis`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bestellen` | Bestellung erstellen | safe | nein | `/api/v1/einkauf/angebote/{entity_id}/actions/bestellen` |

---

### `einkauf/angebot-erfassen` — Angebot erfassen

**Zweck:** Angebot erfassen als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/angebot-erfassen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/angebot-erfassen/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/angebot-erfassen/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__angebot-erfassen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/einkauf/angebote`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Angebot erfassen.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `einkauf/angebote` — Angebote

**Zweck:** Lieferantenangebote vergleichen, pruefen, genehmigen und in Bestellungen ueberfuehren.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/angebote/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/angebote/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/angebote/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__angebote/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/einkauf/angebote`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Angebote warten auf Pruefung?
- Welche Angebote laufen diese Woche ab?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `neu` | Neues Angebot | safe | nein | `Oeffnet die Anlage; Rechte prueft deren Anlageweg.` |
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `einkauf/angebote-vergleich-liste` — Angebotsvergleich

**Zweck:** Angebote zum Vergleich finden.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/angebote-vergleich-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/angebote-vergleich-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/angebote-vergleich-liste/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__angebote-vergleich-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/einkauf/angebote`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Angebote zur Anfrage X?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `einkauf/anlieferavis` — Anlieferavis

**Zweck:** Anlieferavis: Ankuendigung eines Wareneingangs mit Positionen und Lieferdatum.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/anlieferavis/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/anlieferavis/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/anlieferavis/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__anlieferavis/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/einkauf/anlieferavis/{entity_id}`
- `positionen` → `/api/v1/masks/einkauf/anlieferavise/entity/{entity_id}/tabs/positionen`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Wann ist Avis {entity_id} angekuendigt?
- Zeige alle Positionen von Avis {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `wareneingang` | Wareneingang buchen | moderate | nein | `/api/v1/einkauf/anlieferavis/{entity_id}/actions/wareneingang` |

---

### `einkauf/anlieferavis-erfassen` — Anlieferavis erfassen

**Zweck:** Anlieferavis erfassen als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/anlieferavis-erfassen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/anlieferavis-erfassen/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/anlieferavis-erfassen/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__anlieferavis-erfassen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/einkauf/anlieferavis`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Anlieferavis erfassen.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `einkauf/anlieferavis-liste` — Anlieferavis

**Zweck:** Angekuendigte Lieferungen verfolgen, bestaetigen und als Wareneingang buchen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/anlieferavis-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/anlieferavis-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/anlieferavis-liste/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__anlieferavis-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/einkauf/anlieferavis`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Lieferungen sind fuer diese Woche angekuendigt?
- Welche Avise sind noch offen?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `einkauf/auftragsbestaetigung` — Auftragsbestaetigung

**Zweck:** Auftragsbestaetigung: Lieferanten-Rueckmeldung auf Bestellung mit zugesagtem Liefertermin.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/auftragsbestaetigung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/auftragsbestaetigung/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/auftragsbestaetigung/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__auftragsbestaetigung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/einkauf/auftragsbestaetigungen/{entity_id}`
- `positionen` → `/api/v1/masks/einkauf/auftragsbestaetigungen/entity/{entity_id}/tabs/positionen`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Wann hat Lieferant den Liefertermin fuer AB {entity_id} zugesagt?
- Zeige alle Positionen von AB {entity_id}.

**Sensible Felder:** `einzelpreis`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `pruefen` | Pruefen | safe | nein | `/api/v1/einkauf/auftragsbestaetigungen/{entity_id}/actions/pruefen` |
| `bestaetigen` | Bestaetigen | moderate | nein | `/api/v1/einkauf/auftragsbestaetigungen/{entity_id}/actions/bestaetigen` |

---

### `einkauf/auftragsbestaetigung-erfassen` — Auftragsbestaetigung

**Zweck:** Auftragsbestaetigung als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/auftragsbestaetigung-erfassen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/auftragsbestaetigung-erfassen/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/auftragsbestaetigung-erfassen/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__auftragsbestaetigung-erfassen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/einkauf/auftragsbestaetigungen`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Auftragsbestaetigung.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `einkauf/auftragsbestaetigungen` — Auftragsbestaetigungen

**Zweck:** Lieferanten-Bestaetigungen gegen Bestellungen pruefen und bestaetigen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/auftragsbestaetigungen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/auftragsbestaetigungen/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/auftragsbestaetigungen/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__auftragsbestaetigungen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/einkauf/auftragsbestaetigungen`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Auftragsbestaetigungen sind noch ungeprueft?
- Zeige Bestaetigungen mit Abweichung.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `neu` | AB erfassen | safe | nein | `Oeffnet die Anlage; Rechte prueft deren Anlageweg.` |
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `einkauf/bestellung-freigabe` — Bestellfreigabe

**Zweck:** Bestellfreigabe als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/bestellung-freigabe/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/bestellung-freigabe/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/bestellung-freigabe/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__bestellung-freigabe/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/einkauf/bestellungen`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Bestellfreigabe.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `einkauf/bestellungen` — Bestellungen

**Zweck:** Bestellungen an Lieferanten finden, freigeben, versenden und stornieren.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/bestellungen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/bestellungen/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/bestellungen/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__bestellungen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/einkauf/bestellungen`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Bestellungen sind noch Entwurf?
- Welche Liefertermine sind ueberfaellig?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `neu` | Neue Bestellung | safe | nein | `Oeffnet die Anlage; Rechte prueft deren Anlageweg.` |
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `einkauf/bestellvorschlaege-liste` — Bestellvorschlaege

**Zweck:** Bestellvorschlaege: Eintraege finden und Details oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/bestellvorschlaege-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/bestellvorschlaege-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/bestellvorschlaege-liste/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__bestellvorschlaege-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/einkauf/bestellvorschlaege`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche offenen Bestellvorschlaege?
- Zeige aktuelle Bestellvorschlaege.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `einkauf/bestellvorschlag-kontrakt` — Bestellvorschlag Kontrakt

**Zweck:** Bestellvorschlag Kontrakt als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/bestellvorschlag-kontrakt/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/bestellvorschlag-kontrakt/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/bestellvorschlag-kontrakt/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__bestellvorschlag-kontrakt/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/einkauf/bestellvorschlaege/rohware`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Bestellvorschlag Kontrakt.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `einkauf/bestellvorschlag-lager` — Bestellvorschlag Lager

**Zweck:** Bestellvorschlag Lager als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/bestellvorschlag-lager/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/bestellvorschlag-lager/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/bestellvorschlag-lager/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__bestellvorschlag-lager/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/einkauf/bestellvorschlaege/lager`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Bestellvorschlag Lager.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `einkauf/bestellvorschlag-verbrauch` — Bestellvorschlag Verbrauch

**Zweck:** Bestellvorschlag Verbrauch als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/bestellvorschlag-verbrauch/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/bestellvorschlag-verbrauch/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/bestellvorschlag-verbrauch/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__bestellvorschlag-verbrauch/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/einkauf/bestellvorschlaege/bedarf`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Bestellvorschlag Verbrauch.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `einkauf/dienstleistungen-haltung-liste` — Dienstleistungen Haltung

**Zweck:** Dienstleistungsbestellungen finden.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/dienstleistungen-haltung-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/dienstleistungen-haltung-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/dienstleistungen-haltung-liste/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__dienstleistungen-haltung-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/einkauf/bestellungen`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche DL-Bestellungen sind offen?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `einkauf/einkauf-vorgang-liste` — Einkaufsvorgaenge

**Zweck:** Einkaufsvorgaenge finden.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/einkauf-vorgang-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/einkauf-vorgang-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/einkauf-vorgang-liste/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__einkauf-vorgang-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/einkauf/bestellungen`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Vorgaenge warten auf Freigabe?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `einkauf/frachtauftraege-liste` — Frachtauftraege

**Zweck:** Frachtauftraege: Eintraege finden und Details oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/frachtauftraege-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/frachtauftraege-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/frachtauftraege-liste/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__frachtauftraege-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/einkauf/frachtauftraege`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche offenen Frachtauftraege?
- Zeige aktuelle Frachtauftraege.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `einkauf/gutschrift-belastung` — Gutschrift/Belastung

**Zweck:** Gutschrift/Belastung als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/gutschrift-belastung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/gutschrift-belastung/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/gutschrift-belastung/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__gutschrift-belastung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/einkauf/lieferscheine`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Gutschrift/Belastung.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `einkauf/kontrakt-anlage` — Kontrakt-Anlage

**Zweck:** Kontrakt-Anlage als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/kontrakt-anlage/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/kontrakt-anlage/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/kontrakt-anlage/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__kontrakt-anlage/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/einkauf/kontrakte`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Kontrakt-Anlage.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `einkauf/kontrakte-service-liste` — Kontrakte Service

**Zweck:** Service-Kontrakte im Einkauf finden.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/kontrakte-service-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/kontrakte-service-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/kontrakte-service-liste/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__kontrakte-service-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/kontrakte`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Kontrakte laufen aus?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `einkauf/lieferanten` — Lieferanten

**Zweck:** Lieferanten finden und ihre Stammdaten, Bestellungen und Kontakte oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/lieferanten/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/lieferanten/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/lieferanten/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__lieferanten/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/einkauf/lieferanten`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Finde den Lieferanten Muehle Nord.
- Welche Lieferanten sind inaktiv?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `neu` | Neuer Lieferant | safe | nein | `Oeffnet die Anlage; Rechte prueft deren Anlageweg.` |
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `einkauf/lieferanten-angebote` — Lieferanten-Angebote

**Zweck:** Lieferanten-Angebote als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/lieferanten-angebote/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/lieferanten-angebote/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/lieferanten-angebote/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__lieferanten-angebote/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/einkauf/angebote`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Lieferanten-Angebote.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `einkauf/lieferanten-dokumente` — Lieferanten-Dokumente

**Zweck:** Lieferanten-Dokumente als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/lieferanten-dokumente/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/lieferanten-dokumente/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/lieferanten-dokumente/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__lieferanten-dokumente/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/einkauf/suppliers/{supplier_id}/documents`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Lieferanten-Dokumente.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `einkauf/lieferanten-konditionen` — Lieferanten-Konditionen

**Zweck:** Lieferanten-Konditionen als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/lieferanten-konditionen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/lieferanten-konditionen/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/lieferanten-konditionen/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__lieferanten-konditionen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/preise/konditionen`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Lieferanten-Konditionen.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `einkauf/lieferanten-reklamationen` — Lieferanten-Reklamationen

**Zweck:** Lieferanten-Reklamationen als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/lieferanten-reklamationen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/lieferanten-reklamationen/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/lieferanten-reklamationen/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__lieferanten-reklamationen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/qualitaet/reklamationen`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Lieferanten-Reklamationen.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `einkauf/lieferschein-erfassen` — Lieferschein erfassen

**Zweck:** Lieferschein erfassen als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/lieferschein-erfassen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/lieferschein-erfassen/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/lieferschein-erfassen/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__lieferschein-erfassen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/einkauf/lieferscheine`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Lieferschein erfassen.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `einkauf/mahnwesen-lieferanten` — Mahnwesen Lieferanten

**Zweck:** Mahnwesen Lieferanten als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/mahnwesen-lieferanten/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/mahnwesen-lieferanten/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/mahnwesen-lieferanten/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__mahnwesen-lieferanten/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/finance/followup/mahnwesen/preview`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Mahnwesen Lieferanten.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `einkauf/purchase-order` — Bestellung

**Zweck:** Fuehrende Einkaufsbestellung: Bestellfall, L3-Kopf, Positionen mit Kontrakt und Ladetermin, Skontostaffel, Bedarf und Direktlieferung.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/purchase-order/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/purchase-order/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/purchase-order/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__purchase-order/:entityId` |
| Adapter | `native` (temporary=nein) |

**Summary:** `/api/v1/mask-rollouts/einkauf/purchase-order/{entity_id}/screen-summary`

**Data Sources:**

- `entity` → `/api/v1/einkauf/bestellungen/{entity_id}`
- `positionen` → `/api/v1/mask-rollouts/einkauf/purchase-order/{entity_id}/tabs/positionen`
- `kommunikation` → `/api/v1/mask-rollouts/einkauf/purchase-order/{entity_id}/tabs/kommunikation`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Welcher Bestellfall gilt fuer Bestellung {entity_id}?
- Wann ist Ladetermin und Liefertermin von Bestellung {entity_id}?
- Welche Positionen haben noch offene Restmenge?
- Ist Bestellung {entity_id} eine Direktlieferung mit Ueberschlag am Lager?

**Sensible Felder:** `zahlungsbedingung, skonto1_prozent, skonto2_prozent, betrag`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |
| `speichern` | Speichern | safe | nein | `/api/v1/einkauf/bestellungen/{entity_id}/actions/speichern` |
| `versenden` | Versenden | moderate | nein | `/api/v1/einkauf/bestellungen/{entity_id}/versenden` |

---

### `einkauf/rechnung-abgleich` — Rechnung abgleich

**Zweck:** Rechnung abgleich im einkauf-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/rechnung-abgleich/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/rechnung-abgleich/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/rechnung-abgleich/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__rechnung-abgleich/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/einkauf/rechnungseingaenge`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Rechnung abgleich.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `einkauf/rechnung-abgleich-liste` — Rechnungsabgleich

**Zweck:** Rechnungen zum Abgleich finden.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/rechnung-abgleich-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/rechnung-abgleich-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/rechnung-abgleich-liste/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__rechnung-abgleich-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/einkauf/rechnungseingaenge`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Rechnungen passen nicht zur Bestellung?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `einkauf/rechnung-eingang-erfassung` — Rechnung eingang erfassung

**Zweck:** Rechnung eingang erfassung im einkauf-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/rechnung-eingang-erfassung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/rechnung-eingang-erfassung/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/rechnung-eingang-erfassung/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__rechnung-eingang-erfassung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/crm/customers/`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Rechnung eingang erfassung.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `einkauf/rechnungseingaenge-liste` — Rechnungseingaenge

**Zweck:** Eingangsrechnungen vor Pruefung und Verbuchung finden.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/rechnungseingaenge-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/rechnungseingaenge-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/rechnungseingaenge-liste/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__rechnungseingaenge-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/einkauf/rechnungseingaenge`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Rechnungen warten auf Freigabe?
- Welche Eingangsrechnungen sind offen?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `neu` | Rechnungseingang erfassen | safe | nein | `Oeffnet die Anlage; Rechte prueft deren Anlageweg.` |
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `einkauf/rechnungseingang/neu` — Vorgang

**Zweck:** Vorgang im einkauf-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/rechnungseingang/neu/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/rechnungseingang/neu/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/rechnungseingang/neu/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__rechnungseingang__neu/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/chart-of-accounts/`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Vorgang.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `einkauf/reports` — Reports

**Zweck:** Reports mandantensicher als Cockpit bereitstellen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/reports/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/reports/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/reports/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__reports/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/einkauf/anfragen`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Reports.
- Aktualisiere die Kennzahlen.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `einkauf/retouren` — Retouren

**Zweck:** Retouren im einkauf-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/retouren/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/retouren/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/retouren/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__retouren/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/einkauf/retouren`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Retouren.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `einkauf/retouren-liste` — Retouren

**Zweck:** Retouren verfolgen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/retouren-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/retouren-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/retouren-liste/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__retouren-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/einkauf/retouren`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Retouren sind offen?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `einkauf/rfq-bids` — Rfq bids

**Zweck:** Rfq bids im einkauf-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/rfq-bids/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/rfq-bids/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/rfq-bids/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__rfq-bids/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/einkauf/anfragen`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Rfq bids.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `einkauf/service-entry-sheets` — Service entry sheets

**Zweck:** Service entry sheets im einkauf-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/service-entry-sheets/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/service-entry-sheets/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/service-entry-sheets/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__service-entry-sheets/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/einkauf/anfragen`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Service entry sheets.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `einkauf/supplier` — Lieferant

**Zweck:** Lieferantenstamm-Cockpit fuer Einkauf — Stammdaten, offene Bestellungen und Ansprechpartner in einer Ansicht.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/supplier/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/supplier/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/supplier/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__supplier/:entityId` |
| Adapter | `native` (temporary=nein) |

**Summary:** `/api/v1/mask-rollouts/einkauf/supplier/{entity_id}/screen-summary`

**Data Sources:**

- `entity` → `/api/v1/einkauf/lieferanten/{entity_id}`
- `bestellungen` → `/api/v1/mask-rollouts/einkauf/supplier/{entity_id}/tabs/bestellungen`
- `kontakte` → `/api/v1/mask-rollouts/einkauf/supplier/{entity_id}/tabs/kontakte`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige alle offenen Bestellungen von Lieferant {entity_id} mit Status 'offen'.
- Welche Ansprechpartner gibt es bei Lieferant {entity_id}?
- Wie sind die Zahlungsbedingungen und Lieferzeiten von Lieferant {entity_id}?

**Sensible Felder:** `zahlungsbedingungen, lieferzeit_tage`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `/api/v1/einkauf/lieferanten/{entity_id}/actions/bearbeiten` |
| `neue_bestellung` | Bestellung anlegen | safe | nein | `—` |
| `sperren` | Sperren | high | ja | `/api/v1/einkauf/lieferanten/{entity_id}/actions/sperren` |
| `entsperren` | Entsperren | high | ja | `/api/v1/einkauf/lieferanten/{entity_id}/actions/entsperren` |

---

### `einkauf/wareneingang` — Wareneingang

**Zweck:** Wareneingang im einkauf-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/wareneingang/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/wareneingang/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/wareneingang/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__wareneingang/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/purchase-orders`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Wareneingang.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `einkauf/wareneingangsabgleich` — Wareneingangsabgleich

**Zweck:** Wareneingangsabgleich im einkauf-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/wareneingangsabgleich/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/wareneingangsabgleich/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/wareneingangsabgleich/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__wareneingangsabgleich/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/einkauf/anfragen`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Wareneingangsabgleich.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `einkauf/warengruppen` — Warengruppen

**Zweck:** Warengruppen fuer Artikel, Auswertungen und Einkauf pflegen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/warengruppen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/warengruppen/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/warengruppen/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__warengruppen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/stammdaten/warengruppen`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Warengruppen gehoeren zu Saatgut?
- Lege die Warengruppe Biostimulanzien an.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `neu` | Warengruppe anlegen | safe | nein | `/api/v1/stammdaten/warengruppen` |
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `workspace/einkauf` — Einkauf-Cockpit

**Zweck:** Rollen-Startseite Einkauf — offene Bestellungen, Avis und Preisabweichungen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/workspace/einkauf/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/workspace/einkauf/agent-contract` |
| Readiness | `GET /api/v1/masks/workspace/einkauf/readiness` |
| Rollout-Route | `/mask-rollout/workspace__einkauf/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/purchase-orders/statistics`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.speichern` — scope `einkauf:write`, Risiko mittel
- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.status` — scope `einkauf:read`, Risiko niedrig
- `einkauf.bestellung.versenden` — scope `einkauf:write`, Risiko mittel
- `einkauf.angebot.bestellen` — scope `einkauf:write`, Risiko mittel
- `einkauf.anlieferavis.wareneingang` — scope `einkauf:write`, Risiko mittel

**Beispiel-Prompts:**

- Was steht heute im Einkauf an?
- Zeige offene Bestellungen.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

## Domäne: etiketten

### `etiketten/drucken` — Drucken

**Zweck:** Drucken im etiketten-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/etiketten/drucken/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/etiketten/drucken/agent-contract` |
| Readiness | `GET /api/v1/masks/etiketten/drucken/readiness` |
| Rollout-Route | `/mask-rollout/etiketten__drucken/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/etiketten/druckauftrag`

**Beispiel-Prompts:**

- Zeige Drucken.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

## Domäne: export

### `export/ustva` — Umsatzsteuervoranmeldung

**Zweck:** Umsatzsteuervoranmeldung im export-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/export/ustva/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/export/ustva/agent-contract` |
| Readiness | `GET /api/v1/masks/export/ustva/readiness` |
| Rollout-Route | `/mask-rollout/export__ustva/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/export/entities`

**Beispiel-Prompts:**

- Zeige Umsatzsteuervoranmeldung.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

## Domäne: fibu

### `fibu/abschluss-checklist-detail` — Abschluss checklist detail

**Zweck:** Abschluss checklist detail als Stammblatt pflegen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/abschluss-checklist-detail/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/abschluss-checklist-detail/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/abschluss-checklist-detail/readiness` |
| Rollout-Route | `/mask-rollout/fibu__abschluss-checklist-detail/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/finance/closing-checklists/{entity_id}`

**Beispiel-Prompts:**

- Oeffne Abschluss checklist detail.
- Bearbeite Stammdaten.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `fibu/anlagen` — Anlagen Gesamt

**Zweck:** Anlagen Gesamt im fibu-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/anlagen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/anlagen/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/anlagen/readiness` |
| Rollout-Route | `/mask-rollout/fibu__anlagen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/fibu/anlagen`

**Beispiel-Prompts:**

- Zeige Anlagen Gesamt.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fibu/anlagen-suite` — Anlagen suite

**Zweck:** Anlagen suite im fibu-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/anlagen-suite/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/anlagen-suite/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/anlagen-suite/readiness` |
| Rollout-Route | `/mask-rollout/fibu__anlagen-suite/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/asset-ledger-connector/config`

**Beispiel-Prompts:**

- Zeige Anlagen suite.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fibu/atlas` — Atlas

**Zweck:** Atlas im fibu-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/atlas/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/atlas/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/atlas/readiness` |
| Rollout-Route | `/mask-rollout/fibu__atlas/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/fibu/anlagen`

**Beispiel-Prompts:**

- Zeige Atlas.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fibu/bilanz` — Bilanz

**Zweck:** Bilanz im fibu-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/bilanz/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/bilanz/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/bilanz/readiness` |
| Rollout-Route | `/mask-rollout/fibu__bilanz/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/fibu/anlagen`

**Beispiel-Prompts:**

- Zeige Bilanz.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fibu/buchhaltungsuebersicht` — Buchhaltungsuebersicht

**Zweck:** Buchhaltungsuebersicht mandantensicher als Cockpit bereitstellen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/buchhaltungsuebersicht/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/buchhaltungsuebersicht/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/buchhaltungsuebersicht/readiness` |
| Rollout-Route | `/mask-rollout/fibu__buchhaltungsuebersicht/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/fibu/anlagen`

**Beispiel-Prompts:**

- Zeige Buchhaltungsuebersicht.
- Aktualisiere die Kennzahlen.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `fibu/buchungsuebernahme-connectors` — Buchungsuebernahme connectors

**Zweck:** Buchungsuebernahme connectors im fibu-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/buchungsuebernahme-connectors/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/buchungsuebernahme-connectors/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/buchungsuebernahme-connectors/readiness` |
| Rollout-Route | `/mask-rollout/fibu__buchungsuebernahme-connectors/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/fibu/anlagen`

**Beispiel-Prompts:**

- Zeige Buchungsuebernahme connectors.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fibu/bwa` — Bwa

**Zweck:** Bwa im fibu-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/bwa/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/bwa/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/bwa/readiness` |
| Rollout-Route | `/mask-rollout/fibu__bwa/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/fibu/anlagen`

**Beispiel-Prompts:**

- Zeige Bwa.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fibu/debitoren` — Debitoren

**Zweck:** Debitoren im fibu-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/debitoren/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/debitoren/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/debitoren/readiness` |
| Rollout-Route | `/mask-rollout/fibu__debitoren/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/fibu/anlagen`

**Beispiel-Prompts:**

- Zeige Debitoren.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fibu/debitoren-api` — Debitoren api

**Zweck:** Debitoren api im fibu-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/debitoren-api/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/debitoren-api/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/debitoren-api/readiness` |
| Rollout-Route | `/mask-rollout/fibu__debitoren-api/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/fibu/anlagen`

**Beispiel-Prompts:**

- Zeige Debitoren api.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fibu/elster-online` — Elster online

**Zweck:** Elster online im fibu-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/elster-online/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/elster-online/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/elster-online/readiness` |
| Rollout-Route | `/mask-rollout/fibu__elster-online/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/fibu/anlagen`

**Beispiel-Prompts:**

- Zeige Elster online.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fibu/erloeskennziffern` — Erloeskennziffern

**Zweck:** Erloeskennziffern im fibu-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/erloeskennziffern/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/erloeskennziffern/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/erloeskennziffern/readiness` |
| Rollout-Route | `/mask-rollout/fibu__erloeskennziffern/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/fibu/anlagen`

**Beispiel-Prompts:**

- Zeige Erloeskennziffern.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fibu/erloeskontenzuordnung` — Erloeskontenzuordnung

**Zweck:** Erloeskontenzuordnung im fibu-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/erloeskontenzuordnung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/erloeskontenzuordnung/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/erloeskontenzuordnung/readiness` |
| Rollout-Route | `/mask-rollout/fibu__erloeskontenzuordnung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/fibu/anlagen`

**Beispiel-Prompts:**

- Zeige Erloeskontenzuordnung.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fibu/forderungsgruppen` — Forderungsgruppen

**Zweck:** Forderungsgruppen im fibu-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/forderungsgruppen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/forderungsgruppen/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/forderungsgruppen/readiness` |
| Rollout-Route | `/mask-rollout/fibu__forderungsgruppen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/fibu/anlagen`

**Beispiel-Prompts:**

- Zeige Forderungsgruppen.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fibu/geschaeftsjahre` — Neues Geschäftsjahr [JAHR]

**Zweck:** Neues Geschäftsjahr [JAHR] als Stammblatt pflegen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/geschaeftsjahre/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/geschaeftsjahre/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/geschaeftsjahre/readiness` |
| Rollout-Route | `/mask-rollout/fibu__geschaeftsjahre/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/fibu/geschaeftsjahre/detail/{entity_id}`

**Beispiel-Prompts:**

- Oeffne Neues Geschäftsjahr [JAHR].
- Bearbeite Stammdaten.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `fibu/guv` — Guv

**Zweck:** Guv im fibu-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/guv/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/guv/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/guv/readiness` |
| Rollout-Route | `/mask-rollout/fibu__guv/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/fibu/anlagen`

**Beispiel-Prompts:**

- Zeige Guv.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fibu/hauptbuch` — Hauptbuch

**Zweck:** Hauptbuch im fibu-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/hauptbuch/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/hauptbuch/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/hauptbuch/readiness` |
| Rollout-Route | `/mask-rollout/fibu__hauptbuch/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/fibu/anlagen`

**Beispiel-Prompts:**

- Zeige Hauptbuch.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fibu/kontenplan` — Kontenplan

**Zweck:** Kontenplan im fibu-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/kontenplan/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/kontenplan/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/kontenplan/readiness` |
| Rollout-Route | `/mask-rollout/fibu__kontenplan/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/chart-of-accounts/`

**Beispiel-Prompts:**

- Zeige Kontenplan.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fibu/kostenstellenrechnung` — Kostenstellenrechnung

**Zweck:** Kostenstellenrechnung im fibu-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/kostenstellenrechnung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/kostenstellenrechnung/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/kostenstellenrechnung/readiness` |
| Rollout-Route | `/mask-rollout/fibu__kostenstellenrechnung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/fibu/anlagen`

**Beispiel-Prompts:**

- Zeige Kostenstellenrechnung.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fibu/kreditlinien` — Kreditlinien

**Zweck:** Kreditlinien im fibu-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/kreditlinien/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/kreditlinien/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/kreditlinien/readiness` |
| Rollout-Route | `/mask-rollout/fibu__kreditlinien/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/fibu/anlagen`

**Beispiel-Prompts:**

- Zeige Kreditlinien.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fibu/kreditoren` — Kreditoren

**Zweck:** Kreditoren im fibu-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/kreditoren/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/kreditoren/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/kreditoren/readiness` |
| Rollout-Route | `/mask-rollout/fibu__kreditoren/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/fibu/anlagen`

**Beispiel-Prompts:**

- Zeige Kreditoren.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fibu/lohn-connector` — Lohn connector

**Zweck:** Lohn connector im fibu-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/lohn-connector/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/lohn-connector/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/lohn-connector/readiness` |
| Rollout-Route | `/mask-rollout/fibu__lohn-connector/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/lohn-connector/runs`

**Beispiel-Prompts:**

- Zeige Lohn connector.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fibu/monatswerte` — Monatswerte

**Zweck:** Monatswerte im fibu-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/monatswerte/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/monatswerte/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/monatswerte/readiness` |
| Rollout-Route | `/mask-rollout/fibu__monatswerte/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/fibu/anlagen`

**Beispiel-Prompts:**

- Zeige Monatswerte.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fibu/op-skonto-auszifferung` — Auszifferungen

**Zweck:** Auszifferungen als Stammblatt pflegen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/op-skonto-auszifferung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/op-skonto-auszifferung/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/op-skonto-auszifferung/readiness` |
| Rollout-Route | `/mask-rollout/fibu__op-skonto-auszifferung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/fibu/op-auszifferung/{entity_id}`

**Beispiel-Prompts:**

- Oeffne Auszifferungen.
- Bearbeite Stammdaten.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `fibu/op-verwaltung` — Op verwaltung

**Zweck:** Op verwaltung im fibu-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/op-verwaltung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/op-verwaltung/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/op-verwaltung/readiness` |
| Rollout-Route | `/mask-rollout/fibu__op-verwaltung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/fibu/anlagen`

**Beispiel-Prompts:**

- Zeige Op verwaltung.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fibu/periodische-buchungen` — Periodische buchungen

**Zweck:** Periodische buchungen im fibu-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/periodische-buchungen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/periodische-buchungen/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/periodische-buchungen/readiness` |
| Rollout-Route | `/mask-rollout/fibu__periodische-buchungen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/fibu/anlagen`

**Beispiel-Prompts:**

- Zeige Periodische buchungen.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fibu/quadriga-connector` — Quadriga connector

**Zweck:** Quadriga connector im fibu-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/quadriga-connector/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/quadriga-connector/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/quadriga-connector/readiness` |
| Rollout-Route | `/mask-rollout/fibu__quadriga-connector/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/quadriga-connector/config`

**Beispiel-Prompts:**

- Zeige Quadriga connector.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fibu/sachkonto` — Sachkonto

**Zweck:** Sachkonto im fibu-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/sachkonto/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/sachkonto/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/sachkonto/readiness` |
| Rollout-Route | `/mask-rollout/fibu__sachkonto/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/fibu/anlagen`

**Beispiel-Prompts:**

- Zeige Sachkonto.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fibu/schnittstelle-fibu` — Schnittstelle fibu

**Zweck:** Schnittstelle fibu im fibu-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/schnittstelle-fibu/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/schnittstelle-fibu/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/schnittstelle-fibu/readiness` |
| Rollout-Route | `/mask-rollout/fibu__schnittstelle-fibu/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/fibu/anlagen`

**Beispiel-Prompts:**

- Zeige Schnittstelle fibu.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fibu/schnittstellen-center` — Schnittstellen center

**Zweck:** Schnittstellen center im fibu-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/schnittstellen-center/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/schnittstellen-center/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/schnittstellen-center/readiness` |
| Rollout-Route | `/mask-rollout/fibu__schnittstellen-center/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/fibu/anlagen`

**Beispiel-Prompts:**

- Zeige Schnittstellen center.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fibu/sicherheiten` — Sicherheiten

**Zweck:** Sicherheiten im fibu-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/sicherheiten/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/sicherheiten/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/sicherheiten/readiness` |
| Rollout-Route | `/mask-rollout/fibu__sicherheiten/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/fibu/anlagen`

**Beispiel-Prompts:**

- Zeige Sicherheiten.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fibu/stammdaten` — Neues Zahlungsformular [FIZAF]

**Zweck:** Neues Zahlungsformular [FIZAF] als Stammblatt pflegen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/stammdaten/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/stammdaten/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/stammdaten/readiness` |
| Rollout-Route | `/mask-rollout/fibu__stammdaten/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/fibu/stammdaten/zahlungsformulare/{entity_id}`

**Beispiel-Prompts:**

- Oeffne Neues Zahlungsformular [FIZAF].
- Bearbeite Stammdaten.

**Sensible Felder:** `bank_iban`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `fibu/verbindlichkeiten` — Verbindlichkeiten

**Zweck:** Verbindlichkeiten im fibu-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/verbindlichkeiten/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/verbindlichkeiten/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/verbindlichkeiten/readiness` |
| Rollout-Route | `/mask-rollout/fibu__verbindlichkeiten/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/fibu/anlagen`

**Beispiel-Prompts:**

- Zeige Verbindlichkeiten.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fibu/zahlungseingaenge` — Zahlungseingaenge

**Zweck:** Zahlungseingaenge im fibu-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/zahlungseingaenge/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/zahlungseingaenge/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/zahlungseingaenge/readiness` |
| Rollout-Route | `/mask-rollout/fibu__zahlungseingaenge/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/bank-accounts`

**Beispiel-Prompts:**

- Zeige Zahlungseingaenge.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fibu/zahlungslaeufe` — Zahlungslaeufe

**Zweck:** Zahlungslaeufe im fibu-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/zahlungslaeufe/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/zahlungslaeufe/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/zahlungslaeufe/readiness` |
| Rollout-Route | `/mask-rollout/fibu__zahlungslaeufe/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/fibu/anlagen`

**Beispiel-Prompts:**

- Zeige Zahlungslaeufe.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fibu/zahlungsmeldungen` — Neue Zahlungsmeldung [KASSZAME]

**Zweck:** Neue Zahlungsmeldung [KASSZAME] als Stammblatt pflegen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/zahlungsmeldungen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/zahlungsmeldungen/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/zahlungsmeldungen/readiness` |
| Rollout-Route | `/mask-rollout/fibu__zahlungsmeldungen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/fibu/zahlungsmeldungen/{entity_id}`

**Beispiel-Prompts:**

- Oeffne Neue Zahlungsmeldung [KASSZAME].
- Bearbeite Stammdaten.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `fibu/zahlungsvorschlaege` — Zahlungsvorschlaege

**Zweck:** Zahlungsvorschlaege im fibu-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/zahlungsvorschlaege/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/zahlungsvorschlaege/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/zahlungsvorschlaege/readiness` |
| Rollout-Route | `/mask-rollout/fibu__zahlungsvorschlaege/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/fibu/anlagen`

**Beispiel-Prompts:**

- Zeige Zahlungsvorschlaege.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

## Domäne: finance

### `abrechnung/eb-lieferschein-kontrolle` — EB-Lieferschein-Kontrolle

**Zweck:** Fehlende Eingangsbelege und Warenzugaenge kontrollieren.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/abrechnung/eb-lieferschein-kontrolle/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/abrechnung/eb-lieferschein-kontrolle/agent-contract` |
| Readiness | `GET /api/v1/masks/abrechnung/eb-lieferschein-kontrolle/readiness` |
| Rollout-Route | `/mask-rollout/abrechnung__eb-lieferschein-kontrolle/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/document-control/summary`
- `exceptions` → `/api/v1/document-control/exceptions?exception_type=missing_inbound_document`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige nicht fakturierte Lieferscheine.
- Welche Bestellungen sind unerledigt?
- Welche Belegausnahmen sind ueberfaellig?

**Sensible Felder:** `partner_name, partner_ref, notes`

---

### `auswertungen/auftrags-kontrolle` — Auftrags-Kontrolle

**Zweck:** Unerledigte Bestellungen priorisieren und bis zum Quellbeleg verfolgen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/auswertungen/auftrags-kontrolle/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/auswertungen/auftrags-kontrolle/agent-contract` |
| Readiness | `GET /api/v1/masks/auswertungen/auftrags-kontrolle/readiness` |
| Rollout-Route | `/mask-rollout/auswertungen__auftrags-kontrolle/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/document-control/summary`
- `exceptions` → `/api/v1/document-control/exceptions?exception_type=open_purchase_order`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige nicht fakturierte Lieferscheine.
- Welche Bestellungen sind unerledigt?
- Welche Belegausnahmen sind ueberfaellig?

**Sensible Felder:** `partner_name, partner_ref, notes`

---

### `auswertungen/beleg-kontrolle` — Beleg-Kontrolle

**Zweck:** Belegausnahmen mandantensicher priorisieren und zum Ursprungsbeleg springen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/auswertungen/beleg-kontrolle/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/auswertungen/beleg-kontrolle/agent-contract` |
| Readiness | `GET /api/v1/masks/auswertungen/beleg-kontrolle/readiness` |
| Rollout-Route | `/mask-rollout/auswertungen__beleg-kontrolle/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/document-control/summary`
- `exceptions` → `/api/v1/document-control/exceptions`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige nicht fakturierte Lieferscheine.
- Welche Bestellungen sind unerledigt?
- Welche Belegausnahmen sind ueberfaellig?

**Sensible Felder:** `partner_name, partner_ref, notes`

---

### `auswertungen/lieferschein-kontrolle` — Lieferschein-Kontrolle

**Zweck:** Nicht fakturierte Lieferscheine priorisieren und klaeren.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/auswertungen/lieferschein-kontrolle/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/auswertungen/lieferschein-kontrolle/agent-contract` |
| Readiness | `GET /api/v1/masks/auswertungen/lieferschein-kontrolle/readiness` |
| Rollout-Route | `/mask-rollout/auswertungen__lieferschein-kontrolle/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/document-control/summary`
- `exceptions` → `/api/v1/document-control/exceptions?exception_type=uninvoiced_delivery_note`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige nicht fakturierte Lieferscheine.
- Welche Bestellungen sind unerledigt?
- Welche Belegausnahmen sind ueberfaellig?

**Sensible Felder:** `partner_name, partner_ref, notes`

---

### `banken/konten-liste` — Bankkonten

**Zweck:** Bankkonten und Salden im Blick behalten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/banken/konten-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/banken/konten-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/banken/konten-liste/readiness` |
| Rollout-Route | `/mask-rollout/banken__konten-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/banken/konten`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Welches Konto hat den hoechsten Saldo?
- Welche Konten sind inaktiv?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `banken/konten-stamm` — Bankkonten-Stamm

**Zweck:** Bankkonten-Stamm als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/banken/konten-stamm/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/banken/konten-stamm/agent-contract` |
| Readiness | `GET /api/v1/masks/banken/konten-stamm/readiness` |
| Rollout-Route | `/mask-rollout/banken__konten-stamm/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/banken/konten`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige Bankkonten-Stamm.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `banken/lastschriften` — Lastschriften

**Zweck:** Lastschriften als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/banken/lastschriften/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/banken/lastschriften/agent-contract` |
| Readiness | `GET /api/v1/masks/banken/lastschriften/readiness` |
| Rollout-Route | `/mask-rollout/banken__lastschriften/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/finance/payment-runs`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige Lastschriften.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `banken/sepa-export` — SEPA-Export

**Zweck:** SEPA-Export als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/banken/sepa-export/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/banken/sepa-export/agent-contract` |
| Readiness | `GET /api/v1/masks/banken/sepa-export/readiness` |
| Rollout-Route | `/mask-rollout/banken__sepa-export/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/finance/payment-runs`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige SEPA-Export.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `banken/ueberweisungen` — Ueberweisungen

**Zweck:** Ueberweisungen als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/banken/ueberweisungen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/banken/ueberweisungen/agent-contract` |
| Readiness | `GET /api/v1/masks/banken/ueberweisungen/readiness` |
| Rollout-Route | `/mask-rollout/banken__ueberweisungen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/banken/fints/umsaetze`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige Ueberweisungen.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `banken/zahlungsavise` — Zahlungsavise

**Zweck:** Zahlungsavise als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/banken/zahlungsavise/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/banken/zahlungsavise/agent-contract` |
| Readiness | `GET /api/v1/masks/banken/zahlungsavise/readiness` |
| Rollout-Route | `/mask-rollout/banken__zahlungsavise/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/finance/payment-runs`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige Zahlungsavise.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `banken/zahlungsvorschlaege` — Zahlungsvorschlaege

**Zweck:** Zahlungsvorschlaege als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/banken/zahlungsvorschlaege/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/banken/zahlungsvorschlaege/agent-contract` |
| Readiness | `GET /api/v1/masks/banken/zahlungsvorschlaege/readiness` |
| Rollout-Route | `/mask-rollout/banken__zahlungsvorschlaege/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/finance/payment-suggestions`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige Zahlungsvorschlaege.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `einkauf/zahlungsbedingungen` — Zahlungsbedingungen

**Zweck:** Zahlungsbedingungen fuer Kunden, Lieferanten und Belege pflegen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/zahlungsbedingungen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/zahlungsbedingungen/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/zahlungsbedingungen/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__zahlungsbedingungen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/fibu/zahlungsbedingungen`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Welche Zahlungsbedingungen gewaehren 2 % Skonto?
- Lege 30 Tage netto, 10 Tage 2 % an.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `neu` | Zahlungsbedingung anlegen | safe | nein | `/api/v1/fibu/zahlungsbedingungen` |
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `export/umsatzsteuer-voranmeldung-liste` — USt-Voranmeldung

**Zweck:** USt-Voranmeldungen einsehen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/export/umsatzsteuer-voranmeldung-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/export/umsatzsteuer-voranmeldung-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/export/umsatzsteuer-voranmeldung-liste/readiness` |
| Rollout-Route | `/mask-rollout/export__umsatzsteuer-voranmeldung-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/compliance/ustva`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Welche Voranmeldung ist faellig?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fibu/abschluss-checklist` — Abschluss-Checkliste

**Zweck:** Monatsabschluss-Checkliste.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/abschluss-checklist/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/abschluss-checklist/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/abschluss-checklist/readiness` |
| Rollout-Route | `/mask-rollout/fibu__abschluss-checklist/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/finance/closing-checklists/{entity_id}`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Welche Periode hat Checkliste {entity_id}?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `fibu/abschluss-cockpit` — Abschluss-Cockpit

**Zweck:** Monats- und Jahresabschluss-Checklisten mit Fortschritt.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/abschluss-cockpit/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/abschluss-cockpit/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/abschluss-cockpit/readiness` |
| Rollout-Route | `/mask-rollout/fibu__abschluss-cockpit/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/finance/closing-checklists/cockpit/summary`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Wie weit ist der Monatsabschluss?
- Welche Closing-Tasks fehlen?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `fibu/anlage` — Anlage

**Zweck:** Anlagevermoegen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/anlage/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/anlage/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/anlage/readiness` |
| Rollout-Route | `/mask-rollout/fibu__anlage/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/finance/asset-accounting/assets/{entity_id}`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Welchen Anschaffungswert hat Anlage {entity_id}?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `fibu/anlagen-liste` — Anlagen

**Zweck:** Anlagen finden und oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/anlagen-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/anlagen-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/anlagen-liste/readiness` |
| Rollout-Route | `/mask-rollout/fibu__anlagen-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/fixed-assets/detail`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Welche Anlagen haben niedrigen Buchwert?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fibu/buchungsjournal-liste` — Buchungsjournal

**Zweck:** Buchungsjournal: Eintraege finden und Details oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/buchungsjournal-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/buchungsjournal-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/buchungsjournal-liste/readiness` |
| Rollout-Route | `/mask-rollout/fibu__buchungsjournal-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/journal-entries/`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Welche offenen Buchungsjournal?
- Zeige aktuelle Buchungsjournal.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fibu/debitoren-liste` — Debitoren OP

**Zweck:** Offene Debitorenposten finden.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/debitoren-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/debitoren-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/debitoren-liste/readiness` |
| Rollout-Route | `/mask-rollout/fibu__debitoren-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/open-items?typ=debitor`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Welche Posten sind ueberfaellig?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fibu/hauptbuch-liste` — Hauptbuch

**Zweck:** Hauptbuch-Buchungen einsehen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/hauptbuch-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/hauptbuch-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/hauptbuch-liste/readiness` |
| Rollout-Route | `/mask-rollout/fibu__hauptbuch-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/journal-entries/`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Welche Buchungen auf Konto 1200?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fibu/kassenbuch-liste` — Kassenbuch

**Zweck:** Kassenbuch und Tagesabschluesse finden.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/kassenbuch-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/kassenbuch-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/kassenbuch-liste/readiness` |
| Rollout-Route | `/mask-rollout/fibu__kassenbuch-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/kasse/tagesabschluss/aktuell`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Ist der heutige Abschluss offen?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fibu/kontenplan-liste` — Kontenplan

**Zweck:** Kontenplan: Eintraege finden und Details oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/kontenplan-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/kontenplan-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/kontenplan-liste/readiness` |
| Rollout-Route | `/mask-rollout/fibu__kontenplan-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/chart-of-accounts/`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Welche offenen Kontenplan?
- Zeige aktuelle Kontenplan.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fibu/kostenstellen-liste` — Kostenstellen

**Zweck:** Kostenstellen: Eintraege finden und Details oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/kostenstellen-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/kostenstellen-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/kostenstellen-liste/readiness` |
| Rollout-Route | `/mask-rollout/fibu__kostenstellen-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/kostenstellen`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Welche offenen Kostenstellen?
- Zeige aktuelle Kostenstellen.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fibu/kreditoren-liste` — Kreditoren OP

**Zweck:** Offene Kreditorenposten finden.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/kreditoren-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/kreditoren-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/kreditoren-liste/readiness` |
| Rollout-Route | `/mask-rollout/fibu__kreditoren-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/open-items?typ=kreditor`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Welche Verbindlichkeiten sind faellig?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fibu/offene-posten-liste` — Offene Posten

**Zweck:** Offene Posten: Eintraege finden und Details oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/offene-posten-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/offene-posten-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/offene-posten-liste/readiness` |
| Rollout-Route | `/mask-rollout/fibu__offene-posten-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/open-items`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Welche offenen Offene Posten?
- Zeige aktuelle Offene Posten.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fibu/schnittstelle-fibu-liste` — FIBU-Schnittstelle

**Zweck:** FIBU-Schnittstellen-Exporte verfolgen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/schnittstelle-fibu-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/schnittstelle-fibu-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/schnittstelle-fibu-liste/readiness` |
| Rollout-Route | `/mask-rollout/fibu__schnittstelle-fibu-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/connectors/profiles`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Welcher Export ist fehlgeschlagen?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fibu/verbindlichkeiten-liste` — Verbindlichkeiten

**Zweck:** Verbindlichkeiten finden.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/verbindlichkeiten-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/verbindlichkeiten-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/verbindlichkeiten-liste/readiness` |
| Rollout-Route | `/mask-rollout/fibu__verbindlichkeiten-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/open-items?typ=kreditor`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Welche Verbindlichkeiten sind offen?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fibu/zahlungseingaenge-liste` — Zahlungseingaenge

**Zweck:** Zahlungseingaenge: Eintraege finden und Details oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/zahlungseingaenge-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/zahlungseingaenge-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/zahlungseingaenge-liste/readiness` |
| Rollout-Route | `/mask-rollout/fibu__zahlungseingaenge-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/bank-accounts`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Welche offenen Zahlungseingaenge?
- Zeige aktuelle Zahlungseingaenge.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fibu/zahlungslaeufe-liste` — Zahlungslaeufe

**Zweck:** Zahlungslaeufe: Eintraege finden und Details oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fibu/zahlungslaeufe-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fibu/zahlungslaeufe-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/fibu/zahlungslaeufe-liste/readiness` |
| Rollout-Route | `/mask-rollout/fibu__zahlungslaeufe-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/payment-runs`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Welche offenen Zahlungslaeufe?
- Zeige aktuelle Zahlungslaeufe.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `finance/abschluss` — Monats-/Jahresabschluss

**Zweck:** Monats-/Jahresabschluss im finance-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/abschluss/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/abschluss/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/abschluss/readiness` |
| Rollout-Route | `/mask-rollout/finance__abschluss/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/closing-checklists`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige Monats-/Jahresabschluss.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `finance/ap-invoice` — Eingangsrechnung

**Zweck:** Eingangsrechnung: Kopfdaten, Positionen und Freigabe-Historie fuer AP-Buchhalter und Audit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/ap-invoice/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/ap-invoice/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/ap-invoice/readiness` |
| Rollout-Route | `/mask-rollout/finance__ap-invoice/:entityId` |
| Adapter | `native` (temporary=nein) |

**Summary:** `/api/v1/mask-rollouts/finance/ap-invoice/{entity_id}/screen-summary`

**Data Sources:**

- `entity` → `/api/v1/finance/ap/invoices/{entity_id}`
- `positionen` → `/api/v1/mask-rollouts/finance/ap-invoice/{entity_id}/tabs/positionen`
- `freigabe` → `/api/v1/mask-rollouts/finance/ap-invoice/{entity_id}/tabs/freigabe`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Was ist der Freigabe-Status von Eingangsrechnung {entity_id}?
- Wann ist Eingangsrechnung {entity_id} faellig und wie hoch ist der Bruttobetrag?

**Sensible Felder:** `brutto, mwst, faellig_am`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `freigeben` | Freigeben | moderate | ja | `/api/v1/finance/ap/invoices/{entity_id}/actions/freigeben` |

---

### `finance/ap-invoices-liste` — AP-Rechnungen

**Zweck:** AP-Rechnungen: Eintraege finden und Details oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/ap-invoices-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/ap-invoices-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/ap-invoices-liste/readiness` |
| Rollout-Route | `/mask-rollout/finance__ap-invoices-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/ap/invoices/`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Welche offenen AP-Rechnungen?
- Zeige aktuelle AP-Rechnungen.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `finance/ap/invoices` — Ap invoices list

**Zweck:** Ap invoices list im finance-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/ap/invoices/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/ap/invoices/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/ap/invoices/readiness` |
| Rollout-Route | `/mask-rollout/finance__ap__invoices/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/abstimmung/nebenbuch`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige Ap invoices list.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `finance/ap/invoices/new` — Ap invoice form

**Zweck:** Ap invoice form im finance-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/ap/invoices/new/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/ap/invoices/new/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/ap/invoices/new/readiness` |
| Rollout-Route | `/mask-rollout/finance__ap__invoices__new/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/abstimmung/nebenbuch`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige Ap invoice form.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `finance/ar-open-item` — Offener Posten

**Zweck:** Offener Posten: Forderungs-Cockpit fuer Debitorenbuchhaltung mit Faelligkeiten, Skonto und Ausgleichshistorie.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/ar-open-item/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/ar-open-item/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/ar-open-item/readiness` |
| Rollout-Route | `/mask-rollout/finance__ar-open-item/:entityId` |
| Adapter | `native` (temporary=nein) |

**Summary:** `/api/v1/mask-rollouts/finance/ar-open-item/{entity_id}/screen-summary`

**Data Sources:**

- `entity` → `/api/v1/finance/open-items/{entity_id}`
- `ausgleich` → `/api/v1/mask-rollouts/finance/ar-open-item/{entity_id}/tabs/ausgleich`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Wann ist OP {entity_id} faellig und wie hoch ist der offene Betrag?
- Zeige alle bisherigen Zahlungseingaenge fuer OP {entity_id}.

**Sensible Felder:** `brutto, offen, skonto, faellig_am`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `mahnen` | Mahnung erstellen | moderate | nein | `/api/v1/finance/open-items/{entity_id}/actions/mahnen` |

---

### `finance/audit-trail` — Finanz-Audit-Trail

**Zweck:** Revisionssichere Finanz-Audit-Eintraege durchsuchen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/audit-trail/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/audit-trail/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/audit-trail/readiness` |
| Rollout-Route | `/mask-rollout/finance__audit-trail/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/audit/stats`
- `logs` → `/api/v1/audit/logs`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige kritische Audit-Eintraege der letzten Woche.

---

### `finance/audit-trail-liste` — Audit-Trail

**Zweck:** Audit-Trail: Eintraege finden und Details oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/audit-trail-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/audit-trail-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/audit-trail-liste/readiness` |
| Rollout-Route | `/mask-rollout/finance__audit-trail-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/audit/logs`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Welche offenen Audit-Trail?
- Zeige aktuelle Audit-Trail.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `finance/bank-abgleich` — Objekt

**Zweck:** Objekt im finance-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/bank-abgleich/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/bank-abgleich/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/bank-abgleich/readiness` |
| Rollout-Route | `/mask-rollout/finance__bank-abgleich/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/abstimmung/nebenbuch`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige Objekt.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `finance/bank-account` — Bankkonto

**Zweck:** Bankkonto-Stammdaten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/bank-account/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/bank-account/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/bank-account/readiness` |
| Rollout-Route | `/mask-rollout/finance__bank-account/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/finance/bank-accounts/{entity_id}`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Welche IBAN hat Konto {entity_id}?

**Sensible Felder:** `iban`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `finance/bank-stamm` — Bank stamm

**Zweck:** Bank stamm als Stammblatt pflegen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/bank-stamm/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/bank-stamm/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/bank-stamm/readiness` |
| Rollout-Route | `/mask-rollout/finance__bank-stamm/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/finance/abstimmung/nebenbuch/{entity_id}`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Oeffne Bank stamm.
- Bearbeite Stammdaten.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `finance/bankkonten-stamm` — Bankkonten stamm

**Zweck:** Bankkonten stamm als Stammblatt pflegen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/bankkonten-stamm/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/bankkonten-stamm/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/bankkonten-stamm/readiness` |
| Rollout-Route | `/mask-rollout/finance__bankkonten-stamm/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/finance/bank-accounts/{entity_id}`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Oeffne Bankkonten stamm.
- Bearbeite Stammdaten.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `finance/bankkonto` — Bankkonto

**Zweck:** Bankkonto-Stamm: Kontodaten und Buchungshistorie fuer Finanzbuchhaltung.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/bankkonto/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/bankkonto/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/bankkonto/readiness` |
| Rollout-Route | `/mask-rollout/finance__bankkonto/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/banken/konten/{entity_id}`
- `buchungen` → `/api/v1/masks/finance/bankkonten/entity/{entity_id}/tabs/buchungen`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Was ist der aktuelle Saldo von Bankkonto {entity_id}?
- Zeige die letzten Buchungen auf Bankkonto {entity_id}.

**Sensible Felder:** `iban, bic, saldo`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | moderate | nein | `/api/v1/banken/konten/{entity_id}/actions/bearbeiten` |

---

### `finance/bookings/new` — Buchungsjournal

**Zweck:** Buchungsjournal im finance-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/bookings/new/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/bookings/new/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/bookings/new/readiness` |
| Rollout-Route | `/mask-rollout/finance__bookings__new/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/abstimmung/nebenbuch`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige Buchungsjournal.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `finance/buchungserfassung` — Vorgang

**Zweck:** Vorgang im finance-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/buchungserfassung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/buchungserfassung/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/buchungserfassung/readiness` |
| Rollout-Route | `/mask-rollout/finance__buchungserfassung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/journal-entries`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige Vorgang.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `finance/buchungsimport` — Buchungsimport

**Zweck:** Buchungsimport im finance-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/buchungsimport/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/buchungsimport/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/buchungsimport/readiness` |
| Rollout-Route | `/mask-rollout/finance__buchungsimport/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/abstimmung/nebenbuch`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige Buchungsimport.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `finance/buchungsvorlagen` — Buchungsvorlagen

**Zweck:** Wiederkehrende Buchungen als Entwurf erzeugen; der Entwurf geht durch die normale Buchungspruefung.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/buchungsvorlagen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/buchungsvorlagen/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/buchungsvorlagen/readiness` |
| Rollout-Route | `/mask-rollout/finance__buchungsvorlagen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/booking-templates?active_only=false`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Welche Buchungsvorlagen gibt es fuer Abschreibungen?
- Wende die Mietvorlage fuer Oktober an.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `finance/datev-export` — DATEV-Export

**Zweck:** Offene Posten als vereinfachte DATEV-CSV ausgeben.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/datev-export/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/datev-export/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/datev-export/readiness` |
| Rollout-Route | `/mask-rollout/finance__datev-export/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `export-alle` → `/api/v1/finance/datev-export?typ=alle`
- `export-debitor` → `/api/v1/finance/datev-export?typ=debitor`
- `export-kreditor` → `/api/v1/finance/datev-export?typ=kreditor`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Exportiere die offenen Debitorenposten fuer DATEV.

**Sensible Felder:** `csv`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export_erstellen` | Export erstellen | safe | nein | `—` |

---

### `finance/debitor` — Debitor

**Zweck:** Debitoren-Stammdaten: Kreditlimit, offene Posten und Umsatzhistorie fuer Debitorenbuchhaltung.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/debitor/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/debitor/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/debitor/readiness` |
| Rollout-Route | `/mask-rollout/finance__debitor/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/finance/debitoren/{entity_id}`
- `offene_posten` → `/api/v1/masks/finance/debitoren/entity/{entity_id}/tabs/offene-posten`
- `umsaetze` → `/api/v1/masks/finance/debitoren/entity/{entity_id}/tabs/umsaetze`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Was ist das Kreditlimit von Debitor {entity_id}?
- Zeige alle offenen Posten von Debitor {entity_id}.

**Sensible Felder:** `kreditlimit, steuernummer, ust_id`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | moderate | nein | `/api/v1/finance/debitoren/{entity_id}/actions/bearbeiten` |

---

### `finance/debitoren-liste` — Debitoren

**Zweck:** Debitoren mit offenen Forderungen und Mahnstufe finden, oeffnen und sperren.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/debitoren-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/debitoren-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/debitoren-liste/readiness` |
| Rollout-Route | `/mask-rollout/finance__debitoren-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/debitoren`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Welche Debitoren haben Mahnstufe 2 oder hoeher?
- Welche Kunden haben die hoechsten offenen Posten?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `neu` | Neuer Debitor | safe | nein | `Oeffnet die Anlage; Rechte prueft deren Anlageweg.` |
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |
| `mahnwesen` | Mahnwesen | safe | nein | `Oeffnet das Mahnwesen; Mahnlaeufe laufen dort mit Vorschau und Freigabe.` |

---

### `finance/debitoren/new` — Debitoren stamm

**Zweck:** Debitoren stamm als Stammblatt pflegen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/debitoren/new/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/debitoren/new/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/debitoren/new/readiness` |
| Rollout-Route | `/mask-rollout/finance__debitoren__new/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/finance/debtors/{entity_id}`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Oeffne Debitoren stamm.
- Bearbeite Stammdaten.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `finance/dunning-editor` — Mahnvorgang

**Zweck:** Mahnvorgang im finance-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/dunning-editor/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/dunning-editor/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/dunning-editor/readiness` |
| Rollout-Route | `/mask-rollout/finance__dunning-editor/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/debtors`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige Mahnvorgang.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `finance/invoices-list` — Invoices list

**Zweck:** Invoices list im finance-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/invoices-list/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/invoices-list/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/invoices-list/readiness` |
| Rollout-Route | `/mask-rollout/finance__invoices-list/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/abstimmung/nebenbuch`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige Invoices list.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `finance/invoices/new` — Invoice form

**Zweck:** Invoice form im finance-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/invoices/new/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/invoices/new/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/invoices/new/readiness` |
| Rollout-Route | `/mask-rollout/finance__invoices__new/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/invoices`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige Invoice form.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `finance/kasse` — Kasse

**Zweck:** Kasse im finance-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/kasse/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/kasse/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/kasse/readiness` |
| Rollout-Route | `/mask-rollout/finance__kasse/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/abstimmung/nebenbuch`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige Kasse.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `finance/kontenplan` — Chart of accounts

**Zweck:** Chart of accounts im finance-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/kontenplan/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/kontenplan/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/kontenplan/readiness` |
| Rollout-Route | `/mask-rollout/finance__kontenplan/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/abstimmung/nebenbuch`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige Chart of accounts.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `finance/kreditor` — Kreditor

**Zweck:** Kreditoren-Stammdaten: Zahlungsbedingungen, offene Posten und Bestellhistorie fuer Kreditorenbuchhaltung.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/kreditor/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/kreditor/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/kreditor/readiness` |
| Rollout-Route | `/mask-rollout/finance__kreditor/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/finance/kreditoren/{entity_id}`
- `offene_posten` → `/api/v1/masks/finance/kreditoren/entity/{entity_id}/tabs/offene-posten`
- `bestellungen` → `/api/v1/masks/finance/kreditoren/entity/{entity_id}/tabs/bestellungen`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Welche offenen Posten hat Kreditor {entity_id}?
- Zeige alle Bestellungen bei Kreditor {entity_id}.

**Sensible Felder:** `steuernummer, ust_id`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | moderate | nein | `/api/v1/finance/kreditoren/{entity_id}/actions/bearbeiten` |

---

### `finance/kreditoren` — Kreditoren liste

**Zweck:** Kreditoren liste im finance-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/kreditoren/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/kreditoren/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/kreditoren/readiness` |
| Rollout-Route | `/mask-rollout/finance__kreditoren/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/abstimmung/nebenbuch`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige Kreditoren liste.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `finance/kreditoren-liste` — Kreditoren

**Zweck:** Kreditoren finden und ihre Stamm-, Steuer- und Bankdaten oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/kreditoren-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/kreditoren-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/kreditoren-liste/readiness` |
| Rollout-Route | `/mask-rollout/finance__kreditoren-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/kreditoren`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Welche Kreditoren haben keine USt-IdNr.?
- Finde den Kreditor Muehle Nord.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `neu` | Neuer Kreditor | safe | nein | `Oeffnet die Anlage; Rechte prueft deren Anlageweg.` |
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `finance/kreditoren-stamm` — Kreditoren stamm

**Zweck:** Kreditoren stamm als Stammblatt pflegen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/kreditoren-stamm/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/kreditoren-stamm/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/kreditoren-stamm/readiness` |
| Rollout-Route | `/mask-rollout/finance__kreditoren-stamm/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/finance/creditors/{entity_id}`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Oeffne Kreditoren stamm.
- Bearbeite Stammdaten.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `finance/lastschriften-debitoren` — Debitorenlauf

**Zweck:** Debitorenlauf im finance-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/lastschriften-debitoren/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/lastschriften-debitoren/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/lastschriften-debitoren/readiness` |
| Rollout-Route | `/mask-rollout/finance__lastschriften-debitoren/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/direct-debits`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige Debitorenlauf.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `finance/nebenbuch-abstimmung` — Nebenbuch abstimmung

**Zweck:** Nebenbuch abstimmung im finance-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/nebenbuch-abstimmung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/nebenbuch-abstimmung/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/nebenbuch-abstimmung/readiness` |
| Rollout-Route | `/mask-rollout/finance__nebenbuch-abstimmung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/abstimmung/nebenbuch`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige Nebenbuch abstimmung.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `finance/offene-posten` — Offene posten

**Zweck:** Offene posten im finance-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/offene-posten/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/offene-posten/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/offene-posten/readiness` |
| Rollout-Route | `/mask-rollout/finance__offene-posten/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/open-items`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige Offene posten.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `finance/offene-posten-cockpit` — Offene-Posten-Cockpit

**Zweck:** Offene Posten mandantensicher mit Aging-Buckets auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/offene-posten-cockpit/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/offene-posten-cockpit/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/offene-posten-cockpit/readiness` |
| Rollout-Route | `/mask-rollout/finance__offene-posten-cockpit/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/finance/offene-posten`
- `open_items` → `/api/v1/finance/open-items`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Wie hoch sind ueberfaellige Debitoren?
- Zeige OP-Aging.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `finance/op-debitoren` — OP-Lage

**Zweck:** OP-Lage im finance-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/op-debitoren/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/op-debitoren/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/op-debitoren/readiness` |
| Rollout-Route | `/mask-rollout/finance__op-debitoren/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/dunning`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige OP-Lage.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `finance/op-kreditoren` — Op kreditoren

**Zweck:** Op kreditoren im finance-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/op-kreditoren/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/op-kreditoren/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/op-kreditoren/readiness` |
| Rollout-Route | `/mask-rollout/finance__op-kreditoren/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/open-items`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige Op kreditoren.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `finance/payment-matching-liste` — Zahlungsabgleich

**Zweck:** Zahlungsabgleich: Eintraege finden und Details oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/payment-matching-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/payment-matching-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/payment-matching-liste/readiness` |
| Rollout-Route | `/mask-rollout/finance__payment-matching-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/payments/unmatched`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Welche offenen Zahlungsabgleich?
- Zeige aktuelle Zahlungsabgleich.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `finance/payment-run` — Zahlungslauf

**Zweck:** Zahlungslauf-Cockpit (read-only fuer Agenten): Laufdetails und Einzelzahlungen fuer Audit und Reconciliation. Freigabe ist Agent-gesperrt.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/payment-run/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/payment-run/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/payment-run/readiness` |
| Rollout-Route | `/mask-rollout/finance__payment-run/:entityId` |
| Adapter | `native` (temporary=nein) |

**Summary:** `/api/v1/mask-rollouts/finance/payment-run/{entity_id}/screen-summary`

**Data Sources:**

- `entity` → `/api/v1/finance/payment-runs/{entity_id}`
- `zahlungen` → `/api/v1/mask-rollouts/finance/payment-run/{entity_id}/tabs/zahlungen`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Was ist der Status von Zahlungslauf {entity_id} und wie hoch ist der Gesamtbetrag?
- Zeige alle Einzelzahlungen von Zahlungslauf {entity_id} mit Status 'fehler'.

**Sensible Felder:** `initiator_iban, gesamtbetrag, bank`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `freigeben` | Zahlungslauf freigeben | critical | ja | `/api/v1/finance/payment-runs/{entity_id}/actions/freigeben` |

---

### `finance/payments` — Payment matching

**Zweck:** Payment matching im finance-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/payments/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/payments/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/payments/readiness` |
| Rollout-Route | `/mask-rollout/finance__payments/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/payments/unmatched`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige Payment matching.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `finance/periodenabschluss` — Periodenabschluss

**Zweck:** Periodenabschluss im finance-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/periodenabschluss/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/periodenabschluss/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/periodenabschluss/readiness` |
| Rollout-Route | `/mask-rollout/finance__periodenabschluss/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/abstimmung/nebenbuch`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige Periodenabschluss.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `finance/periods` — Periods

**Zweck:** Periods im finance-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/periods/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/periods/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/periods/readiness` |
| Rollout-Route | `/mask-rollout/finance__periods/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/abstimmung/nebenbuch`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige Periods.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `finance/periods-liste` — Buchungsperioden

**Zweck:** Buchungsperioden: Eintraege finden und Details oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/periods-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/periods-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/periods-liste/readiness` |
| Rollout-Route | `/mask-rollout/finance__periods-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/periods/`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Welche offenen Buchungsperioden?
- Zeige aktuelle Buchungsperioden.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `finance/pruefkorb` — Prüfkorb

**Zweck:** Auffälligkeiten an Buchungen, Stornos und Importen für den Controller priorisieren.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/pruefkorb/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/pruefkorb/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/pruefkorb/readiness` |
| Rollout-Route | `/mask-rollout/finance__pruefkorb/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/kontrolle/lagebild`
- `befunde` → `/api/v1/kontrolle/pruefkorb`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Welche Befunde sind im Prüfkorb offen?
- Zeige die kritischen Befunde.
- Welche Auffälligkeiten warten seit mehr als einer Woche?

**Sensible Felder:** `ausgeloest_von, geprueft_von, bewertung, betrag`

---

### `finance/rechnungstapel` — Rechnungstapel

**Zweck:** Rechnungs- und Selbstabrechnungsstapel nachvollziehbar abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/rechnungstapel/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/rechnungstapel/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/rechnungstapel/readiness` |
| Rollout-Route | `/mask-rollout/finance__rechnungstapel/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/billing-batches/summary`
- `batches` → `/api/v1/billing-batches`
- `errors` → `/api/v1/billing-batches/lines?status=failed`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige Fehlerzeilen im Rechnungstapel.
- Welche Selbstabrechner warten auf Freigabe?

**Sensible Felder:** `validation_error, source_ref, maker, checker`

---

### `finance/skonto-optimizer` — Skonto optimizer

**Zweck:** Skonto optimizer im finance-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/skonto-optimizer/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/skonto-optimizer/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/skonto-optimizer/readiness` |
| Rollout-Route | `/mask-rollout/finance__skonto-optimizer/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/open-items`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige Skonto optimizer.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `finance/skonto-optimizer-liste` — Skonto-Optimierung

**Zweck:** Skonto-Optimierung: Eintraege finden und Details oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/skonto-optimizer-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/skonto-optimizer-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/skonto-optimizer-liste/readiness` |
| Rollout-Route | `/mask-rollout/finance__skonto-optimizer-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/open-items`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Welche offenen Skonto-Optimierung?
- Zeige aktuelle Skonto-Optimierung.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `finance/steuerschluessel` — Steuerschlüssel

**Zweck:** Steuerschluessel des Mandanten pflegen: Satz, Umsatzsteuer-, Vorsteuer- und Erloeskonto, Paragraf 24 UStG, Reverse Charge, Gueltigkeit. Aus ihnen nehmen alle Belege ihre Umsatzsteuer.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/steuerschluessel/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/steuerschluessel/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/steuerschluessel/readiness` |
| Rollout-Route | `/mask-rollout/finance__steuerschluessel/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `steuerschluessel` → `/api/v1/finance/tax-keys`
- `konten` → `/api/v1/finance/tax-keys/kontenvorschlaege`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Welche Steuerschluessel buchen nicht automatisch und warum?
- Auf welches Konto bucht Steuerschluessel 3 die Umsatzsteuer?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `speichern` | Steuerschlüssel speichern | moderate | ja | `/api/v1/finance/tax-keys/actions/speichern` |
| `neu` | Neuer Steuerschlüssel | safe | nein | `Leert die Eingabe fuer einen neuen Steuerschluessel.` |

---

### `finance/umsatz` — Reports

**Zweck:** Reports mandantensicher als Cockpit bereitstellen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/umsatz/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/umsatz/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/umsatz/readiness` |
| Rollout-Route | `/mask-rollout/finance__umsatz/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/finance/financial-reports/bwa`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige Reports.
- Aktualisiere die Kennzahlen.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `finance/ustva` — Meldekontext

**Zweck:** Meldekontext im finance-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/ustva/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/ustva/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/ustva/readiness` |
| Rollout-Route | `/mask-rollout/finance__ustva/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/vat-return`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige Meldekontext.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `finance/wechselkurse` — Wechselkurse

**Zweck:** Wechselkurse fuer Fremdwaehrungsbelege pflegen und nachweisen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/wechselkurse/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/wechselkurse/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/wechselkurse/readiness` |
| Rollout-Route | `/mask-rollout/finance__wechselkurse/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/exchange-rates?active_only=false`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Welcher USD-Kurs galt am Monatsende?
- Welche Kurse sind deaktiviert?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `neu` | Kurs erfassen | safe | nein | `/api/v1/finance/exchange-rates` |
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `finance/zahlungseingang` — Zahlungseingang

**Zweck:** Zahlungseingang im finance-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/zahlungseingang/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/zahlungseingang/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/zahlungseingang/readiness` |
| Rollout-Route | `/mask-rollout/finance__zahlungseingang/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/abstimmung/nebenbuch`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige Zahlungseingang.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `finance/zahlungslauf-kreditoren` — Zahlungslage

**Zweck:** Zahlungslage im finance-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/zahlungslauf-kreditoren/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/zahlungslauf-kreditoren/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/zahlungslauf-kreditoren/readiness` |
| Rollout-Route | `/mask-rollout/finance__zahlungslauf-kreditoren/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/payment-runs`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige Zahlungslage.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `schaeden/liste` — Schadenmeldungen

**Zweck:** Schadenmeldungen mit Meldefrist und Regulierungsstand verfolgen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/schaeden/liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/schaeden/liste/agent-contract` |
| Readiness | `GET /api/v1/masks/schaeden/liste/readiness` |
| Rollout-Route | `/mask-rollout/schaeden__liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/schaeden/meldungen`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Welche Schaeden muessen diese Woche gemeldet werden?
- Welche Schaeden sind reguliert?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `neu` | Schaden melden | safe | nein | `Oeffnet die Anlage; Rechte prueft deren Anlageweg.` |
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `stammdaten/hausbank` — Hausbank

**Zweck:** Hausbankenstamm.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/stammdaten/hausbank/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/stammdaten/hausbank/agent-contract` |
| Readiness | `GET /api/v1/masks/stammdaten/hausbank/readiness` |
| Rollout-Route | `/mask-rollout/stammdaten__hausbank/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/stammdaten/hausbanken/{entity_id}`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Welche BLZ hat Hausbank {entity_id}?

**Sensible Felder:** `iban, bic`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `/api/v1/stammdaten/hausbanken/{entity_id}` |

---

### `versicherungen/liste` — Versicherungen

**Zweck:** Versicherungsvertraege mit Praemie und Ablauf im Blick behalten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/versicherungen/liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/versicherungen/liste/agent-contract` |
| Readiness | `GET /api/v1/masks/versicherungen/liste/readiness` |
| Rollout-Route | `/mask-rollout/versicherungen__liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/versicherungen`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Welche Versicherungen laufen dieses Jahr aus?
- Was kosten alle Praemien zusammen?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `workspace/fibu` — FiBu-Cockpit

**Zweck:** Rollen-Startseite FiBu — OP, Zahlungslauf und Abschluss.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/workspace/fibu/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/workspace/fibu/agent-contract` |
| Readiness | `GET /api/v1/masks/workspace/fibu/readiness` |
| Rollout-Route | `/mask-rollout/workspace__fibu/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/finance/offene-posten`

**MCP-Tools (Domäne):**

- `finance.ap_invoice.propose` — scope `finance:write`, Risiko hoch
- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Wie hoch sind offene Posten?
- Was steht im Abschluss an?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

## Domäne: finanzplanung

### `finanzplanung/liquiditaet` — Liquiditaet

**Zweck:** Liquiditaet im finanzplanung-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finanzplanung/liquiditaet/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finanzplanung/liquiditaet/agent-contract` |
| Readiness | `GET /api/v1/masks/finanzplanung/liquiditaet/readiness` |
| Rollout-Route | `/mask-rollout/finanzplanung__liquiditaet/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/liquidity/overview`

**Beispiel-Prompts:**

- Zeige Liquiditaet.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

## Domäne: foerderung

### `foerderung/antrag` — Antrag

**Zweck:** Antrag im foerderung-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/foerderung/antrag/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/foerderung/antrag/agent-contract` |
| Readiness | `GET /api/v1/masks/foerderung/antrag/readiness` |
| Rollout-Route | `/mask-rollout/foerderung__antrag/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/foerderung/antraege`

**Beispiel-Prompts:**

- Zeige Antrag.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `subventionen/dashboard` — Foerder-Dashboard

**Zweck:** Foerderantraege und Bewilligungslage ueberblicken.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/subventionen/dashboard/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/subventionen/dashboard/agent-contract` |
| Readiness | `GET /api/v1/masks/subventionen/dashboard/readiness` |
| Rollout-Route | `/mask-rollout/subventionen__dashboard/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/foerderung/stats`

**Beispiel-Prompts:**

- Wie viele Antraege sind offen?
- Zeige Foerderstatistik.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

## Domäne: fuhrpark

### `fuhrpark/ausgehende-belege-dokumente` — Ausgehende belege dokumente

**Zweck:** Ausgehende belege dokumente im fuhrpark-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fuhrpark/ausgehende-belege-dokumente/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fuhrpark/ausgehende-belege-dokumente/agent-contract` |
| Readiness | `GET /api/v1/masks/fuhrpark/ausgehende-belege-dokumente/readiness` |
| Rollout-Route | `/mask-rollout/fuhrpark__ausgehende-belege-dokumente/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/fuhrpark/ausgehende-dokumente`

**Beispiel-Prompts:**

- Zeige Ausgehende belege dokumente.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fuhrpark/fahrzeug/neu` — Fahrzeug stamm

**Zweck:** Fahrzeug stamm im fuhrpark-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fuhrpark/fahrzeug/neu/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fuhrpark/fahrzeug/neu/agent-contract` |
| Readiness | `GET /api/v1/masks/fuhrpark/fahrzeug/neu/readiness` |
| Rollout-Route | `/mask-rollout/fuhrpark__fahrzeug__neu/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/fuhrpark/ausgehende-dokumente`

**Beispiel-Prompts:**

- Zeige Fahrzeug stamm.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fuhrpark/fuhrpark-auswertung-kosten-pro-fahrzeug` — Fuhrpark auswertung kosten pro fahrzeug

**Zweck:** Fuhrpark auswertung kosten pro fahrzeug im fuhrpark-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fuhrpark/fuhrpark-auswertung-kosten-pro-fahrzeug/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fuhrpark/fuhrpark-auswertung-kosten-pro-fahrzeug/agent-contract` |
| Readiness | `GET /api/v1/masks/fuhrpark/fuhrpark-auswertung-kosten-pro-fahrzeug/readiness` |
| Rollout-Route | `/mask-rollout/fuhrpark__fuhrpark-auswertung-kosten-pro-fahrzeug/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/fuhrpark/ausgehende-dokumente`

**Beispiel-Prompts:**

- Zeige Fuhrpark auswertung kosten pro fahrzeug.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fuhrpark/fuhrpark-auswertungen-menu` — Fuhrpark auswertungen menu

**Zweck:** Fuhrpark auswertungen menu im fuhrpark-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fuhrpark/fuhrpark-auswertungen-menu/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fuhrpark/fuhrpark-auswertungen-menu/agent-contract` |
| Readiness | `GET /api/v1/masks/fuhrpark/fuhrpark-auswertungen-menu/readiness` |
| Rollout-Route | `/mask-rollout/fuhrpark__fuhrpark-auswertungen-menu/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/fuhrpark/ausgehende-dokumente`

**Beispiel-Prompts:**

- Zeige Fuhrpark auswertungen menu.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fuhrpark/fuhrpark-klassisch` — Fuhrpark klassisch

**Zweck:** Fuhrpark klassisch im fuhrpark-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fuhrpark/fuhrpark-klassisch/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fuhrpark/fuhrpark-klassisch/agent-contract` |
| Readiness | `GET /api/v1/masks/fuhrpark/fuhrpark-klassisch/readiness` |
| Rollout-Route | `/mask-rollout/fuhrpark__fuhrpark-klassisch/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/fuhrpark/ausgehende-dokumente`

**Beispiel-Prompts:**

- Zeige Fuhrpark klassisch.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fuhrpark/fuhrpark-menue` — Fuhrpark menue

**Zweck:** Fuhrpark menue im fuhrpark-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fuhrpark/fuhrpark-menue/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fuhrpark/fuhrpark-menue/agent-contract` |
| Readiness | `GET /api/v1/masks/fuhrpark/fuhrpark-menue/readiness` |
| Rollout-Route | `/mask-rollout/fuhrpark__fuhrpark-menue/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/fuhrpark/ausgehende-dokumente`

**Beispiel-Prompts:**

- Zeige Fuhrpark menue.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fuhrpark/fuhrpark-rechnungen` — Fuhrpark rechnungen

**Zweck:** Fuhrpark rechnungen im fuhrpark-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fuhrpark/fuhrpark-rechnungen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fuhrpark/fuhrpark-rechnungen/agent-contract` |
| Readiness | `GET /api/v1/masks/fuhrpark/fuhrpark-rechnungen/readiness` |
| Rollout-Route | `/mask-rollout/fuhrpark__fuhrpark-rechnungen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/fuhrpark/ausgehende-dokumente`

**Beispiel-Prompts:**

- Zeige Fuhrpark rechnungen.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fuhrpark/fuhrpark-stammdaten` — Fuhrpark stammdaten

**Zweck:** Fuhrpark stammdaten im fuhrpark-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fuhrpark/fuhrpark-stammdaten/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fuhrpark/fuhrpark-stammdaten/agent-contract` |
| Readiness | `GET /api/v1/masks/fuhrpark/fuhrpark-stammdaten/readiness` |
| Rollout-Route | `/mask-rollout/fuhrpark__fuhrpark-stammdaten/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/fuhrpark/ausgehende-dokumente`

**Beispiel-Prompts:**

- Zeige Fuhrpark stammdaten.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

## Domäne: futter

### `futter/einzel/liste` — Liste

**Zweck:** Liste im futter-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/futter/einzel/liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/futter/einzel/liste/agent-contract` |
| Readiness | `GET /api/v1/masks/futter/einzel/liste/readiness` |
| Rollout-Route | `/mask-rollout/futter__einzel__liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/futter/chargen`

**Beispiel-Prompts:**

- Zeige Liste.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `futter/einzel/stamm/neu` — Stamm

**Zweck:** Stamm im futter-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/futter/einzel/stamm/neu/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/futter/einzel/stamm/neu/agent-contract` |
| Readiness | `GET /api/v1/masks/futter/einzel/stamm/neu/readiness` |
| Rollout-Route | `/mask-rollout/futter__einzel__stamm__neu/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/futter/chargen`

**Beispiel-Prompts:**

- Zeige Stamm.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `futter/misch/liste` — Liste

**Zweck:** Liste im futter-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/futter/misch/liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/futter/misch/liste/agent-contract` |
| Readiness | `GET /api/v1/masks/futter/misch/liste/readiness` |
| Rollout-Route | `/mask-rollout/futter__misch__liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/futter/chargen`

**Beispiel-Prompts:**

- Zeige Liste.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `futter/misch/stamm/neu` — Rezeptur-Komponenten

**Zweck:** Rezeptur-Komponenten im futter-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/futter/misch/stamm/neu/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/futter/misch/stamm/neu/agent-contract` |
| Readiness | `GET /api/v1/masks/futter/misch/stamm/neu/readiness` |
| Rollout-Route | `/mask-rollout/futter__misch__stamm__neu/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/futter/chargen`

**Beispiel-Prompts:**

- Zeige Rezeptur-Komponenten.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

## Domäne: futtermittel

### `futter/einzel` — Einzelfuttermittel

**Zweck:** Einzelfuttermittel (Futter-Pfad).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/futter/einzel/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/futter/einzel/agent-contract` |
| Readiness | `GET /api/v1/masks/futter/einzel/readiness` |
| Rollout-Route | `/mask-rollout/futter__einzel/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/futter/einzelfuttermittel/{entity_id}`

**Beispiel-Prompts:**

- Welches Protein hat Einzelfutter {entity_id}?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `futter/misch` — Mischfuttermittel

**Zweck:** Mischfuttermittel (Futter-Pfad).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/futter/misch/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/futter/misch/agent-contract` |
| Readiness | `GET /api/v1/masks/futter/misch/readiness` |
| Rollout-Route | `/mask-rollout/futter__misch/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/futter/mischfuttermittel/{entity_id}`

**Beispiel-Prompts:**

- Welchen Status hat Mischfutter {entity_id}?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `futtermittel/analyse` — Futteranalyse

**Zweck:** Laborbefund nachvollziehbar pruefen und genau eine Analyseversion bewusst aktivieren.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/futtermittel/analyse/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/futtermittel/analyse/agent-contract` |
| Readiness | `GET /api/v1/masks/futtermittel/analyse/readiness` |
| Rollout-Route | `/mask-rollout/futtermittel__analyse/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/rations-optimization/feed-analyses/{entity_id}`
- `values` → `/api/v1/agrar/rations-optimization/feed-analyses/{entity_id}/values`
- `findings` → `/api/v1/agrar/rations-optimization/feed-analyses/{entity_id}/findings`
- `history` → `/api/v1/agrar/rations-optimization/feed-analyses/{entity_id}/history`

**Beispiel-Prompts:**

- Welche Blocker verhindern die Freigabe?
- Zeige Original- und Rechenwerte dieser Analyse.

**Sensible Felder:** `original_document_id, original_sha256`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `validate` | Plausibilitaet pruefen | safe | nein | `/api/v1/agrar/rations-optimization/feed-analyses/{entity_id}/actions/validate` |
| `release` | Analyse freigeben | high | ja | `/api/v1/agrar/rations-optimization/feed-analyses/{entity_id}/actions/release` |
| `reject` | Zurueckweisen | moderate | nein | `/api/v1/agrar/rations-optimization/feed-analyses/{entity_id}/actions/reject` |

---

### `futtermittel/analysen` — Futteranalysen

**Zweck:** Futteranalysen nach Plausibilitaet, Freigabe und Aktualitaet priorisieren.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/futtermittel/analysen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/futtermittel/analysen/agent-contract` |
| Readiness | `GET /api/v1/masks/futtermittel/analysen/readiness` |
| Rollout-Route | `/mask-rollout/futtermittel__analysen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/agrar/rations-optimization/feed-analyses`

**Beispiel-Prompts:**

- Welche Analysen warten auf Pruefung?
- Welche aktiven Analysen sind veraltet?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `import_analysis` | Analyse erfassen | safe | nein | `—` |

---

### `futtermittel/beratung` — Beratung

**Zweck:** Beratung im futtermittel-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/futtermittel/beratung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/futtermittel/beratung/agent-contract` |
| Readiness | `GET /api/v1/masks/futtermittel/beratung/readiness` |
| Rollout-Route | `/mask-rollout/futtermittel__beratung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/futtermittel/qs/haccp-plaene`

**Beispiel-Prompts:**

- Zeige Beratung.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `futtermittel/chargen/neu` — Charge-Verfolgung

**Zweck:** Charge-Verfolgung im futtermittel-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/futtermittel/chargen/neu/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/futtermittel/chargen/neu/agent-contract` |
| Readiness | `GET /api/v1/masks/futtermittel/chargen/neu/readiness` |
| Rollout-Route | `/mask-rollout/futtermittel__chargen__neu/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/futter/chargen`

**Beispiel-Prompts:**

- Zeige Charge-Verfolgung.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `futtermittel/einzelfuttermittel` — Einzelfuttermittel

**Zweck:** Einzelfuttermittel-Stamm: Naehrstoffgehalte und Preise fuer Rationsoptimierung.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/futtermittel/einzelfuttermittel/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/futtermittel/einzelfuttermittel/agent-contract` |
| Readiness | `GET /api/v1/masks/futtermittel/einzelfuttermittel/readiness` |
| Rollout-Route | `/mask-rollout/futtermittel__einzelfuttermittel/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/rations-optimization/feed-catalog/feeds/{entity_id}`
- `naehrstoffe` → `/api/v1/agrar/rations-optimization/feed-catalog/feeds/{entity_id}/reference-values`
- `preise` → `/api/v1/agrar/rations-optimization/feed-catalog/feeds/{entity_id}/products`
- `history` → `/api/v1/agrar/rations-optimization/feed-catalog/feeds/{entity_id}/history`

**Beispiel-Prompts:**

- Welche NEL und Rohprotein-Gehalte hat Futtermittel {entity_id}?
- Zeige die aktuellen Preise fuer Futtermittel {entity_id}.

**Sensible Felder:** `preis`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `futtermittel/einzelfuttermittel-liste` — Einzelfuttermittel

**Zweck:** Einzelfuttermittel des Futterkatalogs finden, oeffnen und nicht mehr gefuehrte stilllegen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/futtermittel/einzelfuttermittel-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/futtermittel/einzelfuttermittel-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/futtermittel/einzelfuttermittel-liste/readiness` |
| Rollout-Route | `/mask-rollout/futtermittel__einzelfuttermittel-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/agrar/rations-optimization/feed-catalog/feeds`

**Beispiel-Prompts:**

- Welche Einzelfuttermittel sind freigegeben?
- Welche Futtermittel haben keinen Preis?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `neu` | Neues Einzelfuttermittel | safe | nein | `Oeffnet die Anlage; Rechte prueft deren Anlageweg.` |
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `futtermittel/einzelfuttermittel/liste` — Einzelfuttermittel liste

**Zweck:** Einzelfuttermittel liste im futtermittel-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/futtermittel/einzelfuttermittel/liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/futtermittel/einzelfuttermittel/liste/agent-contract` |
| Readiness | `GET /api/v1/masks/futtermittel/einzelfuttermittel/liste/readiness` |
| Rollout-Route | `/mask-rollout/futtermittel__einzelfuttermittel__liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/futtermittel/qs/haccp-plaene`

**Beispiel-Prompts:**

- Zeige Einzelfuttermittel liste.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `futtermittel/einzelfuttermittel/stamm/new` — Einzelfuttermittel-Stammdaten

**Zweck:** Einzelfuttermittel-Stammdaten als Stammblatt pflegen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/futtermittel/einzelfuttermittel/stamm/new/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/futtermittel/einzelfuttermittel/stamm/new/agent-contract` |
| Readiness | `GET /api/v1/masks/futtermittel/einzelfuttermittel/stamm/new/readiness` |
| Rollout-Route | `/mask-rollout/futtermittel__einzelfuttermittel__stamm__new/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/futter/einzelfuttermittel/{entity_id}`

**Beispiel-Prompts:**

- Oeffne Einzelfuttermittel-Stammdaten.
- Bearbeite Stammdaten.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `futtermittel/fuetterungsdokumentation-mobil` — Fuetterungsdokumentation mobil

**Zweck:** Fuetterungsdokumentation mobil im futtermittel-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/futtermittel/fuetterungsdokumentation-mobil/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/futtermittel/fuetterungsdokumentation-mobil/agent-contract` |
| Readiness | `GET /api/v1/masks/futtermittel/fuetterungsdokumentation-mobil/readiness` |
| Rollout-Route | `/mask-rollout/futtermittel__fuetterungsdokumentation-mobil/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/futtermittel/qs/haccp-plaene`

**Beispiel-Prompts:**

- Zeige Fuetterungsdokumentation mobil.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `futtermittel/futtermittel-bestellung` — Futtermittel bestellung

**Zweck:** Futtermittel bestellung im futtermittel-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/futtermittel/futtermittel-bestellung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/futtermittel/futtermittel-bestellung/agent-contract` |
| Readiness | `GET /api/v1/masks/futtermittel/futtermittel-bestellung/readiness` |
| Rollout-Route | `/mask-rollout/futtermittel__futtermittel-bestellung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/futtermittel/qs/haccp-plaene`

**Beispiel-Prompts:**

- Zeige Futtermittel bestellung.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `futtermittel/futtermittel-qualitaetskontrolle` — Futtermittel-Qualitaetskontrolle

**Zweck:** Futtermittel-QS-Worklist zentral bearbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/futtermittel/futtermittel-qualitaetskontrolle/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/futtermittel/futtermittel-qualitaetskontrolle/agent-contract` |
| Readiness | `GET /api/v1/masks/futtermittel/futtermittel-qualitaetskontrolle/readiness` |
| Rollout-Route | `/mask-rollout/futtermittel__futtermittel-qualitaetskontrolle/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `items` → `/api/v1/futter/qualitaetskontrolle`

**Beispiel-Prompts:**

- Welche QS-Pruefungen sind ueberfaellig?

---

### `futtermittel/futtermittel-statistik` — Futtermittel statistik

**Zweck:** Futtermittel statistik im futtermittel-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/futtermittel/futtermittel-statistik/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/futtermittel/futtermittel-statistik/agent-contract` |
| Readiness | `GET /api/v1/masks/futtermittel/futtermittel-statistik/readiness` |
| Rollout-Route | `/mask-rollout/futtermittel__futtermittel-statistik/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/futtermittel/qs/haccp-plaene`

**Beispiel-Prompts:**

- Zeige Futtermittel statistik.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `futtermittel/grundfutteranalysen` — Grundfutteranalysen native

**Zweck:** Grundfutteranalysen native im futtermittel-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/futtermittel/grundfutteranalysen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/futtermittel/grundfutteranalysen/agent-contract` |
| Readiness | `GET /api/v1/masks/futtermittel/grundfutteranalysen/readiness` |
| Rollout-Route | `/mask-rollout/futtermittel__grundfutteranalysen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/futtermittel/qs/haccp-plaene`

**Beispiel-Prompts:**

- Zeige Grundfutteranalysen native.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `futtermittel/integrationsmonitor` — Integrationsmonitor

**Zweck:** Integrationsmonitor im futtermittel-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/futtermittel/integrationsmonitor/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/futtermittel/integrationsmonitor/agent-contract` |
| Readiness | `GET /api/v1/masks/futtermittel/integrationsmonitor/readiness` |
| Rollout-Route | `/mask-rollout/futtermittel__integrationsmonitor/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/futtermittel/qs/haccp-plaene`

**Beispiel-Prompts:**

- Zeige Integrationsmonitor.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `futtermittel/mischfuttermittel` — Mischfuttermittel

**Zweck:** Mischfuttermittel: Rezeptur-Komponenten und berechnete Naehrstoffgehalte fuer Rationsoptimierung.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/futtermittel/mischfuttermittel/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/futtermittel/mischfuttermittel/agent-contract` |
| Readiness | `GET /api/v1/masks/futtermittel/mischfuttermittel/readiness` |
| Rollout-Route | `/mask-rollout/futtermittel__mischfuttermittel/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/futter/mischfuttermittel/{entity_id}`
- `rezeptur` → `/api/v1/masks/futtermittel/mischfuttermittel/entity/{entity_id}/tabs/rezeptur`
- `naehrstoffe` → `/api/v1/masks/futtermittel/mischfuttermittel/entity/{entity_id}/tabs/naehrstoffe`

**Beispiel-Prompts:**

- Welche Komponenten hat Mischfutter {entity_id}?
- Zeige die berechneten Naehrstoffgehalte von Mischfutter {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `/api/v1/futter/mischfuttermittel/{entity_id}/actions/bearbeiten` |

---

### `futtermittel/mischfuttermittel-liste` — Mischfuttermittel

**Zweck:** Mischfuttermittel je Tierart finden, oeffnen und nicht mehr gefuehrte deaktivieren.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/futtermittel/mischfuttermittel-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/futtermittel/mischfuttermittel-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/futtermittel/mischfuttermittel-liste/readiness` |
| Rollout-Route | `/mask-rollout/futtermittel__mischfuttermittel-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/futter/mischfuttermittel`

**Beispiel-Prompts:**

- Welche Mischfutter fuehren wir fuer Milchkuehe?
- Zeige Mischfutter mit ueber 18 % Protein.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `neu` | Neues Mischfuttermittel | safe | nein | `Oeffnet die Anlage; Rechte prueft deren Anlageweg.` |
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `futtermittel/mischfuttermittel/liste` — Mischfuttermittel liste

**Zweck:** Mischfuttermittel liste im futtermittel-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/futtermittel/mischfuttermittel/liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/futtermittel/mischfuttermittel/liste/agent-contract` |
| Readiness | `GET /api/v1/masks/futtermittel/mischfuttermittel/liste/readiness` |
| Rollout-Route | `/mask-rollout/futtermittel__mischfuttermittel__liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/futtermittel/qs/haccp-plaene`

**Beispiel-Prompts:**

- Zeige Mischfuttermittel liste.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `futtermittel/mischfuttermittel/stamm/new` — Mischfuttermittel-Stammdaten

**Zweck:** Mischfuttermittel-Stammdaten als Stammblatt pflegen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/futtermittel/mischfuttermittel/stamm/new/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/futtermittel/mischfuttermittel/stamm/new/agent-contract` |
| Readiness | `GET /api/v1/masks/futtermittel/mischfuttermittel/stamm/new/readiness` |
| Rollout-Route | `/mask-rollout/futtermittel__mischfuttermittel__stamm__new/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/futter/mischfuttermittel/{entity_id}`

**Beispiel-Prompts:**

- Oeffne Mischfuttermittel-Stammdaten.
- Bearbeite Stammdaten.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `futtermittel/rations-schnittstellen-import` — Rations schnittstellen import

**Zweck:** Rations schnittstellen import im futtermittel-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/futtermittel/rations-schnittstellen-import/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/futtermittel/rations-schnittstellen-import/agent-contract` |
| Readiness | `GET /api/v1/masks/futtermittel/rations-schnittstellen-import/readiness` |
| Rollout-Route | `/mask-rollout/futtermittel__rations-schnittstellen-import/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/futtermittel/qs/haccp-plaene`

**Beispiel-Prompts:**

- Zeige Rations schnittstellen import.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `futtermittel/rations-zugang` — Rations zugang

**Zweck:** Rations zugang im futtermittel-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/futtermittel/rations-zugang/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/futtermittel/rations-zugang/agent-contract` |
| Readiness | `GET /api/v1/masks/futtermittel/rations-zugang/readiness` |
| Rollout-Route | `/mask-rollout/futtermittel__rations-zugang/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/futtermittel/qs/haccp-plaene`

**Beispiel-Prompts:**

- Zeige Rations zugang.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `futtermittel/rationseditor` — Rationseditor

**Zweck:** Rationseditor im futtermittel-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/futtermittel/rationseditor/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/futtermittel/rationseditor/agent-contract` |
| Readiness | `GET /api/v1/masks/futtermittel/rationseditor/readiness` |
| Rollout-Route | `/mask-rollout/futtermittel__rationseditor/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/futtermittel/qs/haccp-plaene`

**Beispiel-Prompts:**

- Zeige Rationseditor.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `futtermittel/rationsoptimierung` — Rationsoptimierung

**Zweck:** Rationsoptimierung mandantensicher als Cockpit bereitstellen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/futtermittel/rationsoptimierung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/futtermittel/rationsoptimierung/agent-contract` |
| Readiness | `GET /api/v1/masks/futtermittel/rationsoptimierung/readiness` |
| Rollout-Route | `/mask-rollout/futtermittel__rationsoptimierung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/futtermittel/qs/haccp-plaene`

**Beispiel-Prompts:**

- Zeige Rationsoptimierung.
- Aktualisiere die Kennzahlen.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `futtermittel/rationsvergleich` — Rationsvergleich

**Zweck:** Rationsvergleich im futtermittel-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/futtermittel/rationsvergleich/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/futtermittel/rationsvergleich/agent-contract` |
| Readiness | `GET /api/v1/masks/futtermittel/rationsvergleich/readiness` |
| Rollout-Route | `/mask-rollout/futtermittel__rationsvergleich/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/futtermittel/qs/haccp-plaene`

**Beispiel-Prompts:**

- Zeige Rationsvergleich.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `futtermittel/wareneingang` — Futtermittel wareneingang

**Zweck:** Futtermittel wareneingang im futtermittel-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/futtermittel/wareneingang/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/futtermittel/wareneingang/agent-contract` |
| Readiness | `GET /api/v1/masks/futtermittel/wareneingang/readiness` |
| Rollout-Route | `/mask-rollout/futtermittel__wareneingang/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/futtermittel/qs/haccp-plaene`

**Beispiel-Prompts:**

- Zeige Futtermittel wareneingang.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

## Domäne: genossenschaft

### `aktien/dividenden` — Dividenden

**Zweck:** Stamm- und Fachmaske fuer Dividenden (aktien/dividenden).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/aktien/dividenden/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/aktien/dividenden/agent-contract` |
| Readiness | `GET /api/v1/masks/aktien/dividenden/readiness` |
| Rollout-Route | `/mask-rollout/aktien__dividenden/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/genossenschaft/mitglieder/{entity_id}`

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Dividenden {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `aktien/hauptversammlung` — Hauptversammlung

**Zweck:** Stamm- und Fachmaske fuer Hauptversammlung (aktien/hauptversammlung).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/aktien/hauptversammlung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/aktien/hauptversammlung/agent-contract` |
| Readiness | `GET /api/v1/masks/aktien/hauptversammlung/readiness` |
| Rollout-Route | `/mask-rollout/aktien__hauptversammlung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/genossenschaft/mitglieder/{entity_id}`

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Hauptversammlung {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `aktien/mitglieder` — Mitglieder

**Zweck:** Stamm- und Fachmaske fuer Mitglieder (aktien/mitglieder).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/aktien/mitglieder/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/aktien/mitglieder/agent-contract` |
| Readiness | `GET /api/v1/masks/aktien/mitglieder/readiness` |
| Rollout-Route | `/mask-rollout/aktien__mitglieder/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/genossenschaft/mitglieder/{entity_id}`

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Mitglieder {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `aktien/stimmrechte` — Stimmrechte

**Zweck:** Stamm- und Fachmaske fuer Stimmrechte (aktien/stimmrechte).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/aktien/stimmrechte/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/aktien/stimmrechte/agent-contract` |
| Readiness | `GET /api/v1/masks/aktien/stimmrechte/readiness` |
| Rollout-Route | `/mask-rollout/aktien__stimmrechte/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/genossenschaft/mitglieder/{entity_id}`

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Stimmrechte {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `aktien/zeichnungen` — Zeichnungen

**Zweck:** Stamm- und Fachmaske fuer Zeichnungen (aktien/zeichnungen).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/aktien/zeichnungen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/aktien/zeichnungen/agent-contract` |
| Readiness | `GET /api/v1/masks/aktien/zeichnungen/readiness` |
| Rollout-Route | `/mask-rollout/aktien__zeichnungen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/genossenschaft/mitglieder/{entity_id}`

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Zeichnungen {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `genossenschaft/mitglieder` — Mitglieder

**Zweck:** Mitglieder im genossenschaft-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/genossenschaft/mitglieder/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/genossenschaft/mitglieder/agent-contract` |
| Readiness | `GET /api/v1/masks/genossenschaft/mitglieder/readiness` |
| Rollout-Route | `/mask-rollout/genossenschaft__mitglieder/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/genossenschaft/mitglieder`

**Beispiel-Prompts:**

- Zeige Mitglieder.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `genossenschaft/mitglieder-liste` — Mitglieder

**Zweck:** Mitglieder: Eintraege finden und Details oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/genossenschaft/mitglieder-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/genossenschaft/mitglieder-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/genossenschaft/mitglieder-liste/readiness` |
| Rollout-Route | `/mask-rollout/genossenschaft__mitglieder-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/genossenschaft/mitglieder`

**Beispiel-Prompts:**

- Welche offenen Mitglieder?
- Zeige aktuelle Mitglieder.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

## Domäne: hr

### `personal/bewerbung-einwilligung` — Einwilligung zur Aufbewahrung

**Zweck:** Einwilligung zur laengeren Aufbewahrung einer Bewerbung erteilen oder widerrufen; das Verzeichnis ist der Nachweis nach Art. 7 Abs. 1 DSGVO.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/personal/bewerbung-einwilligung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/personal/bewerbung-einwilligung/agent-contract` |
| Readiness | `GET /api/v1/masks/personal/bewerbung-einwilligung/readiness` |
| Rollout-Route | `/mask-rollout/personal__bewerbung-einwilligung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/personal/applications/{entity_id}`
- `einwilligung` → `/api/v1/personal/applications/{entity_id}/einwilligung`
- `fassungen` → `/api/v1/personal/applications/einwilligungserklaerungen`

**MCP-Tools (Domäne):**

- `hr.bewerbung.speichern` — scope `hr:write`, Risiko mittel
- `hr.einwilligung.anlegen` — scope `hr:write`, Risiko mittel
- `hr.onboarding.speichern` — scope `hr:write`, Risiko mittel
- `hr.qualifikation.speichern` — scope `hr:write`, Risiko mittel
- `hr.schulung.speichern` — scope `hr:write`, Risiko mittel

**Beispiel-Prompts:**

- Bis wann darf die Bewerbung {entity_id} aufbewahrt werden?

**Sensible Felder:** `applicant_name, erfasst_durch`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `erteilen` | Einwilligung erteilen | safe | nein | `Erteilt die Einwilligung gegen die gewaehlte Fassung.` |
| `widerrufen` | Einwilligung widerrufen | moderate | nein | `Widerruft die Einwilligung sofort, ohne Grund.` |
| `zurueck` | Zu den Bewerbungen | safe | nein | `Wechselt zur Bewerbungsliste.` |
| `erklaerungen` | Einwilligungserklärungen | safe | nein | `Oeffnet die Fassungen der Einwilligungserklaerung.` |

---

### `personal/bewerbungen` — Bewerbungen

**Zweck:** Bewerbungen erfassen. Der Stand folgt den offenen Stufen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/personal/bewerbungen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/personal/bewerbungen/agent-contract` |
| Readiness | `GET /api/v1/masks/personal/bewerbungen/readiness` |
| Rollout-Route | `/mask-rollout/personal__bewerbungen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `bewerbungen` → `/api/v1/personal/applications`

**MCP-Tools (Domäne):**

- `hr.bewerbung.speichern` — scope `hr:write`, Risiko mittel
- `hr.einwilligung.anlegen` — scope `hr:write`, Risiko mittel
- `hr.onboarding.speichern` — scope `hr:write`, Risiko mittel
- `hr.qualifikation.speichern` — scope `hr:write`, Risiko mittel
- `hr.schulung.speichern` — scope `hr:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Bewerbung steht noch im Eingang?

**Sensible Felder:** `applicant_email`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `speichern` | Speichern | safe | nein | `/api/v1/personal/applications/actions/speichern` |
| `neu` | Neu | safe | nein | `Leert die Eingabe fuer eine neue Bewerbung.` |
| `erklaerungen` | Einwilligungserklärungen | safe | nein | `Oeffnet die Fassungen der Einwilligungserklaerung.` |

---

### `personal/einwilligungserklaerungen` — Einwilligungserklärungen

**Zweck:** Fassungen der Einwilligungserklaerung fuer Bewerbungen fuehren; erteilt wird immer gegen eine Fassung.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/personal/einwilligungserklaerungen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/personal/einwilligungserklaerungen/agent-contract` |
| Readiness | `GET /api/v1/masks/personal/einwilligungserklaerungen/readiness` |
| Rollout-Route | `/mask-rollout/personal__einwilligungserklaerungen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `fassungen` → `/api/v1/personal/applications/einwilligungserklaerungen`

**MCP-Tools (Domäne):**

- `hr.bewerbung.speichern` — scope `hr:write`, Risiko mittel
- `hr.einwilligung.anlegen` — scope `hr:write`, Risiko mittel
- `hr.onboarding.speichern` — scope `hr:write`, Risiko mittel
- `hr.qualifikation.speichern` — scope `hr:write`, Risiko mittel
- `hr.schulung.speichern` — scope `hr:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Fassung der Einwilligungserklaerung ist die neueste?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `anlegen` | Fassung anlegen | safe | nein | `/api/v1/personal/applications/einwilligungserklaerungen/actions/anlegen` |
| `neu` | Neu | safe | nein | `Leert die Eingabe fuer eine neue Fassung.` |

---

### `personal/onboarding` — Onboarding

**Zweck:** Einarbeitungslaeufe anlegen. Der Stand folgt den offenen Laeufen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/personal/onboarding/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/personal/onboarding/agent-contract` |
| Readiness | `GET /api/v1/masks/personal/onboarding/readiness` |
| Rollout-Route | `/mask-rollout/personal__onboarding/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `laeufe` → `/api/v1/training/onboarding/runs`

**MCP-Tools (Domäne):**

- `hr.bewerbung.speichern` — scope `hr:write`, Risiko mittel
- `hr.einwilligung.anlegen` — scope `hr:write`, Risiko mittel
- `hr.onboarding.speichern` — scope `hr:write`, Risiko mittel
- `hr.qualifikation.speichern` — scope `hr:write`, Risiko mittel
- `hr.schulung.speichern` — scope `hr:write`, Risiko mittel

**Beispiel-Prompts:**

- Welcher Lauf ist noch nicht abgeschlossen?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `speichern` | Speichern | safe | nein | `/api/v1/training/onboarding/runs/actions/speichern` |
| `neu` | Neu | safe | nein | `Leert die Eingabe fuer einen neuen Lauf.` |

---

### `personal/qualifikationen` — Qualifikationen

**Zweck:** Qualifikationsprofile anlegen. Der Stand folgt der Gueltigkeit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/personal/qualifikationen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/personal/qualifikationen/agent-contract` |
| Readiness | `GET /api/v1/masks/personal/qualifikationen/readiness` |
| Rollout-Route | `/mask-rollout/personal__qualifikationen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `qualifikationen` → `/api/v1/training/qualifications`

**MCP-Tools (Domäne):**

- `hr.bewerbung.speichern` — scope `hr:write`, Risiko mittel
- `hr.einwilligung.anlegen` — scope `hr:write`, Risiko mittel
- `hr.onboarding.speichern` — scope `hr:write`, Risiko mittel
- `hr.qualifikation.speichern` — scope `hr:write`, Risiko mittel
- `hr.schulung.speichern` — scope `hr:write`, Risiko mittel

**Beispiel-Prompts:**

- Welches Profil hat noch kein Gueltig-bis?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `speichern` | Speichern | safe | nein | `/api/v1/training/qualifications/actions/speichern` |
| `neu` | Neu | safe | nein | `Leert die Eingabe fuer ein neues Profil.` |

---

### `personal/schulungen` — Schulungen

**Zweck:** Schulungszuweisungen anlegen. Der Stand folgt den offenen Nachweisen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/personal/schulungen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/personal/schulungen/agent-contract` |
| Readiness | `GET /api/v1/masks/personal/schulungen/readiness` |
| Rollout-Route | `/mask-rollout/personal__schulungen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `schulungen` → `/api/v1/training/assignments`

**MCP-Tools (Domäne):**

- `hr.bewerbung.speichern` — scope `hr:write`, Risiko mittel
- `hr.einwilligung.anlegen` — scope `hr:write`, Risiko mittel
- `hr.onboarding.speichern` — scope `hr:write`, Risiko mittel
- `hr.qualifikation.speichern` — scope `hr:write`, Risiko mittel
- `hr.schulung.speichern` — scope `hr:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Schulung laeuft in den naechsten 60 Tagen ab?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `speichern` | Speichern | safe | nein | `/api/v1/training/assignments/actions/speichern` |
| `neu` | Neu | safe | nein | `Leert die Eingabe fuer eine neue Zuweisung.` |

---

## Domäne: identity

### `auth/callback` — OIDC Callback

**Zweck:** OIDC Callback als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/auth/callback/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/auth/callback/agent-contract` |
| Readiness | `GET /api/v1/masks/auth/callback/readiness` |
| Rollout-Route | `/mask-rollout/auth__callback/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/identity/session`

**Beispiel-Prompts:**

- Zeige OIDC Callback.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `auth/login` — Anmeldung

**Zweck:** Anmeldung als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/auth/login/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/auth/login/agent-contract` |
| Readiness | `GET /api/v1/masks/auth/login/readiness` |
| Rollout-Route | `/mask-rollout/auth__login/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/identity/session`

**Beispiel-Prompts:**

- Zeige Anmeldung.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

## Domäne: integration

### `schnittstelle/legacy-adapter-monitor` — Standard-/Unimet-Adapter

**Zweck:** L3 Standard- und Unimet-Dateien idempotent pruefen, mappen und abstimmen, ohne produktiv zu buchen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/schnittstelle/legacy-adapter-monitor/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/schnittstelle/legacy-adapter-monitor/agent-contract` |
| Readiness | `GET /api/v1/masks/schnittstelle/legacy-adapter-monitor/readiness` |
| Rollout-Route | `/mask-rollout/schnittstelle__legacy-adapter-monitor/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/legacy-interface-adapters/batches`
- `batches` → `/api/v1/legacy-interface-adapters/batches`

**Beispiel-Prompts:**

- Zeige quarantinierte Unimet-Batches.
- Stimme diesen L3-Standard-Batch ab.

**Sensible Felder:** `external_id, payload_hash, error_message`

---

## Domäne: inventory

### `charge/etiketten` — Etiketten

**Zweck:** Etiketten als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/charge/etiketten/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/charge/etiketten/agent-contract` |
| Readiness | `GET /api/v1/masks/charge/etiketten/readiness` |
| Rollout-Route | `/mask-rollout/charge__etiketten/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/etiketten/drucker`

**MCP-Tools (Domäne):**

- `wms.lot.trace` — scope `inventory:read`, Risiko niedrig
- `wms.cell.status` — scope `inventory:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige Etiketten.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `charge/mischung` — Chargen-Mischung

**Zweck:** Chargen-Mischung als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/charge/mischung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/charge/mischung/agent-contract` |
| Readiness | `GET /api/v1/masks/charge/mischung/readiness` |
| Rollout-Route | `/mask-rollout/charge__mischung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/chargen`

**MCP-Tools (Domäne):**

- `wms.lot.trace` — scope `inventory:read`, Risiko niedrig
- `wms.cell.status` — scope `inventory:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige Chargen-Mischung.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `charge/probenahme` — Probenahme

**Zweck:** Probenahme als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/charge/probenahme/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/charge/probenahme/agent-contract` |
| Readiness | `GET /api/v1/masks/charge/probenahme/readiness` |
| Rollout-Route | `/mask-rollout/charge__probenahme/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/chargen/stats/summary`

**MCP-Tools (Domäne):**

- `wms.lot.trace` — scope `inventory:read`, Risiko niedrig
- `wms.cell.status` — scope `inventory:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige Probenahme.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `charge/sperrlager` — Sperrlager

**Zweck:** Sperrlager als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/charge/sperrlager/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/charge/sperrlager/agent-contract` |
| Readiness | `GET /api/v1/masks/charge/sperrlager/readiness` |
| Rollout-Route | `/mask-rollout/charge__sperrlager/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/compliance/artikel-sperren`

**MCP-Tools (Domäne):**

- `wms.lot.trace` — scope `inventory:read`, Risiko niedrig
- `wms.cell.status` — scope `inventory:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige Sperrlager.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `charge/teilung` — Chargenteilung

**Zweck:** Chargenteilung als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/charge/teilung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/charge/teilung/agent-contract` |
| Readiness | `GET /api/v1/masks/charge/teilung/readiness` |
| Rollout-Route | `/mask-rollout/charge__teilung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/chargen`

**MCP-Tools (Domäne):**

- `wms.lot.trace` — scope `inventory:read`, Risiko niedrig
- `wms.cell.status` — scope `inventory:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige Chargenteilung.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `charge/zusammenfuehrung` — Chargenzusammenfuehrung

**Zweck:** Chargenzusammenfuehrung als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/charge/zusammenfuehrung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/charge/zusammenfuehrung/agent-contract` |
| Readiness | `GET /api/v1/masks/charge/zusammenfuehrung/readiness` |
| Rollout-Route | `/mask-rollout/charge__zusammenfuehrung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/chargen`

**MCP-Tools (Domäne):**

- `wms.lot.trace` — scope `inventory:read`, Risiko niedrig
- `wms.cell.status` — scope `inventory:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige Chargenzusammenfuehrung.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `inventory/epcis` — Index

**Zweck:** Index im inventory-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/inventory/epcis/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/inventory/epcis/agent-contract` |
| Readiness | `GET /api/v1/masks/inventory/epcis/readiness` |
| Rollout-Route | `/mask-rollout/inventory__epcis/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/inventory/articles`

**MCP-Tools (Domäne):**

- `wms.lot.trace` — scope `inventory:read`, Risiko niedrig
- `wms.cell.status` — scope `inventory:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige Index.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `lager/foreign-goods-queue` — Fremdware-Queue

**Zweck:** Fremdware-Worklist parallel zur Detailmaske bedienen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/lager/foreign-goods-queue/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/lager/foreign-goods-queue/agent-contract` |
| Readiness | `GET /api/v1/masks/lager/foreign-goods-queue/readiness` |
| Rollout-Route | `/mask-rollout/lager__foreign-goods-queue/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/foreign-goods/summary`
- `foreign_goods` → `/api/v1/foreign-goods`

**MCP-Tools (Domäne):**

- `wms.lot.trace` — scope `inventory:read`, Risiko niedrig
- `wms.cell.status` — scope `inventory:read`, Risiko niedrig

**Beispiel-Prompts:**

- Welche Fremdware-Vorgaenge sind offen?

---

### `lager/fremdware` — Fremdware und Fremdbestand

**Zweck:** Fremde Ware eigentuemer- und mandantensicher im Lager steuern.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/lager/fremdware/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/lager/fremdware/agent-contract` |
| Readiness | `GET /api/v1/masks/lager/fremdware/readiness` |
| Rollout-Route | `/mask-rollout/lager__fremdware/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/foreign-goods/summary`
- `items` → `/api/v1/foreign-goods`

**MCP-Tools (Domäne):**

- `wms.lot.trace` — scope `inventory:read`, Risiko niedrig
- `wms.cell.status` — scope `inventory:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige Fremdbestand nach Eigentuemer.
- Welche Einlagerungen sind ueberfaellig?

**Sensible Felder:** `tenant_id, eigentuemer_id, eigentuemer_name, lagerort, notiz`

---

### `lager/inventur-nebenlaeufe` — Inventur-Nebenlaeufe

**Zweck:** Inventur-Nebenlaeufe hashgebunden und im Vier-Augen-Prinzip steuern.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/lager/inventur-nebenlaeufe/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/lager/inventur-nebenlaeufe/agent-contract` |
| Readiness | `GET /api/v1/masks/lager/inventur-nebenlaeufe/readiness` |
| Rollout-Route | `/mask-rollout/lager__inventur-nebenlaeufe/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/inventory/auxiliary/summary`
- `batches` → `/api/v1/inventory/auxiliary/batches`

**MCP-Tools (Domäne):**

- `wms.lot.trace` — scope `inventory:read`, Risiko niedrig
- `wms.cell.status` — scope `inventory:read`, Risiko niedrig

**Beispiel-Prompts:**

- Erzeuge einen Kontrolllauf.
- Welche Bestandsvortraege warten auf Freigabe?

**Sensible Felder:** `maker, checker, source_hash`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `create_count_sheet` | Zaehlliste | safe | nein | `/api/v1/inventory/auxiliary/actions/create_count_sheet` |
| `create_control` | Kontrolllauf | safe | nein | `/api/v1/inventory/auxiliary/actions/create_control` |
| `create_valuation` | Vorlaeufig bewerten | safe | nein | `/api/v1/inventory/auxiliary/actions/create_valuation` |
| `create_opening` | Bestandsvortrag | high | ja | `—` |

---

### `produktion/chargen-bearbeiten` — Chargen-Nummern bearbeiten

**Zweck:** Chargenkennzeichen pflegen und qualitaetsgepruefte Chargen nachvollziehbar freigeben.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/produktion/chargen-bearbeiten/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/produktion/chargen-bearbeiten/agent-contract` |
| Readiness | `GET /api/v1/masks/produktion/chargen-bearbeiten/readiness` |
| Rollout-Route | `/mask-rollout/produktion__chargen-bearbeiten/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/chargen/stats/summary`
- `charges` → `/api/v1/chargen`

**MCP-Tools (Domäne):**

- `wms.lot.trace` — scope `inventory:read`, Risiko niedrig
- `wms.cell.status` — scope `inventory:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige nicht freigegebene Chargen.
- Pflege die Anerkennungsnummer.

**Sensible Felder:** `lieferanten_charge, anerkennungs_nr, herkunft`

---

## Domäne: kasse

### `kasse/tagesabschluss` — Tagesabschluss

**Zweck:** Tagesabschluss im kasse-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/kasse/tagesabschluss/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/kasse/tagesabschluss/agent-contract` |
| Readiness | `GET /api/v1/masks/kasse/tagesabschluss/readiness` |
| Rollout-Route | `/mask-rollout/kasse__tagesabschluss/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/kasse/tagesabschluss/aktuell`

**Beispiel-Prompts:**

- Zeige Tagesabschluss.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

## Domäne: kontrakte

### `kontrakte/FrmKontraktProtokoll` — FrmKontraktProtokoll

**Zweck:** FrmKontraktProtokoll im kontrakte-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/kontrakte/FrmKontraktProtokoll/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/kontrakte/FrmKontraktProtokoll/agent-contract` |
| Readiness | `GET /api/v1/masks/kontrakte/FrmKontraktProtokoll/readiness` |
| Rollout-Route | `/mask-rollout/kontrakte__FrmKontraktProtokoll/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/kontrakte`

**Beispiel-Prompts:**

- Zeige FrmKontraktProtokoll.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `kontrakte/KontraktAlarmDashboard` — KontraktAlarmDashboard

**Zweck:** KontraktAlarmDashboard mandantensicher als Cockpit bereitstellen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/kontrakte/KontraktAlarmDashboard/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/kontrakte/KontraktAlarmDashboard/agent-contract` |
| Readiness | `GET /api/v1/masks/kontrakte/KontraktAlarmDashboard/readiness` |
| Rollout-Route | `/mask-rollout/kontrakte__KontraktAlarmDashboard/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/kontrakte`

**Beispiel-Prompts:**

- Zeige KontraktAlarmDashboard.
- Aktualisiere die Kennzahlen.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `kontrakte/LstKontraktUebersicht` — LstKontraktUebersicht

**Zweck:** LstKontraktUebersicht mandantensicher als Cockpit bereitstellen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/kontrakte/LstKontraktUebersicht/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/kontrakte/LstKontraktUebersicht/agent-contract` |
| Readiness | `GET /api/v1/masks/kontrakte/LstKontraktUebersicht/readiness` |
| Rollout-Route | `/mask-rollout/kontrakte__LstKontraktUebersicht/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/kontrakte`

**Beispiel-Prompts:**

- Zeige LstKontraktUebersicht.
- Aktualisiere die Kennzahlen.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `kontrakte/kontraktklassen` — Kontraktklassen

**Zweck:** Kontraktklassen im kontrakte-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/kontrakte/kontraktklassen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/kontrakte/kontraktklassen/agent-contract` |
| Readiness | `GET /api/v1/masks/kontrakte/kontraktklassen/readiness` |
| Rollout-Route | `/mask-rollout/kontrakte__kontraktklassen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/kontrakt-klassen`

**Beispiel-Prompts:**

- Zeige Kontraktklassen.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `kontrakte/mengenzeitraeume` — Kontrakt wählen

**Zweck:** Kontrakt wählen als Stammblatt pflegen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/kontrakte/mengenzeitraeume/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/kontrakte/mengenzeitraeume/agent-contract` |
| Readiness | `GET /api/v1/masks/kontrakte/mengenzeitraeume/readiness` |
| Rollout-Route | `/mask-rollout/kontrakte__mengenzeitraeume/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/kontrakte/{entity_id}`

**Beispiel-Prompts:**

- Oeffne Kontrakt wählen.
- Bearbeite Stammdaten.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `kontrakte/positionen` — KontraktPositionsmonitor

**Zweck:** KontraktPositionsmonitor im kontrakte-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/kontrakte/positionen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/kontrakte/positionen/agent-contract` |
| Readiness | `GET /api/v1/masks/kontrakte/positionen/readiness` |
| Rollout-Route | `/mask-rollout/kontrakte__positionen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/kontrakte`

**Beispiel-Prompts:**

- Zeige KontraktPositionsmonitor.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

## Domäne: lager

### `artikel/bestandsuebersicht` — Bestandsuebersicht

**Zweck:** Stamm- und Fachmaske fuer Bestandsuebersicht (artikel/bestandsuebersicht).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/artikel/bestandsuebersicht/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/artikel/bestandsuebersicht/agent-contract` |
| Readiness | `GET /api/v1/masks/artikel/bestandsuebersicht/readiness` |
| Rollout-Route | `/mask-rollout/artikel__bestandsuebersicht/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/articles/{entity_id}`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Bestandsuebersicht {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `/api/v1/articles/{entity_id}/actions/bearbeiten` |

---

### `artikel/chargen-pflicht` — Chargen pflicht

**Zweck:** Stamm- und Fachmaske fuer Chargen pflicht (artikel/chargen-pflicht).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/artikel/chargen-pflicht/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/artikel/chargen-pflicht/agent-contract` |
| Readiness | `GET /api/v1/masks/artikel/chargen-pflicht/readiness` |
| Rollout-Route | `/mask-rollout/artikel__chargen-pflicht/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/articles/{entity_id}`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Chargen pflicht {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `/api/v1/articles/{entity_id}/actions/bearbeiten` |

---

### `artikel/ersatzteile` — Ersatzteile

**Zweck:** Stamm- und Fachmaske fuer Ersatzteile (artikel/ersatzteile).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/artikel/ersatzteile/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/artikel/ersatzteile/agent-contract` |
| Readiness | `GET /api/v1/masks/artikel/ersatzteile/readiness` |
| Rollout-Route | `/mask-rollout/artikel__ersatzteile/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/articles/{entity_id}`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Ersatzteile {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `/api/v1/articles/{entity_id}/actions/bearbeiten` |

---

### `artikel/gebinde` — Gebinde

**Zweck:** Stamm- und Fachmaske fuer Gebinde (artikel/gebinde).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/artikel/gebinde/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/artikel/gebinde/agent-contract` |
| Readiness | `GET /api/v1/masks/artikel/gebinde/readiness` |
| Rollout-Route | `/mask-rollout/artikel__gebinde/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/articles/{entity_id}`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Gebinde {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `/api/v1/articles/{entity_id}/actions/bearbeiten` |

---

### `artikel/gefahrgut` — Gefahrgut

**Zweck:** Stamm- und Fachmaske fuer Gefahrgut (artikel/gefahrgut).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/artikel/gefahrgut/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/artikel/gefahrgut/agent-contract` |
| Readiness | `GET /api/v1/masks/artikel/gefahrgut/readiness` |
| Rollout-Route | `/mask-rollout/artikel__gefahrgut/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/articles/{entity_id}`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Gefahrgut {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `/api/v1/articles/{entity_id}/actions/bearbeiten` |

---

### `artikel/herkunft` — Herkunft

**Zweck:** Stamm- und Fachmaske fuer Herkunft (artikel/herkunft).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/artikel/herkunft/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/artikel/herkunft/agent-contract` |
| Readiness | `GET /api/v1/masks/artikel/herkunft/readiness` |
| Rollout-Route | `/mask-rollout/artikel__herkunft/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/articles/{entity_id}`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Herkunft {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `/api/v1/articles/{entity_id}/actions/bearbeiten` |

---

### `artikel/kategorien` — Kategorien

**Zweck:** Stamm- und Fachmaske fuer Kategorien (artikel/kategorien).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/artikel/kategorien/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/artikel/kategorien/agent-contract` |
| Readiness | `GET /api/v1/masks/artikel/kategorien/readiness` |
| Rollout-Route | `/mask-rollout/artikel__kategorien/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/stammdaten/warengruppen/{entity_id}`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Kategorien {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `/api/v1/stammdaten/warengruppen/{entity_id}/actions/bearbeiten` |

---

### `artikel/konditionen` — Konditionen

**Zweck:** Stamm- und Fachmaske fuer Konditionen (artikel/konditionen).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/artikel/konditionen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/artikel/konditionen/agent-contract` |
| Readiness | `GET /api/v1/masks/artikel/konditionen/readiness` |
| Rollout-Route | `/mask-rollout/artikel__konditionen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/articles/{entity_id}`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Konditionen {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `/api/v1/articles/{entity_id}/actions/bearbeiten` |

---

### `artikel/lieferanten-artikel` — Lieferanten artikel

**Zweck:** Stamm- und Fachmaske fuer Lieferanten artikel (artikel/lieferanten-artikel).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/artikel/lieferanten-artikel/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/artikel/lieferanten-artikel/agent-contract` |
| Readiness | `GET /api/v1/masks/artikel/lieferanten-artikel/readiness` |
| Rollout-Route | `/mask-rollout/artikel__lieferanten-artikel/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/articles/{entity_id}`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Lieferanten artikel {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `/api/v1/articles/{entity_id}/actions/bearbeiten` |

---

### `artikel/liste` — Artikel

**Zweck:** Artikel mit Warengruppe, Preis und Bestand finden und oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/artikel/liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/artikel/liste/agent-contract` |
| Readiness | `GET /api/v1/masks/artikel/liste/readiness` |
| Rollout-Route | `/mask-rollout/artikel__liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/articles/`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Artikel der Warengruppe Duenger fuehren wir?
- Welche Artikel haben keinen Bestand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `neu` | Neuer Artikel | safe | nein | `Oeffnet die Anlage; Rechte prueft deren Anlageweg.` |
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `artikel/preisstaffeln` — Preisstaffeln

**Zweck:** Stamm- und Fachmaske fuer Preisstaffeln (artikel/preisstaffeln).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/artikel/preisstaffeln/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/artikel/preisstaffeln/agent-contract` |
| Readiness | `GET /api/v1/masks/artikel/preisstaffeln/readiness` |
| Rollout-Route | `/mask-rollout/artikel__preisstaffeln/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/articles/{entity_id}`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Preisstaffeln {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `/api/v1/articles/{entity_id}/actions/bearbeiten` |

---

### `artikel/qualitaetsmerkmale` — Qualitaetsmerkmale

**Zweck:** Stamm- und Fachmaske fuer Qualitaetsmerkmale (artikel/qualitaetsmerkmale).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/artikel/qualitaetsmerkmale/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/artikel/qualitaetsmerkmale/agent-contract` |
| Readiness | `GET /api/v1/masks/artikel/qualitaetsmerkmale/readiness` |
| Rollout-Route | `/mask-rollout/artikel__qualitaetsmerkmale/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/articles/{entity_id}`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Qualitaetsmerkmale {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `/api/v1/articles/{entity_id}/actions/bearbeiten` |

---

### `artikel/rabattgruppen` — Rabattgruppen

**Zweck:** Stamm- und Fachmaske fuer Rabattgruppen (artikel/rabattgruppen).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/artikel/rabattgruppen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/artikel/rabattgruppen/agent-contract` |
| Readiness | `GET /api/v1/masks/artikel/rabattgruppen/readiness` |
| Rollout-Route | `/mask-rollout/artikel__rabattgruppen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/articles/{entity_id}`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Rabattgruppen {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `/api/v1/articles/{entity_id}/actions/bearbeiten` |

---

### `artikel/stamm` — Artikel

**Zweck:** Artikelstamm fuer Verkauf, Einkauf und Lager: Kennungen, Preise und Steuer, Lagerfuehrung, Qualitaet; Lieferanten, Preisvereinbarungen und Dokumente.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/artikel/stamm/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/artikel/stamm/agent-contract` |
| Readiness | `GET /api/v1/masks/artikel/stamm/readiness` |
| Rollout-Route | `/mask-rollout/artikel__stamm/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/articles/{entity_id}`
- `lieferanten` → `/api/v1/articles/{entity_id}/suppliers`
- `preise` → `/api/v1/articles/{entity_id}/prices`
- `dokumente` → `/api/v1/articles/{entity_id}/documents`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Welchen Verkaufspreis und Steuerschluessel hat Artikel {entity_id}?
- Welche Lieferanten liefern Artikel {entity_id} und zu welchem EK-Preis?
- Ist Artikel {entity_id} chargen- oder QS-pflichtig?

**Sensible Felder:** `purchase_price`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `/api/v1/articles/{entity_id}/actions/bearbeiten` |

---

### `artikel/stuecklisten` — Stuecklisten

**Zweck:** Stamm- und Fachmaske fuer Stuecklisten (artikel/stuecklisten).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/artikel/stuecklisten/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/artikel/stuecklisten/agent-contract` |
| Readiness | `GET /api/v1/masks/artikel/stuecklisten/readiness` |
| Rollout-Route | `/mask-rollout/artikel__stuecklisten/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/produktion/stuecklisten/{entity_id}`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Stuecklisten {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `artikel/texte-medien` — Texte medien

**Zweck:** Stamm- und Fachmaske fuer Texte medien (artikel/texte-medien).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/artikel/texte-medien/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/artikel/texte-medien/agent-contract` |
| Readiness | `GET /api/v1/masks/artikel/texte-medien/readiness` |
| Rollout-Route | `/mask-rollout/artikel__texte-medien/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/articles/{entity_id}`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Texte medien {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `/api/v1/articles/{entity_id}/actions/bearbeiten` |

---

### `artikel/umrechnungen` — Umrechnungen

**Zweck:** Stamm- und Fachmaske fuer Umrechnungen (artikel/umrechnungen).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/artikel/umrechnungen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/artikel/umrechnungen/agent-contract` |
| Readiness | `GET /api/v1/masks/artikel/umrechnungen/readiness` |
| Rollout-Route | `/mask-rollout/artikel__umrechnungen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/artikel/mengeneinheiten/gruppen/{entity_id}`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Umrechnungen {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `artikel/verpackungen` — Verpackungen

**Zweck:** Stamm- und Fachmaske fuer Verpackungen (artikel/verpackungen).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/artikel/verpackungen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/artikel/verpackungen/agent-contract` |
| Readiness | `GET /api/v1/masks/artikel/verpackungen/readiness` |
| Rollout-Route | `/mask-rollout/artikel__verpackungen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/artikel/verpackungen/{entity_id}`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Verpackungen {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `artikel/zoll-intrastat` — Zoll Intrastat

**Zweck:** Gespeicherte Intrastat-Meldung mit ihren fachlichen Positionswerten lesen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/artikel/zoll-intrastat/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/artikel/zoll-intrastat/agent-contract` |
| Readiness | `GET /api/v1/masks/artikel/zoll-intrastat/readiness` |
| Rollout-Route | `/mask-rollout/artikel__zoll-intrastat/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/intrastat/meldungen/{entity_id}`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Intrastat-Meldung {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `charge/liste` — Chargen

**Zweck:** Chargen nach Artikel, Lagerort und Status finden und ihre Spur oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/charge/liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/charge/liste/agent-contract` |
| Readiness | `GET /api/v1/masks/charge/liste/readiness` |
| Rollout-Route | `/mask-rollout/charge__liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/chargen`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Chargen sind noch in Pruefung?
- Welche Chargen liegen in Silo 3?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `neu` | Wareneingang erfassen | safe | nein | `Oeffnet die Anlage; Rechte prueft deren Anlageweg.` |
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `charge/wareneingang-liste` — Wareneingang Chargen

**Zweck:** Wareneingaenge als Chargen erfassen und finden.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/charge/wareneingang-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/charge/wareneingang-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/charge/wareneingang-liste/readiness` |
| Rollout-Route | `/mask-rollout/charge__wareneingang-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/chargen`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Chargen kamen heute rein?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `disposition/liste` — Disposition

**Zweck:** Unterdeckte Artikel finden und Bestellvorschlaege ausloesen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/disposition/liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/disposition/liste/agent-contract` |
| Readiness | `GET /api/v1/masks/disposition/liste/readiness` |
| Rollout-Route | `/mask-rollout/disposition__liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/disposition`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Artikel liegen unter Mindestbestand?
- Wo ist Bedarf hoch?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `neu` | Bestellvorschlaege | safe | nein | `Oeffnet die Anlage; Rechte prueft deren Anlageweg.` |
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `etiketten/druck-liste` — Etikettendruck

**Zweck:** Etikettendruck-Auftraege finden.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/etiketten/druck-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/etiketten/druck-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/etiketten/druck-liste/readiness` |
| Rollout-Route | `/mask-rollout/etiketten__druck-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/etiketten/druckauftrag`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Druckauftraege sind offen?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `lager/article-stock` — Artikelbestand

**Zweck:** Artikelbestand-Cockpit: Stammdaten, Bestand je Lagerort und Bewegungshistorie fuer Disposition und Einkauf.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/lager/article-stock/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/lager/article-stock/agent-contract` |
| Readiness | `GET /api/v1/masks/lager/article-stock/readiness` |
| Rollout-Route | `/mask-rollout/lager__article-stock/:entityId` |
| Adapter | `native` (temporary=nein) |

**Summary:** `/api/v1/mask-rollouts/lager/article-stock/{entity_id}/screen-summary`

**Data Sources:**

- `entity` → `/api/v1/articles/{entity_id}`
- `bestand` → `/api/v1/mask-rollouts/lager/article-stock/{entity_id}/tabs/bestand`
- `bewegungen` → `/api/v1/mask-rollouts/lager/article-stock/{entity_id}/tabs/bewegungen`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Wie hoch ist der aktuelle Bestand von Artikel {entity_id} je Lagerort?
- Zeige alle Lagerbewegungen von Artikel {entity_id} der letzten 30 Tage.
- Welche Lagerorte haben Bestand unter Mindestbestand fuer Artikel {entity_id}?

**Sensible Felder:** `mindestbestand, meldebestand`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `lager/auslagerung` — Auslagerung

**Zweck:** Auslagerung im lager-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/lager/auslagerung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/lager/auslagerung/agent-contract` |
| Readiness | `GET /api/v1/masks/lager/auslagerung/readiness` |
| Rollout-Route | `/mask-rollout/lager__auslagerung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/lager/bestaende`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Auslagerung.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `lager/bestandsbewertung` — Bestandsbewertung

**Zweck:** Bestandsbewertung im lager-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/lager/bestandsbewertung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/lager/bestandsbewertung/agent-contract` |
| Readiness | `GET /api/v1/masks/lager/bestandsbewertung/readiness` |
| Rollout-Route | `/mask-rollout/lager__bestandsbewertung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/lager/bestaende`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Bestandsbewertung.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `lager/bestandskorrektur` — Bestandskorrektur

**Zweck:** Bestandskorrektur im lager-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/lager/bestandskorrektur/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/lager/bestandskorrektur/agent-contract` |
| Readiness | `GET /api/v1/masks/lager/bestandskorrektur/readiness` |
| Rollout-Route | `/mask-rollout/lager__bestandskorrektur/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/lager/bestaende`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Bestandskorrektur.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `lager/charge` — Charge

**Zweck:** Chargenstamm mit QS- und Rückverfolgungsdaten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/lager/charge/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/lager/charge/agent-contract` |
| Readiness | `GET /api/v1/masks/lager/charge/readiness` |
| Rollout-Route | `/mask-rollout/lager__charge/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/chargen/{entity_id}`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Welchen Status hat Charge {entity_id}?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `lager/einlagerung` — Einlagerung

**Zweck:** Einlagerung im lager-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/lager/einlagerung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/lager/einlagerung/agent-contract` |
| Readiness | `GET /api/v1/masks/lager/einlagerung/readiness` |
| Rollout-Route | `/mask-rollout/lager__einlagerung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/lager/bestaende`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Einlagerung.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `lager/gs1-scanner` — Gs1 scanner

**Zweck:** Gs1 scanner im lager-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/lager/gs1-scanner/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/lager/gs1-scanner/agent-contract` |
| Readiness | `GET /api/v1/masks/lager/gs1-scanner/readiness` |
| Rollout-Route | `/mask-rollout/lager__gs1-scanner/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/lager/bestaende`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Gs1 scanner.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `lager/inventory-dashboard` — Lager-Dashboard

**Zweck:** Lager-KPIs und Sprung in Bestandsmasken.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/lager/inventory-dashboard/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/lager/inventory-dashboard/agent-contract` |
| Readiness | `GET /api/v1/masks/lager/inventory-dashboard/readiness` |
| Rollout-Route | `/mask-rollout/lager__inventory-dashboard/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/lager/dashboard`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Artikel sind unter Mindestbestand?
- Zeige Lager-KPIs.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `lager/inventur` — Inventur

**Zweck:** Inventur im lager-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/lager/inventur/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/lager/inventur/agent-contract` |
| Readiness | `GET /api/v1/masks/lager/inventur/readiness` |
| Rollout-Route | `/mask-rollout/lager__inventur/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/lager/bestaende`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Inventur.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `lager/inventur-liste` — Inventur

**Zweck:** Inventur: Eintraege finden und Details oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/lager/inventur-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/lager/inventur-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/lager/inventur-liste/readiness` |
| Rollout-Route | `/mask-rollout/lager__inventur-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/inventory/inventur`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche offenen Inventur?
- Zeige aktuelle Inventur.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `lager/kommissionierung` — Kommissionierung

**Zweck:** Kommissionierung im lager-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/lager/kommissionierung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/lager/kommissionierung/agent-contract` |
| Readiness | `GET /api/v1/masks/lager/kommissionierung/readiness` |
| Rollout-Route | `/mask-rollout/lager__kommissionierung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/sales/delivery-notes`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Kommissionierung.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `lager/lagerbewegungen-liste` — Lagerbewegungen

**Zweck:** Lagerbewegungen: Eintraege finden und Details oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/lager/lagerbewegungen-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/lager/lagerbewegungen-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/lager/lagerbewegungen-liste/readiness` |
| Rollout-Route | `/mask-rollout/lager__lagerbewegungen-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/inventory/stock-movements/`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche offenen Lagerbewegungen?
- Zeige aktuelle Lagerbewegungen.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `lager/lagerplaetze` — Lagerplaetze

**Zweck:** Lagerplaetze im lager-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/lager/lagerplaetze/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/lager/lagerplaetze/agent-contract` |
| Readiness | `GET /api/v1/masks/lager/lagerplaetze/readiness` |
| Rollout-Route | `/mask-rollout/lager__lagerplaetze/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/lager/bestaende`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Lagerplaetze.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `lager/leitstand` — Lager-Leitstand

**Zweck:** Physische Silozellen-Belegung, Fuellstand und QS-Sperren als klickbares Werkzeug im Lager-Leitstand anzeigen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/lager/leitstand/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/lager/leitstand/agent-contract` |
| Readiness | `GET /api/v1/masks/lager/leitstand/readiness` |
| Rollout-Route | `/mask-rollout/lager__leitstand/:entityId` |
| Adapter | `native` (temporary=nein) |

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Silozellen sind gesperrt?
- Zeige den Fuellstand im Lager-Leitstand.
- Welche Zelle ist ueber 90 Prozent belegt?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `lager/massebilanz` — Neue Massebilanz anlegen

**Zweck:** Neue Massebilanz anlegen als Stammblatt pflegen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/lager/massebilanz/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/lager/massebilanz/agent-contract` |
| Readiness | `GET /api/v1/masks/lager/massebilanz/readiness` |
| Rollout-Route | `/mask-rollout/lager__massebilanz/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/massebilanz/{entity_id}`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Oeffne Neue Massebilanz anlegen.
- Bearbeite Stammdaten.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `lager/materialfluss` — Materialfluss

**Zweck:** Materialfluss im lager-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/lager/materialfluss/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/lager/materialfluss/agent-contract` |
| Readiness | `GET /api/v1/masks/lager/materialfluss/readiness` |
| Rollout-Route | `/mask-rollout/lager__materialfluss/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/lager/bestaende`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Materialfluss.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `lager/materialfluss-visualisierung` — Materialfluss visualisierung

**Zweck:** Materialfluss visualisierung im lager-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/lager/materialfluss-visualisierung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/lager/materialfluss-visualisierung/agent-contract` |
| Readiness | `GET /api/v1/masks/lager/materialfluss-visualisierung/readiness` |
| Rollout-Route | `/mask-rollout/lager__materialfluss-visualisierung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/lager/bestaende`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Materialfluss visualisierung.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `lager/partiestamm` — Partiestamm

**Zweck:** Partiestamm im lager-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/lager/partiestamm/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/lager/partiestamm/agent-contract` |
| Readiness | `GET /api/v1/masks/lager/partiestamm/readiness` |
| Rollout-Route | `/mask-rollout/lager__partiestamm/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/lager/bestaende`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Partiestamm.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `lager/partiestamm-liste` — Partiestamm

**Zweck:** Partiestamm: Eintraege finden und Details oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/lager/partiestamm-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/lager/partiestamm-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/lager/partiestamm-liste/readiness` |
| Rollout-Route | `/mask-rollout/lager__partiestamm-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/lager/partien`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche offenen Partiestamm?
- Zeige aktuelle Partiestamm.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `lager/permanente-inventur` — Abschlüsse

**Zweck:** Abschlüsse als Stammblatt pflegen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/lager/permanente-inventur/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/lager/permanente-inventur/agent-contract` |
| Readiness | `GET /api/v1/masks/lager/permanente-inventur/readiness` |
| Rollout-Route | `/mask-rollout/lager__permanente-inventur/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/inventory/counts/{entity_id}`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Oeffne Abschlüsse.
- Bearbeite Stammdaten.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `lager/rueckverfolgbarkeit` — Rueckverfolgbarkeit

**Zweck:** Rueckverfolgbarkeit im lager-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/lager/rueckverfolgbarkeit/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/lager/rueckverfolgbarkeit/agent-contract` |
| Readiness | `GET /api/v1/masks/lager/rueckverfolgbarkeit/readiness` |
| Rollout-Route | `/mask-rollout/lager__rueckverfolgbarkeit/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/lager/bestaende`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Rueckverfolgbarkeit.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `lager/silo-mobil` — Silo mobil

**Zweck:** Silo mobil im lager-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/lager/silo-mobil/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/lager/silo-mobil/agent-contract` |
| Readiness | `GET /api/v1/masks/lager/silo-mobil/readiness` |
| Rollout-Route | `/mask-rollout/lager__silo-mobil/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/lager/bestaende`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Silo mobil.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `lager/silo-uebersicht` — Silo uebersicht

**Zweck:** Silo uebersicht mandantensicher als Cockpit bereitstellen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/lager/silo-uebersicht/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/lager/silo-uebersicht/agent-contract` |
| Readiness | `GET /api/v1/masks/lager/silo-uebersicht/readiness` |
| Rollout-Route | `/mask-rollout/lager__silo-uebersicht/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/lager/bestaende`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Silo uebersicht.
- Aktualisiere die Kennzahlen.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `lager/silo-uebersicht-liste` — Silo-Uebersicht

**Zweck:** Silo-Uebersicht: Eintraege finden und Details oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/lager/silo-uebersicht-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/lager/silo-uebersicht-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/lager/silo-uebersicht-liste/readiness` |
| Rollout-Route | `/mask-rollout/lager__silo-uebersicht-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/lager/wms/agri/silo-cells`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche offenen Silo-Uebersicht?
- Zeige aktuelle Silo-Uebersicht.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `lager/stock-movement` — Lagerbewegung

**Zweck:** Lagerbewegung: Einzelne Warenbewegung mit Belegpositionen fuer Lager-Audit und Traceability.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/lager/stock-movement/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/lager/stock-movement/agent-contract` |
| Readiness | `GET /api/v1/masks/lager/stock-movement/readiness` |
| Rollout-Route | `/mask-rollout/lager__stock-movement/:entityId` |
| Adapter | `native` (temporary=nein) |

**Summary:** `/api/v1/mask-rollouts/lager/stock-movement/{entity_id}/screen-summary`

**Data Sources:**

- `entity` → `/api/v1/inventory/stock-movements/{entity_id}`
- `details` → `/api/v1/mask-rollouts/lager/stock-movement/{entity_id}/tabs/details`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Was ist der Status und Typ von Lagerbewegung {entity_id}?
- Zeige alle Positionen und betroffenen Lagerorte von Bewegung {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `stornieren` | Stornieren | high | ja | `/api/v1/lager/stock-movements/{entity_id}/actions/stornieren` |

---

### `lager/terminal` — Terminal

**Zweck:** Terminal im lager-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/lager/terminal/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/lager/terminal/agent-contract` |
| Readiness | `GET /api/v1/masks/lager/terminal/readiness` |
| Rollout-Route | `/mask-rollout/lager__terminal/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/lager/bestaende`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Terminal.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `lager/umlagerung` — Lagerbewegungen

**Zweck:** Lagerbewegungen im lager-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/lager/umlagerung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/lager/umlagerung/agent-contract` |
| Readiness | `GET /api/v1/masks/lager/umlagerung/readiness` |
| Rollout-Route | `/mask-rollout/lager__umlagerung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/lager/bestaende`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Lagerbewegungen.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `silo/silo` — Silo

**Zweck:** Silokapazitaeten und Bestand.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/silo/silo/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/silo/silo/agent-contract` |
| Readiness | `GET /api/v1/masks/silo/silo/readiness` |
| Rollout-Route | `/mask-rollout/silo__silo/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/silo/silos/{entity_id}/details`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Wie hoch ist der Fuellstand von Silo {entity_id}?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `stammdaten/individuelle-artikelnummer` — Individuelle Artikelnummer

**Zweck:** Partner-spezifische Artikelnummern.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/stammdaten/individuelle-artikelnummer/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/stammdaten/individuelle-artikelnummer/agent-contract` |
| Readiness | `GET /api/v1/masks/stammdaten/individuelle-artikelnummer/readiness` |
| Rollout-Route | `/mask-rollout/stammdaten__individuelle-artikelnummer/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/artikel/individuelle-nummern/{entity_id}`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Welcher Artikel steckt hinter Nummer {entity_id}?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten nicht verfügbar | safe | nein | `Der bestehende API-Vertrag bietet für individuelle Artikelnummern keine Aktualisierung an.` |

---

### `stammdaten/mengeneinheit` — Mengeneinheit

**Zweck:** Mengeneinheiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/stammdaten/mengeneinheit/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/stammdaten/mengeneinheit/agent-contract` |
| Readiness | `GET /api/v1/masks/stammdaten/mengeneinheit/readiness` |
| Rollout-Route | `/mask-rollout/stammdaten__mengeneinheit/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/artikel/mengeneinheiten/stamm/{entity_id}`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Wie lautet Code von ME {entity_id}?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `/api/v1/artikel/mengeneinheiten/stamm/{entity_id}` |

---

### `wartung/anlagen-liste` — Wartung

**Zweck:** Faellige Wartungen der Anlagen finden.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/wartung/anlagen-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/wartung/anlagen-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/wartung/anlagen-liste/readiness` |
| Rollout-Route | `/mask-rollout/wartung__anlagen-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/wartung/anlagen`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Anlagen sind diesen Monat zur Wartung faellig?
- Welche Anlagen sind defekt?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `workspace/lager` — Lager-Cockpit

**Zweck:** Rollen-Startseite Lager — Annahmen, Wartezeiten und Trockner.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/workspace/lager/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/workspace/lager/agent-contract` |
| Readiness | `GET /api/v1/masks/workspace/lager/readiness` |
| Rollout-Route | `/mask-rollout/workspace__lager/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/lager/dashboard`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig
- `lager.inventur.propose_opening` — scope `lager:write`, Risiko hoch
- `lager.stock_movement.stornieren` — scope `lager:write`, Risiko mittel

**Beispiel-Prompts:**

- Wie viele Annahmen stehen heute an?
- Zeige QS-Warnungen.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

## Domäne: logistics

### `disposition/bestell-vorschlag` — Bestellvorschlag

**Zweck:** Bestellvorschlag als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/disposition/bestell-vorschlag/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/disposition/bestell-vorschlag/agent-contract` |
| Readiness | `GET /api/v1/masks/disposition/bestell-vorschlag/readiness` |
| Rollout-Route | `/mask-rollout/disposition__bestell-vorschlag/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/einkauf/bestellvorschlaege`

**MCP-Tools (Domäne):**

- `logistik.frachttabelle.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.tour.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.loeschen` — scope `logistics:write`, Risiko hoch
- `logistik.terminart.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.rechnung.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.ausgehendes_dokument.speichern` — scope `logistics:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Bestellvorschlag.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `disposition/engpass-monitor` — Engpass-Monitor

**Zweck:** Engpass-Monitor als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/disposition/engpass-monitor/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/disposition/engpass-monitor/agent-contract` |
| Readiness | `GET /api/v1/masks/disposition/engpass-monitor/readiness` |
| Rollout-Route | `/mask-rollout/disposition__engpass-monitor/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/disposition/stats`

**MCP-Tools (Domäne):**

- `logistik.frachttabelle.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.tour.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.loeschen` — scope `logistics:write`, Risiko hoch
- `logistik.terminart.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.rechnung.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.ausgehendes_dokument.speichern` — scope `logistics:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Engpass-Monitor.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `disposition/kontrakt-abruf` — Kontrakt-Abruf

**Zweck:** Kontrakt-Abruf als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/disposition/kontrakt-abruf/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/disposition/kontrakt-abruf/agent-contract` |
| Readiness | `GET /api/v1/masks/disposition/kontrakt-abruf/readiness` |
| Rollout-Route | `/mask-rollout/disposition__kontrakt-abruf/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/kontrakte`

**MCP-Tools (Domäne):**

- `logistik.frachttabelle.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.tour.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.loeschen` — scope `logistics:write`, Risiko hoch
- `logistik.terminart.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.rechnung.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.ausgehendes_dokument.speichern` — scope `logistics:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Kontrakt-Abruf.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `disposition/lager-reichweite` — Lager-Reichweite

**Zweck:** Lager-Reichweite als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/disposition/lager-reichweite/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/disposition/lager-reichweite/agent-contract` |
| Readiness | `GET /api/v1/masks/disposition/lager-reichweite/readiness` |
| Rollout-Route | `/mask-rollout/disposition__lager-reichweite/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/lager/dashboard`

**MCP-Tools (Domäne):**

- `logistik.frachttabelle.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.tour.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.loeschen` — scope `logistics:write`, Risiko hoch
- `logistik.terminart.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.rechnung.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.ausgehendes_dokument.speichern` — scope `logistics:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Lager-Reichweite.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `disposition/saison-planung` — Saison-Planung

**Zweck:** Saison-Planung als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/disposition/saison-planung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/disposition/saison-planung/agent-contract` |
| Readiness | `GET /api/v1/masks/disposition/saison-planung/readiness` |
| Rollout-Route | `/mask-rollout/disposition__saison-planung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/planung/kalender`

**MCP-Tools (Domäne):**

- `logistik.frachttabelle.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.tour.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.loeschen` — scope `logistics:write`, Risiko hoch
- `logistik.terminart.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.rechnung.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.ausgehendes_dokument.speichern` — scope `logistics:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Saison-Planung.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `disposition/strecken-disposition` — Strecken-Disposition

**Zweck:** Strecken-Disposition als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/disposition/strecken-disposition/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/disposition/strecken-disposition/agent-contract` |
| Readiness | `GET /api/v1/masks/disposition/strecken-disposition/readiness` |
| Rollout-Route | `/mask-rollout/disposition__strecken-disposition/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/strecke/streckengeschaefte`

**MCP-Tools (Domäne):**

- `logistik.frachttabelle.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.tour.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.loeschen` — scope `logistics:write`, Risiko hoch
- `logistik.terminart.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.rechnung.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.ausgehendes_dokument.speichern` — scope `logistics:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Strecken-Disposition.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `disposition/touren-disposition` — Touren-Disposition

**Zweck:** Touren-Disposition als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/disposition/touren-disposition/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/disposition/touren-disposition/agent-contract` |
| Readiness | `GET /api/v1/masks/disposition/touren-disposition/readiness` |
| Rollout-Route | `/mask-rollout/disposition__touren-disposition/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/logistik/tours`

**MCP-Tools (Domäne):**

- `logistik.frachttabelle.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.tour.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.loeschen` — scope `logistics:write`, Risiko hoch
- `logistik.terminart.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.rechnung.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.ausgehendes_dokument.speichern` — scope `logistics:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Touren-Disposition.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `disposition/umlagerungs-vorschlag` — Umlagerungs-Vorschlag

**Zweck:** Umlagerungs-Vorschlag als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/disposition/umlagerungs-vorschlag/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/disposition/umlagerungs-vorschlag/agent-contract` |
| Readiness | `GET /api/v1/masks/disposition/umlagerungs-vorschlag/readiness` |
| Rollout-Route | `/mask-rollout/disposition__umlagerungs-vorschlag/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/disposition`

**MCP-Tools (Domäne):**

- `logistik.frachttabelle.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.tour.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.loeschen` — scope `logistics:write`, Risiko hoch
- `logistik.terminart.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.rechnung.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.ausgehendes_dokument.speichern` — scope `logistics:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Umlagerungs-Vorschlag.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `fuhrpark/ausgehende-dokumente` — Ausgehende Belege

**Zweck:** Belegtypen fuer ausgehende Dokumente anlegen. Der Stand folgt dem Formular.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fuhrpark/ausgehende-dokumente/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fuhrpark/ausgehende-dokumente/agent-contract` |
| Readiness | `GET /api/v1/masks/fuhrpark/ausgehende-dokumente/readiness` |
| Rollout-Route | `/mask-rollout/fuhrpark__ausgehende-dokumente/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `dokumente` → `/api/v1/fuhrpark/ausgehende-dokumente`

**MCP-Tools (Domäne):**

- `logistik.frachttabelle.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.tour.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.loeschen` — scope `logistics:write`, Risiko hoch
- `logistik.terminart.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.rechnung.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.ausgehendes_dokument.speichern` — scope `logistics:write`, Risiko mittel

**Beispiel-Prompts:**

- Welcher Belegtyp hat noch kein Formular?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `speichern` | Speichern | safe | nein | `/api/v1/fuhrpark/ausgehende-dokumente/actions/speichern` |
| `neu` | Neu | safe | nein | `Leert die Eingabe fuer einen neuen Belegtyp.` |

---

### `fuhrpark/auswertung-kosten` — Fuhrpark-Kostenauswertung

**Zweck:** Fuhrpark-Kosten je Fahrzeug auswerten und in Stammdaten springen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fuhrpark/auswertung-kosten/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fuhrpark/auswertung-kosten/agent-contract` |
| Readiness | `GET /api/v1/masks/fuhrpark/auswertung-kosten/readiness` |
| Rollout-Route | `/mask-rollout/fuhrpark__auswertung-kosten/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/fuhrpark/fahrzeuge`

**MCP-Tools (Domäne):**

- `logistik.frachttabelle.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.tour.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.loeschen` — scope `logistics:write`, Risiko hoch
- `logistik.terminart.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.rechnung.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.ausgehendes_dokument.speichern` — scope `logistics:write`, Risiko mittel

**Beispiel-Prompts:**

- Welches Fahrzeug verursacht die hoechsten Kosten?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `fuhrpark/auswertungen-menu` — Fuhrpark-Auswertungen

**Zweck:** Einstieg in Fuhrpark-Auswertungen und Reports.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fuhrpark/auswertungen-menu/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fuhrpark/auswertungen-menu/agent-contract` |
| Readiness | `GET /api/v1/masks/fuhrpark/auswertungen-menu/readiness` |
| Rollout-Route | `/mask-rollout/fuhrpark__auswertungen-menu/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/fuhrpark/fahrzeuge`

**MCP-Tools (Domäne):**

- `logistik.frachttabelle.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.tour.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.loeschen` — scope `logistics:write`, Risiko hoch
- `logistik.terminart.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.rechnung.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.ausgehendes_dokument.speichern` — scope `logistics:write`, Risiko mittel

**Beispiel-Prompts:**

- Oeffne Fuhrpark-Auswertungen.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `fuhrpark/fahrzeug-stamm` — Fahrzeug-Stamm

**Zweck:** Fahrzeugakte anlegen und aendern. Der Stand folgt Kennzeichen und Typ.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fuhrpark/fahrzeug-stamm/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fuhrpark/fahrzeug-stamm/agent-contract` |
| Readiness | `GET /api/v1/masks/fuhrpark/fahrzeug-stamm/readiness` |
| Rollout-Route | `/mask-rollout/fuhrpark__fahrzeug-stamm/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/fuhrpark/fahrzeuge/{entity_id}`

**MCP-Tools (Domäne):**

- `logistik.frachttabelle.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.tour.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.loeschen` — scope `logistics:write`, Risiko hoch
- `logistik.terminart.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.rechnung.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.ausgehendes_dokument.speichern` — scope `logistics:write`, Risiko mittel

**Beispiel-Prompts:**

- Welches Fahrzeug hat noch keinen TUEV-Termin?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `speichern` | Speichern | safe | nein | `/api/v1/fuhrpark/fahrzeuge/actions/speichern` |
| `liste` | Zur Liste | safe | nein | `Wechselt zur Fahrzeugliste.` |
| `drucker` | Drucker einrichten | safe | nein | `Hinterlegt den Drucker an der Fahrzeugakte.` |
| `drucken` | Drucken | safe | nein | `Druckt die Fahrzeugakte.` |
| `unfall` | Unfall-Anzeige | moderate | nein | `Erfasst eine Unfallanzeige zum Fahrzeug.` |
| `loeschen` | Fahrzeug löschen | high | ja | `/api/v1/fuhrpark/fahrzeuge/{entity_id}/actions/loeschen` |

---

### `fuhrpark/fahrzeuge` — Fahrzeuge

**Zweck:** Fahrzeuge nach Kennzeichen, Typ und Status suchen und in die Erfassung oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fuhrpark/fahrzeuge/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fuhrpark/fahrzeuge/agent-contract` |
| Readiness | `GET /api/v1/masks/fuhrpark/fahrzeuge/readiness` |
| Rollout-Route | `/mask-rollout/fuhrpark__fahrzeuge/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/fuhrpark/fahrzeuge`

**MCP-Tools (Domäne):**

- `logistik.frachttabelle.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.tour.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.loeschen` — scope `logistics:write`, Risiko hoch
- `logistik.terminart.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.rechnung.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.ausgehendes_dokument.speichern` — scope `logistics:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Fahrzeuge sind verfuegbar?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `neu` | Neues Fahrzeug | safe | nein | `Oeffnet die bestehende Fahrzeug-Erfassung.` |

---

### `fuhrpark/rechnungen` — Fuhrpark-Rechnungen

**Zweck:** Fuhrpark-Rechnungen anlegen und aendern. Der Betrag folgt den Belegen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fuhrpark/rechnungen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fuhrpark/rechnungen/agent-contract` |
| Readiness | `GET /api/v1/masks/fuhrpark/rechnungen/readiness` |
| Rollout-Route | `/mask-rollout/fuhrpark__rechnungen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `rechnungen` → `/api/v1/fuhrpark/rechnungen`

**MCP-Tools (Domäne):**

- `logistik.frachttabelle.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.tour.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.loeschen` — scope `logistics:write`, Risiko hoch
- `logistik.terminart.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.rechnung.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.ausgehendes_dokument.speichern` — scope `logistics:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Fuhrpark-Rechnung hat noch kein Fahrzeug?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `speichern` | Speichern | safe | nein | `/api/v1/fuhrpark/rechnungen/actions/speichern` |
| `neu` | Neu | safe | nein | `Leert die Eingabe fuer eine neue Rechnung.` |

---

### `fuhrpark/terminarten` — Terminarten

**Zweck:** Wartungsintervalle der Terminarten anlegen und aendern.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fuhrpark/terminarten/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fuhrpark/terminarten/agent-contract` |
| Readiness | `GET /api/v1/masks/fuhrpark/terminarten/readiness` |
| Rollout-Route | `/mask-rollout/fuhrpark__terminarten/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `terminarten` → `/api/v1/fuhrpark/terminarten`

**MCP-Tools (Domäne):**

- `logistik.frachttabelle.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.tour.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.loeschen` — scope `logistics:write`, Risiko hoch
- `logistik.terminart.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.rechnung.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.ausgehendes_dokument.speichern` — scope `logistics:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Terminart hat noch kein Kilometerintervall?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `speichern` | Speichern | safe | nein | `/api/v1/fuhrpark/terminarten/actions/speichern` |
| `neu` | Neu | safe | nein | `Leert die Eingabe fuer eine neue Terminart.` |

---

### `fuhrpark/uebersicht` — Fuhrpark

**Zweck:** Vom Fuhrpark in Stammdaten, Rechnungen, Kosten und Belege springen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fuhrpark/uebersicht/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fuhrpark/uebersicht/agent-contract` |
| Readiness | `GET /api/v1/masks/fuhrpark/uebersicht/readiness` |
| Rollout-Route | `/mask-rollout/fuhrpark__uebersicht/:entityId` |
| Adapter | `native` (temporary=nein) |

**MCP-Tools (Domäne):**

- `logistik.frachttabelle.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.tour.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.loeschen` — scope `logistics:write`, Risiko hoch
- `logistik.terminart.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.rechnung.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.ausgehendes_dokument.speichern` — scope `logistics:write`, Risiko mittel

**Beispiel-Prompts:**

- Oeffne Fuhrpark.

---

### `logistik/frachtbrief` — Frachtbriefe

**Zweck:** Transportbelege nach Nummer, Empfaenger und Kennzeichen sichten. Der Lieferschein bleibt der Warenbeleg.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/logistik/frachtbrief/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/logistik/frachtbrief/agent-contract` |
| Readiness | `GET /api/v1/masks/logistik/frachtbrief/readiness` |
| Rollout-Route | `/mask-rollout/logistik__frachtbrief/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/logistik/frachtbriefe`

**MCP-Tools (Domäne):**

- `logistik.frachttabelle.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.tour.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.loeschen` — scope `logistics:write`, Risiko hoch
- `logistik.terminart.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.rechnung.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.ausgehendes_dokument.speichern` — scope `logistics:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Frachtbriefe sind noch erstellt?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `verladung` | Zur Verladung | safe | nein | `—` |

---

### `logistik/frachttabellen` — Frachttabellen

**Zweck:** Frachttabellen und ihre Mengenstaffel anlegen. Der Stand folgt den Positionen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/logistik/frachttabellen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/logistik/frachttabellen/agent-contract` |
| Readiness | `GET /api/v1/masks/logistik/frachttabellen/readiness` |
| Rollout-Route | `/mask-rollout/logistik__frachttabellen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `tabellen` → `/api/v1/logistik/frachttabellen`

**MCP-Tools (Domäne):**

- `logistik.frachttabelle.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.tour.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.loeschen` — scope `logistics:write`, Risiko hoch
- `logistik.terminart.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.rechnung.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.ausgehendes_dokument.speichern` — scope `logistics:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Frachttabelle hat noch keine Staffel?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `anlegen` | Tabelle speichern | safe | nein | `/api/v1/logistik/frachttabellen/actions/anlegen` |
| `position` | Position anlegen | safe | nein | `Erfasst eine Staffelposition in der Maske; gespeichert wird mit der Tabelle.` |

---

### `logistik/tour-fracht-arbeitsraum` — Tour & Fracht

**Zweck:** Touren, Frachtbriefe und Tarife gemeinsam sichten. Die Ampel folgt Bestand und Chargensperre.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/logistik/tour-fracht-arbeitsraum/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/logistik/tour-fracht-arbeitsraum/agent-contract` |
| Readiness | `GET /api/v1/masks/logistik/tour-fracht-arbeitsraum/readiness` |
| Rollout-Route | `/mask-rollout/logistik__tour-fracht-arbeitsraum/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `touren` → `/api/v1/logistik/tours`
- `fracht` → `/api/v1/logistik/frachtbriefe`
- `tarife` → `/api/v1/logistik/freight-tariffs`

**MCP-Tools (Domäne):**

- `logistik.frachttabelle.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.tour.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.loeschen` — scope `logistics:write`, Risiko hoch
- `logistik.terminart.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.rechnung.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.ausgehendes_dokument.speichern` — scope `logistics:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Frachtbriefe sind noch nicht versendet?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `touren` | Zur Tourenplanung | safe | nein | `—` |
| `fracht` | Zu Frachtbriefen | safe | nein | `—` |
| `tabellen` | Frachttabellen | safe | nein | `—` |
| `probe` | Probe berechnen | safe | nein | `Berechnet die Frachtprobe aus den Feldern des Arbeitsraums.` |

---

### `logistik/tourenplanung` — Tourenplanung

**Zweck:** Eine Tour aus Lieferschein, Fahrzeug und Fahrer disponieren. Die Ampel folgt der Besetzung.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/logistik/tourenplanung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/logistik/tourenplanung/agent-contract` |
| Readiness | `GET /api/v1/masks/logistik/tourenplanung/readiness` |
| Rollout-Route | `/mask-rollout/logistik__tourenplanung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `touren` → `/api/v1/logistik/tours`
- `fahrzeuge` → `/api/v1/fuhrpark/fahrzeuge`
- `fahrer` → `/api/v1/transporte/fahrer`

**MCP-Tools (Domäne):**

- `logistik.frachttabelle.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.tour.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.loeschen` — scope `logistics:write`, Risiko hoch
- `logistik.terminart.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.rechnung.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.ausgehendes_dokument.speichern` — scope `logistics:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Touren haben heute noch keinen Fahrer?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `dispo` | Dispo-Arbeitsraum | safe | nein | `Oeffnet den bestehenden Dispo-Arbeitsraum.` |
| `aufloesen` | Auflösen | safe | nein | `Liest den Lieferschein und setzt das Ziel.` |
| `anlegen` | Tour anlegen | safe | nein | `/api/v1/logistik/tours/actions/anlegen` |

---

### `logistik/verladung` — Verladung

**Zweck:** Beladungen nach Kennzeichen, Ware und Lieferschein sichten und eine neue Beladung öffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/logistik/verladung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/logistik/verladung/agent-contract` |
| Readiness | `GET /api/v1/masks/logistik/verladung/readiness` |
| Rollout-Route | `/mask-rollout/logistik__verladung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/verladung`

**MCP-Tools (Domäne):**

- `logistik.frachttabelle.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.tour.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.loeschen` — scope `logistics:write`, Risiko hoch
- `logistik.terminart.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.rechnung.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.ausgehendes_dokument.speichern` — scope `logistics:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Verladungen sind noch geplant?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `neu` | Neue Beladung | safe | nein | `—` |

---

### `logistik/versandprofile` — Versandprofile

**Zweck:** Versandprofile und Lieferavise anlegen. Der Stand folgt den Profilen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/logistik/versandprofile/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/logistik/versandprofile/agent-contract` |
| Readiness | `GET /api/v1/masks/logistik/versandprofile/readiness` |
| Rollout-Route | `/mask-rollout/logistik__versandprofile/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `profile` → `/api/v1/logistik/versand/profile`
- `avise` → `/api/v1/logistik/versand/avise`

**MCP-Tools (Domäne):**

- `logistik.frachttabelle.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.tour.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.loeschen` — scope `logistics:write`, Risiko hoch
- `logistik.terminart.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.rechnung.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.ausgehendes_dokument.speichern` — scope `logistics:write`, Risiko mittel

**Beispiel-Prompts:**

- Welches Versandprofil fehlt noch?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `profil` | Profil speichern | safe | nein | `Legt das Versandprofil an.` |
| `avis` | Avis speichern | safe | nein | `Legt ein Lieferavis an.` |

---

### `strecke/disposition` — Strecken-Disposition

**Zweck:** Strecken disponieren: eine Tour fuer heute anlegen, bestehende Touren sehen und loeschen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/strecke/disposition/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/strecke/disposition/agent-contract` |
| Readiness | `GET /api/v1/masks/strecke/disposition/readiness` |
| Rollout-Route | `/mask-rollout/strecke__disposition/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/tours`

**MCP-Tools (Domäne):**

- `logistik.frachttabelle.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.tour.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.loeschen` — scope `logistics:write`, Risiko hoch
- `logistik.terminart.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.rechnung.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.ausgehendes_dokument.speichern` — scope `logistics:write`, Risiko mittel

**Beispiel-Prompts:**

- Lege eine neue Strecke fuer heute an.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `neu` | Neue Strecke | safe | nein | `—` |

---

### `strecke/dokumente-drucken` — Strecken-Dokumente drucken

**Zweck:** Fracht, Paket, Versand-Avis und Produktion zum Druck oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/strecke/dokumente-drucken/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/strecke/dokumente-drucken/agent-contract` |
| Readiness | `GET /api/v1/masks/strecke/dokumente-drucken/readiness` |
| Rollout-Route | `/mask-rollout/strecke__dokumente-drucken/:entityId` |
| Adapter | `native` (temporary=nein) |

**MCP-Tools (Domäne):**

- `logistik.frachttabelle.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.tour.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.loeschen` — scope `logistics:write`, Risiko hoch
- `logistik.terminart.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.rechnung.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.ausgehendes_dokument.speichern` — scope `logistics:write`, Risiko mittel

**Beispiel-Prompts:**

- Oeffne Strecken-Dokumente drucken.

---

### `strecke/streckengeschaeft` — Streckengeschäft

**Zweck:** Streckengeschaeft erfassen und den Bestand nach Nummer, Lieferant und Artikel suchen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/strecke/streckengeschaeft/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/strecke/streckengeschaeft/agent-contract` |
| Readiness | `GET /api/v1/masks/strecke/streckengeschaeft/readiness` |
| Rollout-Route | `/mask-rollout/strecke__streckengeschaeft/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/strecke/streckengeschaefte`

**MCP-Tools (Domäne):**

- `logistik.frachttabelle.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.tour.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.loeschen` — scope `logistics:write`, Risiko hoch
- `logistik.terminart.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.rechnung.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.ausgehendes_dokument.speichern` — scope `logistics:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Streckengeschaefte sind noch nicht erledigt?
- Zeige die Strecke mit der Partie von heute.

---

### `strecke/vorlaeufig` — Vorläufige Streckengeschäfte

**Zweck:** Vorlaeufige Streckengeschaefte als Touren nach Nummer, Datum und Status suchen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/strecke/vorlaeufig/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/strecke/vorlaeufig/agent-contract` |
| Readiness | `GET /api/v1/masks/strecke/vorlaeufig/readiness` |
| Rollout-Route | `/mask-rollout/strecke__vorlaeufig/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/tours`

**MCP-Tools (Domäne):**

- `logistik.frachttabelle.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.tour.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.loeschen` — scope `logistics:write`, Risiko hoch
- `logistik.terminart.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.rechnung.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.ausgehendes_dokument.speichern` — scope `logistics:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Touren sind noch geplant?

---

### `transporte/fahrer` — Fahrer

**Zweck:** Fahrer nach Name und Status suchen. Touren heute ist die Zahl der heutigen Touren.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/transporte/fahrer/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/transporte/fahrer/agent-contract` |
| Readiness | `GET /api/v1/masks/transporte/fahrer/readiness` |
| Rollout-Route | `/mask-rollout/transporte__fahrer/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/transporte/fahrer`
- `touren` → `/api/v1/logistik/tours`

**MCP-Tools (Domäne):**

- `logistik.frachttabelle.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.tour.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.loeschen` — scope `logistics:write`, Risiko hoch
- `logistik.terminart.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.rechnung.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.ausgehendes_dokument.speichern` — scope `logistics:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Fahrer sind heute unterwegs?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `neu` | Neuer Fahrer | safe | nein | `Oeffnet das bestehende Fahrerformular.` |
| `verfuegbar` | Verfügbaren Fahrer öffnen | safe | nein | `Oeffnet den ersten verfuegbaren Fahrer.` |
| `touren` | Tourenplanung | safe | nein | `Wechselt in die Tourenplanung.` |
| `dokumente` | Dokumente | safe | nein | `Oeffnet die Dokumentenablage.` |
| `export` | Export | safe | nein | `Exportiert die sichtbare Fahrerliste.` |

---

### `versand/versand-avis` — Versand-Avis

**Zweck:** Versand-Avise zur Auswahl stellen und den Empfaenger fuer den Versand nennen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/versand/versand-avis/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/versand/versand-avis/agent-contract` |
| Readiness | `GET /api/v1/masks/versand/versand-avis/readiness` |
| Rollout-Route | `/mask-rollout/versand__versand-avis/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/logistik/versand/avise`

**MCP-Tools (Domäne):**

- `logistik.frachttabelle.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.tour.anlegen` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.fahrzeug.loeschen` — scope `logistics:write`, Risiko hoch
- `logistik.terminart.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.rechnung.speichern` — scope `logistics:write`, Risiko mittel
- `logistik.ausgehendes_dokument.speichern` — scope `logistics:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Avise stehen zum Drucken an?

---

## Domäne: logistik

### `fuhrpark/fahrzeuge-liste` — Fuhrpark

**Zweck:** Fuhrpark: Eintraege finden und Details oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fuhrpark/fahrzeuge-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fuhrpark/fahrzeuge-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/fuhrpark/fahrzeuge-liste/readiness` |
| Rollout-Route | `/mask-rollout/fuhrpark__fahrzeuge-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/fuhrpark/fahrzeuge`

**Beispiel-Prompts:**

- Welche offenen Fuhrpark?
- Zeige aktuelle Fuhrpark.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `fuhrpark/rechnungen-liste` — Fuhrpark-Rechnungen

**Zweck:** Fuhrpark-Rechnungen: Eintraege finden und Details oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/fuhrpark/rechnungen-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/fuhrpark/rechnungen-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/fuhrpark/rechnungen-liste/readiness` |
| Rollout-Route | `/mask-rollout/fuhrpark__rechnungen-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/fuhrpark/rechnungen`

**Beispiel-Prompts:**

- Welche offenen Fuhrpark-Rechnungen?
- Zeige aktuelle Fuhrpark-Rechnungen.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `logistik/frachtbriefe` — Frachtbriefe

**Zweck:** Frachtbriefe im logistik-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/logistik/frachtbriefe/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/logistik/frachtbriefe/agent-contract` |
| Readiness | `GET /api/v1/masks/logistik/frachtbriefe/readiness` |
| Rollout-Route | `/mask-rollout/logistik__frachtbriefe/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/logistik/frachtbriefe`

**Beispiel-Prompts:**

- Zeige Frachtbriefe.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `tankstelle/zapfungen-liste` — Zapfungen

**Zweck:** Zapfungen der Tankstelle nachvollziehen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/tankstelle/zapfungen-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/tankstelle/zapfungen-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/tankstelle/zapfungen-liste/readiness` |
| Rollout-Route | `/mask-rollout/tankstelle__zapfungen-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/tankstelle/zapfungen`

**Beispiel-Prompts:**

- Welche Zapfungen gab es heute?
- Welches Fahrzeug tankte Diesel?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `transporte/fahrer-liste` — Fahrer

**Zweck:** Fahrer: Eintraege finden und Details oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/transporte/fahrer-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/transporte/fahrer-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/transporte/fahrer-liste/readiness` |
| Rollout-Route | `/mask-rollout/transporte__fahrer-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/transporte/fahrer`

**Beispiel-Prompts:**

- Welche offenen Fahrer?
- Zeige aktuelle Fahrer.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `verladung/liste` — Verladungen

**Zweck:** Verladungen: Eintraege finden und Details oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/verladung/liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/verladung/liste/agent-contract` |
| Readiness | `GET /api/v1/masks/verladung/liste/readiness` |
| Rollout-Route | `/mask-rollout/verladung__liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/verladung`

**Beispiel-Prompts:**

- Welche offenen Verladungen?
- Zeige aktuelle Verladungen.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `waage/liste` — Waagen

**Zweck:** Waagenstandorte und Eichtermine im Blick behalten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/waage/liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/waage/liste/agent-contract` |
| Readiness | `GET /api/v1/masks/waage/liste/readiness` |
| Rollout-Route | `/mask-rollout/waage__liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/waage/waagen`

**Beispiel-Prompts:**

- Welche Waage muss als naechstes geeicht werden?
- Welche Waagen sind in Wartung?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

## Domäne: mahnwesen

### `mahnwesen/mahnlauf` — Mahnlauf

**Zweck:** Mahnlauf im mahnwesen-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/mahnwesen/mahnlauf/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/mahnwesen/mahnlauf/agent-contract` |
| Readiness | `GET /api/v1/masks/mahnwesen/mahnlauf/readiness` |
| Rollout-Route | `/mask-rollout/mahnwesen__mahnlauf/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/finance/mahnlauf/candidates`

**Beispiel-Prompts:**

- Zeige Mahnlauf.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

## Domäne: management

### `dashboards/geschaeftsfuehrung` — Geschaeftsfuehrung

**Zweck:** Geschaeftsfuehrungs-Cockpit mit KPIs und Alerts.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/dashboards/geschaeftsfuehrung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/dashboards/geschaeftsfuehrung/agent-contract` |
| Readiness | `GET /api/v1/masks/dashboards/geschaeftsfuehrung/readiness` |
| Rollout-Route | `/mask-rollout/dashboards__geschaeftsfuehrung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/management/dashboard`

**Beispiel-Prompts:**

- Wie ist die Gesamtperformance?
- Wo gibt es Handlungsbedarf?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `management/executive-dashboard` — Executive Dashboard

**Zweck:** Geschaeftsleitung: KPIs, Trends und Handlungsbedarf.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/management/executive-dashboard/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/management/executive-dashboard/agent-contract` |
| Readiness | `GET /api/v1/masks/management/executive-dashboard/readiness` |
| Rollout-Route | `/mask-rollout/management__executive-dashboard/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/management/dashboard`

**Beispiel-Prompts:**

- Wie ist der Umsatz-Trend?
- Welche Alerts sind aktiv?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `workspace/leitung` — Leitung-Cockpit

**Zweck:** Leitungssicht — KPIs, Alerts und Workspaces.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/workspace/leitung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/workspace/leitung/agent-contract` |
| Readiness | `GET /api/v1/masks/workspace/leitung/readiness` |
| Rollout-Route | `/mask-rollout/workspace__leitung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/management/dashboard`

**Beispiel-Prompts:**

- Was braucht heute Entscheidung?
- Zeige kritische Alerts.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

## Domäne: marketing

### `marketing/kampagnen` — Kampagnen

**Zweck:** Kampagnen im marketing-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/marketing/kampagnen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/marketing/kampagnen/agent-contract` |
| Readiness | `GET /api/v1/masks/marketing/kampagnen/readiness` |
| Rollout-Route | `/mask-rollout/marketing__kampagnen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/marketing/kampagnen`

**Beispiel-Prompts:**

- Zeige Kampagnen.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `marketing/kampagnen-liste` — Marketingkampagnen

**Zweck:** Marketingkampagnen und Budgets verfolgen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/marketing/kampagnen-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/marketing/kampagnen-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/marketing/kampagnen-liste/readiness` |
| Rollout-Route | `/mask-rollout/marketing__kampagnen-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/marketing/kampagnen`

**Beispiel-Prompts:**

- Welche Kampagnen laufen gerade?
- Welches Budget ist fuer Q2 geplant?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `neu` | Neue Kampagne | safe | nein | `Oeffnet die Anlage; Rechte prueft deren Anlageweg.` |
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

## Domäne: mobile

### `mobile/scanner` — Scanner

**Zweck:** Scanner im mobile-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/mobile/scanner/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/mobile/scanner/agent-contract` |
| Readiness | `GET /api/v1/masks/mobile/scanner/readiness` |
| Rollout-Route | `/mask-rollout/mobile__scanner/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/mobile/sync-queue`

**MCP-Tools (Domäne):**

- `mobile.sync.process_pending` — scope `mobile:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Scanner.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

## Domäne: nachhaltigkeit

### `nachhaltigkeit/eudr-compliance` — Eudr compliance

**Zweck:** Eudr compliance im nachhaltigkeit-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/nachhaltigkeit/eudr-compliance/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/nachhaltigkeit/eudr-compliance/agent-contract` |
| Readiness | `GET /api/v1/masks/nachhaltigkeit/eudr-compliance/readiness` |
| Rollout-Route | `/mask-rollout/nachhaltigkeit__eudr-compliance/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/compliance/eudr`

**Beispiel-Prompts:**

- Zeige Eudr compliance.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

## Domäne: operations

### `betrieb/gefahrstoff-betriebsanweisung` — Gefahrstoff-Betriebsanweisung

**Zweck:** Gefahrstoff-Betriebsanweisung als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/betrieb/gefahrstoff-betriebsanweisung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/betrieb/gefahrstoff-betriebsanweisung/agent-contract` |
| Readiness | `GET /api/v1/masks/betrieb/gefahrstoff-betriebsanweisung/readiness` |
| Rollout-Route | `/mask-rollout/betrieb__gefahrstoff-betriebsanweisung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/compliance/exports/gefahrstoffdoku`

**Beispiel-Prompts:**

- Zeige Gefahrstoff-Betriebsanweisung.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `betrieb/gefahrstoff-kataster` — Gefahrstoff-Kataster

**Zweck:** Gefahrstoff-Kataster als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/betrieb/gefahrstoff-kataster/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/betrieb/gefahrstoff-kataster/agent-contract` |
| Readiness | `GET /api/v1/masks/betrieb/gefahrstoff-kataster/readiness` |
| Rollout-Route | `/mask-rollout/betrieb__gefahrstoff-kataster/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/compliance/exports/gefahrstoffdoku`

**Beispiel-Prompts:**

- Zeige Gefahrstoff-Kataster.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `betrieb/maschinen-stamm` — Maschinen-Stamm

**Zweck:** Maschinen-Stamm als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/betrieb/maschinen-stamm/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/betrieb/maschinen-stamm/agent-contract` |
| Readiness | `GET /api/v1/masks/betrieb/maschinen-stamm/readiness` |
| Rollout-Route | `/mask-rollout/betrieb__maschinen-stamm/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/maschinen`

**Beispiel-Prompts:**

- Zeige Maschinen-Stamm.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `betrieb/prueffristen` — Prueffristen

**Zweck:** Prueffristen als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/betrieb/prueffristen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/betrieb/prueffristen/agent-contract` |
| Readiness | `GET /api/v1/masks/betrieb/prueffristen/readiness` |
| Rollout-Route | `/mask-rollout/betrieb__prueffristen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/wartung/anlagen`

**Beispiel-Prompts:**

- Zeige Prueffristen.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `betrieb/schadensmeldung` — Schadensmeldung

**Zweck:** Schadensmeldung als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/betrieb/schadensmeldung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/betrieb/schadensmeldung/agent-contract` |
| Readiness | `GET /api/v1/masks/betrieb/schadensmeldung/readiness` |
| Rollout-Route | `/mask-rollout/betrieb__schadensmeldung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/qualitaet/reklamationen`

**Beispiel-Prompts:**

- Zeige Schadensmeldung.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `betrieb/standorte` — Standorte

**Zweck:** Standorte als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/betrieb/standorte/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/betrieb/standorte/agent-contract` |
| Readiness | `GET /api/v1/masks/betrieb/standorte/readiness` |
| Rollout-Route | `/mask-rollout/betrieb__standorte/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/stammdaten/betriebsstaetten`

**Beispiel-Prompts:**

- Zeige Standorte.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `betrieb/unterweisungen` — Unterweisungen

**Zweck:** Unterweisungen als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/betrieb/unterweisungen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/betrieb/unterweisungen/agent-contract` |
| Readiness | `GET /api/v1/masks/betrieb/unterweisungen/readiness` |
| Rollout-Route | `/mask-rollout/betrieb__unterweisungen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/personal/absences`

**Beispiel-Prompts:**

- Zeige Unterweisungen.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `betrieb/wartungsplan` — Wartungsplan

**Zweck:** Wartungsplan als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/betrieb/wartungsplan/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/betrieb/wartungsplan/agent-contract` |
| Readiness | `GET /api/v1/masks/betrieb/wartungsplan/readiness` |
| Rollout-Route | `/mask-rollout/betrieb__wartungsplan/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/wartung/anlagen`

**Beispiel-Prompts:**

- Zeige Wartungsplan.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `qualitaet/ausnahmen` — Betriebs-Ausnahmen

**Zweck:** QS- und Leitungs-Ausnahmen mandantensicher bearbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/qualitaet/ausnahmen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/qualitaet/ausnahmen/agent-contract` |
| Readiness | `GET /api/v1/masks/qualitaet/ausnahmen/readiness` |
| Rollout-Route | `/mask-rollout/qualitaet__ausnahmen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `items` → `/api/v1/operations/exceptions`

**Beispiel-Prompts:**

- Welche Ausnahmen sind eskaliert?

---

## Domäne: personal

### `personal/hrm-operations-gates` — Hrm operations gates

**Zweck:** Hrm operations gates im personal-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/personal/hrm-operations-gates/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/personal/hrm-operations-gates/agent-contract` |
| Readiness | `GET /api/v1/masks/personal/hrm-operations-gates/readiness` |
| Rollout-Route | `/mask-rollout/personal__hrm-operations-gates/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/personal/absences`

**Beispiel-Prompts:**

- Zeige Hrm operations gates.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `personal/mitarbeiter` — Mitarbeiter

**Zweck:** Mitarbeiterstammdaten fuer HR.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/personal/mitarbeiter/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/personal/mitarbeiter/agent-contract` |
| Readiness | `GET /api/v1/masks/personal/mitarbeiter/readiness` |
| Rollout-Route | `/mask-rollout/personal__mitarbeiter/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/personal/mitarbeiter/{entity_id}`

**Beispiel-Prompts:**

- In welcher Abteilung arbeitet Mitarbeiter {entity_id}?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `personal/mitarbeiter-liste` — Mitarbeitende

**Zweck:** Mitarbeitende nach Abteilung und Status finden und ihre Personalakte oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/personal/mitarbeiter-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/personal/mitarbeiter-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/personal/mitarbeiter-liste/readiness` |
| Rollout-Route | `/mask-rollout/personal__mitarbeiter-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/personal/mitarbeiter`

**Beispiel-Prompts:**

- Wer arbeitet im Lager?
- Wer ist seit diesem Jahr dabei?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `neu` | Neue Mitarbeiterin / neuer Mitarbeiter | safe | nein | `Oeffnet die Anlage; Rechte prueft deren Anlageweg.` |
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `personal/mitarbeiter/neu` — Mitarbeiter stamm

**Zweck:** Mitarbeiter stamm als Stammblatt pflegen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/personal/mitarbeiter/neu/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/personal/mitarbeiter/neu/agent-contract` |
| Readiness | `GET /api/v1/masks/personal/mitarbeiter/neu/readiness` |
| Rollout-Route | `/mask-rollout/personal__mitarbeiter__neu/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/personal/mitarbeiter/{entity_id}`

**Beispiel-Prompts:**

- Oeffne Mitarbeiter stamm.
- Bearbeite Stammdaten.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `personal/organigramm` — Organigramm

**Zweck:** Organigramm im personal-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/personal/organigramm/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/personal/organigramm/agent-contract` |
| Readiness | `GET /api/v1/masks/personal/organigramm/readiness` |
| Rollout-Route | `/mask-rollout/personal__organigramm/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/personal/org-chart`

**Beispiel-Prompts:**

- Zeige Organigramm.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `personal/schulung-neu` — Schulung neu

**Zweck:** Schulung neu als Stammblatt pflegen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/personal/schulung-neu/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/personal/schulung-neu/agent-contract` |
| Readiness | `GET /api/v1/masks/personal/schulung-neu/readiness` |
| Rollout-Route | `/mask-rollout/personal__schulung-neu/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/training/courses/{entity_id}`

**Beispiel-Prompts:**

- Oeffne Schulung neu.
- Bearbeite Stammdaten.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `personal/stundenzettel` — Stundenzettel

**Zweck:** Stundenzettel im personal-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/personal/stundenzettel/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/personal/stundenzettel/agent-contract` |
| Readiness | `GET /api/v1/masks/personal/stundenzettel/readiness` |
| Rollout-Route | `/mask-rollout/personal__stundenzettel/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/personal/absences`

**Beispiel-Prompts:**

- Zeige Stundenzettel.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `personal/stundenzettel-liste` — Stundenzettel

**Zweck:** Fahrer-Stundenzettel mit Arbeitszeit und Ueberstunden auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/personal/stundenzettel-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/personal/stundenzettel-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/personal/stundenzettel-liste/readiness` |
| Rollout-Route | `/mask-rollout/personal__stundenzettel-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/personal/stundenzettel`

**Beispiel-Prompts:**

- Wer hatte diese Woche Ueberstunden?
- Wie viele Stunden fuhr Fahrer X im Monat?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `neu` | Stundenzettel erfassen | safe | nein | `Oeffnet die Anlage; Rechte prueft deren Anlageweg.` |
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `personal/zeiterfassung` — Zeiterfassung

**Zweck:** Zeiterfassung im personal-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/personal/zeiterfassung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/personal/zeiterfassung/agent-contract` |
| Readiness | `GET /api/v1/masks/personal/zeiterfassung/readiness` |
| Rollout-Route | `/mask-rollout/personal__zeiterfassung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/personal/absences`

**Beispiel-Prompts:**

- Zeige Zeiterfassung.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `personal/zeiterfassung-liste` — Zeiterfassung

**Zweck:** Zeiterfassung: Eintraege finden und Details oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/personal/zeiterfassung-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/personal/zeiterfassung-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/personal/zeiterfassung-liste/readiness` |
| Rollout-Route | `/mask-rollout/personal__zeiterfassung-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/personal/zeiterfassung`

**Beispiel-Prompts:**

- Welche offenen Zeiterfassung?
- Zeige aktuelle Zeiterfassung.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

## Domäne: platform

### `admin/identity-budgets` — Nutzer- und Agentenkontingente

**Zweck:** Nutzer- und Agentenkontingente

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/admin/identity-budgets/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/admin/identity-budgets/agent-contract` |
| Readiness | `GET /api/v1/masks/admin/identity-budgets/readiness` |
| Rollout-Route | `/mask-rollout/admin__identity-budgets/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/identity/session`
- `records` → `/api/v1/identity/budgets`

**MCP-Tools (Domäne):**

- `admin.postfach.speichern` — scope `admin:write`, Risiko hoch

**Sensible Felder:** `owner, subject, actor`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `allocate` | Kontingent vergeben | moderate | ja | `/api/v1/identity/budgets/actions/allocate` |
| `root` | Mandantenbudget bereitstellen | moderate | ja | `/api/v1/identity/budgets/actions/root` |
| `ledger` | Verbrauchsnebenbuch | safe | nein | `—` |

---

### `admin/postfaecher` — Postfächer

**Zweck:** Postfaecher des Hauses fuer den E-Mail-Versand einrichten, pruefen und freigeben; Bestellungen, Mahnungen, Avise und Newsletter gehen ueber das passende Postfach.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/admin/postfaecher/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/admin/postfaecher/agent-contract` |
| Readiness | `GET /api/v1/masks/admin/postfaecher/readiness` |
| Rollout-Route | `/mask-rollout/admin__postfaecher/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `postfaecher` → `/api/v1/admin/postfaecher`

**MCP-Tools (Domäne):**

- `admin.postfach.speichern` — scope `admin:write`, Risiko hoch

**Beispiel-Prompts:**

- Welches Postfach verschickt Bestellungen?
- Wer darf aus fibu@ senden?

**Sensible Felder:** `passwort`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `speichern` | Postfach speichern | safe | nein | `/api/v1/admin/postfaecher/actions/speichern` |
| `testen` | Testmail senden | safe | nein | `/api/v1/admin/postfaecher/{entity_id}/testen` |
| `anmelden` | Beim Anbieter anmelden | safe | nein | `Fuehrt zur Anmeldung bei Google bzw. Microsoft fuer das geladene Postfach.` |
| `neu` | Neues Postfach | safe | nein | `Leert die Eingabe fuer ein neues Postfach.` |

---

### `admin/token-consumption` — Technisches Verbrauchsnebenbuch

**Zweck:** Technisches Verbrauchsnebenbuch

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/admin/token-consumption/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/admin/token-consumption/agent-contract` |
| Readiness | `GET /api/v1/masks/admin/token-consumption/readiness` |
| Rollout-Route | `/mask-rollout/admin__token-consumption/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/identity/session`
- `records` → `/api/v1/identity/consumption-ledger`

**MCP-Tools (Domäne):**

- `admin.postfach.speichern` — scope `admin:write`, Risiko hoch

**Sensible Felder:** `owner, subject, actor`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `budgets` | Kontingente öffnen | safe | nein | `—` |

---

### `benachrichtigungen/liste` — Benachrichtigungen

**Zweck:** Offene Hinweise und Warnungen sichten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/benachrichtigungen/liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/benachrichtigungen/liste/agent-contract` |
| Readiness | `GET /api/v1/masks/benachrichtigungen/liste/readiness` |
| Rollout-Route | `/mask-rollout/benachrichtigungen__liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/benachrichtigungen`

**MCP-Tools (Domäne):**

- `admin.postfach.speichern` — scope `admin:write`, Risiko hoch

**Beispiel-Prompts:**

- Welche Warnungen sind ungelesen?
- Was ist heute eingegangen?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `dashboard/customizable` — Anpassbares Dashboard

**Zweck:** Persoenliches Dashboard aus freigegebenen Widgets zusammenstellen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/dashboard/customizable/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/dashboard/customizable/agent-contract` |
| Readiness | `GET /api/v1/masks/dashboard/customizable/readiness` |
| Rollout-Route | `/mask-rollout/dashboard__customizable/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/analytics/kpis`

**MCP-Tools (Domäne):**

- `admin.postfach.speichern` — scope `admin:write`, Risiko hoch

**Beispiel-Prompts:**

- Zeige mein Dashboard.
- Welche Widgets sind verfuegbar?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `dashboard/customizable-dashboard` — Anpassbares Dashboard

**Zweck:** Anpassbares Dashboard als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/dashboard/customizable-dashboard/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/dashboard/customizable-dashboard/agent-contract` |
| Readiness | `GET /api/v1/masks/dashboard/customizable-dashboard/readiness` |
| Rollout-Route | `/mask-rollout/dashboard__customizable-dashboard/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/controlling/dashboards`

**MCP-Tools (Domäne):**

- `admin.postfach.speichern` — scope `admin:write`, Risiko hoch

**Beispiel-Prompts:**

- Zeige Anpassbares Dashboard.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `planung/kalender` — Planungskalender

**Zweck:** Zeitbezogene Fristen, Wiedervorlagen und Laeufe ohne Doppelpflege als Planungscockpit sichtbar machen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/planung/kalender/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/planung/kalender/agent-contract` |
| Readiness | `GET /api/v1/masks/planung/kalender/readiness` |
| Rollout-Route | `/mask-rollout/planung__kalender/:entityId` |
| Adapter | `native` (temporary=nein) |

**MCP-Tools (Domäne):**

- `admin.postfach.speichern` — scope `admin:write`, Risiko hoch

**Beispiel-Prompts:**

- Was steht naechste Woche an?
- Zeige Fristen der naechsten 14 Tage.
- Welche OP-Faelligkeiten kommen diese Woche?
- Zeige die Frei/Belegt-Sicht meines Teams.
- Blende abgelehnte Termine ein.

**Sensible Felder:** `owner_id, team_id, title, payload, object_route`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `reproject` | Neu projizieren | moderate | nein | `/api/v1/planung/kalender/reproject` |

---

### `platform/analytics` — Analytics

**Zweck:** Zentrale Analytics-KPIs und Trenduebersicht.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/platform/analytics/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/platform/analytics/agent-contract` |
| Readiness | `GET /api/v1/masks/platform/analytics/readiness` |
| Rollout-Route | `/mask-rollout/platform__analytics/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/analytics/kpis`

**MCP-Tools (Domäne):**

- `admin.postfach.speichern` — scope `admin:write`, Risiko hoch

**Beispiel-Prompts:**

- Zeige Analytics-KPIs.
- Wie entwickeln sich die Trends?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `platform/studio-history` — Studio-Historie

**Zweck:** Versionen, Urheber und Änderungen von Studio-Definitionen nachvollziehen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/platform/studio-history/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/platform/studio-history/agent-contract` |
| Readiness | `GET /api/v1/masks/platform/studio-history/readiness` |
| Rollout-Route | `/mask-rollout/platform__studio-history/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `versions` → `/api/v1/studio/drafts/{entity_id}/history-view`

**MCP-Tools (Domäne):**

- `admin.postfach.speichern` — scope `admin:write`, Risiko hoch

**Sensible Felder:** `actor, before, after`

---

### `platform/studio-history-diff` — Änderungsvergleich

**Zweck:** Versionen, Urheber und Änderungen von Studio-Definitionen nachvollziehen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/platform/studio-history-diff/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/platform/studio-history-diff/agent-contract` |
| Readiness | `GET /api/v1/masks/platform/studio-history-diff/readiness` |
| Rollout-Route | `/mask-rollout/platform__studio-history-diff/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `comparison` → `/api/v1/studio/history-events/{entity_id}/diff`

**MCP-Tools (Domäne):**

- `admin.postfach.speichern` — scope `admin:write`, Risiko hoch

**Sensible Felder:** `actor, before, after`

---

### `process/approval-density` — Freigabe-Dichte

**Zweck:** Freigabe-Engpaesse fuer Leitung sichtbar machen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/process/approval-density/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/process/approval-density/agent-contract` |
| Readiness | `GET /api/v1/masks/process/approval-density/readiness` |
| Rollout-Route | `/mask-rollout/process__approval-density/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `overview` → `/api/v1/process/approval-density/overview`

**MCP-Tools (Domäne):**

- `admin.postfach.speichern` — scope `admin:write`, Risiko hoch

**Beispiel-Prompts:**

- Wo staut sich die Freigabe?

---

### `process/background-jobs` — Hintergrund-Jobs

**Zweck:** Hintergrundverarbeitung ueberwachen und nachsteuern.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/process/background-jobs/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/process/background-jobs/agent-contract` |
| Readiness | `GET /api/v1/masks/process/background-jobs/readiness` |
| Rollout-Route | `/mask-rollout/process__background-jobs/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `queue` → `/api/v1/process/background-jobs/queue`

**MCP-Tools (Domäne):**

- `admin.postfach.speichern` — scope `admin:write`, Risiko hoch

**Beispiel-Prompts:**

- Welche Jobs sind in der Queue fehlgeschlagen?

---

### `schnittstelle/mde-inbox` — MDE-Eingangskorb

**Zweck:** MDE-Ereignisse mandantenbezogen ueberwachen und fehlgeschlagene Verarbeitung nachvollziehbar behandeln.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/schnittstelle/mde-inbox/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/schnittstelle/mde-inbox/agent-contract` |
| Readiness | `GET /api/v1/masks/schnittstelle/mde-inbox/readiness` |
| Rollout-Route | `/mask-rollout/schnittstelle__mde-inbox/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/mobile/sync-summary`
- `queue` → `/api/v1/mobile/sync-queue`

**MCP-Tools (Domäne):**

- `admin.postfach.speichern` — scope `admin:write`, Risiko hoch

**Beispiel-Prompts:**

- Zeige MDE-Ereignisse in Quarantaene.
- Welche Inventurzaehlungen sind fehlgeschlagen?
- Welche Geraete liefern aktuell Fehler?

**Sensible Felder:** `error_message, idempotency_key`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `process_pending` | Ausstehende verarbeiten | moderate | nein | `/api/v1/mobile/sync-process` |

---

### `workflow/workflow-monitoring` — Workflow-Monitoring

**Zweck:** Workflow-Ausfuehrungen und Fehler transparent machen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/workflow/workflow-monitoring/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/workflow/workflow-monitoring/agent-contract` |
| Readiness | `GET /api/v1/masks/workflow/workflow-monitoring/readiness` |
| Rollout-Route | `/mask-rollout/workflow__workflow-monitoring/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/workflow/cockpit/summary`
- `instances` → `/api/v1/workflow/runtime/instances`

**MCP-Tools (Domäne):**

- `admin.postfach.speichern` — scope `admin:write`, Risiko hoch

**Beispiel-Prompts:**

- Welche Workflows sind fehlgeschlagen?

---

## Domäne: portal

### `portal/anfragen` — Anfragen

**Zweck:** Anfragen im portal-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/portal/anfragen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/portal/anfragen/agent-contract` |
| Readiness | `GET /api/v1/masks/portal/anfragen/readiness` |
| Rollout-Route | `/mask-rollout/portal__anfragen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/portal/anfragen`

**Beispiel-Prompts:**

- Zeige Anfragen.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `portal/bestellungen` — Bestellungen

**Zweck:** Bestellungen im portal-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/portal/bestellungen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/portal/bestellungen/agent-contract` |
| Readiness | `GET /api/v1/masks/portal/bestellungen/readiness` |
| Rollout-Route | `/mask-rollout/portal__bestellungen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/portal/anfragen`

**Beispiel-Prompts:**

- Zeige Bestellungen.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `portal/dokumente` — Dokumente

**Zweck:** Dokumente im portal-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/portal/dokumente/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/portal/dokumente/agent-contract` |
| Readiness | `GET /api/v1/masks/portal/dokumente/readiness` |
| Rollout-Route | `/mask-rollout/portal__dokumente/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/portal/anfragen`

**Beispiel-Prompts:**

- Zeige Dokumente.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `portal/empfehlungen` — Empfehlungen

**Zweck:** Empfehlungen im portal-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/portal/empfehlungen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/portal/empfehlungen/agent-contract` |
| Readiness | `GET /api/v1/masks/portal/empfehlungen/readiness` |
| Rollout-Route | `/mask-rollout/portal__empfehlungen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/portal/empfehlungen`

**Beispiel-Prompts:**

- Zeige Empfehlungen.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `portal/feldbuch` — Feldbuch

**Zweck:** Feldbuch im portal-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/portal/feldbuch/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/portal/feldbuch/agent-contract` |
| Readiness | `GET /api/v1/masks/portal/feldbuch/readiness` |
| Rollout-Route | `/mask-rollout/portal__feldbuch/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/portal/anfragen`

**Beispiel-Prompts:**

- Zeige Feldbuch.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `portal/lohndienste/neu` — Lohndienste

**Zweck:** Lohndienste im portal-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/portal/lohndienste/neu/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/portal/lohndienste/neu/agent-contract` |
| Readiness | `GET /api/v1/masks/portal/lohndienste/neu/readiness` |
| Rollout-Route | `/mask-rollout/portal__lohndienste__neu/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/portal/lohndienste`

**Beispiel-Prompts:**

- Zeige Lohndienste.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `portal/naehrstoffbilanzen` — Naehrstoffbilanzen

**Zweck:** Naehrstoffbilanzen mandantensicher als Cockpit bereitstellen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/portal/naehrstoffbilanzen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/portal/naehrstoffbilanzen/agent-contract` |
| Readiness | `GET /api/v1/masks/portal/naehrstoffbilanzen/readiness` |
| Rollout-Route | `/mask-rollout/portal__naehrstoffbilanzen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/portal/anfragen`

**Beispiel-Prompts:**

- Zeige Naehrstoffbilanzen.
- Aktualisiere die Kennzahlen.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `portal/onboarding` — Onboarding

**Zweck:** Onboarding im portal-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/portal/onboarding/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/portal/onboarding/agent-contract` |
| Readiness | `GET /api/v1/masks/portal/onboarding/readiness` |
| Rollout-Route | `/mask-rollout/portal__onboarding/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/portal/interessenten`

**Beispiel-Prompts:**

- Zeige Onboarding.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `portal/preisspiegel` — Preisspiegel

**Zweck:** Preisspiegel im portal-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/portal/preisspiegel/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/portal/preisspiegel/agent-contract` |
| Readiness | `GET /api/v1/masks/portal/preisspiegel/readiness` |
| Rollout-Route | `/mask-rollout/portal__preisspiegel/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/portal/anfragen`

**Beispiel-Prompts:**

- Zeige Preisspiegel.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `portal/rationsoptimierung` — Rationsoptimierung

**Zweck:** Rationsoptimierung im portal-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/portal/rationsoptimierung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/portal/rationsoptimierung/agent-contract` |
| Readiness | `GET /api/v1/masks/portal/rationsoptimierung/readiness` |
| Rollout-Route | `/mask-rollout/portal__rationsoptimierung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/portal/anfragen`

**Beispiel-Prompts:**

- Zeige Rationsoptimierung.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `portal/rechnungen` — Rechnungen

**Zweck:** Rechnungen im portal-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/portal/rechnungen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/portal/rechnungen/agent-contract` |
| Readiness | `GET /api/v1/masks/portal/rechnungen/readiness` |
| Rollout-Route | `/mask-rollout/portal__rechnungen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/portal/anfragen`

**Beispiel-Prompts:**

- Zeige Rechnungen.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `portal/shop` — Shop

**Zweck:** Shop im portal-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/portal/shop/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/portal/shop/agent-contract` |
| Readiness | `GET /api/v1/masks/portal/shop/readiness` |
| Rollout-Route | `/mask-rollout/portal__shop/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/portal/anfragen`

**Beispiel-Prompts:**

- Zeige Shop.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `portal/vertraege` — Vertraege

**Zweck:** Vertraege im portal-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/portal/vertraege/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/portal/vertraege/agent-contract` |
| Readiness | `GET /api/v1/masks/portal/vertraege/readiness` |
| Rollout-Route | `/mask-rollout/portal__vertraege/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/portal/anfragen`

**Beispiel-Prompts:**

- Zeige Vertraege.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `portal/whatsapp-simulator` — Whatsapp simulator

**Zweck:** Whatsapp simulator im portal-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/portal/whatsapp-simulator/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/portal/whatsapp-simulator/agent-contract` |
| Readiness | `GET /api/v1/masks/portal/whatsapp-simulator/readiness` |
| Rollout-Route | `/mask-rollout/portal__whatsapp-simulator/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/portal/anfragen`

**Beispiel-Prompts:**

- Zeige Whatsapp simulator.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `portal/zertifikat` — Zertifikat

**Zweck:** Kundenportal-Zertifikat.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/portal/zertifikat/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/portal/zertifikat/agent-contract` |
| Readiness | `GET /api/v1/masks/portal/zertifikat/readiness` |
| Rollout-Route | `/mask-rollout/portal__zertifikat/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/portal/zertifikate/{entity_id}`

**Beispiel-Prompts:**

- Bis wann ist Zertifikat {entity_id} gueltig?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `portal/zertifikate` — Zertifikate

**Zweck:** Zertifikate des zugeordneten Kundenkontos finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/portal/zertifikate/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/portal/zertifikate/agent-contract` |
| Readiness | `GET /api/v1/masks/portal/zertifikate/readiness` |
| Rollout-Route | `/mask-rollout/portal__zertifikate/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/portal/zertifikate`

**Beispiel-Prompts:**

- Zeige meine Zertifikate.
- Filtere die Zertifikate.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

## Domäne: pos

### `pos/customer-display` — Customer display

**Zweck:** Customer display im pos-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/pos/customer-display/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/pos/customer-display/agent-contract` |
| Readiness | `GET /api/v1/masks/pos/customer-display/readiness` |
| Rollout-Route | `/mask-rollout/pos__customer-display/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/pos/dsfinvk/export`

**Beispiel-Prompts:**

- Zeige Customer display.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `pos/gift-cards` — Gift cards

**Zweck:** Gift cards im pos-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/pos/gift-cards/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/pos/gift-cards/agent-contract` |
| Readiness | `GET /api/v1/masks/pos/gift-cards/readiness` |
| Rollout-Route | `/mask-rollout/pos__gift-cards/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/pos/dsfinvk/export`

**Beispiel-Prompts:**

- Zeige Gift cards.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `pos/promotionen` — Promotionen

**Zweck:** Promotionen im pos-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/pos/promotionen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/pos/promotionen/agent-contract` |
| Readiness | `GET /api/v1/masks/pos/promotionen/readiness` |
| Rollout-Route | `/mask-rollout/pos__promotionen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/pos/promotions`

**Beispiel-Prompts:**

- Zeige Promotionen.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `pos/rabatte` — Rabatte

**Zweck:** Rabatte im pos-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/pos/rabatte/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/pos/rabatte/agent-contract` |
| Readiness | `GET /api/v1/masks/pos/rabatte/readiness` |
| Rollout-Route | `/mask-rollout/pos__rabatte/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/pos/dsfinvk/export`

**Beispiel-Prompts:**

- Zeige Rabatte.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `pos/retoure` — Retoure

**Zweck:** Retoure im pos-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/pos/retoure/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/pos/retoure/agent-contract` |
| Readiness | `GET /api/v1/masks/pos/retoure/readiness` |
| Rollout-Route | `/mask-rollout/pos__retoure/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/pos/dsfinvk/export`

**Beispiel-Prompts:**

- Zeige Retoure.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `pos/suspended-sales` — Suspended sales

**Zweck:** Suspended sales im pos-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/pos/suspended-sales/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/pos/suspended-sales/agent-contract` |
| Readiness | `GET /api/v1/masks/pos/suspended-sales/readiness` |
| Rollout-Route | `/mask-rollout/pos__suspended-sales/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/pos/dsfinvk/export`

**Beispiel-Prompts:**

- Zeige Suspended sales.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `pos/tagesabschluss-enhanced` — Tagesabschluss enhanced

**Zweck:** Tagesabschluss enhanced im pos-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/pos/tagesabschluss-enhanced/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/pos/tagesabschluss-enhanced/agent-contract` |
| Readiness | `GET /api/v1/masks/pos/tagesabschluss-enhanced/readiness` |
| Rollout-Route | `/mask-rollout/pos__tagesabschluss-enhanced/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/pos/dsfinvk/status`

**Beispiel-Prompts:**

- Zeige Tagesabschluss enhanced.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `pos/terminal` — Terminal

**Zweck:** Terminal im pos-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/pos/terminal/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/pos/terminal/agent-contract` |
| Readiness | `GET /api/v1/masks/pos/terminal/readiness` |
| Rollout-Route | `/mask-rollout/pos__terminal/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/pos/dsfinvk/export`

**Beispiel-Prompts:**

- Zeige Terminal.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `pos/tse-journal` — Tse journal

**Zweck:** Tse journal im pos-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/pos/tse-journal/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/pos/tse-journal/agent-contract` |
| Readiness | `GET /api/v1/masks/pos/tse-journal/readiness` |
| Rollout-Route | `/mask-rollout/pos__tse-journal/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/pos/dsfinvk/export`

**Beispiel-Prompts:**

- Zeige Tse journal.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `pos/uebernahme-kasse` — Uebernahme kasse

**Zweck:** Uebernahme kasse im pos-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/pos/uebernahme-kasse/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/pos/uebernahme-kasse/agent-contract` |
| Readiness | `GET /api/v1/masks/pos/uebernahme-kasse/readiness` |
| Rollout-Route | `/mask-rollout/pos__uebernahme-kasse/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/pos/dsfinvk/export`

**Beispiel-Prompts:**

- Zeige Uebernahme kasse.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

## Domäne: preise

### `preise/historie` — Historie

**Zweck:** Historie im preise-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/preise/historie/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/preise/historie/agent-contract` |
| Readiness | `GET /api/v1/masks/preise/historie/readiness` |
| Rollout-Route | `/mask-rollout/preise__historie/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/preise/historie`

**Beispiel-Prompts:**

- Zeige Historie.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `preise/individualpreise` — Neuer {label} [PRI{preisTyp === 'EK' ? 'E' : ''}]

**Zweck:** Neuer {label} [PRI{preisTyp === 'EK' ? 'E' : ''}] als Stammblatt pflegen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/preise/individualpreise/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/preise/individualpreise/agent-contract` |
| Readiness | `GET /api/v1/masks/preise/individualpreise/readiness` |
| Rollout-Route | `/mask-rollout/preise__individualpreise/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/preise/individualpreise/{entity_id}`

**Beispiel-Prompts:**

- Oeffne Neuer {label} [PRI{preisTyp === 'EK' ? 'E' : ''}].
- Bearbeite Stammdaten.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `preise/konditionen` — Konditionen

**Zweck:** Konditionen im preise-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/preise/konditionen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/preise/konditionen/agent-contract` |
| Readiness | `GET /api/v1/masks/preise/konditionen/readiness` |
| Rollout-Route | `/mask-rollout/preise__konditionen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/preise/konditionen`

**Beispiel-Prompts:**

- Zeige Konditionen.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `preise/rabattgruppen` — Neue Rabattgruppe [RAG]

**Zweck:** Neue Rabattgruppe [RAG] als Stammblatt pflegen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/preise/rabattgruppen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/preise/rabattgruppen/agent-contract` |
| Readiness | `GET /api/v1/masks/preise/rabattgruppen/readiness` |
| Rollout-Route | `/mask-rollout/preise__rabattgruppen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/preise/rabatte/gruppen/{entity_id}`

**Beispiel-Prompts:**

- Oeffne Neue Rabattgruppe [RAG].
- Bearbeite Stammdaten.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `preise/zu-abschlaggruppen` — Neue Zu-/Abschlaggruppe [ZAGR]

**Zweck:** Neue Zu-/Abschlaggruppe [ZAGR] als Stammblatt pflegen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/preise/zu-abschlaggruppen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/preise/zu-abschlaggruppen/agent-contract` |
| Readiness | `GET /api/v1/masks/preise/zu-abschlaggruppen/readiness` |
| Rollout-Route | `/mask-rollout/preise__zu-abschlaggruppen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/kontrakte/zuabschlagsgruppen/{entity_id}`

**Beispiel-Prompts:**

- Oeffne Neue Zu-/Abschlaggruppe [ZAGR].
- Bearbeite Stammdaten.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

## Domäne: produktion

### `produktion/mischfutter-produktion` — Mischfutter produktion

**Zweck:** Mischfutter produktion im produktion-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/produktion/mischfutter-produktion/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/produktion/mischfutter-produktion/agent-contract` |
| Readiness | `GET /api/v1/masks/produktion/mischfutter-produktion/readiness` |
| Rollout-Route | `/mask-rollout/produktion__mischfutter-produktion/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/produktion/mischfutter/auftraege`

**MCP-Tools (Domäne):**

- `produktion.control.sync` — scope `ops:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Mischfutter produktion.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `produktion/produktions-dokumente-drucken` — Produktions dokumente drucken

**Zweck:** Produktions dokumente drucken im produktion-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/produktion/produktions-dokumente-drucken/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/produktion/produktions-dokumente-drucken/agent-contract` |
| Readiness | `GET /api/v1/masks/produktion/produktions-dokumente-drucken/readiness` |
| Rollout-Route | `/mask-rollout/produktion__produktions-dokumente-drucken/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/produktion/mischfutter/auftraege`

**MCP-Tools (Domäne):**

- `produktion.control.sync` — scope `ops:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Produktions dokumente drucken.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `produktion/rezepturgruppe` — Rezepturgruppe

**Zweck:** Rezepturgruppen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/produktion/rezepturgruppe/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/produktion/rezepturgruppe/agent-contract` |
| Readiness | `GET /api/v1/masks/produktion/rezepturgruppe/readiness` |
| Rollout-Route | `/mask-rollout/produktion__rezepturgruppe/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/produktion/mischfutter/rezepturgruppen/{entity_id}`

**MCP-Tools (Domäne):**

- `produktion.control.sync` — scope `ops:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Rezepte gehoeren zu Gruppe {entity_id}?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `produktion/rezepturgruppen` — Neue Rezepturgruppe anlegen

**Zweck:** Neue Rezepturgruppe anlegen als Stammblatt pflegen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/produktion/rezepturgruppen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/produktion/rezepturgruppen/agent-contract` |
| Readiness | `GET /api/v1/masks/produktion/rezepturgruppen/readiness` |
| Rollout-Route | `/mask-rollout/produktion__rezepturgruppen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/produktion/mischfutter/rezepturgruppen/{entity_id}`

**MCP-Tools (Domäne):**

- `produktion.control.sync` — scope `ops:write`, Risiko mittel

**Beispiel-Prompts:**

- Oeffne Neue Rezepturgruppe anlegen.
- Bearbeite Stammdaten.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `rezepte/rezept` — Rezept

**Zweck:** Rezeptur-Editor Stammdaten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/rezepte/rezept/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/rezepte/rezept/agent-contract` |
| Readiness | `GET /api/v1/masks/rezepte/rezept/readiness` |
| Rollout-Route | `/mask-rollout/rezepte__rezept/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/futtermittel/rezepte/{entity_id}`

**MCP-Tools (Domäne):**

- `produktion.control.sync` — scope `ops:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Artikelnummer hat Rezept {entity_id}?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

## Domäne: prospecting

### `prospecting/leads` — LeadExplorer

**Zweck:** LeadExplorer im prospecting-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/prospecting/leads/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/prospecting/leads/agent-contract` |
| Readiness | `GET /api/v1/masks/prospecting/leads/readiness` |
| Rollout-Route | `/mask-rollout/prospecting__leads/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/prospecting/lead-candidates`

**Beispiel-Prompts:**

- Zeige LeadExplorer.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

## Domäne: qualitaet

### `admin/qualitaets-cockpit` — Qualitaets-Cockpit

**Zweck:** QS-Lage und Laborauftraege als Admin-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/admin/qualitaets-cockpit/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/admin/qualitaets-cockpit/agent-contract` |
| Readiness | `GET /api/v1/masks/admin/qualitaets-cockpit/readiness` |
| Rollout-Route | `/mask-rollout/admin__qualitaets-cockpit/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/qualitaet/stats`

**MCP-Tools (Domäne):**

- `qualitaet.reklamation.abschliessen` — scope `quality:write`, Risiko mittel

**Beispiel-Prompts:**

- Wie viele Reklamationen sind offen?
- Zeige QS-Statistik.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `labor/proben-liste` — Laborproben

**Zweck:** Laborproben und ihren Bearbeitungsstand verfolgen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/labor/proben-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/labor/proben-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/labor/proben-liste/readiness` |
| Rollout-Route | `/mask-rollout/labor__proben-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/labor/proben`

**MCP-Tools (Domäne):**

- `qualitaet.reklamation.abschliessen` — scope `quality:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Proben sind noch ausstehend?
- Welche Proben gingen diese Woche ans Labor?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `lager/qs-leitstand` — QS-Leitstand

**Zweck:** QS-Sperren und Laborlage im Lager-Leitstand.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/lager/qs-leitstand/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/lager/qs-leitstand/agent-contract` |
| Readiness | `GET /api/v1/masks/lager/qs-leitstand/readiness` |
| Rollout-Route | `/mask-rollout/lager__qs-leitstand/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/qualitaet/stats`

**MCP-Tools (Domäne):**

- `qualitaet.reklamation.abschliessen` — scope `quality:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Chargen sind gesperrt?
- Zeige offene Laborauftraege.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `qualitaet/ausnahmen-liste` — Betriebsausnahmen

**Zweck:** Betriebsausnahmen: Eintraege finden und Details oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/qualitaet/ausnahmen-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/qualitaet/ausnahmen-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/qualitaet/ausnahmen-liste/readiness` |
| Rollout-Route | `/mask-rollout/qualitaet__ausnahmen-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/operations/exceptions`

**MCP-Tools (Domäne):**

- `qualitaet.reklamation.abschliessen` — scope `quality:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche offenen Betriebsausnahmen?
- Zeige aktuelle Betriebsausnahmen.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `qualitaet/labor-auftrag` — Labor auftrag

**Zweck:** Labor auftrag im qualitaet-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/qualitaet/labor-auftrag/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/qualitaet/labor-auftrag/agent-contract` |
| Readiness | `GET /api/v1/masks/qualitaet/labor-auftrag/readiness` |
| Rollout-Route | `/mask-rollout/qualitaet__labor-auftrag/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/qualitaet/labor-auftraege`

**MCP-Tools (Domäne):**

- `qualitaet.reklamation.abschliessen` — scope `quality:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Labor auftrag.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `qualitaet/labor-detail` — Labor detail

**Zweck:** Labor detail als Stammblatt pflegen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/qualitaet/labor-detail/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/qualitaet/labor-detail/agent-contract` |
| Readiness | `GET /api/v1/masks/qualitaet/labor-detail/readiness` |
| Rollout-Route | `/mask-rollout/qualitaet__labor-detail/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/qualitaet/labor-auftraege/{entity_id}`

**MCP-Tools (Domäne):**

- `qualitaet.reklamation.abschliessen` — scope `quality:write`, Risiko mittel

**Beispiel-Prompts:**

- Oeffne Labor detail.
- Bearbeite Stammdaten.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `qualitaet/labor-liste` — Laborauftraege

**Zweck:** Laborauftraege und Befunde nachverfolgen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/qualitaet/labor-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/qualitaet/labor-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/qualitaet/labor-liste/readiness` |
| Rollout-Route | `/mask-rollout/qualitaet__labor-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/qualitaet/labor-auftraege`

**MCP-Tools (Domäne):**

- `qualitaet.reklamation.abschliessen` — scope `quality:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Laborauftraege sind offen?
- Welche Charge wartet auf Befund?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `neu` | Laborauftrag anlegen | safe | nein | `Oeffnet die Anlage; Rechte prueft deren Anlageweg.` |
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `qualitaet/reklamation` — Reklamation

**Zweck:** Reklamation: Qualitaetsmaengel mit Massnahmen und Dokumenten fuer Reklamationsbearbeitung.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/qualitaet/reklamation/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/qualitaet/reklamation/agent-contract` |
| Readiness | `GET /api/v1/masks/qualitaet/reklamation/readiness` |
| Rollout-Route | `/mask-rollout/qualitaet__reklamation/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/reklamationen/{entity_id}`
- `massnahmen` → `/api/v1/masks/qualitaet/reklamationen/entity/{entity_id}/tabs/massnahmen`
- `dokumente` → `/api/v1/masks/qualitaet/reklamationen/entity/{entity_id}/tabs/dokumente`

**MCP-Tools (Domäne):**

- `qualitaet.reklamation.abschliessen` — scope `quality:write`, Risiko mittel

**Beispiel-Prompts:**

- Was ist der Status von Reklamation {entity_id}?
- Zeige alle offenen Massnahmen von Reklamation {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Zustaendigkeit/Frist | safe | nein | `/api/v1/reklamationen/{entity_id}/actions/bearbeiten` |
| `abschliessen` | Abschliessen | moderate | nein | `/api/v1/reklamationen/{entity_id}/actions/abschliessen` |

---

### `qualitaet/reklamation-detail` — Status geaendert

**Zweck:** Status geaendert im qualitaet-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/qualitaet/reklamation-detail/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/qualitaet/reklamation-detail/agent-contract` |
| Readiness | `GET /api/v1/masks/qualitaet/reklamation-detail/readiness` |
| Rollout-Route | `/mask-rollout/qualitaet__reklamation-detail/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/qualitaet/labor-auftraege`

**MCP-Tools (Domäne):**

- `qualitaet.reklamation.abschliessen` — scope `quality:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Status geaendert.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `qualitaet/reklamationen` — Reklamationen

**Zweck:** Reklamationen im qualitaet-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/qualitaet/reklamationen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/qualitaet/reklamationen/agent-contract` |
| Readiness | `GET /api/v1/masks/qualitaet/reklamationen/readiness` |
| Rollout-Route | `/mask-rollout/qualitaet__reklamationen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/qualitaet/labor-auftraege`

**MCP-Tools (Domäne):**

- `qualitaet.reklamation.abschliessen` — scope `quality:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Reklamationen.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `qualitaet/reklamationen-liste` — Reklamationen

**Zweck:** Reklamationen nach Prioritaet und Bearbeitungsstand steuern.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/qualitaet/reklamationen-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/qualitaet/reklamationen-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/qualitaet/reklamationen-liste/readiness` |
| Rollout-Route | `/mask-rollout/qualitaet__reklamationen-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/qualitaet/reklamationen`

**MCP-Tools (Domäne):**

- `qualitaet.reklamation.abschliessen` — scope `quality:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Reklamationen sind offen?
- Welche Faelle sind hoch priorisiert?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `neu` | Neue Reklamation | safe | nein | `Oeffnet die Anlage; Rechte prueft deren Anlageweg.` |
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `strecke/qualitaets-abweichung` — Qualitätsabweichung

**Zweck:** Qualitaetsabweichungen nach Nummer, Kunde, Artikel und Status sichten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/strecke/qualitaets-abweichung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/strecke/qualitaets-abweichung/agent-contract` |
| Readiness | `GET /api/v1/masks/strecke/qualitaets-abweichung/readiness` |
| Rollout-Route | `/mask-rollout/strecke__qualitaets-abweichung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/qualitaet/reklamationen`

**MCP-Tools (Domäne):**

- `qualitaet.reklamation.abschliessen` — scope `quality:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Reklamationen sind noch neu?

---

### `zertifikate/liste` — Zertifikate

**Zweck:** Zertifikate und ablaufende Nachweise im Blick behalten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/zertifikate/liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/zertifikate/liste/agent-contract` |
| Readiness | `GET /api/v1/masks/zertifikate/liste/readiness` |
| Rollout-Route | `/mask-rollout/zertifikate__liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/zertifikate`

**MCP-Tools (Domäne):**

- `qualitaet.reklamation.abschliessen` — scope `quality:write`, Risiko mittel

**Beispiel-Prompts:**

- Welche Zertifikate laufen dieses Quartal ab?
- Welche QS-Nachweise sind gueltig?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

## Domäne: reporting

### `analysis/what-if-simulator` — What if simulator

**Zweck:** Stamm- und Fachmaske fuer What if simulator (analysis/what-if-simulator).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/analysis/what-if-simulator/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/analysis/what-if-simulator/agent-contract` |
| Readiness | `GET /api/v1/masks/analysis/what-if-simulator/readiness` |
| Rollout-Route | `/mask-rollout/analysis__what-if-simulator/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/rations-optimization/feeding/reports/{entity_id}`

**MCP-Tools (Domäne):**

- `reporting.bonus.calculate` — scope `reporting:write`, Risiko mittel
- `reporting.query.import_signed` — scope `reporting:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer What if simulator {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `auswertungen/abfrage-center` — Abfrage-Center

**Zweck:** Freigegebene Read Models ohne beliebiges SQL anwendergerecht abfragen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/auswertungen/abfrage-center/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/auswertungen/abfrage-center/agent-contract` |
| Readiness | `GET /api/v1/masks/auswertungen/abfrage-center/readiness` |
| Rollout-Route | `/mask-rollout/auswertungen__abfrage-center/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/query-center/catalog`
- `definitions` → `/api/v1/query-center`

**MCP-Tools (Domäne):**

- `reporting.bonus.calculate` — scope `reporting:write`, Risiko mittel
- `reporting.query.import_signed` — scope `reporting:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige meine favorisierten Abfragen.
- Erstelle eine begrenzte Vorschau offener Rechnungen.

**Sensible Felder:** `filter_spec, selected_fields`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `create` | Neue Abfrage | safe | nein | `—` |
| `import` | Signiert importieren | moderate | nein | `/api/v1/query-center/actions/import` |

---

### `auswertungen/abfrage-generator` — Abfrage generator

**Zweck:** Stamm- und Fachmaske fuer Abfrage generator (auswertungen/abfrage-generator).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/auswertungen/abfrage-generator/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/auswertungen/abfrage-generator/agent-contract` |
| Readiness | `GET /api/v1/masks/auswertungen/abfrage-generator/readiness` |
| Rollout-Route | `/mask-rollout/auswertungen__abfrage-generator/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/l3-report-catalog/{entity_id}/run`

**MCP-Tools (Domäne):**

- `reporting.bonus.calculate` — scope `reporting:write`, Risiko mittel
- `reporting.query.import_signed` — scope `reporting:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Abfrage generator {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `auswertungen/agrarmarkt-bericht` — Agrarmarkt bericht

**Zweck:** Stamm- und Fachmaske fuer Agrarmarkt bericht (auswertungen/agrarmarkt-bericht).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/auswertungen/agrarmarkt-bericht/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/auswertungen/agrarmarkt-bericht/agent-contract` |
| Readiness | `GET /api/v1/masks/auswertungen/agrarmarkt-bericht/readiness` |
| Rollout-Route | `/mask-rollout/auswertungen__agrarmarkt-bericht/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/massebilanz/{entity_id}/bericht`

**MCP-Tools (Domäne):**

- `reporting.bonus.calculate` — scope `reporting:write`, Risiko mittel
- `reporting.query.import_signed` — scope `reporting:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Agrarmarkt bericht {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `auswertungen/bonus-berechnung` — Bonus-Berechnung

**Zweck:** Bonusfaehige Umsaetze reproduzierbar berechnen und Korrekturen unveraenderbar nachweisen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/auswertungen/bonus-berechnung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/auswertungen/bonus-berechnung/agent-contract` |
| Readiness | `GET /api/v1/masks/auswertungen/bonus-berechnung/readiness` |
| Rollout-Route | `/mask-rollout/auswertungen__bonus-berechnung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/l3-report-catalog/bonus-runs`
- `runs` → `/api/v1/l3-report-catalog/bonus-runs`

**MCP-Tools (Domäne):**

- `reporting.bonus.calculate` — scope `reporting:write`, Risiko mittel
- `reporting.query.import_signed` — scope `reporting:write`, Risiko mittel

**Beispiel-Prompts:**

- Berechne den Kundenbonus fuer dieses Jahr.
- Exportiere diesen Bonuslauf.

**Sensible Felder:** `total_basis, total_bonus, dimension_id, actor`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `calculate` | Bonuslauf berechnen | moderate | nein | `/api/v1/l3-report-catalog/bonus-runs/actions/calculate` |

---

### `auswertungen/deckungsbeitraege` — Deckungsbeitraege

**Zweck:** Stamm- und Fachmaske fuer Deckungsbeitraege (auswertungen/deckungsbeitraege).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/auswertungen/deckungsbeitraege/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/auswertungen/deckungsbeitraege/agent-contract` |
| Readiness | `GET /api/v1/masks/auswertungen/deckungsbeitraege/readiness` |
| Rollout-Route | `/mask-rollout/auswertungen__deckungsbeitraege/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/crm/bedarfsdeckung/{entity_id}`

**MCP-Tools (Domäne):**

- `reporting.bonus.calculate` — scope `reporting:write`, Risiko mittel
- `reporting.query.import_signed` — scope `reporting:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Deckungsbeitraege {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `auswertungen/erntebilanz` — Erntebilanz

**Zweck:** Stamm- und Fachmaske fuer Erntebilanz (auswertungen/erntebilanz).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/auswertungen/erntebilanz/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/auswertungen/erntebilanz/agent-contract` |
| Readiness | `GET /api/v1/masks/auswertungen/erntebilanz/readiness` |
| Rollout-Route | `/mask-rollout/auswertungen__erntebilanz/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/l3-report-catalog/{entity_id}/run`

**MCP-Tools (Domäne):**

- `reporting.bonus.calculate` — scope `reporting:write`, Risiko mittel
- `reporting.query.import_signed` — scope `reporting:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Erntebilanz {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `auswertungen/kundenumsatz` — Kundenumsatz

**Zweck:** Stamm- und Fachmaske fuer Kundenumsatz (auswertungen/kundenumsatz).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/auswertungen/kundenumsatz/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/auswertungen/kundenumsatz/agent-contract` |
| Readiness | `GET /api/v1/masks/auswertungen/kundenumsatz/readiness` |
| Rollout-Route | `/mask-rollout/auswertungen__kundenumsatz/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/l3-report-catalog/{entity_id}/drilldown`

**MCP-Tools (Domäne):**

- `reporting.bonus.calculate` — scope `reporting:write`, Risiko mittel
- `reporting.query.import_signed` — scope `reporting:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Kundenumsatz {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `auswertungen/l3-berichtskatalog` — L3-Berichtskatalog

**Zweck:** Priorisierte L3-Berichte mit identischen Summen in Ansicht und Export bereitstellen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/auswertungen/l3-berichtskatalog/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/auswertungen/l3-berichtskatalog/agent-contract` |
| Readiness | `GET /api/v1/masks/auswertungen/l3-berichtskatalog/readiness` |
| Rollout-Route | `/mask-rollout/auswertungen__l3-berichtskatalog/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/l3-report-catalog`
- `reports` → `/api/v1/l3-report-catalog`

**MCP-Tools (Domäne):**

- `reporting.bonus.calculate` — scope `reporting:write`, Risiko mittel
- `reporting.query.import_signed` — scope `reporting:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Umsatz nach Vertreter.
- Drille die Chargensumme auf Belege herunter.

**Sensible Felder:** `customer_id, representative_id, source_ref`

---

### `auswertungen/lagerumschlag` — Lagerumschlag

**Zweck:** Stamm- und Fachmaske fuer Lagerumschlag (auswertungen/lagerumschlag).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/auswertungen/lagerumschlag/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/auswertungen/lagerumschlag/agent-contract` |
| Readiness | `GET /api/v1/masks/auswertungen/lagerumschlag/readiness` |
| Rollout-Route | `/mask-rollout/auswertungen__lagerumschlag/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/l3-report-catalog/{entity_id}/run`

**MCP-Tools (Domäne):**

- `reporting.bonus.calculate` — scope `reporting:write`, Risiko mittel
- `reporting.query.import_signed` — scope `reporting:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Lagerumschlag {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `auswertungen/lieferantenbewertung` — Lieferantenbewertung

**Zweck:** Stamm- und Fachmaske fuer Lieferantenbewertung (auswertungen/lieferantenbewertung).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/auswertungen/lieferantenbewertung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/auswertungen/lieferantenbewertung/agent-contract` |
| Readiness | `GET /api/v1/masks/auswertungen/lieferantenbewertung/readiness` |
| Rollout-Route | `/mask-rollout/auswertungen__lieferantenbewertung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/l3-report-catalog/{entity_id}/run`

**MCP-Tools (Domäne):**

- `reporting.bonus.calculate` — scope `reporting:write`, Risiko mittel
- `reporting.query.import_signed` — scope `reporting:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Lieferantenbewertung {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `auswertungen/rohertrag` — Rohertrag

**Zweck:** Stamm- und Fachmaske fuer Rohertrag (auswertungen/rohertrag).

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/auswertungen/rohertrag/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/auswertungen/rohertrag/agent-contract` |
| Readiness | `GET /api/v1/masks/auswertungen/rohertrag/readiness` |
| Rollout-Route | `/mask-rollout/auswertungen__rohertrag/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/l3-report-catalog/{entity_id}/run`

**MCP-Tools (Domäne):**

- `reporting.bonus.calculate` — scope `reporting:write`, Risiko mittel
- `reporting.query.import_signed` — scope `reporting:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Stammdaten fuer Rohertrag {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `—` |

---

### `auswertungen/umsatzstatistik` — Umsatzstatistik

**Zweck:** Umsatzstatistik als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/auswertungen/umsatzstatistik/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/auswertungen/umsatzstatistik/agent-contract` |
| Readiness | `GET /api/v1/masks/auswertungen/umsatzstatistik/readiness` |
| Rollout-Route | `/mask-rollout/auswertungen__umsatzstatistik/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/sales/reports/summary`

**MCP-Tools (Domäne):**

- `reporting.bonus.calculate` — scope `reporting:write`, Risiko mittel
- `reporting.query.import_signed` — scope `reporting:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Umsatzstatistik.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `auswertungen/vertriebstrichter` — Vertriebstrichter

**Zweck:** Vertriebstrichter als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/auswertungen/vertriebstrichter/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/auswertungen/vertriebstrichter/agent-contract` |
| Readiness | `GET /api/v1/masks/auswertungen/vertriebstrichter/readiness` |
| Rollout-Route | `/mask-rollout/auswertungen__vertriebstrichter/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/sales/reports/pipeline`

**MCP-Tools (Domäne):**

- `reporting.bonus.calculate` — scope `reporting:write`, Risiko mittel
- `reporting.query.import_signed` — scope `reporting:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Vertriebstrichter.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `auswertungen/warengruppen-analyse` — Warengruppen-Analyse

**Zweck:** Warengruppen-Analyse als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/auswertungen/warengruppen-analyse/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/auswertungen/warengruppen-analyse/agent-contract` |
| Readiness | `GET /api/v1/masks/auswertungen/warengruppen-analyse/readiness` |
| Rollout-Route | `/mask-rollout/auswertungen__warengruppen-analyse/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/einkauf/warengruppen`

**MCP-Tools (Domäne):**

- `reporting.bonus.calculate` — scope `reporting:write`, Risiko mittel
- `reporting.query.import_signed` — scope `reporting:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige Warengruppen-Analyse.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

## Domäne: reports

### `reports/ReportsDashboardCharts` — ReportsDashboardCharts

**Zweck:** ReportsDashboardCharts mandantensicher als Cockpit bereitstellen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/reports/ReportsDashboardCharts/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/reports/ReportsDashboardCharts/agent-contract` |
| Readiness | `GET /api/v1/masks/reports/ReportsDashboardCharts/readiness` |
| Rollout-Route | `/mask-rollout/reports__ReportsDashboardCharts/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/reports/customer-analytics`

**Beispiel-Prompts:**

- Zeige ReportsDashboardCharts.
- Aktualisiere die Kennzahlen.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `reports/deckungsbeitrag` — Deckungsbeitrag

**Zweck:** Deckungsbeitrag im reports-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/reports/deckungsbeitrag/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/reports/deckungsbeitrag/agent-contract` |
| Readiness | `GET /api/v1/masks/reports/deckungsbeitrag/readiness` |
| Rollout-Route | `/mask-rollout/reports__deckungsbeitrag/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/reports/customer-analytics`

**Beispiel-Prompts:**

- Zeige Deckungsbeitrag.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `reports/lagerbestand` — Lagerbestand

**Zweck:** Lagerbestand im reports-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/reports/lagerbestand/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/reports/lagerbestand/agent-contract` |
| Readiness | `GET /api/v1/masks/reports/lagerbestand/readiness` |
| Rollout-Route | `/mask-rollout/reports__lagerbestand/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/reports/customer-analytics`

**Beispiel-Prompts:**

- Zeige Lagerbestand.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `reports/umsatz` — Umsatz

**Zweck:** Umsatz im reports-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/reports/umsatz/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/reports/umsatz/agent-contract` |
| Readiness | `GET /api/v1/masks/reports/umsatz/readiness` |
| Rollout-Route | `/mask-rollout/reports__umsatz/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/reports/customer-analytics`

**Beispiel-Prompts:**

- Zeige Umsatz.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

## Domäne: rezepte

### `rezepte/editor` — Grunddaten

**Zweck:** Grunddaten im rezepte-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/rezepte/editor/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/rezepte/editor/agent-contract` |
| Readiness | `GET /api/v1/masks/rezepte/editor/readiness` |
| Rollout-Route | `/mask-rollout/rezepte__editor/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/fibu/kreditoren`

**Beispiel-Prompts:**

- Zeige Grunddaten.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

## Domäne: sales

### `dashboard/sales-dashboard` — Verkaufs-Dashboard

**Zweck:** Verkaufs-Dashboard als Read-Model-Cockpit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/dashboard/sales-dashboard/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/dashboard/sales-dashboard/agent-contract` |
| Readiness | `GET /api/v1/masks/dashboard/sales-dashboard/readiness` |
| Rollout-Route | `/mask-rollout/dashboard__sales-dashboard/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/sales/reports/summary`

**MCP-Tools (Domäne):**

- `sales.order.status` — scope `sales:read`, Risiko niedrig
- `sales.gutschrift.speichern` — scope `sales:write`, Risiko mittel
- `sales.gutschrift.propose` — scope `sales:write`, Risiko hoch
- `sales.gutschrift.buchen` — scope `sales:write`, Risiko hoch
- `sales.invoice.propose` — scope `sales:write`, Risiko hoch
- `sales.invoice.post` — scope `sales:write`, Risiko hoch

**Beispiel-Prompts:**

- Zeige Verkaufs-Dashboard.
- Was ist der aktuelle Stand?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `dashboard/verkauf` — Verkaufs-Dashboard

**Zweck:** Vertriebs-KPIs mit Sprung in Auftrags- und Rechnungsmasken.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/dashboard/verkauf/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/dashboard/verkauf/agent-contract` |
| Readiness | `GET /api/v1/masks/dashboard/verkauf/readiness` |
| Rollout-Route | `/mask-rollout/dashboard__verkauf/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/sales/reports/summary`

**MCP-Tools (Domäne):**

- `sales.order.status` — scope `sales:read`, Risiko niedrig
- `sales.gutschrift.speichern` — scope `sales:write`, Risiko mittel
- `sales.gutschrift.propose` — scope `sales:write`, Risiko hoch
- `sales.gutschrift.buchen` — scope `sales:write`, Risiko hoch
- `sales.invoice.propose` — scope `sales:write`, Risiko hoch
- `sales.invoice.post` — scope `sales:write`, Risiko hoch

**Beispiel-Prompts:**

- Wie ist der Umsatz im Zeitraum?
- Zeige Top-Kunden.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `sales/angebote-liste` — Verkaufsangebote

**Zweck:** Verkaufsangebote nach Kunde und Status verfolgen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/sales/angebote-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/sales/angebote-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/sales/angebote-liste/readiness` |
| Rollout-Route | `/mask-rollout/sales__angebote-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/sales/offers/`

**MCP-Tools (Domäne):**

- `sales.order.status` — scope `sales:read`, Risiko niedrig
- `sales.gutschrift.speichern` — scope `sales:write`, Risiko mittel
- `sales.gutschrift.propose` — scope `sales:write`, Risiko hoch
- `sales.gutschrift.buchen` — scope `sales:write`, Risiko hoch
- `sales.invoice.propose` — scope `sales:write`, Risiko hoch
- `sales.invoice.post` — scope `sales:write`, Risiko hoch

**Beispiel-Prompts:**

- Welche Angebote laufen diese Woche ab?
- Welche Angebote sind offen?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `neu` | Neues Angebot | safe | nein | `Oeffnet die Anlage; Rechte prueft deren Anlageweg.` |
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `sales/angebote/neu` — Angebot erstellen

**Zweck:** Angebot erstellen im sales-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/sales/angebote/neu/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/sales/angebote/neu/agent-contract` |
| Readiness | `GET /api/v1/masks/sales/angebote/neu/readiness` |
| Rollout-Route | `/mask-rollout/sales__angebote__neu/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/sales/offers/`

**MCP-Tools (Domäne):**

- `sales.order.status` — scope `sales:read`, Risiko niedrig
- `sales.gutschrift.speichern` — scope `sales:write`, Risiko mittel
- `sales.gutschrift.propose` — scope `sales:write`, Risiko hoch
- `sales.gutschrift.buchen` — scope `sales:write`, Risiko hoch
- `sales.invoice.propose` — scope `sales:write`, Risiko hoch
- `sales.invoice.post` — scope `sales:write`, Risiko hoch

**Beispiel-Prompts:**

- Zeige Angebot erstellen.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `sales/auftraege-liste` — Verkaufsauftraege

**Zweck:** Verkaufsauftraege nach Kunde und Lieferstatus steuern.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/sales/auftraege-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/sales/auftraege-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/sales/auftraege-liste/readiness` |
| Rollout-Route | `/mask-rollout/sales__auftraege-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/sales/orders/`

**MCP-Tools (Domäne):**

- `sales.order.status` — scope `sales:read`, Risiko niedrig
- `sales.gutschrift.speichern` — scope `sales:write`, Risiko mittel
- `sales.gutschrift.propose` — scope `sales:write`, Risiko hoch
- `sales.gutschrift.buchen` — scope `sales:write`, Risiko hoch
- `sales.invoice.propose` — scope `sales:write`, Risiko hoch
- `sales.invoice.post` — scope `sales:write`, Risiko hoch

**Beispiel-Prompts:**

- Welche Auftraege sind noch offen?
- Welche Auftraege warten auf Lieferung?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `neu` | Neuer Auftrag | safe | nein | `Oeffnet die Anlage; Rechte prueft deren Anlageweg.` |
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `sales/auftrag-lieferschein-abgleich` — Auftrag lieferschein abgleich

**Zweck:** Auftrag lieferschein abgleich im sales-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/sales/auftrag-lieferschein-abgleich/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/sales/auftrag-lieferschein-abgleich/agent-contract` |
| Readiness | `GET /api/v1/masks/sales/auftrag-lieferschein-abgleich/readiness` |
| Rollout-Route | `/mask-rollout/sales__auftrag-lieferschein-abgleich/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/sales/blanket-orders`

**MCP-Tools (Domäne):**

- `sales.order.status` — scope `sales:read`, Risiko niedrig
- `sales.gutschrift.speichern` — scope `sales:write`, Risiko mittel
- `sales.gutschrift.propose` — scope `sales:write`, Risiko hoch
- `sales.gutschrift.buchen` — scope `sales:write`, Risiko hoch
- `sales.invoice.propose` — scope `sales:write`, Risiko hoch
- `sales.invoice.post` — scope `sales:write`, Risiko hoch

**Beispiel-Prompts:**

- Zeige Auftrag lieferschein abgleich.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `sales/auftragskette` — Auftragskette

**Zweck:** Auftragskette im sales-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/sales/auftragskette/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/sales/auftragskette/agent-contract` |
| Readiness | `GET /api/v1/masks/sales/auftragskette/readiness` |
| Rollout-Route | `/mask-rollout/sales__auftragskette/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/sales/blanket-orders`

**MCP-Tools (Domäne):**

- `sales.order.status` — scope `sales:read`, Risiko niedrig
- `sales.gutschrift.speichern` — scope `sales:write`, Risiko mittel
- `sales.gutschrift.propose` — scope `sales:write`, Risiko hoch
- `sales.gutschrift.buchen` — scope `sales:write`, Risiko hoch
- `sales.invoice.propose` — scope `sales:write`, Risiko hoch
- `sales.invoice.post` — scope `sales:write`, Risiko hoch

**Beispiel-Prompts:**

- Zeige Auftragskette.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `sales/credit-notes` — Credit note editor

**Zweck:** Credit note editor im sales-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/sales/credit-notes/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/sales/credit-notes/agent-contract` |
| Readiness | `GET /api/v1/masks/sales/credit-notes/readiness` |
| Rollout-Route | `/mask-rollout/sales__credit-notes/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/sales/blanket-orders`

**MCP-Tools (Domäne):**

- `sales.order.status` — scope `sales:read`, Risiko niedrig
- `sales.gutschrift.speichern` — scope `sales:write`, Risiko mittel
- `sales.gutschrift.propose` — scope `sales:write`, Risiko hoch
- `sales.gutschrift.buchen` — scope `sales:write`, Risiko hoch
- `sales.invoice.propose` — scope `sales:write`, Risiko hoch
- `sales.invoice.post` — scope `sales:write`, Risiko hoch

**Beispiel-Prompts:**

- Zeige Credit note editor.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `sales/delivery-editor` — Delivery editor

**Zweck:** Delivery editor als Stammblatt pflegen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/sales/delivery-editor/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/sales/delivery-editor/agent-contract` |
| Readiness | `GET /api/v1/masks/sales/delivery-editor/readiness` |
| Rollout-Route | `/mask-rollout/sales__delivery-editor/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/sales/blanket-orders/{entity_id}`

**MCP-Tools (Domäne):**

- `sales.order.status` — scope `sales:read`, Risiko niedrig
- `sales.gutschrift.speichern` — scope `sales:write`, Risiko mittel
- `sales.gutschrift.propose` — scope `sales:write`, Risiko hoch
- `sales.gutschrift.buchen` — scope `sales:write`, Risiko hoch
- `sales.invoice.propose` — scope `sales:write`, Risiko hoch
- `sales.invoice.post` — scope `sales:write`, Risiko hoch

**Beispiel-Prompts:**

- Oeffne Delivery editor.
- Bearbeite Stammdaten.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `sales/delivery-editor-new` — Delivery editor new

**Zweck:** Delivery editor new als Stammblatt pflegen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/sales/delivery-editor-new/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/sales/delivery-editor-new/agent-contract` |
| Readiness | `GET /api/v1/masks/sales/delivery-editor-new/readiness` |
| Rollout-Route | `/mask-rollout/sales__delivery-editor-new/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/sales/blanket-orders/{entity_id}`

**MCP-Tools (Domäne):**

- `sales.order.status` — scope `sales:read`, Risiko niedrig
- `sales.gutschrift.speichern` — scope `sales:write`, Risiko mittel
- `sales.gutschrift.propose` — scope `sales:write`, Risiko hoch
- `sales.gutschrift.buchen` — scope `sales:write`, Risiko hoch
- `sales.invoice.propose` — scope `sales:write`, Risiko hoch
- `sales.invoice.post` — scope `sales:write`, Risiko hoch

**Beispiel-Prompts:**

- Oeffne Delivery editor new.
- Bearbeite Stammdaten.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `sales/delivery-note` — Lieferschein

**Zweck:** Warenbeleg: Kunde, Auftrag, Artikel, Menge und Charge. Fahrzeug und Beförderung stehen am Frachtbrief.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/sales/delivery-note/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/sales/delivery-note/agent-contract` |
| Readiness | `GET /api/v1/masks/sales/delivery-note/readiness` |
| Rollout-Route | `/mask-rollout/sales__delivery-note/:entityId` |
| Adapter | `native` (temporary=nein) |

**Summary:** `/api/v1/mask-rollouts/sales/delivery-note/{entity_id}/screen-summary`

**Data Sources:**

- `entity` → `/api/v1/sales/delivery-notes/{entity_id}`
- `positionen` → `/api/v1/mask-rollouts/sales/delivery-note/{entity_id}/tabs/positionen`
- `dokumente` → `/api/v1/mask-rollouts/sales/delivery-note/{entity_id}/tabs/dokumente`

**MCP-Tools (Domäne):**

- `sales.order.status` — scope `sales:read`, Risiko niedrig
- `sales.gutschrift.speichern` — scope `sales:write`, Risiko mittel
- `sales.gutschrift.propose` — scope `sales:write`, Risiko hoch
- `sales.gutschrift.buchen` — scope `sales:write`, Risiko hoch
- `sales.invoice.propose` — scope `sales:write`, Risiko hoch
- `sales.invoice.post` — scope `sales:write`, Risiko hoch

**Beispiel-Prompts:**

- Zeige alle Positionen und Chargen von Lieferschein {entity_id}.
- Welche Dokumente sind mit Lieferschein {entity_id} verknuepft?
- Was ist der aktuelle Status von Lieferschein {entity_id}?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `drucken` | Lieferschein drucken | safe | nein | `/api/v1/sales/delivery-notes/{entity_id}/actions/drucken` |

---

### `sales/gutschrift` — Gutschrift

**Zweck:** Gutschrift an den Kunden (Rechnungskorrektur) erfassen und buchen: Positionen mit Steuerschluessel, Erloes netto, Umsatzsteuer getrennt, Forderung brutto; ohne eindeutige Steuerangabe wird nicht gebucht, sondern der Pruefgrund genannt.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/sales/gutschrift/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/sales/gutschrift/agent-contract` |
| Readiness | `GET /api/v1/masks/sales/gutschrift/readiness` |
| Rollout-Route | `/mask-rollout/sales__gutschrift/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `gutschriften` → `/api/v1/sales/credit-notes`
- `steuerschluessel` → `/api/v1/finance/tax-keys`
- `steuer` → `/api/v1/sales/credit-notes/steuer-vorschau`
- `vorschlaege` → `/api/v1/sales/credit-notes/buchungsvorschlaege`

**MCP-Tools (Domäne):**

- `sales.order.status` — scope `sales:read`, Risiko niedrig
- `sales.gutschrift.speichern` — scope `sales:write`, Risiko mittel
- `sales.gutschrift.propose` — scope `sales:write`, Risiko hoch
- `sales.gutschrift.buchen` — scope `sales:write`, Risiko hoch
- `sales.invoice.propose` — scope `sales:write`, Risiko hoch
- `sales.invoice.post` — scope `sales:write`, Risiko hoch

**Beispiel-Prompts:**

- Lege eine Gutschrift ueber 1.000 EUR netto mit Steuerschluessel 3 zur Rechnung RE-1001 an.
- Warum wurde Gutschrift {entity_id} nicht gebucht?
- Welche Gutschriften sind noch Entwurf?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `position` | Position übernehmen | safe | nein | `Stellt die Positionseingabe in die Positionsliste der Maske; gespeichert wird erst mit Speichern.` |
| `speichern` | Als Entwurf speichern | safe | nein | `/api/v1/sales/credit-notes/actions/speichern` |
| `buchen` | Buchen | moderate | ja | `/api/v1/sales/credit-notes/{entity_id}/actions/buchen` |
| `vorschlag_freigeben` | Vorschlag freigeben | moderate | ja | `/api/v1/sales/credit-notes/buchungsvorschlaege/{entity_id}/actions/freigeben` |
| `vorschlag_ablehnen` | Vorschlag ablehnen | moderate | ja | `/api/v1/sales/credit-notes/buchungsvorschlaege/{entity_id}/actions/ablehnen` |
| `neu` | Neue Gutschrift | safe | nein | `Leert die Eingabe fuer eine neue Gutschrift.` |

---

### `sales/invoice` — Ausgangsrechnung

**Zweck:** Ausgangsrechnung mit Positionen und dem Nachweis, aus welcher Lieferscheinposition welche berechnete Teilmenge stammt.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/sales/invoice/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/sales/invoice/agent-contract` |
| Readiness | `GET /api/v1/masks/sales/invoice/readiness` |
| Rollout-Route | `/mask-rollout/sales__invoice/:entityId` |
| Adapter | `native` (temporary=nein) |

**Summary:** `/api/v1/sales/invoices/{entity_id}/screen-summary`

**Data Sources:**

- `entity` → `/api/v1/sales/invoices/{entity_id}`
- `positionen` → `/api/v1/sales/invoices/{entity_id}/tabs/positionen`
- `herkunft` → `/api/v1/sales/invoices/{entity_id}/tabs/herkunft`
- `steuer` → `/api/v1/sales/invoices/{entity_id}/tabs/steuer`

**MCP-Tools (Domäne):**

- `sales.order.status` — scope `sales:read`, Risiko niedrig
- `sales.gutschrift.speichern` — scope `sales:write`, Risiko mittel
- `sales.gutschrift.propose` — scope `sales:write`, Risiko hoch
- `sales.gutschrift.buchen` — scope `sales:write`, Risiko hoch
- `sales.invoice.propose` — scope `sales:write`, Risiko hoch
- `sales.invoice.post` — scope `sales:write`, Risiko hoch

**Beispiel-Prompts:**

- Woher stammt die berechnete Menge von Position 2 der Rechnung {entity_id}?
- Welche Positionen der Rechnung {entity_id} sind nicht vollstaendig durch Zuordnungen belegt?
- Aus welchen Lieferscheinen ist Rechnung {entity_id} entstanden?

---

### `sales/invoices` — Ausgangsrechnungen

**Zweck:** Ausgangsrechnungen suchen, nach Faelligkeit und Status priorisieren und den Beleg oeffnen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/sales/invoices/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/sales/invoices/agent-contract` |
| Readiness | `GET /api/v1/masks/sales/invoices/readiness` |
| Rollout-Route | `/mask-rollout/sales__invoices/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/sales/invoices`

**MCP-Tools (Domäne):**

- `sales.order.status` — scope `sales:read`, Risiko niedrig
- `sales.gutschrift.speichern` — scope `sales:write`, Risiko mittel
- `sales.gutschrift.propose` — scope `sales:write`, Risiko hoch
- `sales.gutschrift.buchen` — scope `sales:write`, Risiko hoch
- `sales.invoice.propose` — scope `sales:write`, Risiko hoch
- `sales.invoice.post` — scope `sales:write`, Risiko hoch

**Beispiel-Prompts:**

- Welche Rechnungen sind noch im Entwurf?
- Zeige die Rechnungen des Kunden K-100 aus diesem Monat.
- Gibt es Rechnungen ohne Positionen?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | Liste exportieren | safe | nein | `—` |

---

### `sales/kalkulationen/neu` — Kalkulation

**Zweck:** Kalkulation im sales-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/sales/kalkulationen/neu/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/sales/kalkulationen/neu/agent-contract` |
| Readiness | `GET /api/v1/masks/sales/kalkulationen/neu/readiness` |
| Rollout-Route | `/mask-rollout/sales__kalkulationen__neu/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/sales/blanket-orders`

**MCP-Tools (Domäne):**

- `sales.order.status` — scope `sales:read`, Risiko niedrig
- `sales.gutschrift.speichern` — scope `sales:write`, Risiko mittel
- `sales.gutschrift.propose` — scope `sales:write`, Risiko hoch
- `sales.gutschrift.buchen` — scope `sales:write`, Risiko hoch
- `sales.invoice.propose` — scope `sales:write`, Risiko hoch
- `sales.invoice.post` — scope `sales:write`, Risiko hoch

**Beispiel-Prompts:**

- Zeige Kalkulation.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `sales/kreditlimit-pruefung` — Kreditlimit-Pruefung

**Zweck:** Kreditrisiko vor Auftragsfreigabe bewerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/sales/kreditlimit-pruefung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/sales/kreditlimit-pruefung/agent-contract` |
| Readiness | `GET /api/v1/masks/sales/kreditlimit-pruefung/readiness` |
| Rollout-Route | `/mask-rollout/sales__kreditlimit-pruefung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `items` → `/api/v1/sales/credit-check/customers`

**MCP-Tools (Domäne):**

- `sales.order.status` — scope `sales:read`, Risiko niedrig
- `sales.gutschrift.speichern` — scope `sales:write`, Risiko mittel
- `sales.gutschrift.propose` — scope `sales:write`, Risiko hoch
- `sales.gutschrift.buchen` — scope `sales:write`, Risiko hoch
- `sales.invoice.propose` — scope `sales:write`, Risiko hoch
- `sales.invoice.post` — scope `sales:write`, Risiko hoch

**Beispiel-Prompts:**

- Welche Kunden sind blockiert?

---

### `sales/lieferung-storno` — Lieferung storno

**Zweck:** Lieferung storno im sales-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/sales/lieferung-storno/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/sales/lieferung-storno/agent-contract` |
| Readiness | `GET /api/v1/masks/sales/lieferung-storno/readiness` |
| Rollout-Route | `/mask-rollout/sales__lieferung-storno/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/sales/blanket-orders`

**MCP-Tools (Domäne):**

- `sales.order.status` — scope `sales:read`, Risiko niedrig
- `sales.gutschrift.speichern` — scope `sales:write`, Risiko mittel
- `sales.gutschrift.propose` — scope `sales:write`, Risiko hoch
- `sales.gutschrift.buchen` — scope `sales:write`, Risiko hoch
- `sales.invoice.propose` — scope `sales:write`, Risiko hoch
- `sales.invoice.post` — scope `sales:write`, Risiko hoch

**Beispiel-Prompts:**

- Zeige Lieferung storno.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `sales/lieferungen-liste` — Lieferscheine

**Zweck:** Lieferscheine und Versandstatus nachverfolgen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/sales/lieferungen-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/sales/lieferungen-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/sales/lieferungen-liste/readiness` |
| Rollout-Route | `/mask-rollout/sales__lieferungen-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/sales/delivery-notes`

**MCP-Tools (Domäne):**

- `sales.order.status` — scope `sales:read`, Risiko niedrig
- `sales.gutschrift.speichern` — scope `sales:write`, Risiko mittel
- `sales.gutschrift.propose` — scope `sales:write`, Risiko hoch
- `sales.gutschrift.buchen` — scope `sales:write`, Risiko hoch
- `sales.invoice.propose` — scope `sales:write`, Risiko hoch
- `sales.invoice.post` — scope `sales:write`, Risiko hoch

**Beispiel-Prompts:**

- Welche Lieferscheine sind heute offen?
- Welche Lieferungen sind unterwegs?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `neu` | Lieferschein erfassen | safe | nein | `Oeffnet die Anlage; Rechte prueft deren Anlageweg.` |
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `sales/lieferungen/neu` — Lieferungen liste

**Zweck:** Lieferungen liste im sales-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/sales/lieferungen/neu/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/sales/lieferungen/neu/agent-contract` |
| Readiness | `GET /api/v1/masks/sales/lieferungen/neu/readiness` |
| Rollout-Route | `/mask-rollout/sales__lieferungen__neu/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/sales/blanket-orders`

**MCP-Tools (Domäne):**

- `sales.order.status` — scope `sales:read`, Risiko niedrig
- `sales.gutschrift.speichern` — scope `sales:write`, Risiko mittel
- `sales.gutschrift.propose` — scope `sales:write`, Risiko hoch
- `sales.gutschrift.buchen` — scope `sales:write`, Risiko hoch
- `sales.invoice.propose` — scope `sales:write`, Risiko hoch
- `sales.invoice.post` — scope `sales:write`, Risiko hoch

**Beispiel-Prompts:**

- Zeige Lieferungen liste.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `sales/orders-modern` — Orders modern

**Zweck:** Orders modern im sales-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/sales/orders-modern/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/sales/orders-modern/agent-contract` |
| Readiness | `GET /api/v1/masks/sales/orders-modern/readiness` |
| Rollout-Route | `/mask-rollout/sales__orders-modern/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/sales/blanket-orders`

**MCP-Tools (Domäne):**

- `sales.order.status` — scope `sales:read`, Risiko niedrig
- `sales.gutschrift.speichern` — scope `sales:write`, Risiko mittel
- `sales.gutschrift.propose` — scope `sales:write`, Risiko hoch
- `sales.gutschrift.buchen` — scope `sales:write`, Risiko hoch
- `sales.invoice.propose` — scope `sales:write`, Risiko hoch
- `sales.invoice.post` — scope `sales:write`, Risiko hoch

**Beispiel-Prompts:**

- Zeige Orders modern.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `sales/rechnungen-liste` — Rechnungen liste

**Zweck:** Rechnungen liste im sales-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/sales/rechnungen-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/sales/rechnungen-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/sales/rechnungen-liste/readiness` |
| Rollout-Route | `/mask-rollout/sales__rechnungen-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/sales/blanket-orders`

**MCP-Tools (Domäne):**

- `sales.order.status` — scope `sales:read`, Risiko niedrig
- `sales.gutschrift.speichern` — scope `sales:write`, Risiko mittel
- `sales.gutschrift.propose` — scope `sales:write`, Risiko hoch
- `sales.gutschrift.buchen` — scope `sales:write`, Risiko hoch
- `sales.invoice.propose` — scope `sales:write`, Risiko hoch
- `sales.invoice.post` — scope `sales:write`, Risiko hoch

**Beispiel-Prompts:**

- Zeige Rechnungen liste.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `sales/sales-order` — Verkaufsauftrag

**Zweck:** Verkaufsauftrag-Cockpit: Kopfdaten, Positionen, Lieferscheine und Dokumente fuer Auftragsabwicklung und Kundenkommunikation.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/sales/sales-order/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/sales/sales-order/agent-contract` |
| Readiness | `GET /api/v1/masks/sales/sales-order/readiness` |
| Rollout-Route | `/mask-rollout/sales__sales-order/:entityId` |
| Adapter | `native` (temporary=nein) |

**Summary:** `/api/v1/sales/orders/{order_id}/screen-summary`

**Data Sources:**

- `entity` → `/api/v1/sales/orders/{entity_id}`
- `positionen` → `/api/v1/sales/orders/{entity_id}/tabs/positionen`
- `lieferung` → `/api/v1/sales/orders/{entity_id}/tabs/lieferung`
- `dokumente` → `/api/v1/sales/orders/{entity_id}/tabs/dokumente`

**MCP-Tools (Domäne):**

- `sales.order.status` — scope `sales:read`, Risiko niedrig
- `sales.gutschrift.speichern` — scope `sales:write`, Risiko mittel
- `sales.gutschrift.propose` — scope `sales:write`, Risiko hoch
- `sales.gutschrift.buchen` — scope `sales:write`, Risiko hoch
- `sales.invoice.propose` — scope `sales:write`, Risiko hoch
- `sales.invoice.post` — scope `sales:write`, Risiko hoch

**Beispiel-Prompts:**

- Was ist der Status von Auftrag {entity_id} und welche Positionen sind noch offen?
- Welche Lieferscheine wurden fuer Auftrag {entity_id} erstellt?
- Zeige alle Dokumente von Auftrag {entity_id}.

**Sensible Felder:** `einzelpreis, betrag`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bearbeiten` | Bearbeiten | safe | nein | `/api/v1/sales/orders/{entity_id}/actions/bearbeiten` |

---

### `verkauf/betriebsauftrag` — Betriebsauftrag drucken

**Zweck:** Betriebsauftraege zum Drucken aus den Verkaufsauftraegen heraussuchen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/verkauf/betriebsauftrag/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/verkauf/betriebsauftrag/agent-contract` |
| Readiness | `GET /api/v1/masks/verkauf/betriebsauftrag/readiness` |
| Rollout-Route | `/mask-rollout/verkauf__betriebsauftrag/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/sales/orders/`

**MCP-Tools (Domäne):**

- `sales.order.status` — scope `sales:read`, Risiko niedrig
- `sales.gutschrift.speichern` — scope `sales:write`, Risiko mittel
- `sales.gutschrift.propose` — scope `sales:write`, Risiko hoch
- `sales.gutschrift.buchen` — scope `sales:write`, Risiko hoch
- `sales.invoice.propose` — scope `sales:write`, Risiko hoch
- `sales.invoice.post` — scope `sales:write`, Risiko hoch

**Beispiel-Prompts:**

- Welche Auftraege haben ein Lieferdatum?

---

### `workspace/verkauf` — Verkauf-Cockpit

**Zweck:** Rollen-Startseite Verkauf — Auftragsbestand und Kreditlimit-Warnungen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/workspace/verkauf/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/workspace/verkauf/agent-contract` |
| Readiness | `GET /api/v1/masks/workspace/verkauf/readiness` |
| Rollout-Route | `/mask-rollout/workspace__verkauf/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/sales/reports/summary`

**MCP-Tools (Domäne):**

- `sales.order.status` — scope `sales:read`, Risiko niedrig
- `sales.gutschrift.speichern` — scope `sales:write`, Risiko mittel
- `sales.gutschrift.propose` — scope `sales:write`, Risiko hoch
- `sales.gutschrift.buchen` — scope `sales:write`, Risiko hoch
- `sales.invoice.propose` — scope `sales:write`, Risiko hoch
- `sales.invoice.post` — scope `sales:write`, Risiko hoch

**Beispiel-Prompts:**

- Welche Auftraege sind ueberfaellig?
- Zeige Kreditlimit-Warnungen.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

## Domäne: schaeden

### `schaeden/meldung` — Meldung

**Zweck:** Meldung im schaeden-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/schaeden/meldung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/schaeden/meldung/agent-contract` |
| Readiness | `GET /api/v1/masks/schaeden/meldung/readiness` |
| Rollout-Route | `/mask-rollout/schaeden__meldung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/schaeden/meldungen`

**Beispiel-Prompts:**

- Zeige Meldung.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

## Domäne: service

### `service/abschluss` — Abschluss

**Zweck:** Abschluss im service-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/service/abschluss/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/service/abschluss/agent-contract` |
| Readiness | `GET /api/v1/masks/service/abschluss/readiness` |
| Rollout-Route | `/mask-rollout/service__abschluss/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/service/anfragen`

**Beispiel-Prompts:**

- Zeige Abschluss.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `service/anfrage` — Serviceanfrage

**Zweck:** Serviceanfrage bearbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/service/anfrage/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/service/anfrage/agent-contract` |
| Readiness | `GET /api/v1/masks/service/anfrage/readiness` |
| Rollout-Route | `/mask-rollout/service__anfrage/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/service/anfragen/{entity_id}`

**Beispiel-Prompts:**

- Welche Prioritaet hat Anfrage {entity_id}?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `service/anfrage-detail` — Anfrage detail

**Zweck:** Anfrage detail als Stammblatt pflegen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/service/anfrage-detail/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/service/anfrage-detail/agent-contract` |
| Readiness | `GET /api/v1/masks/service/anfrage-detail/readiness` |
| Rollout-Route | `/mask-rollout/service__anfrage-detail/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/service/anfragen/{entity_id}`

**Beispiel-Prompts:**

- Oeffne Anfrage detail.
- Bearbeite Stammdaten.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `service/anfrage/neu` — Anfrage erstellt

**Zweck:** Anfrage erstellt als Stammblatt pflegen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/service/anfrage/neu/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/service/anfrage/neu/agent-contract` |
| Readiness | `GET /api/v1/masks/service/anfrage/neu/readiness` |
| Rollout-Route | `/mask-rollout/service__anfrage__neu/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/service/anfragen/{entity_id}`

**Beispiel-Prompts:**

- Oeffne Anfrage erstellt.
- Bearbeite Stammdaten.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `service/anfragen` — Anfragen

**Zweck:** Anfragen im service-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/service/anfragen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/service/anfragen/agent-contract` |
| Readiness | `GET /api/v1/masks/service/anfragen/readiness` |
| Rollout-Route | `/mask-rollout/service__anfragen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/service/anfragen`

**Beispiel-Prompts:**

- Zeige Anfragen.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `service/anfragen-liste` — Serviceanfragen

**Zweck:** Service-Tickets nach Prioritaet und Status abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/service/anfragen-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/service/anfragen-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/service/anfragen-liste/readiness` |
| Rollout-Route | `/mask-rollout/service__anfragen-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/service/anfragen`

**Beispiel-Prompts:**

- Welche Tickets sind hoch priorisiert?
- Was ist heute neu eingegangen?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `neu` | Neue Anfrage | safe | nein | `Oeffnet die Anlage; Rechte prueft deren Anlageweg.` |
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `service/rueckmeldung` — Rueckmeldung

**Zweck:** Rueckmeldung im service-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/service/rueckmeldung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/service/rueckmeldung/agent-contract` |
| Readiness | `GET /api/v1/masks/service/rueckmeldung/readiness` |
| Rollout-Route | `/mask-rollout/service__rueckmeldung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/service/anfragen`

**Beispiel-Prompts:**

- Zeige Rueckmeldung.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

## Domäne: setup

### `setup/firma` — Firma

**Zweck:** Firma im setup-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/setup/firma/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/setup/firma/agent-contract` |
| Readiness | `GET /api/v1/masks/setup/firma/readiness` |
| Rollout-Route | `/mask-rollout/setup__firma/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/setup/firma`

**Beispiel-Prompts:**

- Zeige Firma.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

## Domäne: silo

### `silo/kapazitaeten` — Silos Gesamt

**Zweck:** Silos Gesamt im silo-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/silo/kapazitaeten/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/silo/kapazitaeten/agent-contract` |
| Readiness | `GET /api/v1/masks/silo/kapazitaeten/readiness` |
| Rollout-Route | `/mask-rollout/silo__kapazitaeten/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/silo/kapazitaeten`

**Beispiel-Prompts:**

- Zeige Silos Gesamt.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

## Domäne: stammdaten

### `stammdaten/artikel-stoffstrom` — Stoffstrom-Datensätze

**Zweck:** Stoffstrom-Datensätze als Stammblatt pflegen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/stammdaten/artikel-stoffstrom/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/stammdaten/artikel-stoffstrom/agent-contract` |
| Readiness | `GET /api/v1/masks/stammdaten/artikel-stoffstrom/readiness` |
| Rollout-Route | `/mask-rollout/stammdaten__artikel-stoffstrom/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/stammdaten/betriebsstaetten/{entity_id}`

**Beispiel-Prompts:**

- Oeffne Stoffstrom-Datensätze.
- Bearbeite Stammdaten.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `stammdaten/artikelbestandteile` — Neuen Bestandteil anlegen

**Zweck:** Neuen Bestandteil anlegen als Stammblatt pflegen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/stammdaten/artikelbestandteile/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/stammdaten/artikelbestandteile/agent-contract` |
| Readiness | `GET /api/v1/masks/stammdaten/artikelbestandteile/readiness` |
| Rollout-Route | `/mask-rollout/stammdaten__artikelbestandteile/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/stammdaten/betriebsstaetten/{entity_id}`

**Beispiel-Prompts:**

- Oeffne Neuen Bestandteil anlegen.
- Bearbeite Stammdaten.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `stammdaten/artikelverpackung` — Neue Verpackung anlegen

**Zweck:** Neue Verpackung anlegen als Stammblatt pflegen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/stammdaten/artikelverpackung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/stammdaten/artikelverpackung/agent-contract` |
| Readiness | `GET /api/v1/masks/stammdaten/artikelverpackung/readiness` |
| Rollout-Route | `/mask-rollout/stammdaten__artikelverpackung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/stammdaten/betriebsstaetten/{entity_id}`

**Beispiel-Prompts:**

- Oeffne Neue Verpackung anlegen.
- Bearbeite Stammdaten.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `stammdaten/betriebsstaetten` — Neue Betriebsstätte

**Zweck:** Neue Betriebsstätte als Stammblatt pflegen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/stammdaten/betriebsstaetten/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/stammdaten/betriebsstaetten/agent-contract` |
| Readiness | `GET /api/v1/masks/stammdaten/betriebsstaetten/readiness` |
| Rollout-Route | `/mask-rollout/stammdaten__betriebsstaetten/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/stammdaten/betriebsstaetten/{entity_id}`

**Beispiel-Prompts:**

- Oeffne Neue Betriebsstätte.
- Bearbeite Stammdaten.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `stammdaten/hausbanken` — Neue Hausbank anlegen

**Zweck:** Neue Hausbank anlegen als Stammblatt pflegen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/stammdaten/hausbanken/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/stammdaten/hausbanken/agent-contract` |
| Readiness | `GET /api/v1/masks/stammdaten/hausbanken/readiness` |
| Rollout-Route | `/mask-rollout/stammdaten__hausbanken/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/stammdaten/betriebsstaetten/{entity_id}`

**Beispiel-Prompts:**

- Oeffne Neue Hausbank anlegen.
- Bearbeite Stammdaten.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `stammdaten/individuelle-artikelnummern` — Neue Zuordnung anlegen

**Zweck:** Neue Zuordnung anlegen als Stammblatt pflegen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/stammdaten/individuelle-artikelnummern/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/stammdaten/individuelle-artikelnummern/agent-contract` |
| Readiness | `GET /api/v1/masks/stammdaten/individuelle-artikelnummern/readiness` |
| Rollout-Route | `/mask-rollout/stammdaten__individuelle-artikelnummern/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/stammdaten/betriebsstaetten/{entity_id}`

**Beispiel-Prompts:**

- Oeffne Neue Zuordnung anlegen.
- Bearbeite Stammdaten.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `stammdaten/mengeneinheiten` — Neue Mengeneinheit

**Zweck:** Neue Mengeneinheit als Stammblatt pflegen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/stammdaten/mengeneinheiten/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/stammdaten/mengeneinheiten/agent-contract` |
| Readiness | `GET /api/v1/masks/stammdaten/mengeneinheiten/readiness` |
| Rollout-Route | `/mask-rollout/stammdaten__mengeneinheiten/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/stammdaten/betriebsstaetten/{entity_id}`

**Beispiel-Prompts:**

- Oeffne Neue Mengeneinheit.
- Bearbeite Stammdaten.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

## Domäne: strecke

### `strecke/menu` — Menu

**Zweck:** Menu im strecke-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/strecke/menu/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/strecke/menu/agent-contract` |
| Readiness | `GET /api/v1/masks/strecke/menu/readiness` |
| Rollout-Route | `/mask-rollout/strecke__menu/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/strecke/speditionen/frachttarife`

**Beispiel-Prompts:**

- Zeige Menu.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `strecke/nawaro-uebersicht` — Nawaro uebersicht

**Zweck:** Nawaro uebersicht mandantensicher als Cockpit bereitstellen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/strecke/nawaro-uebersicht/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/strecke/nawaro-uebersicht/agent-contract` |
| Readiness | `GET /api/v1/masks/strecke/nawaro-uebersicht/readiness` |
| Rollout-Route | `/mask-rollout/strecke__nawaro-uebersicht/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/strecke/speditionen/frachttarife`

**Beispiel-Prompts:**

- Zeige Nawaro uebersicht.
- Aktualisiere die Kennzahlen.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `strecke/nawaro-uebersicht-drucken` — Nawaro uebersicht drucken

**Zweck:** Nawaro uebersicht drucken mandantensicher als Cockpit bereitstellen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/strecke/nawaro-uebersicht-drucken/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/strecke/nawaro-uebersicht-drucken/agent-contract` |
| Readiness | `GET /api/v1/masks/strecke/nawaro-uebersicht-drucken/readiness` |
| Rollout-Route | `/mask-rollout/strecke__nawaro-uebersicht-drucken/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/strecke/speditionen/frachttarife`

**Beispiel-Prompts:**

- Zeige Nawaro uebersicht drucken.
- Aktualisiere die Kennzahlen.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `strecke/speditionen-fracht-preise` — Speditionen fracht preise

**Zweck:** Speditionen fracht preise im strecke-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/strecke/speditionen-fracht-preise/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/strecke/speditionen-fracht-preise/agent-contract` |
| Readiness | `GET /api/v1/masks/strecke/speditionen-fracht-preise/readiness` |
| Rollout-Route | `/mask-rollout/strecke__speditionen-fracht-preise/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/strecke/speditionen/frachttarife`

**Beispiel-Prompts:**

- Zeige Speditionen fracht preise.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `strecke/vorlaeufige-streckengeschaefte` — Vorlaeufige streckengeschaefte

**Zweck:** Vorlaeufige streckengeschaefte im strecke-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/strecke/vorlaeufige-streckengeschaefte/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/strecke/vorlaeufige-streckengeschaefte/agent-contract` |
| Readiness | `GET /api/v1/masks/strecke/vorlaeufige-streckengeschaefte/readiness` |
| Rollout-Route | `/mask-rollout/strecke__vorlaeufige-streckengeschaefte/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/strecke/speditionen/frachttarife`

**Beispiel-Prompts:**

- Zeige Vorlaeufige streckengeschaefte.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

## Domäne: system

### `system/live-monitor` — Live monitor

**Zweck:** Live monitor im system-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/system/live-monitor/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/system/live-monitor/agent-contract` |
| Readiness | `GET /api/v1/masks/system/live-monitor/readiness` |
| Rollout-Route | `/mask-rollout/system__live-monitor/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/system/business`

**Beispiel-Prompts:**

- Zeige Live monitor.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

## Domäne: tankstelle

### `tankstelle/zapfungen` — Zapfungen

**Zweck:** Zapfungen im tankstelle-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/tankstelle/zapfungen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/tankstelle/zapfungen/agent-contract` |
| Readiness | `GET /api/v1/masks/tankstelle/zapfungen/readiness` |
| Rollout-Route | `/mask-rollout/tankstelle__zapfungen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/tankstelle/bestand`

**Beispiel-Prompts:**

- Zeige Zapfungen.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

## Domäne: transporte

### `transporte/fahrer/neu` — Fahrer liste

**Zweck:** Fahrer liste im transporte-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/transporte/fahrer/neu/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/transporte/fahrer/neu/agent-contract` |
| Readiness | `GET /api/v1/masks/transporte/fahrer/neu/readiness` |
| Rollout-Route | `/mask-rollout/transporte__fahrer__neu/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/transporte/fahrer`

**Beispiel-Prompts:**

- Zeige Fahrer liste.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

## Domäne: verkauf

### `verkauf/auftraege` — Auftraege liste

**Zweck:** Auftraege liste im verkauf-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/verkauf/auftraege/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/verkauf/auftraege/agent-contract` |
| Readiness | `GET /api/v1/masks/verkauf/auftraege/readiness` |
| Rollout-Route | `/mask-rollout/verkauf__auftraege/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/verkauf/kunden`

**Beispiel-Prompts:**

- Zeige Auftraege liste.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `verkauf/auftraege/neu` — Order editor

**Zweck:** Order editor als Stammblatt pflegen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/verkauf/auftraege/neu/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/verkauf/auftraege/neu/agent-contract` |
| Readiness | `GET /api/v1/masks/verkauf/auftraege/neu/readiness` |
| Rollout-Route | `/mask-rollout/verkauf__auftraege__neu/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/verkauf/kunden/{entity_id}`

**Beispiel-Prompts:**

- Oeffne Order editor.
- Bearbeite Stammdaten.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `verkauf/betriebs-auftraege` — Betriebs auftraege

**Zweck:** Betriebs auftraege im verkauf-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/verkauf/betriebs-auftraege/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/verkauf/betriebs-auftraege/agent-contract` |
| Readiness | `GET /api/v1/masks/verkauf/betriebs-auftraege/readiness` |
| Rollout-Route | `/mask-rollout/verkauf__betriebs-auftraege/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/verkauf/kunden`

**Beispiel-Prompts:**

- Zeige Betriebs auftraege.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `verkauf/dauerauftraege` — Neuen Dauerauftrag anlegen

**Zweck:** Neuen Dauerauftrag anlegen als Stammblatt pflegen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/verkauf/dauerauftraege/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/verkauf/dauerauftraege/agent-contract` |
| Readiness | `GET /api/v1/masks/verkauf/dauerauftraege/readiness` |
| Rollout-Route | `/mask-rollout/verkauf__dauerauftraege/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/verkauf/kunden/{entity_id}`

**Beispiel-Prompts:**

- Oeffne Neuen Dauerauftrag anlegen.
- Bearbeite Stammdaten.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `verkauf/kommissions-auftraege` — Kommissions auftraege

**Zweck:** Kommissions auftraege im verkauf-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/verkauf/kommissions-auftraege/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/verkauf/kommissions-auftraege/agent-contract` |
| Readiness | `GET /api/v1/masks/verkauf/kommissions-auftraege/readiness` |
| Rollout-Route | `/mask-rollout/verkauf__kommissions-auftraege/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/verkauf/kunden`

**Beispiel-Prompts:**

- Zeige Kommissions auftraege.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `verkauf/kunde` — Kunde

**Zweck:** Kundenstamm Verkauf.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/verkauf/kunde/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/verkauf/kunde/agent-contract` |
| Readiness | `GET /api/v1/masks/verkauf/kunde/readiness` |
| Rollout-Route | `/mask-rollout/verkauf__kunde/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/crm/customers/{entity_id}`

**Beispiel-Prompts:**

- Wo sitzt Kunde {entity_id}?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `verkauf/kunde-neu` — Kunde neu

**Zweck:** Kunde neu als Stammblatt pflegen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/verkauf/kunde-neu/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/verkauf/kunde-neu/agent-contract` |
| Readiness | `GET /api/v1/masks/verkauf/kunde-neu/readiness` |
| Rollout-Route | `/mask-rollout/verkauf__kunde-neu/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/verkauf/kunden/{entity_id}`

**Beispiel-Prompts:**

- Oeffne Kunde neu.
- Bearbeite Stammdaten.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `verkauf/kunden-liste` — Kunden liste

**Zweck:** Kunden liste im verkauf-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/verkauf/kunden-liste/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/verkauf/kunden-liste/agent-contract` |
| Readiness | `GET /api/v1/masks/verkauf/kunden-liste/readiness` |
| Rollout-Route | `/mask-rollout/verkauf__kunden-liste/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/crm/customers/lookup`

**Beispiel-Prompts:**

- Zeige Kunden liste.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `verkauf/kunden-stamm` — Vorlage übernommen

**Zweck:** Vorlage übernommen als Stammblatt pflegen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/verkauf/kunden-stamm/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/verkauf/kunden-stamm/agent-contract` |
| Readiness | `GET /api/v1/masks/verkauf/kunden-stamm/readiness` |
| Rollout-Route | `/mask-rollout/verkauf__kunden-stamm/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/verkauf/kunden/{entity_id}`

**Beispiel-Prompts:**

- Oeffne Vorlage übernommen.
- Bearbeite Stammdaten.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `verkauf/kunden-stamm-enhanced` — Kunden stamm enhanced

**Zweck:** Kunden stamm enhanced als Stammblatt pflegen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/verkauf/kunden-stamm-enhanced/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/verkauf/kunden-stamm-enhanced/agent-contract` |
| Readiness | `GET /api/v1/masks/verkauf/kunden-stamm-enhanced/readiness` |
| Rollout-Route | `/mask-rollout/verkauf__kunden-stamm-enhanced/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/verkauf/kunden/{entity_id}`

**Beispiel-Prompts:**

- Oeffne Kunden stamm enhanced.
- Bearbeite Stammdaten.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `verkauf/lieferschein-erfassung` — Lieferschein erfassung

**Zweck:** Lieferschein erfassung im verkauf-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/verkauf/lieferschein-erfassung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/verkauf/lieferschein-erfassung/agent-contract` |
| Readiness | `GET /api/v1/masks/verkauf/lieferschein-erfassung/readiness` |
| Rollout-Route | `/mask-rollout/verkauf__lieferschein-erfassung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/admin/branches`

**Beispiel-Prompts:**

- Zeige Lieferschein erfassung.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `verkauf/rechnungen` — Rechnungen worklist

**Zweck:** Rechnungen worklist im verkauf-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/verkauf/rechnungen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/verkauf/rechnungen/agent-contract` |
| Readiness | `GET /api/v1/masks/verkauf/rechnungen/readiness` |
| Rollout-Route | `/mask-rollout/verkauf__rechnungen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/verkauf/kunden`

**Beispiel-Prompts:**

- Zeige Rechnungen worklist.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `verkauf/rechnungen/neu` — Invoice editor

**Zweck:** Invoice editor als Stammblatt pflegen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/verkauf/rechnungen/neu/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/verkauf/rechnungen/neu/agent-contract` |
| Readiness | `GET /api/v1/masks/verkauf/rechnungen/neu/readiness` |
| Rollout-Route | `/mask-rollout/verkauf__rechnungen__neu/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/verkauf/kunden/{entity_id}`

**Beispiel-Prompts:**

- Oeffne Invoice editor.
- Bearbeite Stammdaten.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `verkauf/unerledigte-auftrags-positionen` — Unerledigte auftrags positionen

**Zweck:** Unerledigte auftrags positionen im verkauf-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/verkauf/unerledigte-auftrags-positionen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/verkauf/unerledigte-auftrags-positionen/agent-contract` |
| Readiness | `GET /api/v1/masks/verkauf/unerledigte-auftrags-positionen/readiness` |
| Rollout-Route | `/mask-rollout/verkauf__unerledigte-auftrags-positionen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/verkauf/kunden`

**Beispiel-Prompts:**

- Zeige Unerledigte auftrags positionen.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

## Domäne: verladung

### `verladung/lkw-beladung` — Lkw beladung

**Zweck:** Lkw beladung im verladung-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/verladung/lkw-beladung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/verladung/lkw-beladung/agent-contract` |
| Readiness | `GET /api/v1/masks/verladung/lkw-beladung/readiness` |
| Rollout-Route | `/mask-rollout/verladung__lkw-beladung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/silo/kapazitaeten`

**Beispiel-Prompts:**

- Zeige Lkw beladung.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

## Domäne: vertrag

### `vertrag/neu` — Gespeichert

**Zweck:** Gespeichert im vertrag-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/vertrag/neu/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/vertrag/neu/agent-contract` |
| Readiness | `GET /api/v1/masks/vertrag/neu/readiness` |
| Rollout-Route | `/mask-rollout/vertrag__neu/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/price-hedge/hedges`

**Beispiel-Prompts:**

- Zeige Gespeichert.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `vertrag/rahmenvertraege` — Rahmenvertraege

**Zweck:** Rahmenvertraege im vertrag-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/vertrag/rahmenvertraege/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/vertrag/rahmenvertraege/agent-contract` |
| Readiness | `GET /api/v1/masks/vertrag/rahmenvertraege/readiness` |
| Rollout-Route | `/mask-rollout/vertrag__rahmenvertraege/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/vertrag/rahmenvertraege`

**Beispiel-Prompts:**

- Zeige Rahmenvertraege.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

## Domäne: vertrieb

### `vertrieb/kundenumsatz` — Kundenumsatz

**Zweck:** Kundenumsatz im vertrieb-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/vertrieb/kundenumsatz/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/vertrieb/kundenumsatz/agent-contract` |
| Readiness | `GET /api/v1/masks/vertrieb/kundenumsatz/readiness` |
| Rollout-Route | `/mask-rollout/vertrieb__kundenumsatz/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/crm/customers/`

**Beispiel-Prompts:**

- Zeige Kundenumsatz.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

## Domäne: waage

### `waage/neu` — Liste

**Zweck:** Liste im waage-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/waage/neu/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/waage/neu/agent-contract` |
| Readiness | `GET /api/v1/masks/waage/neu/readiness` |
| Rollout-Route | `/mask-rollout/waage__neu/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/waage/hofliste`

**Beispiel-Prompts:**

- Zeige Liste.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `waage/vorlagen` — Vorlagen

**Zweck:** Vorlagen im waage-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/waage/vorlagen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/waage/vorlagen/agent-contract` |
| Readiness | `GET /api/v1/masks/waage/vorlagen/readiness` |
| Rollout-Route | `/mask-rollout/waage__vorlagen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/waage/vorlagen`

**Beispiel-Prompts:**

- Zeige Vorlagen.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `waage/wiegeschein` — Wiegeschein

**Zweck:** Wiegeschein-Detail.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/waage/wiegeschein/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/waage/wiegeschein/agent-contract` |
| Readiness | `GET /api/v1/masks/waage/wiegeschein/readiness` |
| Rollout-Route | `/mask-rollout/waage__wiegeschein/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/weighing-tickets/{entity_id}`

**Beispiel-Prompts:**

- Welches Nettogewicht hat Wiegeschein {entity_id}?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `waage/wiegeschein-detail` — Wiegeschein detail

**Zweck:** Wiegeschein detail im waage-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/waage/wiegeschein-detail/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/waage/wiegeschein-detail/agent-contract` |
| Readiness | `GET /api/v1/masks/waage/wiegeschein-detail/readiness` |
| Rollout-Route | `/mask-rollout/waage__wiegeschein-detail/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/waage/hofliste`

**Beispiel-Prompts:**

- Zeige Wiegeschein detail.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `waage/wiegungen` — Wiegungen

**Zweck:** Wiegungen im waage-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/waage/wiegungen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/waage/wiegungen/agent-contract` |
| Readiness | `GET /api/v1/masks/waage/wiegungen/readiness` |
| Rollout-Route | `/mask-rollout/waage__wiegungen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/waage/hofliste`

**Beispiel-Prompts:**

- Zeige Wiegungen.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

## Domäne: workflow

### `workflow/flow-spine-complaint-to-resolution` — Flow spine complaint to resolution

**Zweck:** Flow spine complaint to resolution im workflow-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/workflow/flow-spine-complaint-to-resolution/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/workflow/flow-spine-complaint-to-resolution/agent-contract` |
| Readiness | `GET /api/v1/masks/workflow/flow-spine-complaint-to-resolution/readiness` |
| Rollout-Route | `/mask-rollout/workflow__flow-spine-complaint-to-resolution/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/workflow/cockpit-db/dead-letter`

**Beispiel-Prompts:**

- Zeige Flow spine complaint to resolution.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `workflow/flow-spine-compliance-to-report` — Flow spine compliance to report

**Zweck:** Flow spine compliance to report mandantensicher als Cockpit bereitstellen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/workflow/flow-spine-compliance-to-report/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/workflow/flow-spine-compliance-to-report/agent-contract` |
| Readiness | `GET /api/v1/masks/workflow/flow-spine-compliance-to-report/readiness` |
| Rollout-Route | `/mask-rollout/workflow__flow-spine-compliance-to-report/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/workflow/cockpit-db/dead-letter`

**Beispiel-Prompts:**

- Zeige Flow spine compliance to report.
- Aktualisiere die Kennzahlen.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `workflow/flow-spine-contract-to-settlement` — Flow spine contract to settlement

**Zweck:** Flow spine contract to settlement im workflow-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/workflow/flow-spine-contract-to-settlement/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/workflow/flow-spine-contract-to-settlement/agent-contract` |
| Readiness | `GET /api/v1/masks/workflow/flow-spine-contract-to-settlement/readiness` |
| Rollout-Route | `/mask-rollout/workflow__flow-spine-contract-to-settlement/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/workflow/cockpit-db/dead-letter`

**Beispiel-Prompts:**

- Zeige Flow spine contract to settlement.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `workflow/flow-spine-finance-to-close` — Flow spine finance to close

**Zweck:** Flow spine finance to close im workflow-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/workflow/flow-spine-finance-to-close/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/workflow/flow-spine-finance-to-close/agent-contract` |
| Readiness | `GET /api/v1/masks/workflow/flow-spine-finance-to-close/readiness` |
| Rollout-Route | `/mask-rollout/workflow__flow-spine-finance-to-close/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/workflow/cockpit-db/dead-letter`

**Beispiel-Prompts:**

- Zeige Flow spine finance to close.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `workflow/flow-spine-harvest-to-settlement` — Flow spine harvest to settlement

**Zweck:** Flow spine harvest to settlement im workflow-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/workflow/flow-spine-harvest-to-settlement/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/workflow/flow-spine-harvest-to-settlement/agent-contract` |
| Readiness | `GET /api/v1/masks/workflow/flow-spine-harvest-to-settlement/readiness` |
| Rollout-Route | `/mask-rollout/workflow__flow-spine-harvest-to-settlement/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/workflow/cockpit-db/dead-letter`

**Beispiel-Prompts:**

- Zeige Flow spine harvest to settlement.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `workflow/flow-spine-inventory-to-settlement` — Flow spine inventory to settlement

**Zweck:** Flow spine inventory to settlement im workflow-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/workflow/flow-spine-inventory-to-settlement/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/workflow/flow-spine-inventory-to-settlement/agent-contract` |
| Readiness | `GET /api/v1/masks/workflow/flow-spine-inventory-to-settlement/readiness` |
| Rollout-Route | `/mask-rollout/workflow__flow-spine-inventory-to-settlement/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/workflow/cockpit-db/dead-letter`

**Beispiel-Prompts:**

- Zeige Flow spine inventory to settlement.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `workflow/flow-spine-order-to-cash` — Flow spine order to cash

**Zweck:** Flow spine order to cash im workflow-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/workflow/flow-spine-order-to-cash/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/workflow/flow-spine-order-to-cash/agent-contract` |
| Readiness | `GET /api/v1/masks/workflow/flow-spine-order-to-cash/readiness` |
| Rollout-Route | `/mask-rollout/workflow__flow-spine-order-to-cash/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/workflow/cockpit-db/dead-letter`

**Beispiel-Prompts:**

- Zeige Flow spine order to cash.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `workflow/flow-spine-procure-to-pay` — Flow spine procure to pay

**Zweck:** Flow spine procure to pay im workflow-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/workflow/flow-spine-procure-to-pay/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/workflow/flow-spine-procure-to-pay/agent-contract` |
| Readiness | `GET /api/v1/masks/workflow/flow-spine-procure-to-pay/readiness` |
| Rollout-Route | `/mask-rollout/workflow__flow-spine-procure-to-pay/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/workflow/cockpit-db/dead-letter`

**Beispiel-Prompts:**

- Zeige Flow spine procure to pay.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `workflow/flow-spine-service-to-customer` — Flow spine service to customer

**Zweck:** Flow spine service to customer im workflow-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/workflow/flow-spine-service-to-customer/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/workflow/flow-spine-service-to-customer/agent-contract` |
| Readiness | `GET /api/v1/masks/workflow/flow-spine-service-to-customer/readiness` |
| Rollout-Route | `/mask-rollout/workflow__flow-spine-service-to-customer/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/workflow/cockpit-db/dead-letter`

**Beispiel-Prompts:**

- Zeige Flow spine service to customer.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `workflow/flow-spine-studio` — Flow spine studio

**Zweck:** Flow spine studio im workflow-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/workflow/flow-spine-studio/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/workflow/flow-spine-studio/agent-contract` |
| Readiness | `GET /api/v1/masks/workflow/flow-spine-studio/readiness` |
| Rollout-Route | `/mask-rollout/workflow__flow-spine-studio/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/workflow/cockpit-db/dead-letter`

**Beispiel-Prompts:**

- Zeige Flow spine studio.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `workflow/leitstand` — Workflow-Leitstand

**Zweck:** Workflow-Instanzen mandantensicher ueberwachen und eingreifen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/workflow/leitstand/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/workflow/leitstand/agent-contract` |
| Readiness | `GET /api/v1/masks/workflow/leitstand/readiness` |
| Rollout-Route | `/mask-rollout/workflow__leitstand/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/workflow/cockpit/summary`
- `processes` → `/api/v1/workflow/cockpit/processes`

**Beispiel-Prompts:**

- Welche Prozesse sind blockiert?
- Zeige fehlgeschlagene Instanzen.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `workflow/process-mining` — Process Mining

**Zweck:** Process-Mining-Report fuer Finance-Prozesse auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/workflow/process-mining/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/workflow/process-mining/agent-contract` |
| Readiness | `GET /api/v1/masks/workflow/process-mining/readiness` |
| Rollout-Route | `/mask-rollout/workflow__process-mining/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/process-mining/finance/report`

**Beispiel-Prompts:**

- Wo sind Finance-Bottlenecks?
- Zeige Top-Prozesse.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `workflow/process-mining-analytics` — Process mining analytics

**Zweck:** Process mining analytics mandantensicher als Cockpit bereitstellen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/workflow/process-mining-analytics/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/workflow/process-mining-analytics/agent-contract` |
| Readiness | `GET /api/v1/masks/workflow/process-mining-analytics/readiness` |
| Rollout-Route | `/mask-rollout/workflow__process-mining-analytics/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/workflow/cockpit-db/dead-letter`

**Beispiel-Prompts:**

- Zeige Process mining analytics.
- Aktualisiere die Kennzahlen.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `workflow/workflow-regeln` — Workflow regeln

**Zweck:** Workflow regeln im workflow-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/workflow/workflow-regeln/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/workflow/workflow-regeln/agent-contract` |
| Readiness | `GET /api/v1/masks/workflow/workflow-regeln/readiness` |
| Rollout-Route | `/mask-rollout/workflow__workflow-regeln/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/workflow/cockpit-db/dead-letter`

**Beispiel-Prompts:**

- Zeige Workflow regeln.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `workflow/workflow-sandbox` — Workflow sandbox

**Zweck:** Workflow sandbox im workflow-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/workflow/workflow-sandbox/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/workflow/workflow-sandbox/agent-contract` |
| Readiness | `GET /api/v1/masks/workflow/workflow-sandbox/readiness` |
| Rollout-Route | `/mask-rollout/workflow__workflow-sandbox/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/admin/process-variants`

**Beispiel-Prompts:**

- Zeige Workflow sandbox.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

## Domäne: workflows

### `workflows/history` — Workflow monitoring

**Zweck:** Workflow monitoring im workflows-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/workflows/history/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/workflows/history/agent-contract` |
| Readiness | `GET /api/v1/masks/workflows/history/readiness` |
| Rollout-Route | `/mask-rollout/workflows__history/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/agent/integrations/providers/superglue/sync-history`

**Beispiel-Prompts:**

- Zeige Workflow monitoring.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `workflows/supervisor` — Supervisor

**Zweck:** Supervisor im workflows-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/workflows/supervisor/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/workflows/supervisor/agent-contract` |
| Readiness | `GET /api/v1/masks/workflows/supervisor/readiness` |
| Rollout-Route | `/mask-rollout/workflows__supervisor/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/agents/neuroassist/runs`

**Beispiel-Prompts:**

- Zeige Supervisor.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

## Domäne: workspace

### `contracts-v2` — Contracts v2

**Zweck:** Contracts v2 im workspace-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/contracts-v2/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/contracts-v2/agent-contract` |
| Readiness | `GET /api/v1/masks/contracts-v2/readiness` |
| Rollout-Route | `/mask-rollout/contracts-v2/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/kontrakte`

**MCP-Tools (Domäne):**

- `workspace.fachaktion.katalog` — scope `agent:read`, Risiko niedrig
- `workspace.fachaktion.resolve` — scope `agent:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige Contracts v2.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---

### `inventory-reports` — Inventory reports

**Zweck:** Inventory reports mandantensicher als Cockpit bereitstellen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/inventory-reports/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/inventory-reports/agent-contract` |
| Readiness | `GET /api/v1/masks/inventory-reports/readiness` |
| Rollout-Route | `/mask-rollout/inventory-reports/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/inventory/reports/stock-alerts`

**MCP-Tools (Domäne):**

- `workspace.fachaktion.katalog` — scope `agent:read`, Risiko niedrig
- `workspace.fachaktion.resolve` — scope `agent:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige Inventory reports.
- Aktualisiere die Kennzahlen.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `reports` — Reports

**Zweck:** Reports mandantensicher als Cockpit bereitstellen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/reports/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/reports/agent-contract` |
| Readiness | `GET /api/v1/masks/reports/readiness` |
| Rollout-Route | `/mask-rollout/reports/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/rations-optimization/feeding/reports`

**MCP-Tools (Domäne):**

- `workspace.fachaktion.katalog` — scope `agent:read`, Risiko niedrig
- `workspace.fachaktion.resolve` — scope `agent:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige Reports.
- Aktualisiere die Kennzahlen.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `start-dashboard` — Start dashboard

**Zweck:** Start dashboard mandantensicher als Cockpit bereitstellen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/start-dashboard/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/start-dashboard/agent-contract` |
| Readiness | `GET /api/v1/masks/start-dashboard/readiness` |
| Rollout-Route | `/mask-rollout/start-dashboard/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/analytics/kpis`

**MCP-Tools (Domäne):**

- `workspace.fachaktion.katalog` — scope `agent:read`, Risiko niedrig
- `workspace.fachaktion.resolve` — scope `agent:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige Start dashboard.
- Aktualisiere die Kennzahlen.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `workspace/letzte-dokumente` — Letzte Dokumente

**Zweck:** Die eigenen zuletzt geoeffneten und weiterhin berechtigten ERP-Dokumente wiederfinden.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/workspace/letzte-dokumente/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/workspace/letzte-dokumente/agent-contract` |
| Readiness | `GET /api/v1/masks/workspace/letzte-dokumente/readiness` |
| Rollout-Route | `/mask-rollout/workspace__letzte-dokumente/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/recent-documents`
- `documents` → `/api/v1/recent-documents`

**MCP-Tools (Domäne):**

- `workspace.fachaktion.katalog` — scope `agent:read`, Risiko niedrig
- `workspace.fachaktion.resolve` — scope `agent:read`, Risiko niedrig

**Beispiel-Prompts:**

- Oeffne meinen letzten Lieferschein.
- Zeige meine zuletzt geoeffneten Rechnungen.

**Sensible Felder:** `partner_name, document_number, route`

---

### `workspace/start-dashboard` — Start-Dashboard

**Zweck:** Startseite mit Sprung in rollenbasierte Workspaces.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/workspace/start-dashboard/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/workspace/start-dashboard/agent-contract` |
| Readiness | `GET /api/v1/masks/workspace/start-dashboard/readiness` |
| Rollout-Route | `/mask-rollout/workspace__start-dashboard/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/analytics/kpis`

**MCP-Tools (Domäne):**

- `workspace.fachaktion.katalog` — scope `agent:read`, Risiko niedrig
- `workspace.fachaktion.resolve` — scope `agent:read`, Risiko niedrig

**Beispiel-Prompts:**

- Was steht heute an?
- Oeffne mein Einkaufs-Cockpit.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

## Domäne: zertifikate

### `zertifikate/neu` — Liste

**Zweck:** Liste im zertifikate-Bereich finden und auswerten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/zertifikate/neu/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/zertifikate/neu/agent-contract` |
| Readiness | `GET /api/v1/masks/zertifikate/neu/readiness` |
| Rollout-Route | `/mask-rollout/zertifikate__neu/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/zertifikate`

**Beispiel-Prompts:**

- Zeige Liste.
- Filtere die Liste.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export` | CSV-Export | safe | nein | `Exportiert die Liste mit ihren Spalten; keine Serverwirkung.` |

---
