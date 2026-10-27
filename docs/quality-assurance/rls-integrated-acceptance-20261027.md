---
title: Integrierte RLS-Abnahme nach PR73 und Agrarergänzung
type: qa
audience: [entwickler, qa, betrieb, agent]
owner: Codex
status: active
last_reviewed: 2026-10-27
---

# Integrierte Abnahme am 27.10.2026

## Basis und Umfang

Claudes Kette bis PR73 wurde geordnet integriert, einschliesslich des
Dokumentationsnachtrags 183b2bc9e. Dessen Autornachweise sind 228 RLS- und
387 Docflow-/GoBD-Tests; sie werden nicht als eigene Wiederholung ausgegeben.

Die eigene Folgemigration rls_verified_agrar_20261027 haengt hinter
rls_docflow_child_keys_20261027. Sie sichert Biostimulanzien und
Kontraktallokationen mit getrennten Policies ohne gemeinsame Lesefreigabe.
Voraussetzungen sind die verifizierte Mandantenbindung der Biostimulanz-
und Wiegescheinadapter sowie die mandantengebundene Wiegescheinreferenz im
Allokationsservice. Ungueltige Referenzen und nichtpositive/nichtendliche
Mengen werden vor Restmengenmutation abgewiesen.

## Eigene Nachweise

- Vollstaendige integrierte RLS-Suite samt Rollenprovisionierung,
  Systemmandanten-Ratsche, Allokationsservice, Biostimulanzien-HTTP und
  Buchungsvorlagen-Maskenvertrag: **269 bestanden**, keine Skips,
  Laufzeit 448,91 Sekunden.
- Vorbereitete Studio-API-Vertraege nach der RLS-Integration: **77 bestanden**,
  keine Skips, Laufzeit 33,02 Sekunden. Darunter die vier bestehenden
  PostgreSQL-Faelle. Ein Teil der isolierten HTTP-Vertraege verwendet weiterhin
  SQLite im Speicher; dies ist kein PostgreSQL- oder RLS-Nachweis.
- OpenAPI-Summaryabdeckung: **3752/3752**, keine fehlende Summary.
- Datenqualitaets-Ausgabegrenze nach Router-Auslagerung: **17 bestanden**.
- Vorheriger Frontend-Meilenstein: **65 bestanden**, vollstaendige
  Typpruefung erfolgreich; kein visueller Browsernachweis daraus abgeleitet.

Die neuen Schreibgrenzentests fuehren die tatsaechlichen Policy-Implementierungen
mit TEXT- und UUID-Spalten aus, ersetzen eine alte ALL-Policy, pruefen
Wiederholbarkeit und laufen als valeo_app ohne Superuser/BYPASSRLS.

## Schema und Ressourcen

Die vollstaendige Migrationskette wurde ausschliesslich innerhalb einer
zurueckgerollten Transaktion auf dem vorhandenen valeo_probe eingespielt.
Resultat: 775 Tabellen, davon **522 mit RLS**; 193 zurueckgestellte
Mandantentabellen, ready leer, unbegruendeter Altbestand null. Die zwei
geschlossenen Ausnahmen wurden entfernt und die Ratsche von 195 auf 193 gesenkt.

Nach Ende beider Laeufe: Revision unveraendert loading_stop_fk_20261023,
keine weitere Sitzung auf dem Pruefstand und keine eigene Regressionstabelle.
Das Fenster ist fuer Claude freigegeben. Keine neue Datenbank, kein neuer
Container, kein Reset und kein Live-RLS-Rollout.

## Grenzen der Gesamtfreigabe

GitHub Quality Gate 40488618550 bleibt rot: Frontend 189 fehlgeschlagene Tests
und Doku-Code-Drift 263. Die dort zusaetzlich gefundene Router-Groessenregression
wurde anschliessend durch echte Auslagerung behoben und die Ratsche auf 6100
gesenkt. Secret Scan, Dependency Scan, FSX und Produktionsvertraege bestanden
im genannten Lauf. Kein Gesamtgruen und keine pauschale Masken-/Fachketten-
oder Live-Freigabe.

Die 77 API-Vertraege bestaetigen vorbereitete Quellen der privaten
Integrationsansicht; ihre gesamte Studio-/Projektionslieferung bleibt ein
separater Integrationsslice. Generierte Gesamtartefakte duerfen nur gemeinsam
mit ihren jeweiligen kanonischen Quellen veroeffentlicht werden.


## Buchungsvorlagenmaske aus Claudes Handshake

Der kanonische Builder kennzeichnet gemeinsame Vorlagen mit Gemeinsam und
zeigt Loeschen nur bei shared=false. Anwenden bleibt fuer aktive gemeinsame
Vorlagen moeglich. Der Buildervertrag ist Teil der 269 bestandenen Tests.
Der gesamte Studio-Versionskatalog und das Agentenhandbuch werden mit dem
noch ausstehenden Studio-/Projektions-Integrationsslice aus allen
kanonischen Quellen neu erzeugt; hier wird kein neuer produktiver
Studio-Release behauptet.
