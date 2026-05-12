# HR-Time kanonisches Kerndatenmodell

Stand: 2026-05-08

## Zweck

Dieses Dokument ist die verbindliche Datenmodell-Basis fuer die HR-Time-Slices.
Es verhindert, dass Zeiterfassung, Abwesenheit, Fahrerzeit, Dienstplanung,
Kalender, Payroll, Tourenplanung und Saisonplanung eigene, widerspruechliche
Mitarbeiter- oder Zeitbegriffe erzeugen.

## Modellgrenzen

`domain_hr` ist fachlich fuehrend fuer:

- HR-Time-Profil je Mitarbeiter und Tenant
- Arbeitszeit- und Abwesenheitsbuchungen als kanonische Zeitereignisse
- Fahrerzeitereignisse mit Tour-/Fahrzeug-/Tacho-Bezug
- Planungsblocker fuer Schicht, Kalender, Kampagne und Payroll

Nicht fuehrend ist `domain_hr` fuer:

- Identitaet und Login: bleibt `domain_shared.users` / Keycloak
- Kunden, Auftraege, Frachtbrief, Waage: bleiben jeweilige ERP-Domaenen
- Lohnabrechnung: HR-Time liefert Export- und Auditwerte, Payroll-System bleibt extern oder eigener Folgeslice
- private Kalenderinhalte: HR-Time speichert nur notwendige Busy-/Blocker-Informationen

## Kanonische Identitaeten

| Begriff | Format | Fuehrung | Regel |
|---------|--------|----------|-------|
| `tenant_id` | Text/UUID-kompatibel | Plattform | Muss auf jedem HR-Time-Datensatz stehen. Keine tenant-uebergreifenden Joins ohne expliziten Scope. |
| `employee_ref` | stabiler String, bevorzugt User-ID | HR-Time Mapping | Muss unveraenderlich fuer Buchungen bleiben, auch wenn Name/E-Mail wechseln. |
| `display_name` | Text | HR-Time Read Model | Darf geaendert werden, nie als technischer Key nutzen. |
| `manager_ref` | `employee_ref` | HR-Time Mapping | Optional; Freigabe- und Eskalationslogik nutzt diesen Bezug. |
| `tour_ref` | String | Tourenplanung | Optional bei Standardzeit, Pflicht bei Fahrerarbeit mit Tourbezug. |
| `vehicle_ref` | String | Fuhrpark | Pflicht bei `DRIVING` und `VEHICLE_CHANGE`. |
| `calendar_event_ref` | String | Kalenderadapter | Externe Event-ID plus Provider-Scope, nicht als HR-Primary-Key nutzen. |

## Kernentitaeten

### `EmployeeTimeProfile`

Ein Profil beschreibt die planungs- und abrechnungsrelevante Sicht auf eine Person.

Pflichtfelder:

- `tenant_id`
- `employee_ref`
- `display_name`
- `role_code`, `role_label`
- `location_code`
- `department`
- `employment_type`: `full_time`, `part_time`, `temp`, `seasonal`, `contractor`
- `weekly_hours`
- `time_model`: `standard`, `shift`, `driver`, `field_service`, `seasonal`, `flex`
- `status`: `active`, `inactive`, `on_leave`

Optionale Felder:

- `manager_ref`
- `cost_center`
- `payroll_group`
- `qualifications`
- `can_drive`
- `driver_card_id`
- `vehicle_refs`
- `calendar_provider`

Konsistenzregeln:

- `can_drive = true` erfordert mindestens eine Fahrerqualifikation vor produktiver Tourzuweisung.
- `time_model = driver` setzt `can_drive = true` oder einen bewusst dokumentierten Ausnahmegrund voraus.
- `status != active` blockiert neue Schicht-, Tour- und Aussendienstplanung.
- `weekly_hours` ist Planungsbasis, nicht automatisch Rechtsfreigabe fuer Ueberstunden.

### `TimeEntry`

Ein `TimeEntry` ist die kanonische Arbeitszeit-, Abwesenheits- oder Korrekturbuchung.

Pflichtfelder:

- `tenant_id`
- `employee_ref`
- `entry_date`
- `hours`
- `entry_type`: `Arbeit`, `Urlaub`, `Krank`, `Bereitschaft`, `Schulung`, `Korrektur`
- `source`: `manual`, `terminal`, `mobile`, `timesheet`, `absence`, `calendar`, `import`
- `status`: `Draft`, `Submitted`, `Approved`, `Rejected`, `Corrected`, `Exported`

Optionale Felder:

- `start_time`, `end_time`
- `cost_center`
- `work_area`
- `correction_reason`
- `notes`
- `approved_by`, `approved_at`
- `audit_ref`

Konsistenzregeln:

- `hours >= 0`
- `Approved` braucht `approved_by` oder eine dokumentierte Auto-Freigabe-Regel.
- `Corrected` braucht `correction_reason`.
- `Exported` darf nicht ohne neuen Korrekturdatensatz veraendert werden.
- Abwesenheiten mit `Approved` wirken als Blocker fuer Tour, Schicht, Aussendienst und Payroll.

### `DriverTimeEvent`

Ein `DriverTimeEvent` ist granularer als ein `TimeEntry` und bildet Fahreraktivitaeten ab.

Pflichtfelder:

- `tenant_id`
- `employee_ref`
- `event_date`
- `event_type`: `DRIVING`, `LOADING`, `UNLOADING`, `OTHER_WORK`, `AVAILABILITY`, `BREAK`, `DAILY_REST`, `WEEKLY_REST`, `TOUR_START`, `TOUR_END`, `VEHICLE_CHANGE`, `TACHO_IMPORT`
- `source`: `manual`, `driver_app`, `tacho`, `telematics`, `dispatch`
- `starts_at`, `ends_at`, `duration_minutes`

Optionale Felder:

- `tour_ref`
- `vehicle_ref`
- `location_ref`
- `correction_status`
- `correction_reason`
- `audit_ref`
- `raw_payload`

Konsistenzregeln:

- `ends_at > starts_at`
- `DRIVING` und `VEHICLE_CHANGE` brauchen `vehicle_ref`.
- produktive Fahrerereignisse ausser Ruhezeiten brauchen im Regelfall `tour_ref`.
- Ueberlappungen pro `employee_ref` sind Blocker, ausser ein fachlich erlaubtes Parallelereignis ist explizit modelliert.
- Tacho-/Telematikwerte sind Nachweisquelle; manuelle Abweichungen brauchen Begruendung und Freigabe.

## API-Resource-URLs

Die API-URLs sind fachliche Ressourcen, nicht UI-Layouts.

| Resource | URL | Zweck |
|----------|-----|-------|
| Mitarbeiter | `GET /api/v1/personal/mitarbeiter` | bestehende Mitarbeiterliste aus User-/HR-Read-Model. |
| HR-Time-Profile | `GET /api/v1/personal/time-profiles` | kanonische Planungsprofile fuer Schicht, Fahrer, Kalender, Payroll. |
| Zeiteintraege | `GET /api/v1/personal/zeiterfassung` | kanonische Zeit-/Abwesenheitsbuchungen. |
| Zeitbuchung erstellen | `POST /api/v1/personal/time-entries` | neue kanonische Zeitbuchung im Status `Draft`. |
| Zeitbuchung einreichen | `POST /api/v1/personal/time-entries/{id}/submit` | Statusuebergang `Draft`, `Rejected`, `Corrected` nach `Submitted`. |
| Zeitbuchung freigeben | `POST /api/v1/personal/time-entries/{id}/approve` | Statusuebergang `Submitted` nach `Approved` mit Freigeber. |
| Zeitbuchung korrigieren | `POST /api/v1/personal/time-entries/{id}/correct` | Korrektur mit Pflichtgrund; `Exported` wird nicht still veraendert. |
| Abwesenheiten lesen | `GET /api/v1/personal/absences` | kanonische Abwesenheitsblocker aus Zeit-/Absence-Read-Model. |
| Abwesenheiten importieren | `POST /api/v1/personal/absences/import` | Importvertrag fuer Urlaubsverwaltung/SaaS; schreibt `TimeEntry(source=absence)`. |
| Schichten lesen | `GET /api/v1/personal/shifts` | geplante Schichten/Einsaetze mit Besetzung und Konflikten. |
| Schicht erstellen | `POST /api/v1/personal/shifts` | erstellt eine Schicht und prueft Mindestbesetzung, Profile, Qualifikationen und Abwesenheiten. |
| Kalenderereignisse lesen | `GET /api/v1/personal/calendar-events` | provider-neutrale Kalenderblocker, Schichten, Touren, Abwesenheiten und Aussendiensttermine. |
| Kalenderereignis erstellen | `POST /api/v1/personal/calendar-events` | schreibt ein internes oder importiertes Event mit Sync-State, Sichtbarkeit und Konfliktlevel. |
| Payroll-Exporte lesen | `GET /api/v1/personal/payroll-exports` | erzeugte Lohnexportpakete mit Items und Blockern. |
| Payroll-Export erzeugen | `POST /api/v1/personal/payroll-exports` | baut Exportpaket aus freigegebenen Zeitwerten und meldet nicht freigegebene Buchungen als Blocker. |
| Kampagnenkapazitaet lesen | `GET /api/v1/personal/campaign-capacity` | Saison-/Kampagnenplaene mit Rollenbedarf und Engpaessen. |
| Kampagnenkapazitaet erstellen | `POST /api/v1/personal/campaign-capacity` | bewertet Rollenbedarf gegen Profile, Abwesenheiten und Schichten. |
| Aussendienstplan lesen | `GET /api/v1/personal/field-service-plan` | geplante Kunden-/Feldbesuche mit Kampagnen- und Konfliktbezug. |
| Aussendiensttermin erstellen | `POST /api/v1/personal/field-service-plan` | plant Besuch und prueft Profil, Abwesenheit und Kalenderblocker. |
| Driver-Time Summary | `GET /api/v1/personal/driver-time/summary` | Fahrerzeit-KPIs, Ereignisse, Plausibilitaetsbefunde. |
| Time Cockpit | `GET /api/v1/personal/time-cockpit` | operative Freigabe-, Compliance- und Payroll-Sicht. |
| Stundenzettel | `POST/GET /api/v1/personal/stundenzettel` | Legacy-/Pilotvertrag fuer Fahrer-Stundenzettel. |

Folge-URLs muessen diese Begriffe wiederverwenden:


## Konsistenzanalyse

| Risiko | Konflikt | Entscheidung |
|--------|----------|--------------|
| User-ID vs. Name | Stundenzettel nutzen aktuell Fahrernamen; produktive Buchungen brauchen stabile IDs. | `employee_ref` wird stabiler Key. Anzeigenamen bleiben reine Labels. |
| Standardzeit vs. Fahrerzeit | Fahrerzeit ist granularer und rechtlich anders. | `DriverTimeEvent` bleibt eigene Entitaet; aggregierte Arbeitszeit fliesst als `TimeEntry` in Payroll. |
| Abwesenheit vs. Tour/Schicht | Abwesenheiten koennen externe Quelle haben. | Genehmigte Abwesenheit wird als `TimeEntry(entry_type=Urlaub/Krank, source=absence)` oder als Absence-Read-Model gespiegelt und blockiert Planung. |
| Kalender vs. Datenschutz | Private Termine duerfen nicht in HR/Dispo sichtbar werden. | Kalenderadapter speichert nur Busy-Blocker und technische Event-Refs, keine privaten Inhalte. |
| Payroll vs. Korrektur | Exportierte Zeiten duerfen nicht still veraendert werden. | Nach Export nur Korrekturbuchung mit Audit-Ref, nie Mutation ohne Spur. |
| Saisonplanung vs. Einzelbuchung | Kampagnen brauchen Prognose, Zeitbuchung ist Ist. | Kampagnenkapazitaet nutzt Profile, Abwesenheiten, Schichten und geplante Touren; Ist-Zeit bleibt separat. |
| Mandantenfaehigkeit | HR-Daten sind besonders sensibel. | Jede Tabelle und jeder API-Zugriff braucht `tenant_id`; keine globalen HR-Views. |

## Umsetzung fuer `HR-TIME-DATA-001`

Dieser Slice darf nur die belastbare Basis schaffen:

- SQL-Vertrag fuer `employee_time_profiles`, erweiterte `time_entries` und `driver_time_events`
- API `GET /api/v1/personal/time-profiles`
- Fallback aus `domain_shared.users`, falls das neue Profil-Read-Model noch nicht befuellt ist
- Pilot-Fallback, falls lokale Datenbanktabellen fehlen
- Tests fuer Profil-Mapping, KPI-Zusammenfassung und Endpoint-Vertrag

Nicht Teil dieses Slices:

- Schreibworkflow fuer Zeiten
- Genehmigungsaktionen
- echter Urlaubsverwaltung-Connector
- Kalender-OAuth
- Payroll-/DATEV-Datei
- Kampagnen-Optimierung
