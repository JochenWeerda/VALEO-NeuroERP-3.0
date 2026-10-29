---
title: Studio Fachvertraege und kontingentierte Modellinterpretation
type: explanation
audience: [architect, entwickler, agent]
owner: Codex
status: proposed
last_reviewed: 2026-10-15
---

# ADR Studio: Fachvertraege und kontingentierte Modellinterpretation

**Status:** Proposed. **Datum:** 2026-10-15. Konkretisierung des beauftragten STUDIO-SEMANTIC-001 innerhalb der bestehenden Platform-/Agrar-Grenze; kein neuer Container, Identitaetsdienst oder Datenbankschema.

## Kontext

Das bestehende Studio bietet feste Vorlagen, aber noch keine fachsprachlich gefuehrte Auswahl gepruefter Eingabevertraege. Nutzer benoetigen eine interaktive Vorschau ohne erfundene Datenbindungen und ohne unkontingentierte Modellaufrufe. Die bestehende Meridian-Engine und Identitaetsgrenze bleiben fuehrend.

## Entscheidung

Der vorhandene Studio-Katalog erhaelt fachsprachliche Metadaten zu einem expliziten versionierten manuellen Agrar-Vorschauvertrag. Parameter stammen aus dem vorhandenen Domain-Kalkulator. Der Server erzeugt eine normale Meridian-ScreenDefinition. Nutzer waehlen fachlich benannte optionale Felder; verpflichtende und unbekannte Bindungen koennen sie nicht umgehen. Modellantworten duerfen weder freie Felder noch SQL, Endpoints, Commands oder Freigaben bestimmen.

Der kataloggefuehrte Dialog funktioniert ohne Modell. Optional interpretiert das bestehende mandantenspezifische LLMGateway Anforderungen. Die bestehende Identitaetsquote reserviert vor der Anfrage und rechnet tatsaechliche Anbieter-Token im technischen Nebenbuch ab. Redis-Ausfuehrungsbelege verhindern erneute Provideraufrufe mit gleichem Auftrag auch bei verlorener Antwort. Ungeklaerte Timeouts/Verbrauchswerte behalten ihre Reservierung zur spaeteren Abstimmung. Ein Kosten-/Token-Overrun liefert kein Ergebnis und bleibt klaerungspflichtig; Reservierung ist eine konservative Byte-/Ausgabeobergrenze samt Framingreserve, kein behaupteter exakter Tokenizer.

## Konsequenzen

Keine neue Rechtewelt: vorhandene Belegrollen plus Budgeteigentum und verifizierter Mandant. Keine automatische Kontingentvergabe. Der Vorschlag wird erst durch ausdrueckliche Uebernahme und den vorhandenen Speichervorgang zum versionierten Entwurf. Die persistierte Unterhaltung ist Nutzereingabe, kein verifizierter Modell-/Freigabebeleg; Auditautor kommt weiterhin aus der geprueften Identitaet.

Die interaktive Vorschau verwendet echte Domain-Berechnung und keine produktiven Geschaeftsdaten. Sie liefert keinen Freigabenachweis fuer Waagenbindung, Lieferanten-/Kontraktaufloesung, Meldungen oder konfigurierbare Trocknungsregeln. Der manuelle Vorschauvertrag wird vom produktiven grain.v1-Profil ausdruecklich abgewiesen. Fachliche Vollintegration benoetigt eigene Vertraege und Prozessabnahmen. Bestehende Freigaben werden bei geaendertem Artefakthash nicht neu erfunden.

## Abnahme

[Pruefergebnisse und Browsernachweis](../quality-assurance/studio-semantic-20261015.md), [verbindlicher Auftrag](../architecture/studio-semantic-standard.md). Code-/Doku-Abnahme bedeutet keine vollstaendige produktive Getreideannahme oder gruene Gesamt-CI.

## Anbieter-Verbrauchsvertraege

Die Implementierung liest die dokumentierten Usage-Felder aus den vorhandenen Providerantworten: [Claude Prompt Caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching), [OpenAI Chat Completions](https://platform.openai.com/docs/api-reference/chat/object) und [Ollama Chat](https://docs.ollama.com/api/chat). Diese technischen Tokenzaehler sind keine Geldbetraege und kein finanzbuchhalterisches Nebenbuch.
