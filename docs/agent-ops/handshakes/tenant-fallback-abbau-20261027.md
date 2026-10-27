---
title: Handshake TENANT-FALLBACK-ABBAU-20261027
type: handshake
audience: [agent]
owner: Claude Code
status: aktiv
last_reviewed: 2026-10-27
version: 1.0.0
description: Uebergabe Claude -> Codex fuer den Abbau aller eingefrorenen Rueckfaelle auf den Mandanten 'default' und die Service-Anfragen in der Datenbank.
---

# Handshake TENANT-FALLBACK-ABBAU-20261027 (Claude Code → Codex)

## Basis und Reihenfolge

- Basis `claude/ustva-wahrheit-20261027`, Zweig `claude/tenant-fallback-abbau-20261027`; nach dem UStVA-PR integrieren.
- Alembic `vat_return_bearbeiter_20261027 → service_anfragen_20261027`, ein Head. Zwei neue Tabellen unter getrennten
  Policies; Rechte fuer `valeo_app` vergibt wie bei allen Tabellen deine Rollenverwaltung.

## Fuer dich

1. **Live-relevant:** Tankstelle, Wartung, Versicherungen, Projekte, Verladung, Ernteplanung, EDI, Controlling- und
   Finanzaktionen, Superglue-Uebersichten und Nummernkreise nehmen den Mandanten aus dem Token; ohne Token-Mandant
   kein Rueckfall auf `default`. Vorher sahen die ersten fuenf alle Mandanten.
2. **API-Vertrag:** `tenant_id` entfaellt in den Anlagemodellen dieser Router (`ZapfungPayload`, `AnlagePayload`,
   `ProtokollPayload`, `ProjektPayload`, `AufgabePayload`, `VersicherungPayload`, `VerladungPayload`, `ErntePayload`,
   `EdiNachrichtEmpfangRequest`, `EdiPartnerCreateRequest`). `/service/anfragen` liefert gespeicherte Anfragen; die zwei
   erfundenen Vorbelegungen gibt es nicht mehr. Status `erledigt` nur ueber `/service/abschluss`.
3. **Daten:** `domain_ops.edi_nachrichten` hat live 31 Zeilen mit Mandant `default` — zuordnen oder entfernen.
4. **Folge-Slice RLS-DOMAIN-OPS** (Schema, siehe QA): Eindeutigkeiten je Mandant, Server-Vorgaben, Policies, Tabellen
   ohne Mandant.
5. Nicht beruehrt: Studio/Masken, Systemrollen, Codex-Claims, Live.
