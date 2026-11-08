---
title: Produktions-App fuer interne Neuro-Aufrufe
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: abgeschlossen
last_reviewed: 2026-10-14
---

# Gemeinsame REST-Zugangsgrenze

Der Default-Neurotransport importiert jetzt main.app, die Anwendung des Backendcontainers. app.main ist die separate Test-Kompatibilitaetsoberflaeche und darf keine produktive Alternative sein. Explizit injizierte Clients bleiben fuer isolierte Tests moeglich. Es gibt keinen automatischen Testfallback bei fehlender Produktions-App. Bestehende Write-Sperren und Tokenpruefung bleiben bestehen.

16 isolierte Transport-/Bindungsfaelle bestanden. Der neue Regressionstest stellt zwei unterschiedliche Apps bereit: Produktion antwortet 403, Kompatibilitaet wuerde Erfolg liefern. Der Adapter trifft Produktion und propagiert deren 403 ohne Tokenoffenlegung. Ein zweiter Fall prueft fehlende Produktion ohne Fallback. Fuer diesen App-Auswahlvertrag wird die vorgelagerte JWT-Pruefung explizit ersetzt; dies ist kein neuer Nachweis echter Provider-/Domainrollenpruefung oder einer vollstaendigen Fachaktion. Keine DB, Migration oder neue Container.

Offen bleiben POST-Payload-Vertraege, Capability-Freigabeversion und Kanalgleichwertigkeit sowie Studio-Historienanzeige, Simulation und Release-Sperre. Die Korrektur ist eine Voraussetzung fuer deren belastbare Rechteabnahme.
