---
title: Gepruefter Buchungsurheber an Agrar-Materialflusswegen
type: reference
audience: [entwickler, qa, agent]
owner: Codex
status: aktiv
last_reviewed: 2026-10-22
version: 1.0.0
description: Vier Lagerbuchungswege projizieren den geprueften Token-sub statt fremder Rumpfwerte.
---

# Gepruefter Urheber

Transfer, Spuelcharge, Lot-Verknuepfung und automatische Lotbuchung verwendeten booked_by aus dem Aufruf oder system. Die vorhandene Lagerrolle verhinderte keine falsche Urheberzuordnung. Alle vier Wege beziehen den Urheber jetzt ueber die bestehende get_current_user-Abhaengigkeit aus der verifizierten Providerkennung. Rumpf booked_by und X-User-ID bestimmen den Buchungsurheber nicht. Die alte optionale Eingabe ist kompatibel, aber im API-Schema ausdruecklich als ignoriert/deprecated gekennzeichnet.

Bisherige Lagerrollen, Mandantenpruefung und Domainservices bleiben unveraendert. Keine neue Identitaet oder Rollenquelle, keine Migration oder neue Datenbank/Container. Keine Aussage, dass diese vier alten Buchungsprozesse damit insgesamt fachlich oder transaktional vollstaendig abgenommen waeren.

## Nachweise

24 echte HTTP-Vertraege mit RSA/JWKS und produktiver Bearer-/Mandantenmiddleware. Nur der abschliessende Domainservice ist ein Aufrufspy; Authentifizierung und Rollen wurden nicht ueberschrieben. Acht positive Varianten waren vorher rot (system oder gefaelschte Kennung),16 Berechtigungs-/Signatur-/Mandantenfaelle bereits gruen. Final alle24 gruen, zusaetzlich fehlender sub auf allen vier Wegen401. Rollenlos, manager und LAGER_LESEN403; anonyme/anders signierte Tokens401; fremder Mandantenselector403, kein Domainserviceaufruf. Bestehender separater Sessionvertrag deckt Redis ab; die JWT-Fixture isoliert dessen Validierung.

Mit den vorhandenen Materialfluss-/Lot-Fachservicevertraegen gemeinsam63 bestanden. Diese Fachservicevertraege verwenden Datenbankspies, keine reale Lagerbuchung. OpenAPI genau vier geaenderte Schemaeigenschaften (booked_by), alle3246 Pfade unveraendert. Rollenratsche0, Godfile-Ratsche gruen; physischer Tabellenkatalog bei Projektionserzeugung bytegenau bewahrt.

## Materialfluss-Bedienvertrag

Neun neue echte React-Vertraege mit synthetischen API-Hookantworten: Demo ohne Lager bietet keine Anlage, Lagerwahl zeigt ehrlichen leeren Livebestand, API-Fehler wird nicht durch Demo verdeckt, Pflichtfelder verhindern Auftrag, Lagerwechsel verwirft alte Eingaben, erfolgreicher Auftrag wird an die neue Lagerkennung gebunden, abgelehnte Anlage behaelt Eingaben, Zellkapazitaet wird numerisch uebertragen, abgelehnte QS-Aenderung springt auf bestaetigten Stand zurueck, Knotenstatus bindet an angezeigten Datensatz/Lager. Graphbibliothek und Seitenchrome sind ausgenommen; Fachformulare bleiben echt. Dies ersetzt keine serverseitige Mandanten- oder Buchungskettenpruefung.

## Belegeditor-CI

Run39737807365 hatte genau einen roten Frontendtest: native-docflow-edit wartete auf die Dialoghuelle und las dann synchron eine noch nicht initialisierte Tabellenzeile. Die Abnahme wartet jetzt auf das tatsaechliche Mengenfeld; beim abgelehnten Speichern auf die Fehlermeldung, bevor erhaltene Eingaben und identischer Wiederholungsauftrag geprueft werden. Keine Sleeps, Timeoutaufweitung oder Produktlogikaenderung. Zusammen mit den neuen Materialflussfaellen12 UI-Vertraege mit Coverage gruen; TypeScript gruen.

Der umfassende Backendlauf auf a94436cdd mit der korrigierten Drei-Wurzeln-Coverage besteht. Neuer gesamter Frontend-/Sonarlauf fuer diesen Nachtrag erforderlich; globales80-Prozent-Ziel und komplette Altmaskenablaese bleiben offen.
