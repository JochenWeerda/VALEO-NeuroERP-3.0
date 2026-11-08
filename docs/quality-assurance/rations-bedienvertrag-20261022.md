---
title: Rationsberatung Bedienvertrag und sichere Einreichung
type: reference
audience: [entwickler, qa, agent]
owner: Codex
status: aktiv
last_reviewed: 2026-10-22
version: 1.0.0
description: Reale React-Bedienvertraege decken Demo- und Einreichkonsistenzfehler auf.
---

# Rationsberatung: Einreichgrenze

Der neue Bedienvertrag verwendet den echten React-Arbeitsplatz mit React Query. Ausschliesslich API-Grenzen liefern synthetische Antworten. Keine gemockten internen Komponenten oder Zustandssetter. Der durchgeklickte Ablauf umfasst Start, dreistufigen Wizard, Solverantwort, Workbench, Diagnose und Review.

## Gefundene und reparierte Produktfehler

- Demoergebnisse konnten regulaer in den fachlichen Lebenszyklus eingereicht werden. Demo und nicht optimale Ergebnisse sind jetzt sichtbar gesperrt; auch die Mutationsfunktion prueft diese Grenze vor allen Auftraegen. Dies ist eine Bediengrenze, kein Ersatz fuer die bestehenden serverseitigen Rollen-/Freigabepruefungen.
- Der Snapshot zeigte die vom Server bestaetigte Tieranzahl, die Gesamtfuttermenge verwendete aber noch die Wizardanzahl. Mengen und Gruppenbezug verwenden jetzt dieselbe bestaetigte Anzahl. Beispiel:20kg/Kuh bei80 bestaetigten Tieren ergibt1600kg statt1160kg aus der alten58er-Gruppe.
- Einreichfehler wurden ausschliesslich in der ausgeblendeten Workbench gehalten. Review zeigt sie jetzt als Alert; vor einem neuen Versuch wird der alte Fehler geloescht.

Die serverseitig bestaetigte Anzahl muss zudem eine positive sichere Ganzzahl sein.0,-1,1.5,NaN undInfinity stoppen vor Readiness-/Entwurfs-/Statusauftrag. Normale optimale Beratung bleibt einreichbar. Die Statusanfrage zielt auf in_review mit der bestaetigten Entwurfsversion; sie gibt die Ration nicht selbst frei. Abgelehnte Speicherung/Pruefung bleibt sichtbar, keine nachgelagerte Freigabe wird gesendet.

## Nachweise

11 neue Bedienfaelle gruen, bestehende7 Skalierungs- und3 Patchfaelle separat im Regressionsteil (vor letzter Erweiterung insgesamt14 Faelle in drei Dateien). Urspruenglicher Demo-Test war gegen alten Stand rot. Der normale Einreichvertrag hat den Mengenwiderspruch separat reproduziert. Zuschnitt: lokale React-/API-Grenztests, keine reale Solver-, Browser-, Buchungs- oder neue Datenbankabnahme.

Die Sonar-Erfassung besass daneben einen Wurzelwiderspruch: Sonar bewertet app/modules/services, pytest.ini instrumentierte nur app. Derselbe bestehende Volltestlauf erfasst jetzt alle drei Produktwurzeln; Reporter coverage.xml, Backendminimum60 und Sonarminimum80 bleiben unveraendert. Ein eigener Konfigurationsvertrag prueft die Quellparitaet. Kein Coverageausschluss und keine Umdeutung von Produktcode als Test.


Zusaetzlicher roter Uebergangsvertrag: Neue Ration nach Demo muss das alte Ergebnis und den Demokontext beenden. Frischer Wizard verwirft diese alte Ergebnis-/Vorschaubindung; erst eine eigene neue Berechnung erlaubt wieder Einreichung. Nachoptimierung eines vorhandenen Ergebnisses bleibt ein gesonderter Kontext.


Abschliessend21 Faelle in allen drei Rationsdateien gruen. Der vollstaendige Frontendlauf mit CI-Coverage bestand1487 Tests in293 Dateien (307,64s) vor dem letzten Demo-Neustartnachtrag; dessen gezielter Regressionsteil bestand danach erneut. TypeScript vor dem letzten Nachtrag gruen; abschliessender Typnachlauf und neuer GitHub-Lauf bleiben noetig. Bestehende JSDOM-Navigations-/API-Warnungen im Volltestlauf sind kein Browsernachweis.
