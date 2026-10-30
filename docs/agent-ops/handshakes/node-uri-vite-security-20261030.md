# Handshake: URI-/Vite-Security und Backport-Review 2026-10-30

Owner Codex-runtime-security; Claims 124e20632 und ff4ee395. Bearbeitete Dateien: Root package.json, pnpm-lock.yaml, config/security/npm-backport-reviews.json, scripts/verify_node_security_releases.cjs und docs/quality-assurance/node-uri-vite-security-20261030.md. Integration und Commit beim Lead.

Die Herstellerfixes fuer GHSA-qr28-fpjm-wq7f und GHSA-8g5g-mxqh-grgj sind auf 0.5.1 und 6.4.5 angehoben; beide Advisory-Verhaltenspruefungen belegen Original rot und Fix gruen. Ein bestehendes braces-Advisory wurde zurueckgezogen; deepmerge bleibt aktiv, beide ohne dort genannten Fix. Bestehende Patch- und installierte Dateihashes geprueft; technische Re-Review bis exklusiv 2026-11-06 dokumentiert.

pnpm 9.12 Frozen-Installation in isoliertem Vollgraph mit --ignore-scripts: 36 Workspaces, Lock unveraendert. Security-Haupteinstieg 56/56; Produktionsaudit 0 Findings, Gate 0 blocked und Laufzeitvertraege gruen. Siehe QA; keine Datenbank oder Container.
