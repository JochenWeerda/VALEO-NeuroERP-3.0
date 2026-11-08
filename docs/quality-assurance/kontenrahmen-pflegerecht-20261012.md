# Gemeinsamer Kontenrahmen: Lesen und Pflegen sind getrennte Rechte

Stand: 2026-10-12 · Slice `KONTENRAHMEN-PFLEGERECHT-20261012` · Auftrag: „getrennte Rechte umsetzen" ·
Hinweis von Codex (`KONTENPLAN-VERIFIED-SHARED-POLICY-20261012`, zweite Hälfte) · baut auf
[Kontenplan: Mandant aus dem Kontext](kontenplan-mandant-20261012.md)

## Befund

Der gemeinsame Kontenrahmen liegt unter dem Mandanten `system` und gilt für jedes Haus einer
Installation. Jeder Mandant mit Schreibrolle durfte dessen Konten ändern und deaktivieren – die
Änderung traf alle Häuser.

## Entscheidung

| | Recht |
|---|---|
| gemeinsamen Rahmen sehen | wie bisher: jeder, der den Kontenplan lesen darf |
| Konto des gemeinsamen Rahmens ändern oder deaktivieren | Finanzrolle des Wegs **und** `KONTENRAHMEN_PFLEGE` (oder `admin`) |
| eigenes Konto anlegen, ändern, deaktivieren | wie bisher: Finanzrolle des Wegs |

Ohne das Pflegerecht antwortet der Weg 403 mit einem Satz, der das Recht nennt; am Konto ändert sich
nichts. Das Pflegerecht allein ist keine Schreibrolle.

**Warum ein eigenes Recht statt „nur `admin`":** In einer Installation mit einem Haus pflegt die
Finanzleitung den Rahmen selbst. Sie bekommt dafür `KONTENRAHMEN_PFLEGE` – eine Zuweisung im
Anmeldedienst, kein Umbau. Bei mehreren Häusern bleibt das Recht bei dem, der den Rahmen verantwortet.

**Was bewusst nicht gebaut ist:** eine Kopie des Kontos je Mandant beim ersten Ändern. Buchungen
hängen an der Kennung des Kontos; eine Kopie hätte zwei Konten mit derselben Nummer erzeugt.

## Mitbehoben

**Deaktivieren antwortete immer mit 500.** Der Weg gab `{"message": …}` zurück, das Antwortschema
verlangt `success`. Das Konto war danach deaktiviert, der Aufrufer sah einen Fehler – die Pflegemaske
meldete „Fehler beim Deaktivieren", obwohl es geklappt hatte.

## Geänderte Dateien

- `app/auth/finance_roles.py` – `KONTENRAHMEN_PFLEGE` (additiv)
- `app/api/v1/endpoints/chart_of_accounts.py` – `_pflegbar` an Ändern und Deaktivieren, Antwort des
  Deaktivierens
- `tests/test_kontenplan_mandant_vertrag.py` – acht neue Fälle

## Nachweis

| Prüfung | Ergebnis |
|---|---|
| `tests/test_kontenplan_mandant_vertrag.py` gegen `valeo_probe` (echte Datenbank, zwei Mandanten) | 18 bestanden |
| alle Testdateien, die Kontenplan oder Finanzrollen berühren | 1271 bestanden, 2 übersprungen |
| Schnittstellenbeschreibung der Kontenplan-Pfade | unverändert |

Die neuen Fälle: Finanzleitung eines Hauses (mit und ohne `manager`) ändert und deaktiviert ein
`system`-Konto nicht (403, Konto unverändert, für das andere Haus weiter lesbar); mit
`KONTENRAHMEN_PFLEGE` oder `admin` geht beides; das Pflegerecht ohne Finanzrolle reicht nicht; das
eigene Konto braucht kein Pflegerecht.

Keine Sichtprüfung: Der Entwicklungsnutzer trägt `admin` und darf damit pflegen.

## Betrieb

Wer den gemeinsamen Kontenrahmen pflegen soll, braucht im Anmeldedienst zusätzlich
`KONTENRAHMEN_PFLEGE`. **Ohne diese Zuweisung kann nach dem Einspielen niemand außer `admin` ein
Konto des gemeinsamen Rahmens ändern** – in der Entwicklungsdatenbank sind das 28 von 29 Konten.

## Offen

- **Die Pflegemaske zeigt die Ablehnung nicht verständlich.** `pages/finance/chart-of-accounts.tsx`
  bietet „Bearbeiten" und „Deaktivieren" an jedem Konto an und meldet bei 403 nur „Fehler beim
  Aktualisieren". Die Datei trägt fremde, nicht committete Änderungen und ist deshalb nicht angefasst.
- **Mandant aus dem Token:** Der Mandant kommt weiter aus dem Kopf `X-Tenant-ID`, den die Middleware
  nicht mit dem Token abgleicht (erste Hälfte von Codex' Hinweis, betrifft 326 Dateien). Offen ist,
  ob der Anmeldedienst den Mandanten im Token mitgibt.
- **Gleiche Kontonummer im Haus und im Rahmen:** Ein Haus kann ein eigenes Konto mit einer Nummer
  anlegen, die es im gemeinsamen Rahmen schon gibt; die Liste zeigt dann beide.
