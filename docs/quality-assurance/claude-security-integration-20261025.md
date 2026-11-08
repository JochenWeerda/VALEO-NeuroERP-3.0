---
title: Integration der beiden Claude-Sicherheitslieferungen
type: verification
owner: Codex
status: geprueft
last_reviewed: 2026-10-25
---

# Gepruefte Zusammenfuehrung

Quelle: claude/dev-dependency-security-20261025, Commit5468de5ce, einschliesslich der gestapelten Produktionskorrekturen aus PR40. Gemeinsame Basis28d85dedb.146 geaenderte Pfade wurden gegen Basis und vorhandene Reparaturansicht vor dem Kopieren auf Konflikte geprueft. Nur der append-only Workboardteil wurde zusammengefuehrt. Keine aktiven Studio-/DMS-/Workspaceaenderungen ueberschrieben, keine Rootkopie oder gemeinsame Installation geaendert.

GitHub direkt verifiziert: Security Scan40198322483 auf5f7a6b2de success. Quality Gate40198929357 auf7e5e41674: Dependency Scan, Improvement integrity und weitere unabhaengige Gates success; Backend/Frontend bleiben mit den dokumentierten Altbefunden rot. Keine Gesamtfreigabe.

49 Sicherheitsregressionen der gelieferten Quellen erneut bestanden, mit bereits vorhandener passender Installation aus wt-depsec. Zod4.6.7/Vitest4.1.12 dort direkt verifiziert. Dies ist keine neue Frozen-Installation; der reproduzierbare Installationsnachweis stammt aus Claudes separat dokumentierter Lieferung und wird im neuen CI erneut geprueft.

Artillery/Detox und ihre unbenutzten Sicherheitspatches werden nicht wieder eingefuehrt. Node-forge bleibt an unveraenderte Quell-/Manifest-/Locknachweise und review_by2026-10-28 gebunden. Die offenen Drizzle-/HR-Index-/Testcontainers-Themen aus dem Handshake bleiben gesonderte Arbeiten; keine DB/Container fuer diese Integration angelegt.

Die zusaetzliche Workspace-Pruefung fand eine bislang nur lokal vorhandene Abhaengigkeit @dnd-kit/core. Diese ist nicht Teil der Claude-Lieferung und wird als eigener Integrationsnachlauf behandelt; deshalb wird hier keine vollstaendige Workspace-/Frontendabnahme behauptet.

Integrationskorrektur: Die bestehende ESLint-Konfiguration markiert die Repositorywurzel nun mit root=true. In der verschachtelten geprueften Ansicht wurden sonst dieselben TypeScript-Plugins aus zwei unterschiedlichen Installationspfaden geladen. Regeln, Parser, Ausnahmen und Dateiabnahme bleiben unveraendert; nur die unbeabsichtigte Vererbung ueber die Projektwurzel endet. Die erste Commitpruefung brach deshalb ehrlich ab; kein Commit wurde dabei erzeugt.
