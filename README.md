# VALEO NeuroERP 3.0

[Deutsch](#deutsch) · [English](#english)

## Deutsch

**Das ERP für Agrargenossenschaften und Landhandel, in dem Menschen und KI-Agenten an denselben Belegen arbeiten — nachvollziehbar, mandantensicher und GoBD-fest.**

VALEO NeuroERP ist von Grund auf für den Agrarhandel gebaut: Kontrakte, Ernte und Abrechnung, Einkauf, Verkauf, Lager, Waage und Logistik bilden den Kern. Finanzbuchhaltung, CRM, Personal und Dokumente sind eingebunden. Darüber liegt eine Plattform, die jede Fachaktion gleichermaßen für die Oberfläche, für Schnittstellen und für Agenten öffnet.

### Was VALEO auszeichnet

**1. Ein Beleg, eine Wahrheit.**
Angebot, Auftrag, Lieferschein, Rechnung und Gutschrift — im Einkauf Bestellung, Wareneingang und Eingangsrechnung — liegen in einem gemeinsamen Belegspeicher (DocFlow). Folgebelege entstehen durch Umwandlung mit Restmengen je Position. Charge, Kontrakt und Herkunft wandern mit. Es gibt keine Abgleichläufe zwischen Modulen, weil es keine Kopien gibt.

**2. GoBD ist eingebaut, nicht angeflanscht.**
Gebuchte Belege sind unveränderlich. Jeder Statuswechsel steht mit Kommando und Grund in einer Historie, die ein Datenbank-Trigger schreibt und die sich deshalb nicht vergessen lässt. Ein Nachdruck verlangt eine Begründung und trägt den Vermerk „NACHDRUCK“. Stornos buchen gegen, statt zu löschen. Als Nächstes kommen das archivierte Original jeder gebuchten Rechnung (in derselben Transaktion) und die E-Rechnung (XRechnung), die vor der Auslieferung archiviert wird.

**3. Eine Fachaktion, alle Zugänge.**
„Auftrag bestätigen“, „Beleg freigeben“ oder „Rechnung buchen“ gibt es genau einmal als Fachkommando. Belegmaske, REST, CLI und MCP rufen dasselbe Kommando auf: mit denselben Rollen, derselben Mandantengrenze, demselben Wiederholungsschutz und demselben Protokoll. Was ein Mensch in der Maske darf, darf ein Agent nur mit denselben Rechten.

**4. Agenten mit Verantwortung statt Blackbox.**
Die Agent Trust & Autonomy Engine (ADR-086) entscheidet risikobasiert: Betragsgrenzen, Funktionstrennung, Freigabe durch eine zweite Person. Wann ein Agent selbst buchen darf, legt eine versionierte Politik fest. Wirksam wird sie je Mandant erst, wenn eine berechtigte Person diese Fassung freigibt — nie ein Agent. Jeder Agentenschritt bleibt am Beleg nachvollziehbar.

**5. Agrarfachlichkeit bis ins Detail.**
Mengen rechnet VALEO in der Handelsgröße des Landhandels (dt), umgerechnet über eine zentrale Einheitentabelle. Ein Lieferschein bucht den Lagerabgang über die WMS-Pickliste. Die Umsatzsteuer kommt aus einer einzigen Quelle, dem Steuerschlüssel: keine pauschalen 19 %, kein Rechnen am Schlüssel vorbei.

**6. Mandantentrennung bis in die Datenbank.**
Row-Level-Security in PostgreSQL, Identität ausschließlich aus dem Token, Mandantenbindung in der Middleware. Ein Portal-Kunde sieht nur seine eigenen Belege, serverseitig erzwungen.

**7. Masken aus dem Studio, gleiche Bedienung überall.**
Belegmasken sind eine versionierte Maskenfamilie: Jede Belegart ist eine Variante desselben Aufbaus mit Kopf, Partner, Positionen, Summen und Aktionsleiste. Wer einen Auftrag bedienen kann, kann auch Lieferschein und Rechnung bedienen. Masken entstehen deklarativ im Studio statt als handgeschriebener Code.

**8. Qualität mit Ratschen.**
Über 4.900 Backend-Tests, viele davon gegen echtes PostgreSQL-Schema. Migrationen werden gegen eine frisch aufgebaute Prüfstand-Datenbank geprüft. Ratschen verhindern, dass Altlasten, Godfiles oder ungeschützte Schreibwege wieder wachsen. Generierte Verträge (OpenAPI, Masken-, MCP- und Rechteprojektionen) werden in der CI auf Drift geprüft.

### Aktueller Schwerpunkt: DocFlow als einziger Belegspeicher (BELEG-052)

Verkauf und Einkauf werden schrittweise auf den gemeinsamen Belegspeicher umgestellt. Je Belegart gilt dasselbe Vorgehen:

1. Zugänge umstellen.
2. Altwege entfernen.
3. Altbestand übernehmen oder bereinigen.

Bereits in `main`:
- Auftrag mit eigener Auftragsbestätigung (Stand „bestätigt“).
- Kopfbausteine (Lieferung, Zahlung, Texte, Kontakt, Referenzen).
- Lagerabgang über die WMS-Pickliste aus dem Lieferschein.
- Belegdruck mit Druckvermerk.

Danach folgen die Rechnung (mit E-Rechnung und archiviertem Original), der Einkauf (Wareneingang bucht den Lagerzugang, Anlieferavis und Angebot laufen über DocFlow) und die Studio-Masken der übrigen Bereiche. Details: [Belegmasken-Masterplan](docs/design/belegmaske-varianten-masterplan.md).

| Einblick | Quelle |
| --- | --- |
| Belegmaske und BELEG-052 | [Masterplan und Umsetzungsstand](docs/design/belegmaske-varianten-masterplan.md) |
| Agentenautonomie | [ADR-086](docs/adr/adr-086-risk-based-autonomous-erp.md) · [MCP-Schreibstandard](docs/architecture/mcp-write-standard.md) |
| Lieferstand und Prozesswellen | [Process Kernel Status](docs/architecture/process-kernel/STATUS.md) |
| Laufende Arbeit | [Active Workboard](docs/agent-ops/active-workboard.md) |
| Masken, Studio und Parität | [Universal Mask Runtime Status](docs/architecture/uix/universal-mask-runtime-status.md) |
| Betrieb und Freigaben | [Production Readiness Runbook](docs/operations/production-readiness-runbook.md) |
| Architektur und Agenten | [Architekturindex](config/architecture-index.yaml) · [Agent-Handbuch](docs/agent-handbuch/index.md) |

### Technik

Python 3.11 / FastAPI, SQLAlchemy 2.0, Alembic und PostgreSQL 15 (mehrere Schemas, Row-Level-Security). Frontend: React 18, TypeScript, Vite, Tailwind, Radix UI, TanStack Query. Dazu OIDC (Keycloak, Azure AD, Auth0), Redis, NATS JetStream mit Outbox-Muster, Paperless-ngx als DMS sowie MCP und CLI für Agenten.

### Lokal entwickeln

Voraussetzungen: Python 3.11, Node.js mit Corepack und pnpm 9.12.0, eine PostgreSQL-Entwicklungsdatenbank. Umgebungsvariablen anhand von [.env.example](.env.example) und der [Frontend-Vorlage](packages/frontend-web/.env.example) einrichten. **Zugangsdaten gehören in die lokale `.env`, nie ins Repository.**

```sh
python -m venv .venv
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
alembic upgrade head
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

In einem zweiten Terminal:

```sh
corepack enable
pnpm install --frozen-lockfile
pnpm --filter @valero-neuroerp/frontend-web dev --host 127.0.0.1 --port 3000
```

Danach erreichbar:
- Frontend: `http://localhost:3000`
- API-Dokumentation: `http://localhost:8000/docs`

Alternativ beschreibt [docker-compose.dev.yml](docker-compose.dev.yml) einen schlanken Entwicklungsstack.

Die Compose-Dateien für Staging verlangen ihre Passwörter aus der Umgebung und starten ohne sie nicht. Die Werte im lokalen `docker-compose.yml` sind reine Entwicklungsvorgaben für den eigenen Rechner und gehören nie in einen erreichbaren Betrieb.

### Qualität und Zusammenarbeit

Für Änderungen gelten [AGENTS.md](AGENTS.md), [CLAUDE.md](CLAUDE.md), die [Startcheckliste](docs/agent-ops/session-start-checklist.md) und das Workboard. Für datenbankabhängige Tests gilt der [Prüfstand](docs/quality-assurance/pruefstand-datenbank.md): das Schema auf einer frischen Datenbank prüfen, die Daten auf der gewachsenen.

Weitere Einstiege: [Dokumentation](docs/README.md) · [Benutzerhandbuch](docs/benutzerhandbuch/index.md) · [Architektur](docs/architecture/index.md) · [MIT-Lizenz](LICENSE).

## English

**The ERP for agricultural cooperatives and agricultural trade where people and AI agents work on the same documents — traceable, tenant-safe and compliant with German bookkeeping law (GoBD).**

### What sets VALEO apart

- **One document, one truth.** Quotes, orders, delivery notes, invoices and credit notes — on the purchasing side purchase orders, goods receipts and supplier invoices — live in one document store (DocFlow). Follow-up documents are converted with per-line remaining quantities; batch, contract and origin travel with them.
- **GoBD built in.** Posted documents are immutable. A database trigger writes status history with command and reason. Reprints require a reason and are marked as such. Reversals post counter-entries instead of deleting. Next up: the archived invoice original and e-invoices (XRechnung) archived before delivery.
- **One business action, every channel.** Each action exists once as a domain command. Screens, REST, CLI and MCP call that same command, with the same roles, tenant boundary, idempotency and audit log.
- **Accountable agents.** The Agent Trust & Autonomy Engine (ADR-086) applies risk-based rules: amount limits, segregation of duties, four-eyes approval. A versioned policy defines when an agent may post on its own. It takes effect per tenant only once an authorized person approves it, never an agent.
- **Deep agricultural domain.** Quantities are kept in the trade unit (dt) through one central unit table. Delivery notes post stock movements through the WMS pick list. VAT comes from a single source, the tax key.
- **Tenant isolation down to the database.** PostgreSQL row-level security, identity from the token only, server-enforced portal scoping.
- **Studio-built screens.** Document screens form a versioned family: each document type is a variant of one layout, so whoever can work an order can work every document in the chain.
- **Quality ratchets.** More than 4,900 backend tests, many against a real PostgreSQL schema. Migrations are verified on a freshly built test database. CI checks generated contracts for drift.

Current focus: making DocFlow the single document store across sales and purchasing (BELEG-052); see the [document screen master plan](docs/design/belegmaske-varianten-masterplan.md). For local setup use the [commands above](#lokal-entwickeln). Keep credentials in your local `.env`, never in the repository. Start contributions with [AGENTS.md](AGENTS.md) and the [documentation overview](docs/README.md).
