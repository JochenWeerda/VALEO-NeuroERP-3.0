---
title: Child tenant producers after RLS integration
type: reference
audience: [entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-10-28
version: 1.0.0
description: Explicit parent tenant propagation and pending canonical SQL acceptance.
---

# Child tenant producers

Strict CI exposes producers predating the mandatory child tenant columns.
HarvestAcceptancePosition now maps tenant_id and both creation paths explicitly
set it from the service tenant. No default tenant is introduced. Recipe fixture
components and the existing procurement seed helper explicitly reuse their
already specified parent tenant. No assertion or schema constraint is removed.

The existing harvest service unit suite passes 14 cases. Two new cases invoke
the real creation service and real ORM models with a mocked transaction for two
distinct tenants: head/child tenant and parent ID agree, quantity is retained,
and exactly one commit is requested. This proves producer behavior, not SQL RLS.

Actual strict SQL reruns remain pending until the coordinated existing probe
upgrade can proceed without foreign sessions. The current probe revision is
loading_stop_fk_20261023; no reset, new database/container or live migration was
performed. The code correction is reviewable; this document explicitly leaves
the mandatory SQL acceptance open.
