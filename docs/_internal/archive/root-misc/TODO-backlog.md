# Kuratiertes TODO-Backlog (Fokus)

> Automatisch erzeugt am 2026-05-05 21:01:23.
> Enthält bis zu 40 Einträge aus `packages/frontend-web/`, `app/`, `services/`, `packages/erp-domain/`.
> Vollständige Rohliste: `todo-repo-scan.md`, `memory-bank/todo.md`, Maschinenlesbar: `todo-report.json` (inkl. `next_slices`).

## Hohe Priorität

- **[packages/erp-domain]** `packages/erp-domain/src/presentation/controllers/anfrage.controller.ts`:L89 — total: anfragen.length // TODO: Pagination-Info
- **[packages/erp-domain]** `packages/erp-domain/src/presentation/controllers/angebot.controller.ts`:L91 — total: angebote.length // TODO: Pagination-Info
- **[packages/erp-domain]** `packages/erp-domain/src/presentation/controllers/anlieferavis.controller.ts`:L82 — total: avise.length // TODO: Pagination-Info
- **[packages/erp-domain]** `packages/erp-domain/src/presentation/controllers/audit-log.controller.ts`:L26 — total: logs.length // TODO: Pagination-Info
- **[packages/erp-domain]** `packages/erp-domain/src/presentation/controllers/auftragsbestaetigung.controller.ts`:L81 — total: abs.length // TODO: Pagination-Info
- **[packages/erp-domain]** `packages/erp-domain/src/presentation/controllers/rechnungseingang.controller.ts`:L92 — total: rechnungen.length // TODO: Pagination-Info
- **[packages/erp-domain]** `packages/erp-domain/src/presentation/controllers/sales-offer.controller.ts`:L49 — const actorId = 'system' // TODO: Aus Auth-Middleware
- **[packages/erp-domain]** `packages/erp-domain/src/presentation/controllers/sales-offer.controller.ts`:L51 — // TODO: CustomerInquiry laden und SalesOffer erstellen
- **[packages/erp-domain]** `packages/erp-domain/src/presentation/controllers/sales-offer.controller.ts`:L109 — total: salesOffers.length // TODO: Pagination-Info
- **[packages/erp-domain]** `packages/erp-domain/src/presentation/controllers/workflow-execution.controller.ts`:L83 — total: executions.length // TODO: Pagination-Info
- **[packages/erp-domain]** `packages/erp-domain/src/presentation/controllers/workflow-rule.controller.ts`:L84 — total: rules.length // TODO: Pagination-Info
## Normale Priorität

- **[app]** `app/api/v1/endpoints/strecke.py`:L76 — In-memory store (TODO: replace with DB table)
- **[app]** `app/domains/agrar/api/psm_proplanta.py`:L83 — TODO: Could send notification or update status
- **[app]** `app/domains/crm/services/daily_report_service.py`:L385 — TODO: Send via email, Teams, Telegram, etc.
- **[app]** `app/einkauf/router.py`:L658 — TODO(phase-4): Echte Extraktion via pdfplumber / tesseract / Cloud-OCR einbauen
- **[packages/erp-domain]** `packages/erp-domain/src/application/services/anfrage.service.ts`:L63 — actorId: data.anforderer, // TODO: Aus Context holen
- **[packages/erp-domain]** `packages/erp-domain/src/application/services/anfrage.service.ts`:L131 — // TODO: Anfrage mit neuen Daten aktualisieren
- **[packages/erp-domain]** `packages/erp-domain/src/application/services/anfrage.service.ts`:L142 — after: anfrage, // TODO: updatedAnfrage
- **[packages/erp-domain]** `packages/erp-domain/src/application/services/anfrage.service.ts`:L146 — return anfrage // TODO: saved
- **[packages/erp-domain]** `packages/erp-domain/src/application/services/angebot.service.ts`:L65 — actorId: data.lieferantId, // TODO: Aus Context holen
- **[packages/erp-domain]** `packages/erp-domain/src/application/services/angebot.service.ts`:L191 — // TODO: Angebot mit neuen Daten aktualisieren
- **[packages/erp-domain]** `packages/erp-domain/src/application/services/angebot.service.ts`:L202 — after: angebot, // TODO: updatedAngebot
- **[packages/erp-domain]** `packages/erp-domain/src/application/services/angebot.service.ts`:L206 — return angebot // TODO: saved
- **[packages/erp-domain]** `packages/erp-domain/src/application/services/anlieferavis.service.ts`:L74 — actorId: 'system', // TODO: Aus Context holen
- **[packages/erp-domain]** `packages/erp-domain/src/application/services/anlieferavis.service.ts`:L172 — // TODO: Anlieferavis mit neuen Daten aktualisieren
- **[packages/erp-domain]** `packages/erp-domain/src/application/services/anlieferavis.service.ts`:L183 — after: avis, // TODO: updatedAvis
- **[packages/erp-domain]** `packages/erp-domain/src/application/services/anlieferavis.service.ts`:L187 — return avis // TODO: saved
- **[packages/erp-domain]** `packages/erp-domain/src/application/services/audit.service.ts`:L30 — // TODO: Implementiere tatsächliche Datenbank-Persistierung
- **[packages/erp-domain]** `packages/erp-domain/src/application/services/audit.service.ts`:L35 — // TODO: Implementiere Historien-Abfrage
- **[packages/erp-domain]** `packages/erp-domain/src/application/services/audit.service.ts`:L41 — // TODO: Implementiere Benutzeraktivitäten-Abfrage
- **[packages/erp-domain]** `packages/erp-domain/src/application/services/auftragsbestaetigung.service.ts`:L72 — actorId: 'system', // TODO: Aus Context holen
- **[packages/erp-domain]** `packages/erp-domain/src/application/services/auftragsbestaetigung.service.ts`:L170 — // TODO: Auftragsbestätigung mit neuen Daten aktualisieren
- **[packages/erp-domain]** `packages/erp-domain/src/application/services/auftragsbestaetigung.service.ts`:L181 — after: ab, // TODO: updatedAb
- **[packages/erp-domain]** `packages/erp-domain/src/application/services/auftragsbestaetigung.service.ts`:L185 — return ab // TODO: saved
- **[packages/erp-domain]** `packages/erp-domain/src/application/services/rechnungseingang.service.ts`:L91 — actorId: 'system', // TODO: Aus Context holen
- **[packages/erp-domain]** `packages/erp-domain/src/application/services/rechnungseingang.service.ts`:L249 — // TODO: Rechnungseingang mit neuen Daten aktualisieren
- **[packages/erp-domain]** `packages/erp-domain/src/application/services/rechnungseingang.service.ts`:L260 — after: rechnung, // TODO: updatedRechnung
- **[packages/erp-domain]** `packages/erp-domain/src/application/services/rechnungseingang.service.ts`:L264 — return rechnung // TODO: saved
- **[packages/erp-domain]** `packages/erp-domain/src/application/services/sales-offer.service.ts`:L60 — actorId: 'system', // TODO: Aus Context holen
- **[packages/erp-domain]** `packages/erp-domain/src/application/services/sales-offer.service.ts`:L107 — // TODO: CustomerInquiry Repository aktualisieren
