# AI & Research Vision

**Zweck:** `Referenzdokument` fuer AI-Leitbild, Forschungsrichtung und Einordnung des Produkts als agentenfaehige Plattform.

VALEO NeuroERP is designed as an experimental open-source ERP and automation platform where classical enterprise resource planning meets AI-assisted workflows. This document outlines the project's AI and research orientation.

## Einordnung

This file is a `derived view` of the AI direction and not the operative delivery source. For implementation and delivery status, use [Process Kernel Status](architecture/process-kernel/STATUS.md), [Architecture Index](architecture/index.md), and [PLAN_GAPS_023_024_043_049.md](../PLAN_GAPS_023_024_043_049.md).

## Goals

- AI-assisted decision-making: support users with intelligent suggestions, automation, and data analysis inside ERP-style environments.
- Automation pipelines: event-driven architecture with reliable async workflows that can be extended with agents and rules.
- Intelligent knowledge systems: structured enterprise data and domain models suitable for LLM integrations, RAG, and agent tooling.

## Relation to Modules

- Finance: AI-assisted bookkeeping, bank reconciliation, and structured journal entries.
- Agrar: harvest acceptance, contracts, drying rules, and pricing logic.
- KI-Usability: unified AI usability layer with voice-to-intent, command palette, shortcuts, and action registry.

## Extensibility for Agents and LLMs

The platform is intended as a modular research and development environment where:

- AI agents can interact with domain APIs and event streams.
- Automation frameworks can plug into the same data structures and workflows.
- Documentation and architecture support both human and AI-assisted development.

## For AI and ML Teams

If you are building agents, RAG, or automation on top of enterprise data, VALEO NeuroERP can work as an open testbed. Use cases and collaborations are welcome via GitHub discussions or issues.

## Referenzen

- [Architecture Index](architecture/index.md)
- [Process Kernel Status](architecture/process-kernel/STATUS.md)
- [Agent Integration](AGENT-INTEGRATION.md)
