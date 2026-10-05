# FSX-090 — Nachweisverfahren

Stand: 2026-09-15 · Gehoert zu `docs/design/flow-spine-entlastung-masterplan.md`.

Der Nachweis zerfaellt in zwei Verfahren, weil ein Automat nicht messen kann, was
er nicht erlebt. Beide sind noetig; keines ersetzt das andere.

## FSX-090a — technische Interaktionsmessung

**Was gemessen wird:** Maskenwechsel, Klicks, Feldeingaben, Netzwerkrunden je
Aufgabe.

**Was ausdruecklich nicht gemessen wird:** Bedienzeit. Playwright tippt ohne
Zoegern, sucht nichts und liest nichts. Eine "Dauer" aus diesem Lauf waere die
Zahl, die am ehesten falsch zitiert wuerde — deshalb erhebt der Helfer sie gar
nicht erst.

**Werkzeug:**
- `packages/frontend-web/tests/e2e/helpers/flow-spine-task-metrics.ts`
- `packages/frontend-web/tests/e2e/fsx-090a-direktbestellung.spec.ts`

**Vergleich alt gegen neu** — zwei Laeufe, bewusst nicht automatisiert:

```
git worktree add ../valeo-vor-fsx cb7a38f99   # letzter Commit vor FSX-002
# dort: Abhaengigkeiten, Build, Stack starten
FSX_MESSUNG_VARIANTE=vor-fsx FSX_MESSUNG_COMMIT=cb7a38f99 npx playwright test fsx-090a
# im Hauptbaum:
FSX_MESSUNG_VARIANTE=nach-fsx FSX_MESSUNG_COMMIT=$(git rev-parse --short HEAD) npx playwright test fsx-090a
```

Ein automatisierter Zweibaum-Vergleich waere ein Bauwerk, das bei jeder
Toolchain-Aenderung bricht — fuer eine Messung, die zweimal stattfindet.

**Status:** Das Werkzeug ist gebaut und typgeprueft, **aber noch nicht gelaufen**.
Es braucht einen laufenden Stack (Frontend, Backend, Datenbank). Solange keine
Protokollzeile vorliegt, gibt es zu FSX-090a nichts zu berichten.

## FSX-090b — Nutzerbeobachtung

**Was gemessen wird:** tatsaechliche Bearbeitungszeit, Suchpausen,
Fehlbedienungen, Rueckfragen — und ob Sperren, Teilmengen und Freigaben **ohne
Erklaerung** verstanden werden.

**Teilnehmer:** mindestens fuenf Personen je Rolle — Innendienst, Waage,
Buchhaltung. Weniger erlaubt keine Aussage ueber Muster, nur ueber Einzelfaelle.

**Aufgaben:**

1. Direktbestellung aus einem Procure-to-Pay-Vorgang erfassen.
2. Eine Reklamation zu einem bereits abgeschlossenen Vorgang anlegen.
3. Einen blockierten Vorgang erklaeren: *warum* geht es nicht weiter?

**Protokoll je Teilnehmer und Aufgabe:**

| Feld | Erhebung |
|------|----------|
| Zeit bis erste sinnvolle Eingabe | Stoppuhr, Beobachter |
| Zeit bis Aufgabe abgeschlossen | Stoppuhr |
| Suchpausen (> 3 s ohne Eingabe, Blick wandert) | Strichliste |
| Fehlbedienungen (Klick, der zurueckgenommen wird) | Strichliste |
| Rueckfragen an den Beobachter | woertlich notieren |
| Sperre verstanden? | ja / teilweise / nein, mit eigener Begruendung des Teilnehmers |
| Teilmenge verstanden? | ja / teilweise / nein |

**Abbruchkriterium, verbindlich:** Wird eine Sperre oder Teilmenge in der neuen
Fassung **seltener** verstanden als in der alten, wird der betroffene Rollout
zurueckgestellt — auch bei besseren 090a-Zahlen. Struktur schlaegt nicht
Verstaendlichkeit.

**Status:** offen. Braucht echte Nutzer und eine Terminabsprache; das ist ein
externes Gate und von hier aus nicht zu schliessen.

## Was von beiden abhaengt

- **FSX-013 Rollout** auf die restlichen 17 Handover-Masken. Der Pilot in
  `einkauf/bestellung-anlegen` steht; eine Zeile, die 18-mal falsch ist, waere
  schlimmer als 18 Hinweiskaesten.
- Die Aussage, dass die Vereinfachung **besser** ist. Bis dahin ist sie
  plausibel begruendet und nachgewiesen nur in dem, was sie entfernt hat:
  erfundene Kennzahlen, tote Schalter, Technik im Arbeitsbereich.
