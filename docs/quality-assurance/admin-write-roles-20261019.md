# Administrative Schreibwege mit ausdruecklicher Rolle (ADMIN-WRITE-ROLES-20261019)

## Nutzerentscheid (19.10.2026)

Schreibwege brauchen eine ausdrueckliche serverseitige Berechtigung aus dem bestehenden Rollenmodell. Die Ratsche
verhindert neue Luecken, ersetzt aber deren Schliessung nicht. Administrative Aenderungen werden zuerst
abgesichert; Fachaktionen behalten ihre Bereichsrollen und Freigaben. Das Inventar
(`config/write_routes_without_roles.json`) ist eine Pruefliste: Delegierte Commands koennen Rechte tiefer im Aufruf
pruefen.

## Ergebnis

Alle 82 offenen Schreibwege unter `/api/v1/admin*` tragen jetzt eine Rollen-Abhaengigkeit am Decorator (Lesewege
unveraendert), nach dem Modell von `admin_core`:

| Art | Rolle | Wege |
|---|---|---|
| Konfiguration (Niederlassungen, Geraete, Mobil/Stationen, Monitoring, Nummernkreise, Ausgabeprofile, Vordrucke, Berichtsrechte, DMS, LLM-Gateway, Migration, Setup, Kassen/TSE-Geraete) | `admin` | 77 |
| Massenimport Kasse, DSFinV-K-Export, TSE-Export | `admin`, `FINANCE_ADMIN` | 3 |
| TSE-Transaktion starten/abschliessen (Kassiervorgang, Fachaktion) | `SALES_BEARBEITEN`, `SALES_ADMIN`, `admin`, `manager` | 2 |

Bestehende Entscheidungen bleiben (z. B. Erntefenster aus Vorlage: Leitung `admin`/`manager`).

## Nachweis

- `tests/test_admin_schreibwege_rollen.py`: Jeder Admin-Schreibweg weist Fachrollen ohne Leitung mit 403 ab (die
  Rolle greift vor jedem Datenzugriff); die Erlaubt-Faelle (admin, Finanzleitung, Verkauf am Kassiervorgang) prueft
  der Vertrag statisch an der Rollen-Abhaengigkeit, ohne Handler auszufuehren (Kassenuebernahme, Steuerexport, TSE
  und DMS haben Wirkung oder rufen externe Dienste).
- Rollen-Ratsche: 1603 -> 1521 Bestandswege.
- 51 Suiten der Admin-Router gruen.

## Nebenbefunde dieses Laufs

- `test_reporting_command_atomic` war seit Schritt 7 des Rollouts rot (Mini-App ohne gepruefte Claims); jetzt mit
  `testgrenze.setze_identitaet`.
- Seit Mahnen fuer Agenten gesperrt ist, sperrte die zentrale Agentengrenze auch das **Lese**-Werkzeug
  `fibu.dunning.status`. Statusleser (`mapped_read`) loesen keine Maskenaktion aus und zaehlen nicht mehr.

## Nicht gelaufen

Ein Lauf der gesamten Backend-Suite wurde vom System wegen Speichermangels abgebrochen, bevor er Ergebnisse schrieb.
Belegt sind die gezielten Suiten oben sowie die 106 Suiten der in Schritt 7 geaenderten Router (3768 gruen; der eine
Fehlschlag ist hier behoben). Ein Gesamtlauf steht aus.
