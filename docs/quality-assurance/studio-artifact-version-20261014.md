---
title: Erhalt der Tool-Vertragsschemaversion
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-10-14
---

# Versionsprojektion als erster P0-Slice

Das externe Agentenmanifest uebernimmt die schema_version des Process-Kernel-Toolvertrags. Bisher fiel jede Quellversion auf den Standardwert 1 zurueck. MCP transportiert die Quellversion im Metadatenfeld _meta.valeo/schemaVersion; die REST-Vertragsansicht gibt sie explizit aus. Die vorhandenen Rollen, Freigaben und Ausfuehrungsentscheidungen werden dadurch nicht veraendert.

Die Regression verwendet eine Nichtstandardversion 7 und prueft Manifest, MCP und HTTP-Projektionen. Dies beweist Schema-Versionsprojektion, nicht die Gleichwertigkeit der Fachausfuehrung oder eine genehmigte Capability-Version. Die beiden vorhandenen ERP-/Process-Kernel-Kataloge muessen noch auf ihre unterschiedlichen Zwecke und Ausfuehrungsbindungen abgeglichen werden. Ein generierter gleicher Fingerprint allein reicht nicht fuer REST-/MCP-/CLI-Gleichwertigkeit.

Offen: verbindliches CI-Artefaktgate gegen reale REST-Schemas und Berechtigungen; kanonische freigegebene Capability-Version; CLI-Bindung; Studio-Historienanzeige und Prozesssimulation. STUDIO-RELEASE-001 bleibt der verbindliche Nutzerauftrag: Aktivierung nur auf unveraenderlicher gepruefter Version mit synchronen Schnittstellen, nachvollziehbarer Historie, geprueften Invarianten und bestandenen Pflichtsimulationen. Eine technische Release-Sperre ist in diesem Slice noch nicht implementiert. Keine neue DB oder Migration.
