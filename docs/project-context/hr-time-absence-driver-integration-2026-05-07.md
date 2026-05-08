# HR Time, Abwesenheit und Driver-Time-Layer

## Zweck

Diese Notiz haelt die Zielarchitektur fuer deutsche Arbeitszeit-/Abwesenheitsverwaltung im VALEO-Kontext fest.
Der unmittelbare Anlass ist die Bewertung lizenzrechtlich unproblematischer Kandidaten fuer 27 Mitarbeitende, davon ein relevanter Anteil LKW-Fahrer.

## Entscheidung

VALEO uebernimmt keine AGPL-/GPL-Zeiterfassung als Codebasis.

Stattdessen gilt:

- Abwesenheiten werden mit `urlaubsverwaltung/urlaubsverwaltung` als bevorzugtem Kandidaten geprueft, weil das Projekt fachlich deutsch gepraegt und unter Apache-2.0 lizenziert ist.
- Klassische Zeiterfassung wird entweder als kommerzieller deutscher SaaS-Dienst angebunden oder als schlanker VALEO-eigener Service gebaut.
- Fahrerzeiten werden in einem VALEO-eigenen Driver-Time-Layer modelliert, weil LKW-Fahrer andere Ereignisse, Nachweise und Plausibilitaetsregeln brauchen als reine Buero-Zeiterfassung.
- `urlaubsverwaltung/zeiterfassung` und vergleichbare AGPL-Projekte duerfen nur als fachliche Referenz oder unmodifizierter, klar getrennter Fremddienst bewertet werden, nicht als kopierte oder geforkte VALEO-Codebasis.

## Lizenzbewertung

| Kandidat | Lizenz | Bewertung fuer VALEO |
|----------|--------|----------------------|
| `urlaubsverwaltung/urlaubsverwaltung` | Apache-2.0 | Bevorzugter Open-Source-Kandidat fuer Urlaub, Krankheit und Abwesenheitsfreigaben. Permissiv, mit Notice-Pflichten handhabbar. |
| `urlaubsverwaltung/zeiterfassung` | AGPL-3.0 | Fachlich passend, aber als Codebasis vermeiden. AGPL erzeugt bei modifizierter Netzbereitstellung Source-Offer-Pflichten fuer die betroffene Anwendung. |
| Horilla | LGPL-2.1 | Als separater HRMS-Dienst moeglich, fachlich aber breiter und weniger deutsch-spezifisch. Keine bevorzugte Codebasis fuer VALEO. |
| cityssm Attendance Tracking | MIT | Lizenzrechtlich einfach, fachlich aber eher Abwesenheits-/Call-Out-Nische, nicht ausreichend fuer deutsche Arbeitszeit plus Fahrerlogik. |
| Kommerzieller deutscher SaaS | Vertraglich | Lizenzrechtlich oft sauber, wenn AVV/DPA, Datenexport, SSO/API und Auftragsverarbeitung passen. Fachliche Abhaengigkeit und Kosten separat pruefen. |

## GitHub Topic Scan HRMS

Die GitHub-Topic-Seite `human-resources-management-system` wurde als zusaetzlicher Kandidatenpool geprueft.
Sie listet 67 oeffentliche Repositories; die sichtbaren Top-Treffer bestaetigen die bisherige Lizenzlinie.

| Kandidat | Lizenz / Signal | Bewertung |
|----------|-----------------|-----------|
| OrangeHRM | GPL-3.0 | Reifes HRMS, aber Copyleft. Als separater Fremddienst moeglich, nicht als VALEO-Codebasis. |
| MintHCM | AGPL-3.0 | Funktional breites HCM, aber wegen AGPL nicht als integrierte oder modifizierte VALEO-Codebasis geeignet. |
| Headcount | AGPL-3.0 | Modernere HRM-Anwendung mit Time-off/Employee Self Service, aber AGPL. Nicht als VALEO-Codebasis. |
| GleamHRM | GPL-3.0 | HRM mit Leave und Attendance, aber alter Laravel-Stack und GPL-3.0. Nicht bevorzugt. |
| Diverse kleinere HRMS-Demos | oft keine klare Lizenz, alt oder Demo-/Studienprojekt | Fuer VALEO nicht belastbar genug; fehlende Lizenz ist rechtlich schlechter als eine unpassende Lizenz. |

Fazit: Die Topic-Seite liefert keinen besseren permissiven Kandidaten fuer deutsche Arbeitszeit-/Abwesenheitsverwaltung mit Fahrerbezug.
Sie staerkt die Entscheidung, Abwesenheiten ueber Apache-2.0-Urlaubsverwaltung zu pruefen und Fahrerzeit als VALEO-eigenen Bounded Context zu modellieren.

### MintHCM Zusatzpruefung

Der von GitHub ueber Camo referenzierte MintHCM-GIF verweist auf die MintHCM-Produktpraesentation.
Fachlich ist MintHCM deutlich breiter als eine reine Zeiterfassung: README und Projektprofil nennen unter anderem Recruitment, Time Management, Onboarding/Offboarding, Kalender, Leave Management, Ressourcenbuchung, Travel & Expenses, Workplace Management, Analytics, Rollen/Rechte, Mitarbeiterprofile, Kompetenzen, Bewertungen sowie mobile Apps.

Die technische Basis ist fuer VALEO jedoch kein einfacher Fit:

- MintHCM basiert auf SugarCRM CE und SuiteCRM.
- Stack laut README: Apache2, PHP 8.0, MySQL 8.0 oder MariaDB, ElasticSearch 7.9.
- API ist SuiteCRM-aehnlich, aber mit projektspezifischen Abweichungen.
- Das Repo weist AGPL-3.0 aus.

Bewertung: MintHCM ist als fachlicher Vergleichskandidat interessant, aber wegen AGPL-3.0, CRM-Herkunft und separatem PHP/MySQL/Elastic-Stack keine bevorzugte VALEO-Codebasis. Wenn ueberhaupt, dann nur als strikt getrennter Evaluierungsdienst ohne Fork und ohne Codeuebernahme.

## Zielarchitektur

```text
Keycloak / OIDC
  |
  +-- Urlaubsverwaltung (Apache-2.0, separater Dienst)
  |     - Urlaub
  |     - Krankheit
  |     - Genehmigungen
  |     - Abwesenheitsexporte
  |
  +-- VALEO HR-Time API
        - Mitarbeitenden-/Rollen-Mapping
        - Abwesenheits-Read-Model
        - Zeiterfassungs-Adapter
        - Driver-Time-Layer
        - Payroll-/DATEV-/Lohnexport
```

Die Integrationsgrenze ist bewusst serviceorientiert. Fremdsysteme laufen getrennt, VALEO importiert oder synchronisiert definierte Read-Models und uebernimmt nicht deren fachliche Kernlogik als eingebetteten Code.

## Driver-Time-Layer

Der Driver-Time-Layer ist ein eigener VALEO-Bounded-Context fuer LKW-Fahrer.

Kanonische Ereignisse:

- `DRIVING`: Fahren
- `LOADING`: Beladen
- `UNLOADING`: Entladen
- `OTHER_WORK`: sonstige Arbeit
- `AVAILABILITY`: Bereitschaft / Wartezeit
- `BREAK`: Pause
- `DAILY_REST`: taegliche Ruhezeit
- `WEEKLY_REST`: woechentliche Ruhezeit
- `TOUR_START` / `TOUR_END`: Tourrahmen
- `VEHICLE_CHANGE`: Fahrzeugwechsel
- `TACHO_IMPORT`: Import aus digitalem Tachographen oder Telematik

Mindestdaten pro Ereignis:

- Mitarbeiter-ID
- Zeitstempel von/bis
- Ereignistyp
- Fahrzeug-ID, wenn relevant
- Tour-ID, wenn relevant
- Standort oder Geofence, wenn vorhanden
- Quelle: manuell, App, Tacho, Telematik, Dispo
- Korrekturstatus und Audit-Referenz

## Plausibilitaets- und Compliance-Layer

Der erste VALEO-Pilot soll keine vollstaendige Rechtsauslegung automatisieren. Er soll Regeln als Hinweise und Blockerklassen fuehren:

- fehlende Ruhezeit vor Tourstart
- unplausible Ueberlappungen von Fahren, Pause und Beladen
- Tour ohne Fahrzeug oder Fahrer
- Tacho-Import weicht von manueller Buchung ab
- fehlende Korrekturbegruendung
- Abwesenheit kollidiert mit Tour oder Zeitereignis
- Export ist blockiert, wenn Pflichtnachweise fehlen

Rechtsquellen fuer die Detailkalibrierung sind insbesondere die EU-Regeln zu Lenk- und Ruhezeiten sowie deutsches Arbeitszeitrecht. Die fachliche Freigabe muss mit HR/Dispo und rechtlicher Beratung erfolgen.

## Integrationsschnittstellen

### Abwesenheiten

Urlaubsverwaltung liefert:

- Mitarbeiterstamm-Referenz
- Abwesenheitstyp
- Zeitraum
- Genehmigungsstatus
- Vertretung / Verantwortliche
- Aenderungszeitpunkt

VALEO nutzt diese Daten:

- in Tourplanung und Disposition als Verfuegbarkeitsblocker
- in Payroll-/Lohnexporten
- in HR-Reports
- als Kontext fuer Agenten-Hinweise

### Klassische Zeiterfassung

Fuer Buero, Lager, Waage und Werkstatt reichen generische Zeitereignisse:

- Start
- Ende
- Pause
- Kostenstelle / Arbeitsbereich
- Korrekturgrund
- Freigabestatus

Die Umsetzung kann entweder ueber einen deutschen SaaS-Adapter oder ueber einen kleinen VALEO-Service erfolgen. Ein SaaS-Kandidat muss SSO/OIDC, AVV/DPA, Export, API und Datenportabilitaet nachweisen.

### Fahrerzeit

Fahrerereignisse bleiben in VALEO, weil sie mit Tour, Fahrzeug, Waage, Frachtbrief, Be-/Entladung und Spaesen gekoppelt sind.

Der Tacho-/Telematik-Import wird als spaetere Adapter-Schicht geplant. Bis dahin kann der Pilot manuelle Ereignisse, Tourbezug und Plausibilitaet abbilden.

## Pilotumfang

Pilot `HR-TIME-PILOT-001`:

- 27 Mitarbeitende als Mandanten-/Stammdatenrahmen
- 5 Pilotnutzer, davon mindestens 2 LKW-Fahrer
- Abwesenheit: Urlaubsverwaltung getrennt starten oder als Demo-Container bewerten
- VALEO: Driver-Time-Datenmodell, manuelle Ereigniserfassung, Tour-/Fahrzeugbezug, Abwesenheitskollisionen
- Export: CSV/JSON-Vertrag fuer Lohn/Payroll, noch keine produktive DATEV-Anbindung

Umsetzungsstand 2026-05-07:

- `packages/hr-domain/src/domain/entities/driver-time-event.ts` definiert den ersten VALEO-eigenen Driver-Time-Contract mit Ereignisart, Quelle, Tour, Fahrzeug, Standort, Korrekturstatus und Audit-Referenz.
- `packages/hr-domain/src/domain/services/driver-time-service.ts` liefert Tages-/Fahrerzusammenfassungen und Plausibilitaetsbefunde fuer Ueberlappungen, fehlenden Tour-/Fahrzeugbezug, Abwesenheitskollisionen und Tacho-/Manuell-Abweichungen.
- `app/api/v1/endpoints/personal.py` stellt mit `GET /api/v1/personal/driver-time/summary` den ersten Backend-Toolvertrag fuer Fahrerzeit-KPIs, Ereignisse und Plausibilitaetsbefunde bereit.
- `app/api/v1/endpoints/personal.py` stellt mit `GET /api/v1/personal/time-cockpit` zusaetzlich ein professionelles Time-&-Labor-Cockpit bereit: Perioden-KPIs, Freigabequeue, Compliance-Befunde, Payroll-Readiness und Driver-Time-Zusammenfassung.
- `packages/frontend-web/src/lib/api/personal.ts` exponiert `useDriverTimeSummary` und `useTimeCockpit`; `packages/frontend-web/src/pages/personal/zeiterfassung.tsx` nutzt diese Vertraege statt harter lokaler Driver-Time-Daten.

Orientierung fuer den weiteren Profi-Ausbau:

- SAP SuccessFactors Time Tracking/Time Management: integrierte Time-Off-/Time-Sheet-Prozesse, Clock-In/Clock-Out, Perioden- und Payroll-Ausrichtung.
- Oracle Time and Labor: Integration mit Global HR, Absence Management, Payroll und Project Costing.
- Shiftfy: Zeiterfassung, Schichtplanung, Abwesenheiten, Berichte, Manager-Freigabe, Audit-Trail und Kommentarfunktion.

VALEO muss diese Muster domänenspezifisch erweitern: Driver-Time, Tour/Fahrzeug, Lenk-/Ruhezeit-Plausibilitaet, Waage/Frachtbrief und spaetere Tacho-/Telematik-Adapter.

Nicht im ersten Pilot:

- automatischer Tacho-Download
- vollstaendige Bussgeld-/Rechtsbewertung
- produktiver SaaS-Wechsel
- tiefe Modifikation fremder Open-Source-Projekte

## Offene Pruefungen

- Rechtspruefung Apache-2.0-Notices und AGPL-Abgrenzung.
- Anbieterpruefung fuer deutschen SaaS: AVV/DPA, Hostingort, Subprozessoren, Datenexport, API, SSO.
- Fachfreigabe der Fahrerereignisse durch Dispo und HR.
- Entscheidung, ob klassische Zeiterfassung im Pilot gebaut oder angebunden wird.
- Tacho-/Telematik-Schnittstellen und Datenformate erheben.

## Quellenstand

Geprueft am 2026-05-07:

- `urlaubsverwaltung/urlaubsverwaltung`: GitHub weist Apache-2.0 aus: https://github.com/urlaubsverwaltung/urlaubsverwaltung
- `urlaubsverwaltung/zeiterfassung`: Lizenzdatei ist AGPL-3.0: https://raw.githubusercontent.com/urlaubsverwaltung/zeiterfassung/main/LICENSE.md
- GitHub Topic `human-resources-management-system`: https://github.com/topics/human-resources-management-system
- OrangeHRM: GitHub weist GPL-3.0 aus: https://github.com/orangehrm/orangehrm
- MintHCM: Lizenzdatei ist AGPL-3.0: https://raw.githubusercontent.com/minthcm/minthcm/master/LICENSE
- MintHCM README mit Featureliste, Stack und API-Hinweisen: https://github.com/minthcm/minthcm
- Headcount: Lizenzdatei ist AGPL-3.0: https://raw.githubusercontent.com/bluewave-labs/Headcount/main/LICENSE
- GleamHRM: Lizenzdatei ist GPL-3.0: https://raw.githubusercontent.com/glowlogix/gleamhrm/master/LICENSE
- EU-Regelwerk zu Lenk- und Ruhezeiten: Verordnung (EG) Nr. 561/2006 und Folgeregeln: https://eur-lex.europa.eu/eli/reg/2006/561/oj
- BAuA/BMAS bestaetigen die Pflicht zu einem objektiven, verlaesslichen und zugaenglichen Arbeitszeiterfassungssystem sowie den Arbeitsschutzbezug: https://www.baua.de/DE/Themen/Arbeitsgestaltung/Arbeitszeit/Arbeitszeiterfassung
