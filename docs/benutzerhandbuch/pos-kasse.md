---
title: POS und Kasse
type: how-to
audience: [endnutzer, power-user]
owner: Codex
status: aktiv
last_reviewed: 2026-06-26
version: 3.1.0
---

# POS und Kasse

Diese Anleitung beschreibt den operativen Kassenablauf: Bon erfassen,
Zahlungsart buchen, TSE-/DSFinV-K-Status pruefen und Tagesabschluss an die
Finanzbuchhaltung uebergeben.

!!! warning "Produktive TSE-Freigabe"
    Repo-seitig sind POS-, TSE-, DSFinV-K- und FIBU-Vertraege dokumentiert und
    ueber Mock-/Testpfade pruefbar. Fuer den produktiven Betrieb bleiben
    TSE-Herstellerabnahme, DSFinV-K-Pruefwerkzeug, Steuerberaterfreigabe und
    echte Provider-Zugangsdaten externe Gates.

## Voraussetzungen

- Sie sind am richtigen Mandanten angemeldet.
- Kasse, Terminal und Benutzerrolle sind fuer den POS freigegeben.
- Fuer produktive Abschluesse muss die TSE erreichbar und betriebsbereit sein.
- Artikel, Steuerkennzeichen und Zahlungsmittel sind gepflegt.

## Kassenverkauf buchen

1. Oeffnen Sie *POS* -> *POS-Terminal*.
2. Waehlen oder scannen Sie die Artikel.
3. Pruefen Sie Menge, Preis, Rabatt und Steuerkennzeichen.
4. Waehlen Sie die Zahlungsart: Bar, EC/Karte, Gutschein oder Split-Payment.
5. Schliessen Sie den Bon ab.
6. Pruefen Sie auf dem Bon die Bonnummer, Zeit, Betrag, Steueranteile und
   TSE-Status.

## Gutschein ausgeben oder einloesen

1. Oeffnen Sie *POS* -> *Gutscheine* oder nutzen Sie die Gutschein-Aktion im
   POS-Terminal.
2. Fuer Ausgabe: Betrag und Empfaengerhinweis erfassen, Zahlung buchen und Bon
   drucken.
3. Fuer Einloesung: Gutscheincode scannen oder eingeben.
4. Restbetrag pruefen und mit weiterer Zahlungsart ausgleichen.

## Retoure oder Storno buchen

1. Oeffnen Sie den betroffenen Bon oder starten Sie eine Retoure im POS.
2. Waehlen Sie die Positionen, die storniert oder zurueckgenommen werden.
3. Erfassen Sie den Grund.
4. Buchen Sie die Rueckzahlung in der fachlich korrekten Zahlungsart.
5. Drucken Sie den Storno-/Retourenbeleg.

## Tagesabschluss ausfuehren

1. Oeffnen Sie *POS* -> *Tagesabschluss*.
2. Pruefen Sie Barbestand, Kartensummen, Gutscheine, Entnahmen und Differenzen.
3. Klaeren Sie offene oder fehlerhafte Bons vor dem Abschluss.
4. Starten Sie den Tagesabschluss.
5. Pruefen Sie den Abschlussbeleg und den Link zum TSE-Journal.
6. Oeffnen Sie bei Bedarf *FIBU* -> *Uebernahme Buchungen Tagesabschluss POS*,
   um die Uebergabe in die Finanzbuchhaltung zu kontrollieren.

## Ergebnis

- Jeder Bon hat eine nachvollziehbare Bonnummer, Zahlungsart und TSE-Spur.
- Der Tagesabschluss enthaelt Bar-, Karten-, Gutschein- und Entnahme-Summen.
- Die FIBU-Uebergabe ist als Prozessschritt sichtbar und kann bei Blockern
  fail-closed gestoppt werden.

## Haeufige Fehler

| Fehler | Ursache | Behebung |
| --- | --- | --- |
| Bon ohne TSE-Status | TSE nicht erreichbar oder Provider nicht freigegeben | TSE-Journal pruefen, Abschluss nicht produktiv freigeben |
| Zahlungsdifferenz | Barbestand oder Kartenabschluss stimmt nicht | Differenz klaeren, Entnahme oder Korrektur erfassen |
| Gutschein wird nicht akzeptiert | Code ungueltig, bereits verbraucht oder Mandant falsch | Gutscheinstatus pruefen |
| Tagesabschluss blockiert | Offene Bons, TSE-Blocker oder FIBU-Mapping fehlt | Offene Positionen bereinigen, Mapping/Freigabe pruefen |

## Quellen und Reverse-Pflege

- `packages/frontend-web/src/app/navigation/domains/operations.tsx`: POS-Menue
  mit POS-Terminal, TSE-Journal, Tagesabschluss und Gutscheinen.
- `packages/frontend-web/src/app/navigation/domains/finance.tsx` und
  `packages/frontend-web/src/app/navigation/fibu-suite.tsx`: FIBU-Uebernahme
  Tagesabschluss POS.
- `packages/frontend-web/src/pages/pos/tagesabschluss-enhanced.tsx` und
  `packages/frontend-web/src/pages/pos/tse-journal.tsx`: Tagesabschluss- und
  DSFinV-K-/TSE-Journal-Aktionen.
- `docs/agent-ops/slices/POS-FISCAL-PROVIDERS-001.yaml` und
  `docs/agent-ops/slices/POS-FISCAL-OPS-002.yaml`: Provider- und
  Betriebsvertraege.
- `docs/agent-ops/slices/SEMANTIC-E2E-P2P-FIBU-POS-QS-001.yaml`: semantische
  POS/TSE-Kette mit externen Mock-Gates.

Reverse-Pflege: Wenn POS-Zahlungsarten, Tagesabschluss-Status, TSE-Provider,
DSFinV-K-Export oder FIBU-Uebergabe geaendert werden, diese Seite und die
entsprechenden POS-/Finance-Runbooks im gleichen Slice aktualisieren.
