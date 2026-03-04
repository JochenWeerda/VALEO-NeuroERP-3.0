# AI & Research Vision

VALEO NeuroERP is designed as an **experimental open-source ERP and automation platform** where classical enterprise resource planning meets AI-assisted workflows. This document outlines the project’s AI and research orientation.

## Goals

- **AI-assisted decision-making** – Support users with intelligent suggestions, automation, and data analysis inside ERP-style environments.
- **Automation pipelines** – Event-driven architecture (NATS JetStream, outbox pattern) for reliable async workflows that can be extended with agents and rules.
- **Intelligent knowledge systems** – Structured enterprise data and domain models that are suitable for LLM integrations, RAG, and agent tooling.

## Relation to modules

- **Finance** – AI-powered bookkeeping, bank reconciliation, and structured journal entries; suitable for automation and consistency checks.
- **Agrar** – Harvest acceptance, contracts, drying rules, and pricing; rich domain logic for decision support and automation.
- **KI-Usability** – Unified AI usability layer: voice-to-intent, command palette, shortcuts, and action registry. See [architecture/KI-USABILITY-MICROSERVICES.md](architecture/KI-USABILITY-MICROSERVICES.md).

## Extensibility for agents and LLMs

The platform is intended as a **modular research and development environment** where:

- AI agents can interact with domain APIs and event streams.
- Automation frameworks can plug into the same data structures and workflows.
- Documentation and architecture support both human and AI-assisted development (e.g. [CLAUDE.md](../CLAUDE.md) for repository context).

Claude and other AI tools would be valuable for code generation, refactoring, documentation, architectural planning, and designing AI-assisted workflows and knowledge systems. This vision aligns with the project’s use as a foundation for experimenting with AI-driven enterprise tools.
