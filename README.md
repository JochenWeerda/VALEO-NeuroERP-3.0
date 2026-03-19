# VALEO NeuroERP 3.0 🚀

**Zweck:** Einstiegs- und `Referenzdokument` fuer Produktidee, Projektueberblick und weiterfuehrende Architekturpfade. Nicht der operative Lieferstand.

Experimental **open-source ERP and automation platform** combining classical enterprise resource planning with AI-assisted workflows. A modular research and development environment for AI agents, automation pipelines, and enterprise data.

![Deploy Staging](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/workflows/deploy-staging.yml/badge.svg)
![Security Scan](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/workflows/security-scan.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-blue)
![Version](https://img.shields.io/badge/version-3.0.0-blue)

**Status:** 🚧 **In Development** | **Version:** 3.0.0-alpha | **Authentication:** ✅ OIDC Enabled

*Maintained by a generalist in agricultural trading (field service) with a focus on AI automation – building an open, AI-friendly ERP experimentation platform.*

> ⚠️ **Hinweis:** Das System befindet sich noch in aktiver Entwicklung. Es fehlen noch etliche Tests, GAP-Schließungen und Issue-Resolutionen, bevor es als production-ready eingestuft werden kann.

## 🌟 Key Features

### ✅ Production-Ready Authentication
- **OIDC Integration** with Azure AD, Keycloak, Auth0 support
- **JWT Token Management** with automatic refresh
- **Multi-Provider Support** for enterprise SSO
- **Role-Based Access Control** (RBAC) with scopes

### 🏗️ Modern Architecture
- **Frontend:** React 18 + TypeScript + Vite
- **Backend:** Python FastAPI + PostgreSQL
- **Real-Time:** Server-Sent Events (SSE) + WebSocket support
- **Authentication:** OIDC with JWT tokens
- **Deployment:** Docker + Kubernetes ready

### 🔗 Live API Integration
- **Production Backend Schnittstellen** (not mocks)
- **Real-Time Data Flow** between frontend and backend
- **Comprehensive Error Handling** and logging
- **Request/Response Interceptors** for authentication

## 🏢 Core Domains

| Domain | Status | Description |
|--------|--------|-------------|
| **Inventory** | ✅ Complete | Warehouse management, putaway/slotting, cycle counting |
| **ERP** | ✅ Complete | Order management, core business logic |
| **Finance** | ✅ Complete | AI-powered bookkeeping, bank reconciliation |
| **HR** | ✅ Complete | Employee management, time tracking, payroll |
| **Production** | ✅ Complete | Recipe management, quality control, batch tracking |
| **Sales** | ✅ Complete | Quote and invoice management |
| **Analytics** | ✅ Complete | KPI calculation, forecasting, reporting |
| **Regulatory** | ✅ Complete | Compliance checking, GHG calculations |
| **Logistics** | ✅ Complete | Dispatch, routing, telematics |
| **Quality** | ✅ Complete | CAPA management, non-conformities |
| **Procurement** | ✅ Complete | Supplier risk management |
| **Weighing** | ✅ Complete | Weighing ticket management |

## 🤖 AI & Automation

- **AI-assisted workflows** – Decision support, automation pipelines, and intelligent knowledge systems
- **Event-driven architecture** – NATS JetStream, outbox pattern for reliable async events
- **Extensibility** – Designed for AI agents, LLM integrations, and automation frameworks
- **Voice/Intent & Command Palette** – See [docs/architecture/KI-USABILITY-MICROSERVICES.md](docs/architecture/KI-USABILITY-MICROSERVICES.md) for unified AI usability (voice-to-intent, shortcuts, actions)

See [docs/AI-VISION.md](docs/AI-VISION.md) for the project’s AI and research vision.

## Project Purpose / Ziel und Zweck

### Deutsch

#### 1. Ziel und Zweck des Vorhabens

Mit VALEO NeuroERP soll ein neuartiges ERP-System entstehen, das nicht nur klassische Unternehmensprozesse abbildet, sondern konsequent fuer die Zusammenarbeit von Menschen und KI-Agenten ausgelegt ist.

Im Zentrum steht die Annahme, dass sich Computerarbeit grundlegend veraendert: weg von klassischer UI-zentrierter Softwarebedienung, hin zu einer Arbeitsweise, in der Nutzer als "Manager of Infinite Minds" agieren und operative Aufgaben zunehmend durch KI-Agenten, Skills, APIs und zentrale Wissensspeicher erledigt werden.

VALEO NeuroERP soll dafuer die infrastrukturelle Grundlage schaffen.

#### 2. Ausgangssituation

Unternehmen arbeiten heute meist mit:

- isolierten Softwareloesungen
- unstrukturierten Dokumenten
- manuellen Freigaben
- Wissenssilos
- UI-zentrierten Prozessen
- und nur punktuell eingesetzten KI-Tools

Diese Struktur ist fuer das entstehende Agentenzeitalter nicht ausreichend. KI-Agenten benoetigen:

- strukturierte Daten
- APIs
- maschinenlesbare Inhalte
- standardisierte Skills
- und einen zentralen, verlaesslichen Wissensspeicher

Fehlen diese Grundlagen, bleiben Agenten blind, ungenau oder unsicher.

#### 3. Vision

VALEO NeuroERP soll das Unternehmen in die Lage versetzen, als hybrides System aus Menschen und Agenten zu arbeiten.

Das System soll:

- Unternehmenswissen zentralisieren
- Prozesse fuer Menschen und Agenten gleichermassen zugaenglich machen
- operative Aufgaben automatisieren
- proaktive KI-Assistenz ermoeglichen
- qualitative und quantitative Unternehmensdaten zusammenfuehren
- und damit ein neues Betriebssystem fuer agentenfaehiges Arbeiten bilden

#### 4. Projektziele

##### 4.1 Fachliche Ziele

VALEO NeuroERP soll:

- einen zentralen KI-Wissensspeicher bereitstellen
- ERP-relevante Informationen vereinheitlichen
- Prozesse standardisieren
- Agenten auf Unternehmenswissen zugreifen lassen
- Controlling, Kommunikation, Marketing, Support und operative Ablaeufe KI-faehig machen
- konsistente Ergebnisse ueber Teams hinweg sicherstellen
- Onboarding beschleunigen
- und den Verlust von Wissen beim Ausscheiden von Mitarbeitern verhindern

##### 4.2 Strategische Ziele

Das System soll Unternehmen:

- fuer das Agentenzeitalter kompatibel machen
- unabhaengiger von einzelnen Tools und Hypes machen
- die Grundlage fuer Corporate LLMs, Voice Agents, Chatbots und Agent-Teams liefern
- und eine skalierbare Infrastruktur schaffen, die auch zukuenftige KI-Modelle nutzen kann

#### 5. Nicht-Ziele / Abgrenzung

VALEO NeuroERP ist nicht primaer:

- nur ein Chatbot
- nur ein Wissensmanagementsystem
- nur ein DMS
- nur ein klassisches ERP
- oder nur ein Automatisierungstool

Es soll vielmehr eine integrierte agentenfaehige ERP- und Wissensinfrastruktur sein.

#### 6. Zielgruppen / Nutzergruppen

Das System richtet sich an:

- Geschaeftsfuehrung
- Bereichsleiter
- Controlling
- Vertrieb
- Marketing
- Support
- HR
- IT / Administration
- operative Mitarbeiter
- KI-Agenten / Agententeams als digitale Akteure innerhalb definierter Rechte- und Rollenmodelle

#### 7. Fachliches Grundkonzept

Das fachliche Konzept von VALEO NeuroERP basiert auf fuenf Saeulen:

##### 7.1 Zentraler KI-Wissensspeicher

Alle relevanten Unternehmensinformationen sollen zentral strukturiert gespeichert werden, darunter:

- SOPs
- Produktwissen
- Leistungsbeschreibungen
- Kommunikationsrichtlinien
- Angebote
- Supportwissen
- Wettbewerbsdaten
- Marktdaten
- interne Standards
- Prozessdefinitionen
- quantitative Kennzahlen
- qualitative Wissensinhalte

##### 7.2 Agentenfaehigkeit

Das System muss so aufgebaut sein, dass KI-Agenten nicht ueber grafische Oberflaechen arbeiten muessen, sondern direkt ueber:

- APIs
- Datenbanken
- Skills
- Konnektoren
- und maschinenlesbare Kontexte

##### 7.3 Skill-basierte Prozesssteuerung

Wiederkehrende Aufgaben sollen in standardisierte Skills ueberfuehrt werden, damit Agenten definierte Prozesse reproduzierbar ausfuehren koennen.

##### 7.4 Multi-Channel-Zugriff

Nutzer und Agenten sollen ueber verschiedene Kanaele mit dem System interagieren koennen, z. B.:

- Slack
- Microsoft Teams
- Web-Frontend
- Mobile Interfaces
- Voice Interfaces
- ggf. WhatsApp / Messenger-Kanaele

##### 7.5 Mensch-Agenten-Kollaboration

Das System soll nicht nur Einzelagenten unterstuetzen, sondern kooperative Arbeitsweisen aehnlich einem Schwarmmodell ermoeglichen: Informationen, Ergebnisse, Verbesserungen und neue Skills sollen unternehmensweit verfuegbar gemacht werden koennen.

#### 8. Produktanforderungen

##### 8.1 Muss-Anforderungen

###### 8.1.1 Wissensspeicher

Das System muss:

- einen zentralen Wissensspeicher bereitstellen
- strukturierte und maschinenlesbare Formate unterstuetzen
- qualitative und quantitative Daten verarbeiten
- Versionierung und Pflege von Wissen ermoeglichen
- Silos aus unterschiedlichen Quellen zusammenfuehren

###### 8.1.2 Datenformate

Das System muss bevorzugt mit agentenfaehigen Formaten arbeiten, insbesondere:

- Markdown
- JSON
- strukturierte Tabellen
- relationale Daten
- API-Ressourcen

PDFs, Word-Dateien und andere menschenzentrierte Formate duerfen nur als Eingangsquellen dienen und sollen intern in agentenlesbare Formate transformiert werden.

###### 8.1.3 Schnittstellen

Das System muss offene Schnittstellen bieten fuer:

- ERP-Module
- CRM
- DMS
- Kommunikationssysteme
- Datenbanken
- BI-Systeme
- externe KI-Modelle
- Automatisierungstools
- Voice-Agent-Plattformen
- Connectoren / MCP-artige Anbindungen

###### 8.1.4 Agentenarbeitsfaehigkeit

Das System muss Agenten ermoeglichen:

- auf Wissen zuzugreifen
- Aufgaben zu planen
- strukturierte Ergebnisse zurueckzugeben
- standardisierte Skills auszufuehren
- quantitative Daten korrekt abzufragen
- qualitative Inhalte zu erzeugen
- proaktiv Hinweise oder Aufgaben auszuloesen
- unter Rechtekontrolle zu operieren

###### 8.1.5 Kommunikationsintegration

Das System muss ueber Unternehmenskommunikationskanaele bedienbar sein, insbesondere:

- Slack
- Microsoft Teams

Fragen wie Umsatzentwicklung, Richtlinien, Handlungsempfehlungen oder Prozesswissen sollen dort direkt beantwortbar sein.

###### 8.1.6 Controlling-Faehigkeit

Das System muss:

- auf Unternehmenskennzahlen zugreifen koennen
- SQL-aehnliche Abfragen unterstuetzen
- Dashboards und Analysen bereitstellen
- Quartalsentwicklungen, Trends und Auswertungen liefern
- Halluzinationen durch strukturierte Datenzugriffe minimieren

###### 8.1.7 Standardisierung und Kontextinjektion

Das System muss Unternehmensstandards automatisch in KI-gestuetzte Arbeitsprozesse einfliessen lassen, insbesondere:

- Kommunikationsrichtlinien
- Markenstil
- Formulierungsstandards
- Freigabelogiken
- Rollenwissen
- Produktkontext
- Zielgruppenverstaendnis

Nutzer sollen nicht jeden Kontext jedes Mal neu prompten muessen.

###### 8.1.8 Rechte und Sicherheit

Das System muss:

- rollenbasiert arbeiten
- Zugriffe von Menschen und Agenten trennen koennen
- Systeme sicher anbinden
- Protokollierung ermoeglichen
- kritische Aktionen absichern
- Sicherheitsrisiken bei agentischem Zugriff minimieren

##### 8.2 Soll-Anforderungen

Das System soll:

- proaktive Agenteninteraktion ermoeglichen
- Erinnerungen, Empfehlungen oder Aufgaben initiieren
- Knowledge Graphs zur Visualisierung von Prozessen und Systemzusammenhaengen anbieten
- Onboarding-Prozesse unterstuetzen
- Best Practices teamweit verfuegbar machen
- Optimierungen aus Teamschwarm-Logik in Standards ueberfuehren

##### 8.3 Kann-Anforderungen

Das System kann spaeter ergaenzen:

- Voice Agents
- automatisierte Content-Produktion
- Social-Media-Workflows
- Agententeams fuer Fachbereiche
- Executive Assistants
- autonome Monitoring-Agenten
- automatische Skill-Erstellung aus beobachteten Prozessen

#### 9. Fachliche Kernfunktionen

##### 9.1 Wissensaufnahme

Erfassung und Strukturierung von:

- Handbuechern
- SOPs
- E-Mails
- Supportwissen
- Richtlinien
- Praesentationen
- Angebotslogiken
- Finanzdaten
- Prozesswissen
- Medieninhalten

##### 9.2 Wissensabfrage

Beantwortung fachlicher Fragen aus allen Unternehmensbereichen ueber natuerliche Sprache.

##### 9.3 Wissensveredelung

Umwandlung unstrukturierter Inhalte in agentenlesbare und standardisierte Wissensobjekte.

##### 9.4 Skill-Verwaltung

Anlage, Verwaltung und Ausfuehrung standardisierter Skills fuer definierte Anwendungsfaelle.

##### 9.5 Agentenorchestrierung

Koordination mehrerer Agenten oder spezialisierter Agentenrollen.

##### 9.6 KPI- und Controlling-Funktion

Verknuepfung von quantitativen Datenquellen mit qualitativen Empfehlungen.

##### 9.7 Kommunikations- und Arbeitslayer

Zugriff ueber Chat, Teams, Slack, Web und perspektivisch Sprache.

##### 9.8 Prozess- und Systemgraph

Visualisierung von Datenstroemen, Systemabhaengigkeiten, Prozessverknuepfungen und Wissensbeziehungen.

#### 10. Beispielhafte Use Cases

##### 10.1 Vertriebsanalyse

Ein Nutzer fragt im Chat:
"Wie hat sich der Umsatz quartalsweise entwickelt und welches Quartal war am staerksten?"

Das System greift auf strukturierte Finanzdaten zu und antwortet faktenbasiert.

##### 10.2 Marketing-Content

Ein Agent erhaelt ein Video und erstellt daraus nach Unternehmensstandard eine Social-Media-Story im Corporate Design.

##### 10.3 Support-Wissenszugriff

Ein Mitarbeiter stellt eine Kundenfrage im Teams-Chat und erhaelt eine konsistente Antwort auf Basis des zentralen Wissens.

##### 10.4 Onboarding

Neue Mitarbeiter erhalten ueber den Systemkontext automatisch Zugriff auf relevante Standards, Richtlinien und Best Practices.

##### 10.5 Prozessoptimierung

Ein Agent oder Team identifiziert eine bessere Vorgehensweise und spielt diese als neuen Standard in den Workspace zurueck.

#### 11. Qualitaetsanforderungen

VALEO NeuroERP muss folgende Qualitaetsmerkmale erfuellen:

##### 11.1 Konsistenz

Antworten und Ergebnisse sollen auf Unternehmensstandards basieren.

##### 11.2 Nachvollziehbarkeit

Datenquellen, Antworten und Agentenaktionen sollen protokollierbar sein.

##### 11.3 Skalierbarkeit

Das System soll mit wachsender Datenmenge, Nutzerzahl und Agentenzahl skalieren.

##### 11.4 Zukunftsfaehigkeit

Die Architektur soll modellagnostisch sein, sodass neue KI-Modelle integrierbar bleiben.

##### 11.5 Sicherheit

Besonderes Augenmerk gilt agentischem Zugriff auf Systeme und Daten.

##### 11.6 Robustheit

Fehlende oder schlechte Datenqualitaet soll erkennbar werden; riskante Schlussfolgerungen sollen begrenzt werden.

#### 12. Technische Leitplanken

Die konkrete technische Umsetzung ist Teil des Pflichtenhefts. Aus fachlicher Sicht gelten folgende Leitplanken:

- API-first-Architektur
- zentrale Daten- und Wissensschicht
- Trennung von Wissensspeicher, Agentenlayer und Frontends
- modulare Integrationsfaehigkeit
- Nutzung strukturierter Datenmodelle
- Unterstuetzung maschinenlesbarer Formate
- Anschlussfaehigkeit an KI-Modelle und Automatisierungsdienste

#### 13. Risiken

Folgende Risiken sind zu beruecksichtigen:

- fehlende Datenstruktur im Unternehmen
- Wissenssilos
- Abhaengigkeit von unsauberen Quelldaten
- Sicherheitsprobleme durch zu weitreichende Agentenrechte
- falsche Priorisierung auf Tools statt Infrastruktur
- mangelnde Akzeptanz im Team
- fehlende Governance bei Standards und Wissenspflege

#### 14. Erfolgsfaktoren

Der Erfolg haengt wesentlich davon ab, dass:

- zuerst das Fundament geschaffen wird
- Wissen strukturiert und zentralisiert wird
- APIs sauber verfuegbar sind
- Standards definiert sind
- Menschen und Agenten gemeinsam gedacht werden
- und das System nicht als Einzeltool, sondern als Unternehmensinfrastruktur verstanden wird

#### 15. Erfolgskriterien / Abnahmekriterien

VALEO NeuroERP gilt fachlich als erfolgreich, wenn:

- ein zentraler KI-Wissensspeicher produktiv nutzbar ist
- Mitarbeiter ueber Chat-/Arbeitskanaele auf Unternehmenswissen zugreifen koennen
- quantitative und qualitative Fragen beantwortbar sind
- definierte Skills reproduzierbar ausgefuehrt werden
- Unternehmensstandards automatisch in KI-Arbeitsprozesse einfliessen
- erste Agentenprozesse sicher und messbar produktiv laufen
- und das System als Grundlage weiterer Agentenloesungen dient

#### 16. Zusammenfassung der Kernanforderung

VALEO NeuroERP soll kein klassisches ERP mit KI-Add-on sein, sondern eine agentenfaehige Unternehmensinfrastruktur, deren Kern aus einem strukturierten Wissensspeicher, offenen Schnittstellen, standardisierten Skills und einer kollaborativen Mensch-Agenten-Arbeitslogik besteht.

### English

#### 1. Objective and Purpose of the Initiative

VALEO NeuroERP is intended to become a new kind of ERP system that not only models traditional business processes, but is consistently designed for collaboration between humans and AI agents.

At its core is the assumption that computer-based work is changing fundamentally: away from classic UI-centered software operation, toward a way of working in which users act as "Managers of Infinite Minds" and operational tasks are increasingly handled by AI agents, skills, APIs, and central knowledge stores.

VALEO NeuroERP is intended to provide the infrastructure foundation for this shift.

#### 2. Initial Situation

Today, companies mostly work with:

- isolated software solutions
- unstructured documents
- manual approvals
- knowledge silos
- UI-centered processes
- and AI tools that are only used selectively

This structure is not sufficient for the emerging agent era. AI agents require:

- structured data
- APIs
- machine-readable content
- standardized skills
- and a central, reliable knowledge store

Without these foundations, agents remain blind, imprecise, or unreliable.

#### 3. Vision

VALEO NeuroERP is intended to enable companies to operate as a hybrid system of humans and agents.

The system is intended to:

- centralize enterprise knowledge
- make processes equally accessible to humans and agents
- automate operational tasks
- enable proactive AI assistance
- combine qualitative and quantitative business data
- and thereby form a new operating system for agent-ready work

#### 4. Project Goals

##### 4.1 Functional Goals

VALEO NeuroERP is intended to:

- provide a central AI knowledge store
- unify ERP-relevant information
- standardize processes
- allow agents to access enterprise knowledge
- make controlling, communication, marketing, support, and operational workflows AI-capable
- ensure consistent results across teams
- accelerate onboarding
- and prevent knowledge loss when employees leave

##### 4.2 Strategic Goals

The system is intended to help companies:

- become compatible with the agent era
- become less dependent on individual tools and hype cycles
- build the foundation for corporate LLMs, voice agents, chatbots, and agent teams
- and create a scalable infrastructure that can also leverage future AI models

#### 5. Non-Goals / Scope Boundaries

VALEO NeuroERP is not primarily:

- just a chatbot
- just a knowledge management system
- just a DMS
- just a traditional ERP
- or just an automation tool

Instead, it is intended to be an integrated, agent-ready ERP and knowledge infrastructure.

#### 6. Target Groups / User Groups

The system is aimed at:

- executive management
- department heads
- controlling
- sales
- marketing
- support
- HR
- IT / administration
- operational staff
- AI agents / agent teams as digital actors within defined rights and role models

#### 7. Functional Core Concept

The functional concept of VALEO NeuroERP is based on five pillars:

##### 7.1 Central AI Knowledge Store

All relevant company information should be stored centrally in a structured form, including:

- SOPs
- product knowledge
- service descriptions
- communication guidelines
- offers
- support knowledge
- competitor data
- market data
- internal standards
- process definitions
- quantitative metrics
- qualitative knowledge content

##### 7.2 Agent Capability

The system must be designed so that AI agents do not have to work through graphical interfaces, but directly via:

- APIs
- databases
- skills
- connectors
- and machine-readable contexts

##### 7.3 Skill-Based Process Control

Recurring tasks should be transformed into standardized skills so that agents can execute defined processes reproducibly.

##### 7.4 Multi-Channel Access

Users and agents should be able to interact with the system through multiple channels, for example:

- Slack
- Microsoft Teams
- web frontend
- mobile interfaces
- voice interfaces
- where applicable, WhatsApp / messenger channels

##### 7.5 Human-Agent Collaboration

The system should not only support individual agents, but also enable collaborative ways of working similar to a swarm model: information, results, improvements, and new skills should be made available across the company.

#### 8. Product Requirements

##### 8.1 Must-Have Requirements

###### 8.1.1 Knowledge Store

The system must:

- provide a central knowledge store
- support structured and machine-readable formats
- process qualitative and quantitative data
- enable versioning and maintenance of knowledge
- consolidate silos from different sources

###### 8.1.2 Data Formats

The system must primarily work with agent-ready formats, especially:

- Markdown
- JSON
- structured tables
- relational data
- API resources

PDFs, Word files, and other human-centered formats may only serve as input sources and should be transformed internally into agent-readable formats.

###### 8.1.3 Interfaces

The system must offer open interfaces for:

- ERP modules
- CRM
- DMS
- communication systems
- databases
- BI systems
- external AI models
- automation tools
- voice-agent platforms
- connectors / MCP-like integrations

###### 8.1.4 Agent Work Capability

The system must enable agents to:

- access knowledge
- plan tasks
- return structured results
- execute standardized skills
- query quantitative data correctly
- generate qualitative content
- proactively trigger hints or tasks
- operate under rights control

###### 8.1.5 Communication Integration

The system must be operable through enterprise communication channels, especially:

- Slack
- Microsoft Teams

Questions such as revenue development, policies, recommendations for action, or process knowledge should be answerable directly there.

###### 8.1.6 Controlling Capability

The system must:

- be able to access business metrics
- support SQL-like queries
- provide dashboards and analyses
- deliver quarterly developments, trends, and evaluations
- minimize hallucinations through structured data access

###### 8.1.7 Standardization and Context Injection

The system must automatically inject company standards into AI-supported work processes, especially:

- communication guidelines
- brand style
- wording standards
- approval logic
- role knowledge
- product context
- target-group understanding

Users should not have to re-prompt every context every time.

###### 8.1.8 Rights and Security

The system must:

- work on a role-based basis
- separate access by humans and agents
- connect systems securely
- enable logging
- secure critical actions
- minimize security risks in agentic access

##### 8.2 Should-Have Requirements

The system should:

- enable proactive agent interaction
- initiate reminders, recommendations, or tasks
- offer knowledge graphs for visualizing processes and system relationships
- support onboarding processes
- make best practices available across teams
- turn optimizations from team-swarm logic into standards

##### 8.3 Could-Have Requirements

The system may later add:

- voice agents
- automated content production
- social media workflows
- agent teams for business functions
- executive assistants
- autonomous monitoring agents
- automatic skill creation from observed processes

#### 9. Functional Core Features

##### 9.1 Knowledge Ingestion

Capture and structuring of:

- manuals
- SOPs
- emails
- support knowledge
- policies
- presentations
- offer logic
- financial data
- process knowledge
- media content

##### 9.2 Knowledge Retrieval

Answering business questions from all company areas through natural language.

##### 9.3 Knowledge Refinement

Transformation of unstructured content into agent-readable and standardized knowledge objects.

##### 9.4 Skill Management

Creation, management, and execution of standardized skills for defined use cases.

##### 9.5 Agent Orchestration

Coordination of multiple agents or specialized agent roles.

##### 9.6 KPI and Controlling Function

Linking quantitative data sources with qualitative recommendations.

##### 9.7 Communication and Work Layer

Access via chat, Teams, Slack, web, and prospectively voice.

##### 9.8 Process and System Graph

Visualization of data flows, system dependencies, process links, and knowledge relationships.

#### 10. Example Use Cases

##### 10.1 Sales Analysis

A user asks in chat:
"How has revenue developed quarter by quarter, and which quarter was the strongest?"

The system accesses structured financial data and responds factually.

##### 10.2 Marketing Content

An agent receives a video and creates a social media story in the corporate design according to company standards.

##### 10.3 Support Knowledge Access

An employee asks a customer question in a Teams chat and receives a consistent answer based on the central knowledge store.

##### 10.4 Onboarding

New employees automatically receive access to relevant standards, guidelines, and best practices through system context.

##### 10.5 Process Optimization

An agent or team identifies a better way of working and feeds it back into the workspace as a new standard.

#### 11. Quality Requirements

VALEO NeuroERP must fulfill the following quality characteristics:

##### 11.1 Consistency

Answers and results should be based on company standards.

##### 11.2 Traceability

Data sources, answers, and agent actions should be loggable.

##### 11.3 Scalability

The system should scale with growing data volume, user count, and agent count.

##### 11.4 Future Readiness

The architecture should be model-agnostic so that new AI models remain integrable.

##### 11.5 Security

Particular attention must be paid to agentic access to systems and data.

##### 11.6 Robustness

Missing or poor data quality should become visible; risky conclusions should be limited.

#### 12. Technical Guardrails

The concrete technical implementation is part of the detailed specification. From a functional perspective, the following guardrails apply:

- API-first architecture
- central data and knowledge layer
- separation of knowledge store, agent layer, and frontends
- modular integration capability
- use of structured data models
- support for machine-readable formats
- connectivity to AI models and automation services

#### 13. Risks

The following risks must be considered:

- missing data structure within the company
- knowledge silos
- dependence on poor-quality source data
- security issues caused by overly broad agent permissions
- wrong prioritization of tools instead of infrastructure
- lack of acceptance in the team
- missing governance for standards and knowledge maintenance

#### 14. Success Factors

Success depends largely on the following:

- the foundation is built first
- knowledge is structured and centralized
- APIs are cleanly available
- standards are defined
- humans and agents are designed together
- and the system is understood as company infrastructure rather than a standalone tool

#### 15. Success Criteria / Acceptance Criteria

VALEO NeuroERP is functionally successful when:

- a central AI knowledge store is productively usable
- employees can access enterprise knowledge through chat and work channels
- quantitative and qualitative questions can be answered
- defined skills are executed reproducibly
- company standards automatically flow into AI work processes
- initial agent processes run safely, measurably, and productively
- and the system serves as the foundation for further agent solutions

#### 16. Summary of the Core Requirement

VALEO NeuroERP is not intended to be a traditional ERP with an AI add-on, but an agent-ready enterprise infrastructure whose core consists of a structured knowledge store, open interfaces, standardized skills, and a collaborative human-agent work logic.

## Architecture Guidance

- [Architecture Index](docs/architecture/index.md)
- [Target State Landhandel ERP](docs/architecture/target-state-landhandel-erp.md)
- [ADR-003 Canonical Domain Model](docs/adr/adr-003-canonical-domain-model.md)
- [ADR-004 Command-/Action-Layer](docs/adr/adr-004-command-action-layer.md)
- [ADR-005 Workflow-/Policy-Kern](docs/adr/adr-005-workflow-policy-kern.md)
- [ADR-006 Read-Model / Query-Contract-Prinzip](docs/adr/adr-006-read-model-query-contract-prinzip.md)
- [ADR-007 Agent-/Tool-Contract-Governance](docs/adr/adr-007-agent-tool-contract-governance.md)

## 📸 Screenshots

| Dashboard / Navigation | Finance – Open Items | Agrar – Ernteannahme |
|------------------------|----------------------|----------------------|
| ![Dashboard](docs/screenshots/dashboard.png?v=2) | ![Finance](docs/screenshots/finance.png?v=2) | ![Agrar](docs/screenshots/agrar.png?v=2) |

Screenshots are from staging or local. Add `dashboard.png`, `finance.png`, and `agrar.png` to [docs/screenshots/](docs/screenshots/) (see [docs/screenshots/README.md](docs/screenshots/README.md) for how to capture them).

## 🚀 Quick Start

### Prerequisites
- **Git** (for cloning)
- **Docker & Docker Compose** (for local development)
- **OIDC Provider** (Azure AD, Keycloak, or Auth0 for production auth)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/JochenWeerda/VALEO-NeuroERP-3.0.git
cd VALEO-NeuroERP-3.0
```

2. **Start the complete stack:**
```bash
# Start all services (databases, backend, frontend)
docker-compose up -d

# Or start individual components
docker-compose up -d postgres redis
python main.py  # Backend API
cd packages/frontend-web && npm run dev  # Frontend
```

3. **Datenbank-Migrationen ausführen (alle Tabellen anlegen):**
```bash
# Nach Neuinstallation oder Clone: Alle Schemas und Tabellen anlegen
alembic upgrade head
```
Dabei werden alle im Repository enthaltenen Alembic-Migrationen nacheinander angewendet (domain_shared, domain_ops, domain_erp, domain_inventory, domain_crm, domain_finance, …). Ohne diesen Schritt fehlen Tabellen und die API kann fehlschlagen.

### Frontend Commands (pnpm)

```bash
cd packages/frontend-web
pnpm install
pnpm dev          # Start Vite Dev-Server
pnpm build        # Production Build
pnpm typecheck    # TypeScript Project Check
pnpm lint         # ESLint (fails on warnings)
pnpm storybook    # UI Workbench
```

4. **Configure Authentication:**
```bash
# Copy environment template
cp .env.example .env

# Configure your OIDC provider in .env:
# VITE_OIDC_DISCOVERY_URL=https://your-provider.com/.well-known/openid_configuration
# VITE_OIDC_CLIENT_ID=your-client-id
# API_DEV_TOKEN=dev-token  # Change for local security
```

5. **Access the application:**
- **Frontend:** http://localhost:3000
- **Backend Modul:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

## 🔐 Authentication Setup

### Production OIDC Configuration

The system supports multiple OIDC providers:

#### Azure Active Directory
```env
VITE_OIDC_DISCOVERY_URL=https://login.microsoftonline.com/YOUR_TENANT_ID/v2.0/.well-known/openid_configuration
VITE_OIDC_CLIENT_ID=your-azure-client-id
```

#### Keycloak
```env
VITE_OIDC_DISCOVERY_URL=https://your-keycloak.com/realms/YOUR_REALM/.well-known/openid_configuration
VITE_OIDC_CLIENT_ID=your-keycloak-client-id
```

#### Auth0
```env
VITE_OIDC_DISCOVERY_URL=https://your-domain.auth0.com/.well-known/openid_configuration
VITE_OIDC_CLIENT_ID=your-auth0-client-id
```

### Development Mode
For development without OIDC setup, the system includes demo authentication endpoints (not for production use).

## 📊 System Status

| Component | Status | Health Check |
|-----------|--------|--------------|
| **Frontend** | ✅ Running | http://localhost:3000 |
| **Backend API** | ✅ Running | http://localhost:8000/healthz |
| **Database** | ✅ Running | PostgreSQL 15+ |
| **Authentication** | ✅ Configured | OIDC with JWT |
| **Real-Time Events** | ✅ Active | SSE WebSocket |
| **API Integration** | ✅ Verified | Production endpoints |

## 🛠️ Development

### Project Structure
```
├── packages/
│   ├── frontend-web/          # React frontend with authentication
│   ├── inventory-domain/      # Inventory management
│   ├── erp-domain/           # ERP core functionality
│   ├── finance-domain/       # Financial services
│   └── ...                   # Other domain modules
├── app/                      # Python FastAPI backend
├── main.py                   # Main application entry point
├── docker-compose.yml        # Complete stack definition
└── docs/                     # Documentation
```

### Key Technologies
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS
- **Backend:** Python 3.11, FastAPI, PostgreSQL, Redis
- **Authentication:** OIDC, JWT, OAuth2
- **Real-Time:** Server-Sent Events, WebSocket
- **Deployment:** Docker, Kubernetes, Helm
- **Monitoring:** Prometheus, Grafana, Loki

## 🔒 Security Features

- ✅ **OIDC Authentication** with enterprise providers
- ✅ **JWT Token Management** with secure storage
- ✅ **CORS Configuration** for cross-origin requests
- ✅ **Rate Limiting** and request throttling
- ✅ **Input Validation** and sanitization
- ✅ **Audit Logging** for all operations
- ✅ **Role-Based Access Control** (RBAC)

## 🚢 Deployment

### Staging Deployment (Docker Desktop on Windows)

**Quick-Start:**
```powershell
# Deploy Staging-Stack
.\scripts\staging-deploy.ps1

# Run Smoke-Tests
.\scripts\smoke-tests-staging.sh

# Access Frontend
# http://localhost:3001
# Login: test-admin / Test123!
```

**Auto-Deploy via GitHub Actions:**
```bash
# Push to develop branch triggers automatic deployment
git push origin develop

# Or manually trigger via GitHub UI:
# https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/workflows/deploy-staging.yml
```

**Dokumentation:**
- [STAGING-DEPLOYMENT.md](./STAGING-DEPLOYMENT.md) - Vollständige Staging-Anleitung
- [GITHUB-ACTIONS-STAGING-SETUP.md](./GITHUB-ACTIONS-STAGING-SETUP.md) - Auto-Deploy Setup
- [scripts/README.md](./scripts/README.md) - Scripts-Dokumentation

### Production Deployment
```bash
# Build and deploy with Docker
docker-compose -f docker-compose.prod.yml up -d

# Or deploy to Kubernetes
kubectl apply -f k8s/
```

**Dokumentation:**
- [DEPLOYMENT-PLAN.md](./DEPLOYMENT-PLAN.md) - Production-Deployment-Plan
- [PRODUCTION-AUTH-SETUP.md](./PRODUCTION-AUTH-SETUP.md) - Authentication-Setup
- [docs/db/l3_import.md](./docs/db/l3_import.md) - L3 Datenimport & Bootstrap

### Environment Configuration
- **Development:** `.env` with local configuration (`API_DEV_TOKEN`, `API_URL`, database DSN)
- **Frontend Dev:** `packages/frontend-web/env.example` (`VITE_API_DEV_TOKEN`, `VITE_API_BASE_URL`)
- **Staging:** `env.example.staging` - Docker Desktop (Windows)
- **Production:** Environment variables or Kubernetes secrets
- **Feature Flags:** `VITE_FEATURE_SSE`, `VITE_FEATURE_COMMAND_PALETTE`, `VITE_FEATURE_AGRAR` (remote overrides via `VITE_FLAGS_URL`, fallback to `/flags.json`)

### Database Init & Seed Data
```bash
# Start local PostgreSQL (falls noch nicht vorhanden)
docker run --name neuroerp-db -d \
  -e POSTGRES_DB=valeo_neuro_erp \
  -e POSTGRES_USER=valeo_dev \
  -e POSTGRES_PASSWORD=REDACTED_PASSWORD \
  -p 5432:5432 postgres:15

# Initialize database schema (runs SQLAlchemy Base metadata)
PYTHONPATH=. python scripts/init_db.py

# Insert sample inventory data for POS/Inventory views
PYTHONPATH=. python -m app.seeds.inventory_seed
```

> Playwright API checks require `API_URL` (and optionally `API_DEV_TOKEN`) to be exported before running `pnpm playwright test`.

### OIDC / Auth Setup
- Schnelleinführung: siehe `docs/setup/oidc_dev_setup.md` für Dev-Token, Keycloak-Docker und Provider-spezifische Hinweise.
- Für produktive Tenants Dev-Token deaktivieren und Tokens per JWT verifizieren (siehe Roadmap Phase 2).
- Relevante Variablen: `OIDC_CLIENT_ID`, `OIDC_ISSUER_URL`, `OIDC_JWKS_URL` (werden sonst aus Keycloak-Einstellungen abgeleitet).

## 📈 Monitoring & Observability

- **Metrics:** Prometheus metrics at `/metrics`
- **Logging:** Structured JSON logging with Loki
- **Tracing:** OpenTelemetry distributed tracing
- **Dashboards:** Grafana dashboards for system monitoring
- **Health Checks:** `/healthz` and `/readyz` endpoints

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

We use the [good first issue](.github/ISSUE_TEMPLATE/good_first_issue.md) template for small, contributor-friendly tasks. AI-assisted development is welcome. Please mark AI involvement in commit messages (e.g. `[AI-Assisted]` or `[AI-Generated]`) and in PR descriptions so that reviewers have full transparency.

## 📄 License

MIT License – see [LICENSE](LICENSE). Copyright (c) 2024 Jochen Weerda.

## 🆘 Support

- **Documentation:** See `/docs` folder
- **API Documentation:** http://localhost:8000/docs when running
- **Health Check:** `/healthz` endpoint

## Referenzen

- [Process Kernel Status](docs/architecture/process-kernel/STATUS.md)
- [Process Kernel Delivery Map](docs/architecture/process-kernel/DELIVERY-MAP.md)
- [Architecture Index](docs/architecture/index.md)
- [AI Vision](docs/AI-VISION.md)
- [Agent Integration](docs/AGENT-INTEGRATION.md)

---

**🆕 Latest Updates**

- ✅ Staging deployment automated (Docker Desktop + GitHub Actions)
- ✅ 18 automated smoke tests for staging
- ✅ OIDC authentication, real API integration, frontend-backend integration
- ✅ Finance module with 23+ backend APIs, IBAN lookup, i18n (German)
- 🤖 AI & automation focus – event-driven architecture, extensible for agents and workflows

**Repository:** https://github.com/JochenWeerda/VALEO-NeuroERP-3.0

