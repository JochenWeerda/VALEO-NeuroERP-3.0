# Fehlende Rolle: eine verständliche Meldung an einer Stelle

Stand: 2026-10-12 · Slice `MASKEN-ROLLENHINWEIS-20261012` · delegierter offener Punkt aus den
Rollen-Slices ([Hauptbuch](hauptbuch-rollen-20261011.md) bis
[übrige Finanzwege](finanz-rest-rollen-20261012.md))

## Befund

Rund 360 Finanzwege lehnen eine Anfrage ohne passende Rolle mit 403 und dem Satz
`Insufficient role. Required: ('FINANCE_LESEN', …)` ab. Nur Mahnlauf und Kontenplan übersetzten das.
Jede andere Maske zeigte den englischen Satz, „Fehler beim Laden" oder – wo der Fehler geschluckt wird –
eine leere Liste. Wem nur eine Rolle fehlte, der erfuhr es nicht.

## Entscheidung

Eine Stelle statt jeder Maske: der Antwort-Interceptor in `lib/api-client.ts`.

- Erkennt die Ablehnung am Satzanfang `Insufficient role` und macht daraus:
  „Dafür fehlt Ihnen die Berechtigung. Nötig ist eine dieser Rollen: FINANCE_BEARBEITEN,
  FINANCE_ADMIN. Bitte wenden Sie sich an Ihre Administration."
- Die Rollennamen bleiben wörtlich – wer die Rolle vergibt, braucht genau diesen Namen. `admin` und
  `manager` werden nicht genannt.
- Der Satz **ersetzt `detail`** in der Fehlerantwort: Masken, die den Fehlertext selbst anzeigen,
  zeigen denselben deutschen Satz.
- Zusätzlich **eine** Meldung (Toast mit fester Kennung): Scheitern zwanzig Abfragen einer Maske
  zugleich, erscheint eine Meldung, nicht zwanzig.
- Jede andere 403-Antwort bleibt unberührt – etwa „Dieses Konto gehört zum gemeinsamen Kontenrahmen"
  oder die Ablehnung eines fremden Mandanten.

## Geänderte Dateien

- `packages/frontend-web/src/lib/role-hint.ts` (neu)
- `packages/frontend-web/src/lib/api-client.ts` – nur der Antwort-Interceptor
- `packages/frontend-web/src/__tests__/lib/role-hint.test.ts` (neu)

## Nachweis

| Prüfung | Ergebnis |
|---|---|
| `role-hint.test.ts` – mehrere Rollen, eine Rolle, nur allgemeine Rollen, fremde Meldungen bleiben, Verdrahtung im Interceptor | 5 bestanden |
| Mahnlauf-Tests, die den API-Client benutzen (`mahnlauf-auswahl`, `mahnlauf-versand`) | 14 bestanden |
| `tsc --noEmit`, ESLint | ohne Fehler |

**Nicht geprüft: die Meldung im Browser.** Das Entwicklungs-Backend nimmt den Dev-Token nicht mehr an,
und ein Provider-Konto ohne Finanzrolle liegt für die Sichtprüfung nicht vor. Belegt ist die
Übersetzung als reine Funktion und ihre Verdrahtung über den Quelltext, nicht das Zusammenspiel mit
einer echten 403-Antwort.

## Offen

- **Sichtprüfung** mit einem Konto ohne Finanzrolle.
- **Doppelte Meldung:** Masken, die den Fehler selbst als Toast zeigen (Kontenplan), melden jetzt
  zweimal denselben Satz – einmal zentral, einmal selbst.
- **Leere Listen bleiben leer.** Die zentrale Meldung sagt, warum; die Maske selbst zeigt weiter „0"
  oder nichts, wenn sie den Fehler schluckt (z. B. Einkaufs-Dashboard bei den offenen Posten).
- **Andere Ablehnungstexte** (`Insufficient permissions …` aus den Scope-Prüfungen) sind nicht
  übersetzt.
