---
title: Studio Runtime Gate E – Arbeitsinventar
type: reference
audience: [agent, entwickler, qa]
owner: STUDIO-RUNTIME52-CATALOG
status: aktiv
last_reviewed: 2026-10-28
description: Ursprüngliche 52 offene Runtime-IDs und Anforderungen an ihre fachliche Abnahme.
---

# Studio Runtime Gate E – Arbeitsinventar

Dieses Inventar dokumentiert die 52 IDs des Gate-Reports aus Revision `452a8da5a` im akzeptierten Snapshot `artifacts/migration-repair-source`. Der zwischenzeitlich aktualisierte [Gate-Report](../architecture/uix/made-by-studio-gate-report.md) weist nach einer Katalogumstellung 51 offene IDs aus. Die Katalogmigration ist mit 63 gezielten Tests, Typpruefung, Build und visueller Komponentenabnahme belegt; siehe [Abnahme](studio-process-catalog-20261028.md). Die ursprüngliche Liste bleibt hier vollständig nachvollziehbar.

Status „offen“ bedeutet, dass die funktionale Runtime-Verdrahtung und fachliche Abnahme durch dieses Inventar nicht nachgewiesen sind. `auth/login` und `auth/callback` sind Infrastruktur- und Sicherheitsabläufe; sie benötigen eine gesonderte Prüfung.

| Screen-ID | Familie | Status | Hinweis |
|---|---|---|---|
| `admin/control-center` | Administration | offen | – |
| `admin/webhooks-liste` | Administration | offen | – |
| `annahme/lkw-registrierung` | Annahme | offen | – |
| `annahme/qualitaets-check` | Annahme | offen | – |
| `annahme/warteschlange` | Annahme | offen | – |
| `auth/callback` | Authentifizierung (Infrastruktur) | offen | – |
| `auth/login` | Authentifizierung (Infrastruktur) | offen | – |
| `crm/aktivitaeten-liste` | CRM | offen | – |
| `crm/campaign` | CRM | offen | – |
| `crm/campaign-template` | CRM | offen | – |
| `crm/consent` | CRM | offen | – |
| `crm/gdpr-request` | CRM | offen | – |
| `crm/kunden-cockpit` | CRM | offen | – |
| `crm/segment` | CRM | offen | – |
| `einkauf/rechnungseingang/neu` | Einkauf | offen | – |
| `fibu/debitoren` | Finanzbuchhaltung | offen | – |
| `fibu/debitoren-liste` | Finanzbuchhaltung | offen | – |
| `finance/bank-abgleich` | Finance | offen | – |
| `finance/debitoren/new` | Finance | offen | – |
| `finance/invoices/new` | Finance | offen | – |
| `futtermittel/einzelfuttermittel/stamm/new` | Futtermittel | offen | – |
| `futtermittel/fuetterungsdokumentation-mobil` | Futtermittel | offen | – |
| `futtermittel/mischfuttermittel/stamm/new` | Futtermittel | offen | – |
| `futtermittel/rationseditor` | Futtermittel | offen | – |
| `futtermittel/rationsoptimierung` | Futtermittel | offen | – |
| `kontrakte/FrmKontraktProtokoll` | Kontrakte | offen | – |
| `lager/materialfluss` | Lager | offen | – |
| `mahnwesen/mahnlauf` | Mahnwesen | offen | – |
| `portal/rationsoptimierung` | Portal | offen | – |
| `sales/angebote-liste` | Vertrieb und Belege | offen | – |
| `sales/credit-notes` | Vertrieb und Belege | offen | – |
| `sales/lieferungen-liste` | Vertrieb und Belege | offen | – |
| `sales/lieferungen/neu` | Vertrieb und Belege | offen | – |
| `verkauf/auftraege/neu` | Vertrieb und Belege | offen | – |
| `verkauf/kunde` | Vertrieb und Belege | offen | – |
| `verkauf/kunden-stamm` | Vertrieb und Belege | offen | – |
| `verkauf/rechnungen` | Vertrieb und Belege | offen | – |
| `waage/liste` | Waage | offen | – |
| `waage/neu` | Waage | offen | – |
| `waage/waagen-liste` | Waage | offen | – |
| `waage/wiegungen` | Waage | offen | – |
| `waage/wiegungen-liste` | Waage | offen | – |
| `workflow/flow-spine-complaint-to-resolution` | Workflow | offen | – |
| `workflow/flow-spine-compliance-to-report` | Workflow | offen | – |
| `workflow/flow-spine-contract-to-settlement` | Workflow | offen | – |
| `workflow/flow-spine-finance-to-close` | Workflow | offen | – |
| `workflow/flow-spine-harvest-to-settlement` | Workflow | offen | – |
| `workflow/flow-spine-inventory-to-settlement` | Workflow | offen | – |
| `workflow/flow-spine-order-to-cash` | Workflow | offen | – |
| `workflow/flow-spine-procure-to-pay` | Workflow | offen | – |
| `workflow/flow-spine-service-to-customer` | Workflow | offen | – |
| `workflow/flow-spine-studio` | Workflow | Komponentenabnahme bestanden | Eigene Katalogmigration; neun Prozessraeume bleiben offen |

## Reihenfolge und Abnahme

Priorität als Arbeitsannahme: zuerst Vertrieb und Belege sowie Annahme und Waage, danach Finanzbuchhaltung und Finance, CRM und Futtermittel. Kontrakte, Lager, Mahnwesen und Portal folgen nach fachlichen Abhängigkeiten. Workflow sowie Administration und Authentifizierung erhalten eigene, auf ihre Abläufe zugeschnittene Prüfungen. Diese Reihenfolge ist kein Terminversprechen.

Jede Familie benötigt einen gesonderten Claim mit Dateibesitz und eine fachliche Paritätsabnahme: aktive Routen und Identitäten, Datenquellen, Navigation und Aktionen, Eingaben und Zustände, Rechte sowie Fehlerfälle gegen die bestehende Bedienung prüfen. Neuanlage- und Bearbeitungsmodi sind eigenständig zu bewerten. Die sichtbare Runtime muss die fachliche Oberfläche tatsächlich tragen; ein dekorativer Marker oder Wrapper belegt keine Parität. Gate E ist anschließend erneut auszuführen und durch geeignete fachliche und UI-Prüfungen zu ergänzen.

## Duplikate und Bereinigung

Eine gemeinsame Routendatei belegt keine identische Definition. Für `fibu/debitoren` und `fibu/debitoren-liste` sind unterschiedliche Datenquellen dokumentiert; ebenso für `waage/wiegungen` und `waage/wiegungen-liste`. `waage/liste` und `waage/waagen-liste` teilen eine Datenquelle, unterscheiden sich aber bei Feldern, Domäne und Detailroute. `verkauf/kunde` und `verkauf/kunden-stamm` sind unterschiedliche Definitionen. `sales/lieferungen/neu` wird auf die Lieferungen-Route umgeleitet; `waage/neu` wird aus der aktiven Waagenliste aufgerufen. Insbesondere eine neue Maskenidentität darf bei abweichendem Modus nicht allein wegen gemeinsamer Routendatei entfallen.

Für keine dieser IDs ist eine Entfernung ohne Funktionsverlust nachgewiesen. Vor jeder kanonischen Bereinigung sind Definition, aktive Verbraucher, Studio- und MCP-Verträge sowie die vollständige Funktionsübernahme zu belegen. Eine Alias-Umkennzeichnung zur bloßen Verbesserung des Gate-Ergebnisses ist keine Abnahme.
