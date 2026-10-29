---
title: Handshake Maskenmigrationsreparatur und Adaptive Workspace
type: reference
owner: Codex
status: aktiv
last_reviewed: 2026-10-22
---

# Handshake 2026-10-22

Reparaturmeilenstein `6ff9d93f4`: 195 Backend-Vertraege,196 UI-Vertraege,76 echte SQL-Faelle gruen; Typpruefung und Produktionsbuild der isolierten Commit-Ansicht gruen. Alle veroeffentlichten Reparaturdateien stimmen mit der geprueften Ansicht ueberein. GitHub-main bleibt bis zur Gesamtintegration auf8086c464f; Reparaturzweig codex/migration-parity-repair-20261022.

## Gemeinsame Arbeitskopie

491 unveraenderte eigene Dateien sicher integriert, zwoelf parallele Arbeitskopien zusammengefuehrt. Im Compiler, Schema und Renderer bleiben die fremden specialized/Dispositions-Erweiterungen erhalten; eigene Tabellen-/Rollen-/Versionsreparaturen kommen hinzu. Der geteilte Index wird nicht geaendert. Neun konfliktbehaftete beziehungsweise vom Dateizugriff blockierte generierte Arbeitskopien bleiben geschuetzt; die geprueften konsistenten Generatorfassungen liegen im Reparaturcommit. Keine pauschale Synchronisierung fremder WIP.

Die Routen wurden anschliessend aus der tatsaechlichen gemeinsamen Arbeitskopie neu erzeugt (942 Eintraege einschliesslich paralleler Route). Dadurch sind campaignId/campaignName/campaignStart/campaignEnd und requisitionId/contractId/rfqId wieder korrekt typisiert.

## An aktiven ADAPTIVE-WORKSPACE-20261022-Owner

Die lokale Gesamt-Typpruefung meldet noch fuenf Fehler ausserhalb der isolierten Commit-Ansicht:

- app/routing/route-contract.test.ts:20: Der Test verwendet search, die aktuelle generierte Suchparameterliste enthaelt diesen Schluessel nicht.
- components/adaptive-workspace/inbox/inbox-rank.ts:81–84: Vier Vergleiche von laut Vertrag konstant false deklarierten Feldern gegen true. Runtime-Abwehr ungueltiger Live-Daten bleibt fachlich sinnvoll, aber ein Schnittmengentyp erweitert false nicht zu boolean. Eine explizite Prueffunktion mit unknown-Eingang kann den tatsaechlichen Laufzeitwert weiterhin strikt gegen true pruefen, ohne Rechte zu vergeben oder die Schutzpruefung zu entfernen.

Diese aktive Fremdarbeit wurde nicht ueberschrieben. Die drei bereits vorher diagnostizierten Start-Dashboard-Bedienbefunde bleiben ebenfalls beim Workspace-Owner. Keine gruene Gesamtarbeitskopie behaupten, solange diese Befunde offen sind.

## Weitere Migrationsabnahme

Die strengen Inventare enthalten50 Legacy-Wrapper,53 handgebaute Routen und echte API-/Runtime-Nachweisluecken. Eine generische neue Liste ersetzt keinen bestehenden Fachablauf. Keine alten Bedienvertraege entfernen, bevor gleichwertige zentrale Vertraege und die reale Maskenabnahme vorliegen. Neue Parent-Builder bleiben bestehen.
