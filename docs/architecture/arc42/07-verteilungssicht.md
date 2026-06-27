---
title: arc42 — 7. Verteilungssicht
type: explanation
audience: [entwickler, betrieb]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-27
version: 1.0.0
---

# 7. Verteilungssicht

## Deployment (Development)

Standard-Stack: `docker compose up` — siehe [Lokales Setup](../../entwickler/lokales-setup.md).

Container-Liste abgeleitet aus [`docker-compose.yml`](../../../docker-compose.yml):

→ **[Container-Inventar](../../entwickler/container-inventory.md)** (Generator: `scripts/generate_container_inventory.py`)

## Netzwerk

Alle Anwendungs-Container im Docker-Netzwerk `valeo-network`. Frontend (3000) proxied `/api/v1` → Backend (8000), `/api/mcp` → BFF (4001).

## Production

→ [Production Readiness](../../admin/production-readiness-runbook.md), `docker-compose.production.yml` (Prometheus, Grafana, Loki)

[← Kapitel 6](06-laufzeitsicht.md) | [Kapitel 8 →](08-querschnitt.md)
