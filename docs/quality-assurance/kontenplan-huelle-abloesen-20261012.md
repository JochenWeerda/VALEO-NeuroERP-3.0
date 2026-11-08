# Kontenplan: Hülle abgelöst

Stand: 2026-10-12 · Slice `KONTENPLAN-HUELLE-ABLOESEN-20261012` · Befund aus
[Kontenplan: Mandant aus dem Kontext](kontenplan-mandant-20261012.md)

## Befund (Sichtprüfung, Vite :3001, Playwright headless)

Unter `/finance/kontenplan` lag eine generierte Maske (`pages/finance/kontenplan.tsx`):

- Kontonummer, Bezeichnung, Kontenart, Kontengruppe und Periode ausgefüllt, **Speichern** gedrückt:
  Die Maske zeigt „Gespeichert – Die Änderungen wurden erfolgreich gespeichert". Im Netzwerk steht
  **kein** schreibender Aufruf an `chart-of-accounts`.
- Die Felder heißen `kontonummer`, `bezeichnung`, `kontenart`; der Weg erwartet `account_number`,
  `account_name`, `account_type`. Periode, Steuerschlüssel, UStVA-Position, Anfangsbestand und
  Sperrstatus hat das Konto gar nicht.
- Die Maske öffnete immer ein neues Konto – ein vorhandenes ließ sich nicht aufrufen.

Die Pflegemaske unter `/finance/chart-of-accounts` kann dasselbe wirklich: In der Sichtprüfung legte
„Neues Konto → Erstellen" das Konto an (`POST /api/v1/finance/chart-of-accounts/ → 200`), es erschien
in der Liste. Bis zum Vortag scheiterte genau dieser Aufruf mit 500 (siehe verlinkter Befund).

## Entscheidung

„Was nicht einfach läuft, läuft einfach nicht." Zwei Masken für dasselbe, von denen eine Erfolg
meldet und nichts tut, sind eine zu viel. Die Hülle ist gelöscht; `/finance/kontenplan` zeigt die
Pflegemaske. Bestehende Links und Lesezeichen bleiben gültig.

`/fibu/kontenplan` (Übersicht mit Sprung ins Sachkonto, Eintrag in der Navigation) bleibt unberührt.

## Geänderte Dateien

- `packages/frontend-web/src/pages/finance/kontenplan.tsx` – entfernt
- `packages/frontend-web/src/app/route-aliases.json` und die Routenerzeugnisse (939 Routen wie zuvor)
- `packages/frontend-web/src/__tests__/pages/finance/kontenplan-route.test.ts` (neu)

Die Pflegemaske selbst ist nicht angefasst (dort liegen fremde, nicht committete Änderungen).

## Nachweis

| Prüfung | Ergebnis |
|---|---|
| `node scripts/generate-tanstack-routes.mjs`, `node scripts/check-routing-integrity.mjs` | 939 Routen, Prüfung grün |
| Routenvertrag `kontenplan-route.test.ts` | 3 bestanden |
| `tsc --noEmit` | ohne Fehler |
| Sichtprüfung nach der Umstellung: `/finance/kontenplan` | Pflegemaske mit 29 Konten, „Neues Konto“ und „Bearbeiten“ vorhanden, kein schreibender Aufruf beim Öffnen |

Das Testkonto aus der Sichtprüfung ist aus der Entwicklungsdatenbank wieder entfernt.

## Offen

- **Benutzerhandbuch:** `docs/benutzerhandbuch/finanzbuchhaltung.md` und das Bildschirmfoto-Verzeichnis
  beschreiben unter „Kontenplan" noch die abgelöste Maske.
- **Rückgabe des Finanzdienstes:** `financeService.createAccount`/`updateAccount`/`getAccount` lesen
  `response.data.data`; der Weg antwortet mit dem Konto direkt. Die Pflegemaske nutzt den Rückgabewert
  nicht, deshalb fällt es nicht auf – wer ihn nutzt, bekommt `undefined`.
- **Brotkrumen:** Die Pflegemaske zeigt „Chart Of Accounts" als Brotkrumen.
- **Drei Kontenplan-Wege bleiben:** `/finance/kontenplan` und `/finance/chart-of-accounts` (Pflege)
  sowie `/fibu/kontenplan` (Übersicht).
