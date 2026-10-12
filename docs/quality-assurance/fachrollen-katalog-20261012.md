# Fachrollen: Der Anmeldedienst kennt die Rollen nicht, die der Code verlangt

Stand: 2026-10-12 · Slice `FACHROLLEN-KATALOG-20261012` · Befund aus den Rollen-Slices
([Hauptbuch](hauptbuch-rollen-20261011.md) bis [übrige Finanzwege](finanz-rest-rollen-20261012.md))

## Befund

Der Code prüft **34 Fachrollen** – `FINANCE_LESEN`, `FINANCE_BEARBEITEN`, `FINANCE_ADMIN`,
`KONTENPLAN_PFLEGE`, `KONTENRAHMEN_PFLEGE`, dazu die Lese-, Bearbeiter- und Leitungsrollen von
Verkauf, Vertrieb, Einkauf, Lager, Personal, Agrar, Ernteannahme, Kontrakt, Futtermittel und
Qualität.

Die Realm-Datei des Anmeldedienstes (`config/keycloak/realm-export.json`) definiert sechs Rollen:
`admin`, `auditor`, `crm_manager`, `finance_manager`, `inventory_manager`, `user`. **Keine der 34
Fachrollen ist dabei.** Auch `manager`, das viele Wege als zweite allgemeine Rolle zulassen, gibt es
dort nicht (nur `finance_manager` und zwei weitere).

Folge: In einer Installation aus dieser Realm-Datei kann niemand eine Fachrolle bekommen. Jeder Weg
mit Rollenprüfung – seit Oktober rund 360 Finanzwege – ist dann für alle außer `admin` zu. Solange
der Dev-Token alle Rollen mitbrachte, fiel das nicht auf; seit dem 12.10.2026 gibt es ihn nicht mehr.

Die QA-Dokumente der Rollen-Slices schrieben jeweils „im Anmeldedienst zuweisen". Das setzte Rollen
voraus, die dort nicht angelegt sind.

## Lieferung

Die Realm-Dateien bearbeitet derzeit ein anderer Agent (`IDENTITY-CONTROL-20261012`, mit nicht
committeten Änderungen). Deshalb hier **kein Eingriff in den Realm**, sondern die Liste daneben:

- **`config/keycloak/fachrollen.json`** – alle 34 Fachrollen mit deutscher Beschreibung. Die Liste,
  aus der der Anmeldedienst eingerichtet wird.
- **`scripts/check_fachrollen.py`**
  - ohne Argument: schreibt den Katalog aus dem Code neu; von Hand geschärfte Beschreibungen bleiben
  - `--check`: Fehlerstatus, wenn Code und Katalog auseinanderlaufen
  - `--realm`: zeigt, welche Katalogrollen der Realm-Datei fehlen (heute alle 34)
- **`tests/test_fachrollen_katalog.py`** – hält den Katalog am Code fest: Eine neue Rolle im Code ohne
  Katalogeintrag macht den Test rot.

Gesucht wird nach Rollennamen der Form `BEREICH_STUFE` mit den Stufen `LESEN`, `BEARBEITEN`, `ADMIN`,
`LOESCHEN`, `PFLEGE` in allen Dateien unter `app/`.

## Nachweis

| Prüfung | Ergebnis |
|---|---|
| `tests/test_fachrollen_katalog.py` | 4 bestanden |
| `python scripts/check_fachrollen.py --check` | aktuell, 34 Rollen |
| `python scripts/check_fachrollen.py --realm` gegen die Realm-Datei im Repository | 0 von 34 vorhanden |

**Nicht geprüft:** der laufende Anmeldedienst. Welche Rollen dort tatsächlich angelegt sind, zeigt
nur der Dienst selbst; geprüft ist die Realm-Datei im Repository (Stand `HEAD` und die nicht
committete Fassung im Arbeitsbaum – beide ohne Fachrollen).

## Vor einer Inbetriebnahme

1. Die 34 Rollen aus `fachrollen.json` als Realm-Rollen anlegen (Realm-Datei und laufender Dienst –
   eine geänderte Realm-Datei wird nicht von selbst übernommen).
2. `manager` entweder als Rolle anlegen oder aus den Rollensätzen im Code nehmen. Heute steht es in
   `finance_read`, `finance_write`, `beleg_write` und anderen, ohne im Realm zu existieren.
3. Den Benutzern ihre Rollen geben: Buchhaltung `FINANCE_BEARBEITEN`, Finanzleitung `FINANCE_ADMIN`,
   Prüfer `FINANCE_LESEN`, Kontenpflege `KONTENPLAN_PFLEGE`.
4. `python scripts/check_fachrollen.py --realm` muss ohne fehlende Rolle enden.

## Offen

- **Die Rollen im Realm anlegen** – beim Eigentümer der Realm-Dateien.
- **Die sechs vorhandenen Realm-Rollen** (`finance_manager`, `crm_manager`, `inventory_manager`,
  `auditor`) verlangt kein Weg mit dem hier gesuchten Namensmuster. Ob andere Stellen sie prüfen, ist
  nicht vermessen.
- **Rollenbündel:** 34 Einzelrollen je Benutzer zuzuweisen ist mühsam. Zusammengesetzte Rollen oder
  Gruppen („Buchhaltung", „Finanzleitung", „Verkauf Innendienst") wären der nächste Schritt.
- **`--realm` läuft nicht in der CI.** Die Prüfung würde heute rot enden und gehört erst eingeschaltet,
  wenn die Rollen angelegt sind.
