# Rollen- und Berechtigungskonzept

Quelle: `00_hrm_go_live_gesamtwerk.md`, Abschnitt 7.

## Ziel

Ziel ist ein rollenbasierter, zweckgebundener und nachvollziehbarer Zugriff auf Beschaeftigtendaten.

## Rollenuebersicht

| Rolle | Beschreibung | Zugriff |
|---|---|---|
| Employee Self Service | Beschaeftigte | Eigene Daten lesen, Antraege stellen |
| Manager Self Service | Fuehrungskraefte | Teamdaten eingeschraenkt lesen, Freigaben |
| HR Admin | HR-Abteilung | Personalprozesse verwalten |
| Payroll Admin | Lohnbuchhaltung | Payroll-relevante Daten |
| IT Admin | IT-Betrieb | Technische Verwaltung, keine HR-Inhalte soweit moeglich |
| Datenschutz | Datenschutzpruefung | Pruef- und Audit-Zugriff |
| Legal | Rechtspruefung | Dokumentklassen, Retention, Vertragspruefung |
| Auditor | Pruefung | Read-only auf Nachweise und Auditdaten |
| Geschaeftsfuehrung | Management | Aggregierte Reports, Freigaben |

## Kritische Rechte

- Export von Personaldaten
- Loeschung von HR-Daten
- Aenderung von Payroll-Daten
- Zugriff auf eAU-/Krankmeldungsdaten
- Rollenvergabe
- Auditlog-Zugriff
- Personenbezogene HR-Reports
- Optional freigegebene KI-Assistenzfunktionen
- Massenaenderungen

