# Screen-Governance

Verbindliche Schichtung für operative Masken. Keine zweite ScreenDefinition.

## Schichten

| Schicht | Zuständigkeit | Ort |
| --- | --- | --- |
| Domain / Application | Was fachlich gilt | Domäne, Policies |
| Queries + Commands | Daten lesen, Befehle ausführen | API-Hooks, Action Registry der Seite |
| ScreenContext | Daten, Rechte, Zustand, Befehle, Navigation | `governance/screen-context.ts` |
| ScreenDefinition | Was sichtbar ist und welcher Befehl dazu gehört | Schema-Version 1 |
| MaskBuilder | Wie daraus die Oberfläche wird | Compiler und Fast-Renderer |

Der Builder ruft keine API auf und enthält keine Abfrage auf eine Masken-Id.

## Screen-Typen

Gespeichert werden `mode`, `layout.floorplan` und `layout.columnNavigation`.

| Floorplan | Abgeleiteter Typ |
| --- | --- |
| `worklist` | `WORKLIST` |
| `objectPage` | `DETAIL` |
| `worklist` oder `objectPage` mit `listDetail` | `MASTER_DETAIL` |
| `transaction`, `wizard` | `PROCESS` |
| `cockpit` | `DASHBOARD` |
| `analyticalList` | `REPORT` |

`screenType`, `listReport` und `form` als eigene Felder weist der Validator ab. Eine neue Schema-Version ist eine Migration von Version 1, kein paralleles Dokument.

## Aktionen und Bedingungen

Die Definition nennt den Befehl. Die Seite registriert die Funktion.

```ts
command: "tour.create"
enabledWhen: "tour.canCreate"
```

`tour.canCreate` setzt die Anwendung. Einfache UI-Bedingungen bleiben deklarativ (`all`, `any`, `path`, `exists`, `equals`, `notEquals`). Die bestehenden Felder `visibleWhen` und `disabledWhen` wertet dieselbe Engine aus.

Tourenplanung bleibt ein Cockpit und damit `DASHBOARD`. Fahrer und Fahrzeuge sind Arbeitslisten mit `listDetail` und damit `MASTER_DETAIL`.

Referenzbefehle:

- Tourenplanung: `tour.openWorkspace`, `tour.resolveDeliveryNote`, `tour.create`, `tour.openLoading`, `tour.showHints`, `tour.cancel`
- Fahrer: `driver.create`, `driver.openAvailable`, `driver.openTours`, `driver.openDocuments`, `driver.export`
- Fahrzeuge: `vehicle.create`

## Bausteine und Tokens

Feldtypen bilden die erlaubten Bausteine: TextField, NumberField, DateField, DateTimeField, Select, EntityPicker, MultiEntityPicker, Checkbox, DataTable. Status, Kennzahlen und die Aktionsleiste kommen aus den vorhandenen Renderern. Dichte `comfortable | compact | expertDense` und die Touch-Höhe bleiben die Tokens. Neue Bausteine erweitern diese Liste.

## CI

`tests/test_screen_governance.py` prüft die drei Referenzmasken.

Fehler sind unter anderem: fehlende Identität, unbekannter Floorplan, doppeltes Feld, unbekannter Feldtyp, unbekannte Datenquelle, unbekannter Referenzbefehl, `UX001` ab drei Primäraktionen, `UX014` destruktive Aktion ohne Bestätigung.

Warnungen sind unter anderem: zwei Primäraktionen, Status vor den Eingaben (`UX004`), mehr als acht Felder ohne Gruppierung, Tabelle ohne Filter, EntityPicker ohne Suchminimum.
