# GAP-Analyse Lastenheft (SOLL) vs. aktueller IST-Zustand

Stand: 2026-03-19

## Scope

Diese GAP-Analyse vergleicht den neuen Lastenheft-Abschnitt in der [README](../../README.md) mit dem aktuell im Repository sichtbaren IST-Zustand.

Bewertungsgrundlage:

- produktiver Code in `app/`, `services/`, `packages/`
- aktive Architektur- und Statusdokumente in `docs/`
- vorhandene API- und Workflow-Verkabelung

Nicht Bestandteil:

- Runtime-Validierung in einer laufenden Umgebung
- fachliche Abnahme mit echten Unternehmensdaten
- Bewertung von externen Systemen, die nur dokumentiert, aber nicht im Repo verdrahtet sind

## Kurzfazit

VALEO NeuroERP ist im IST bereits deutlich staerker als ein klassisches UI-zentriertes ERP-Projekt. Die Architektur ist API-first, workflow- und policy-getrieben, agentenfaehige Kernbausteine sind vorhanden, und fuer Finance, Workflow, Audit, OIDC, RAG und NeuroASSIST existiert substanzieller Code.

Der groesste Abstand zum Lastenheft liegt nicht in fehlender Grundarchitektur, sondern in der Produktisierung des agentenfaehigen Unternehmenswissens. Es gibt RAG-, Dokument-, Voice-, Workflow- und Agentenbausteine, aber noch keinen klar durchgaengigen, zentralen KI-Wissensspeicher als produktive, domainuebergreifende Kernfunktion. Ebenfalls deutlich offen sind echte Multi-Channel-Arbeitskanaele fuer Slack/Teams, unternehmensweite Wissens- und Skill-Rueckfuehrung, sowie ein echter Knowledge Graph im Sinne des Lastenhefts.

Gesamtbewertung als belastbare Repo-Schaetzung:

- Architektur-Fundament: stark
- Prozess- und Agentenfaehigkeit: fortgeschritten
- Wissenszentrierte Unternehmensinfrastruktur: teilweise umgesetzt
- Kollaborative Mensch-Agenten-Betriebslogik: in Teilen vorbereitet, noch nicht durchgaengig produktisiert

## Bewertungslogik

- `Erfuellt`: produktiv und repo-seitig sichtbar umgesetzt
- `Teilweise erfuellt`: tragfaehige Bausteine vorhanden, aber nicht durchgaengig oder nicht als Gesamtfaehigkeit produktisiert
- `Weitgehend offen`: eher Architektur, Prototyp oder Teilimplementierung als belastbare Gesamtloesung

## Soll-Ist-Matrix

| Sollbereich | IST-Zustand | Bewertung | GAP |
|---|---|---|---|
| Zentraler KI-Wissensspeicher | RAG- und Vector-Store-Bausteine sind vorhanden, ebenso Dokument- und Suchstrukturen. Ein einheitlicher, domainuebergreifender Wissensspeicher mit klarer Produktoberflaeche fehlt noch. In `crm-service` ist der Knowledge-Base-Router sogar noch auskommentiert. | Teilweise erfuellt | Zentrales Wissensmodell, Governance, CRUD, Versionierung und einheitliche Retrieval-Schicht fehlen als sichtbares Kernprodukt. |
| Agentenfaehigkeit ueber APIs, Skills, Kontexte | Sehr gute Grundlage: NeuroASSIST, LangGraph-Workflow-Runner, Agent-Manifest, OpenAPI, MCP, Prozesskernel, Contracts und Auditmodelle sind vorhanden. | Erfuellt bis teilweise erfuellt | Stark bei Architektur und Laufzeitmodellen; offen ist die breite fachliche Abdeckung ueber alle Unternehmensbereiche. |
| Skill-basierte Prozesssteuerung | Workflow-/Policy-Kern und zahlreiche Vertragsmodule sind stark ausgebaut; Prozesskernel Waves 1-50 sind als abgeschlossen dokumentiert. | Erfuellt | Das Lastenheft wird hier am ehesten getroffen. Die Luecke ist eher fachliche Breite als technisches Fundament. |
| Multi-Channel-Zugriff fuer Nutzer und Agenten | Web-Frontend und Voice/Intent sind vorhanden. Teams/WhatsApp existieren eher als Notification- oder Adapter-Bausteine, nicht als vollwertige Arbeitskanaele fuer Fachdialoge mit dem ERP. | Teilweise erfuellt | Slack/Teams als direkte Arbeitsoberflaechen fuer Wissensabfrage und Prozessausfuehrung sind nicht durchgaengig umgesetzt. |
| Mensch-Agenten-Kollaboration als Unternehmenslogik | Gates, Delegation, Audit und Workflow-Stages sind stark modelliert. Es fehlt aber noch eine sichtbare unternehmensweite Rueckfuehrung neuer Erkenntnisse, Standards und Skills in einen gemeinsamen Wissens- und Skill-Layer. | Teilweise erfuellt | Kollaboration ist technisch vorbereitet, aber nicht als organisationsweites Betriebsmodell fertig ausgebaut. |
| Wissensaufnahme und Wissensveredelung | Dokumenten- und RAG-Komponenten existieren. Es ist aber kein durchgaengiger Standardpfad sichtbar, der Word/PDF/unstrukturierte Inhalte konsistent in agentenlesbare Wissensobjekte ueberfuehrt. | Teilweise erfuellt | Intake-, Normalisierungs- und Governance-Pipeline fuer Unternehmenswissen ist noch nicht als End-to-End-Kernprodukt erkennbar. |
| Offene Schnittstellen / API-first | Sehr stark abgedeckt: OpenAPI, MCP, modulare Services, dokumentierte Integrationsgrenzen, OIDC, Tenant-Header und zahlreiche APIs sind vorhanden. | Erfuellt | Hauptluecke ist weniger die API-Schicht als deren fachlich konsolidierte Nutzung fuer Wissen und Agenten. |
| Controlling / KPI / Read Models | Finance-Read-Models, Cockpit-Modelle, Reporting, Audit- und Prozessdaten sind vorhanden. | Erfuellt bis teilweise erfuellt | Stark fuer Finance und Prozesssicht; fuer ein vollintegriertes unternehmensweites Agenten-Controlling fehlt noch die vereinheitlichte Quersicht. |
| Standardisierung und Kontextinjektion | Vertrage, Rollen, Gates, Policy, Explainability und Agent-Contracts sind stark vorhanden. Die automatische, unternehmensweite Kontextinjektion fuer Markenstil, Richtlinien und Wissensstandards ist jedoch nicht als einheitlicher Produktmechanismus sichtbar. | Teilweise erfuellt | Standards sind modelliert, aber noch nicht konsistent als "always-on context layer" quer ueber alle KI-Prozesse umgesetzt. |
| Rechte und Sicherheit | OIDC, Rollenextraktion, Audit, Delegation und Governance sind gut ausgebaut. Externe Agenten-API-Keys bzw. dedizierte Credentials sind laut Doku noch in Planung. | Teilweise erfuellt | Solides Fundament vorhanden; fuer das Lastenheft fehlt noch die vollstaendige Aussenanbindung externer Agenten unter eigenem Sicherheitsmodell. |
| Onboarding und Wissensweitergabe | Onboarding-Checklisten und Runs existieren im HR-/Training-Kontext. Die automatische Versorgung neuer Mitarbeiter mit Standards, Richtlinien und Best Practices aus einem zentralen Wissenskontext ist noch nicht sichtbar. | Teilweise erfuellt | Onboarding ist eher als HR-Funktion vorhanden, nicht als agentenfaehige Wissenseinweisung. |
| Knowledge Graph / Prozess- und Systemgraph | Prozessgraphen und Data-Lineage-Graphen sind implementiert. Ein echter Unternehmens-Knowledge-Graph fuer Wissen, Entitaeten, Prozesse, Rollen und Kontexte ist nicht erkennbar. | Teilweise erfuellt | Es gibt Graph-Bausteine, aber nicht den im Lastenheft gemeinten zentralen Knowledge Graph. |
| Proaktive Agenteninteraktion | Monitoring-, Worker-, Notification- und Workflow-Bausteine sind vorhanden. Proaktive, fachlich gesteuerte Agenteninteraktion ist aber noch nicht flaechig als Nutzerfunktion sichtbar. | Teilweise erfuellt | Gute technische Vorbedingungen, aber noch keine durchgaengige produktive Assistenzschicht. |
| Voice Agents / Executive Assistants / Agent Teams | Voice-Intent ist vorhanden, NeuroASSIST adressiert agentische Orchestrierung. Vollwertige Voice Agents, Executive Assistants und Agent Teams fuer Fachbereiche sind noch Zukunftsbild bzw. Teilimplementierung. | Weitgehend offen | Das Lastenheft benennt diese Punkte zurecht als Ausbaupfad, nicht als aktuellen Reifegrad. |

## Wichtigste positive Abdeckungen

### 1. API-first und Integrationsfaehigkeit sind bereits real

Das Projekt ist klar nicht mehr nur UI-zentriert. Die Integrationsbasis ist fuer agentenfaehiges Arbeiten bereits stark:

- [docs/AGENT-INTEGRATION.md](../AGENT-INTEGRATION.md)
- [docs/architecture/index.md](../architecture/index.md)
- [app/auth/oidc.py](../../app/auth/oidc.py)
- [app/api/v1/endpoints/agents.py](../../app/api/v1/endpoints/agents.py)

Das ist ein echter Vorsprung gegenueber vielen ERP-Projekten, die zuerst Masken bauen und erst spaeter APIs nachziehen.

### 2. Prozesskernel, Policy und Audit sind ein tragfaehiges Fundament

Der Workflow-/Policy-Kern ist im Repo einer der staerksten Bereiche:

- [docs/architecture/process-kernel/STATUS.md](../architecture/process-kernel/STATUS.md)
- [docs/adr/adr-005-workflow-policy-kern.md](../adr/adr-005-workflow-policy-kern.md)
- [docs/adr/adr-028-workflow-access-control-und-delegation.md](../adr/adr-028-workflow-access-control-und-delegation.md)
- [app/agents/neuroassist_service.py](../../app/agents/neuroassist_service.py)

Das deckt einen grossen Teil der Soll-Anforderungen rund um reproduzierbare Skills, Gates, Nachvollziehbarkeit und kontrollierte Ausfuehrung bereits heute ab.

### 3. Finance- und Prozess-Read-Models sind fuer agentisches Controlling nutzbar

Fuer strukturierte Abfragen und faktenbasierte Antworten ist bereits viel vorhanden:

- [app/api/v1/endpoints/finance_read_models.py](../../app/api/v1/endpoints/finance_read_models.py)
- [app/api/v1/endpoints/finance_invoices.py](../../app/api/v1/endpoints/finance_invoices.py)
- [app/api/v1/endpoints/process_kernel_api.py](../../app/api/v1/endpoints/process_kernel_api.py)

Das entspricht dem Lastenheft deutlich besser als ein reines Chatbot-System ohne strukturierte Datenbasis.

## Groesste fachliche Luecken

### 1. Kein klarer zentraler KI-Wissensspeicher als Produktkern

Es gibt mehrere relevante Bausteine:

- [app/infrastructure/rag/vector_store.py](../../app/infrastructure/rag/vector_store.py)
- [app/infrastructure/rag/indexer.py](../../app/infrastructure/rag/indexer.py)
- [app/workers/rag_indexer.py](../../app/workers/rag_indexer.py)
- [services/ai/app/services/vector_store.py](../../services/ai/app/services/vector_store.py)
- [services/crm-service/app/api/v1/api.py](../../services/crm-service/app/api/v1/api.py)

Aber der Soll-Zustand verlangt mehr als RAG-Faehigkeit. Er verlangt einen zentralen, gepflegten, versionierten Unternehmenswissensspeicher fuer Menschen und Agenten. Genau diese fachliche Mitte ist im IST noch fragmentiert.

### 2. Multi-Channel ist eher "Benachrichtigung" als "Arbeitskanal"

Aktuell sichtbar:

- Voice und Intent-Aufloesung mit Frontend-Anbindung
- Teams-/Webhook-Benachrichtigung in einzelnen Services
- WhatsApp-Adapter im Notifications-Domain-Paket

Belege:

- [services/ki-usability/app/api/v1/endpoints/voice.py](../../services/ki-usability/app/api/v1/endpoints/voice.py)
- [packages/frontend-web/src/features/ki-usability/hooks/useVoiceIntent.ts](../../packages/frontend-web/src/features/ki-usability/hooks/useVoiceIntent.ts)
- [packages/frontend-web/src/components/navigation/TopBar.tsx](../../packages/frontend-web/src/components/navigation/TopBar.tsx)
- [app/services/notification_service.py](../../app/services/notification_service.py)
- [services/inventory/app/integration/notifier.py](../../services/inventory/app/integration/notifier.py)
- [packages/notifications-domain/src/domain/adapters/whatsapp-adapter.ts](../../packages/notifications-domain/src/domain/adapters/whatsapp-adapter.ts)

Was fehlt, ist der eigentliche Soll-Kern: fachliche Fragen und Aktionen direkt in Slack oder Teams mit Rollen, Wissenskontext, Audit und Process Handover.

### 3. Knowledge Graph im Sinne des Lastenhefts fehlt

Vorhanden sind:

- Prozessgraphen
- Dependency-Graphen
- Data-Lineage-Graphen

Belege:

- [app/core/data_lineage_contracts.py](../../app/core/data_lineage_contracts.py)
- [app/core/process_dependency_contracts.py](../../app/core/process_dependency_contracts.py)
- [app/api/v1/endpoints/process_kernel_api.py](../../app/api/v1/endpoints/process_kernel_api.py)

Das ist wertvoll, aber noch kein Unternehmens-Knowledge-Graph, der Wissen, Rollen, Regeln, Prozesse, Entitaeten und Skills gemeinsam modelliert.

### 4. Onboarding ist noch nicht als Wissenskontext-Maschine umgesetzt

Es gibt HR-nahe Onboarding-CRUDs:

- [app/api/v1/endpoints/training.py](../../app/api/v1/endpoints/training.py)

Aber noch nicht sichtbar ist:

- automatische Versorgung mit Standards
- kontextabhaengige Best Practices
- Wissenszugriff fuer neue Mitarbeitende ueber denselben zentralen Agenten-/Wissenslayer

### 5. Externe Agenten sind angebunden, aber noch nicht vollstaendig als eigener Sicherheitsfall

Das Repo ist hier weit, aber noch nicht fertig:

- OpenAPI, MCP, OIDC und Agent-Manifest existieren
- dedizierte API-Keys bzw. Agent-Credentials sind laut Doku noch in Planung

Belege:

- [docs/AGENT-INTEGRATION.md](../AGENT-INTEGRATION.md)
- [app/auth/oidc.py](../../app/auth/oidc.py)

Fuer das Lastenheft ist das relevant, weil Agenten als digitale Akteure mit definierten Rechten und Rollen auftreten sollen.

## Reifegrad nach Lastenheft-Kapiteln

| Kapitel | Reifegrad |
|---|---|
| 1-4 Zielbild, Vision, Projektziele | Architektur und Richtung klar getroffen |
| 5 Nicht-Ziele / Abgrenzung | Gut getroffen, da mehr als Chatbot/DMS/Automatisierung sichtbar ist |
| 6 Zielgruppen | Teilweise getroffen, Fachrollen sichtbar; Agententeams noch nicht breit produktiv |
| 7 Fachliches Grundkonzept | Stark bei Agentenfaehigkeit und Prozesssteuerung, schwach beim zentralen Wissensspeicher |
| 8 Produktanforderungen Muss | API, Security, Audit, Read Models gut; Knowledge Core und Multi-Channel noch lueckig |
| 8 Produktanforderungen Soll/Kann | In vielen Punkten vorbereitet, aber noch nicht durchgaengig produktisiert |
| 9 Kernfunktionen | Controlling, Workflows, Agentik stark; Wissensveredelung und Skill-Rueckfuehrung noch offen |
| 10 Use Cases | Einige bereits plausibel abbildbar, vor allem Finance/Workflow; Marketing/Support/Onboarding noch teilweise |
| 11 Qualitaetsanforderungen | Nachvollziehbarkeit, Skalierbarkeit, Zukunftsfaehigkeit stark; Robustheit des Wissenslayers noch offen |
| 12 Technische Leitplanken | Sehr gut getroffen |
| 13-15 Risiken, Erfolgsfaktoren, Erfolgskriterien | Das Repo zeigt genau, dass Infrastruktur staerker als Wissenszentralisierung ist; hier liegt der Haupthebel |

## Priorisierte GAPs

### Prioritaet A

1. Zentralen KI-Wissensspeicher als Produktkern definieren und verdrahten.
2. Einheitliche Wissensobjekte fuer SOPs, Richtlinien, Produktwissen, Supportwissen, Markt- und Wettbewerbsdaten schaffen.
3. Retrieval-Schicht fuer Menschen und Agenten vereinheitlichen statt RAG, Dokumente und Fachwissen verteilt zu halten.
4. Slack/Teams als echte Arbeitskanaele mit Rollen, Audit und Prozessuebergaben anbinden.

### Prioritaet B

1. Standards- und Kontextinjektions-Layer fuer Markenstil, Richtlinien, Rollenwissen und Freigabelogik produktiv machen.
2. Onboarding mit Wissensspeicher und Agentenkontext koppeln.
3. Wissensveredelungspipeline fuer PDF, Word und Freitext in kanonische Wissensobjekte aufbauen.
4. Externe Agenten mit eigenem Credential- und Delegationsmodell absichern.

### Prioritaet C

1. Knowledge Graph ueber Prozessgraph und Lineage hinaus auf Unternehmenswissen erweitern.
2. Proaktive Agentenfunktionen quer ueber Finance, Support, Marketing und Operations ausrollen.
3. Skill-Rueckfuehrung und organisationsweite Wiederverwendung neuer Skills etablieren.

## Konkrete Handlungsempfehlung

Die naechste Ausbaustufe sollte nicht bei weiteren Einzelmasken oder neuen Einzelagenten beginnen. Der groesste Hebel liegt in einer fachlich klaren Mitte:

1. `Knowledge Core`
2. `Context Injection Layer`
3. `Agent Access + Governance Layer`
4. `Multi-Channel Work Surfaces`

Wenn diese vier Schichten konsistent zusammengezogen werden, schliesst VALEO NeuroERP den groessten Abstand zum Lastenheft. Ohne diese Konsolidierung bleibt das Projekt stark in Architektur und Teilfaehigkeiten, aber noch nicht vollstaendig als agentenfaehige Unternehmensinfrastruktur.

## Endbewertung

Das IST ist fuer ein agentenorientiertes ERP ungewoehnlich weit in Richtung Infrastruktur, Governance und Prozessfaehigkeit. Der eigentliche Soll-Kern des Lastenhefts - ein zentraler, verlaesslicher, unternehmensweiter Wissens- und Agentenarbeitsraum - ist jedoch noch nicht als durchgaengiges Produkt realisiert.

Kurzform:

- stark umgesetzt: API-first, Workflow/Policy, Audit, OIDC, Read Models, Agenten-Grundlagen
- teilweise umgesetzt: RAG, Voice, Notifications, Onboarding, Graph-Bausteine
- klar offen: zentraler KI-Wissensspeicher, echte Teams/Slack-Arbeitskanaele, Knowledge Graph, organisationsweite Skill- und Wissensrueckfuehrung
