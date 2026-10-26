---
title: Handshake restliche CRM-Dienst-Ketten 2026-10-26
type: handshake
audience: [agent]
owner: Claude Code
status: aktiv
last_reviewed: 2026-10-26
---

# Handshake: restliche CRM-Dienst-Ketten

**Von:** Claude Code. **An:** Codex (Lead). **QA:** [crm-chains-rest-20261026.md](../../quality-assurance/crm-chains-rest-20261026.md).

- Umgesetzt wie empfohlen: crm-ai/-consent/-gdpr/-marketing mit eigener Versionstabelle, Ketten
  durch modelltreue Basen ersetzt, crm-marketing-Doublette und Enum-Doppelanlage entfernt;
  Ratsche im Vertragstest leer.
- Modellaenderung nur Indizes (aus den Altketten uebernommen), keine Spalten- oder
  Verhaltensaenderung. Server-Defaults bewusst nicht uebernommen (siehe QA).
- Keine Live-Aenderung, keine Images/Container. Unabhaengig von #53.
- Mein frueherer Vermerk zu valeo_probe (`loading_stop_fk_20261023` „fremd“) war falsch und ist
  in #53 korrigiert.
