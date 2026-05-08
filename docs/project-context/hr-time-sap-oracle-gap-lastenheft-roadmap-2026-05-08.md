# HR-Time GAP, Lastenheft und Roadmap gegen SAP / Oracle HRM

Stand: 2026-05-08

## Zweck

Dieses Dokument uebersetzt den SAP-/Oracle-/Shiftfy-Benchmark in ein VALEO-spezifisches Lastenheft fuer Arbeitszeit, Abwesenheit, Fahrerzeit, Dienstplanung und Landhandel-Saisonplanung.

Die Zielrichtung bleibt:

- keine Ableitung aus AGPL-/GPL-Zeiterfassungs-Code
- Abwesenheit bevorzugt ueber `urlaubsverwaltung/urlaubsverwaltung` oder einen sauber angebundenen Dienst
- VALEO-eigener Time-&-Labor-Kern fuer Landhandel, Fahrerzeit, Tour/Fahrzeug, Waage, Kampagnen und Aussendienst
- spaetere Anbieteranbindung nur ueber klare API-, Datenschutz-, Export- und Lizenzgrenzen

Verbindliche Datenmodellbasis fuer die Umsetzung ist `docs/project-context/hr-time-canonical-core-data-model-2026-05-08.md`.

## Benchmark-Referenz

| Referenz | Relevante Muster fuer VALEO | Konsequenz |
|----------|-----------------------------|------------|
| SAP SuccessFactors Time Tracking | Clock-in/out auf Desktop, Mobile und Terminal; Genehmigungscenter; Compliance-Konfiguration fuer Pausen, Ueberstunden, Schichtzulagen; Alerts; Analytics; Payroll-/S/4HANA-Kostenzuordnung; Schichtplanung ueber Integration oder Partnerloesung. | VALEO braucht einen Time-&-Labor-Kern mit Freigabequeue, Regelengine, Kostenstellen-/Projektbezug, Analytics und Integrationsschnittstellen. |
| SAP Employee Central Time Sheet | Positive und negative Zeitaufzeichnung, woechentliche Freigabe, alternative Kostenstellen, Ruecknahme und Aenderung bereits genehmigter Zeiten. | VALEO muss Buchungskorrekturen, Audit und Kostenstellenwechsel als Pflichtfaehigkeit fuehren. |
| Oracle Cloud HCM Time and Labor | Regelbasierte, kalenderbasierte Time Cards; konfigurierbare Layouts; Echtzeit-Regeln; Integration mit Global HR, Absence Management, Global Payroll und Project Costing. | VALEO sollte Zeitdaten nicht isoliert bauen, sondern als kanonischen Vertrag fuer HR-Stamm, Abwesenheit, Lohn, Kostenrechnung und Projekte. |
| Shiftfy | Deutsche Zeiterfassung per App, automatische Pausenberechnung nach ArbZG, Schichtplanung, Abwesenheiten, Audit-Trail, Projektbuchung, DATEV-Export, Teamkalender, Standorte, Qualifikationen, PWA. | Fuer 27 Mitarbeitende ist der Bedienstandard klar: einfach, mobil, auditierbar, lohnfaehig. VALEO muss aber Fahrer-, Tour- und Landhandel-Spezifika darueberlegen. |

## GAP-Liste

Prioritaeten: P0 = produktionskritisch, P1 = Pilot-/Rollout-kritisch, P2 = Ausbau/Optimierung.

| Bereich | Benchmark-Faehigkeit | VALEO-Stand | GAP | Zielbild | Naechster Slice |
|---------|----------------------|-------------|-----|----------|-----------------|
| HR-Stamm und Rollen | SAP/Oracle koppeln Zeit an Mitarbeiter, Organisation, Manager, Kalender, Payroll und Kostenstellen. | Personal-API und Time-Cockpit existieren, aber kein vollstaendiges HR-Time-Stammdatenmodell. | P0 | Canonical `EmployeeTimeProfile` mit Rolle, Standort, Vertragsmodell, Manager, Qualifikationen, Kostenstelle, Fahrzeug-/Tourfaehigkeit. | `HR-TIME-DATA-001` |
| Zeiterfassung | Clock-in/out, Timesheet, Korrektur, Freigabe, mobile Nutzung. | Cockpit und Summary-API vorhanden; Persistenz und Buchungsworkflow fehlen. | P0 | Produktive Zeitereignisse mit Status, Korrekturgrund, Audit, Quelle und Freigabe. | `HR-TIME-BOOK-001` |
| Abwesenheit | Time Off/Absence Management mit Genehmigung und Kalenderwirkung. | Strategie fuer Urlaubsverwaltung dokumentiert, aber kein Connector. | P0 | Abwesenheiten als Verfuegbarkeitsblocker in Dienstplanung, Tour, Aussendienst und Payroll. | `HR-TIME-ABS-001` |
| Fahrerzeit | SAP/Oracle decken Standardzeit, aber keine VALEO-spezifische Tour-/Waage-/Tacho-Tiefe. | Driver-Time-Pilot und Summary vorhanden. | P0 | Persistenter Driver-Time-Layer mit Tacho-/Telematik-Import, Tour, Fahrzeug, Be-/Entladen, Bereitschaft, Spesen. | `HR-TIME-DRIVER-002` |
| Regelengine | Pausen, Ruhezeiten, Ueberstunden, Zuschlaege, lokale Regeln. | Erste Plausibilitaetsbefunde im Cockpit. | P0 | Regelkatalog mit Schweregrad, Quelle, fachlicher Freigabe und Payroll-Auswirkung. | `HR-TIME-RULES-001` |
| Schicht- und Einsatzplanung | SAP/Partner und Shiftfy bieten Schichtplanung, Vorlagen, Teamkalender. | Noch keine echte Dienstplanung. | P0 | Planbare Schichten, Verfuegbarkeit, Qualifikationen, Standorte, Saisonkapazitaeten. | `HR-TIME-SCHED-001` |
| Payroll/DATEV/Lohn | SAP/Oracle integrieren Payroll/Costing; Shiftfy bietet DATEV/CSV. | Payroll-Readiness-KPIs, aber kein Exportvertrag. | P0 | Exportfaehige, freigegebene Zeitwerte mit Lohnarten, Kostenstellen, Zuschlaegen, Abwesenheit. | `HR-TIME-PAY-001` |
| Kalenderintegration | SAP/Oracle nutzen Kalenderlogik; Shiftfy Teamkalender. | Kein Outlook/Google/ICS-Connector. | P1 | Bidirektionale Kalenderblocker fuer Urlaub, Schicht, Tour, Aussendienst, Schulung, Wartung. | `HR-TIME-CAL-001` |
| Saison- und Arbeitsspitzenplanung | Enterprise-HCM eher generisch; Landhandel braucht Ernte-/Kampagnenlogik. | Nicht umgesetzt. | P1 | Kapazitaetsplanung nach Ernte, Saat, Duengung, Pflanzenschutz, Silo, Waage, Lager und Fuhrpark. | `HR-TIME-SEASON-001` |
| Kampagneninterferenzen | Standard-HCM erkennt Termin-/Schichtkonflikte, nicht Landhandel-Prozessketten. | Nicht umgesetzt. | P1 | Konfliktmatrix Kampagne vs. Fahrer, Waage, Silo, Labor, Lager, Aussendienst, Lieferfenster. | `HR-TIME-CAMPAIGN-001` |
| Aussendienstplanung | HCM hat Kalender/Abwesenheit; CRM-/Routenlogik separat. | Noch nicht mit HR-Time gekoppelt. | P1 | Agrarberater-/Vertriebsbesuche mit Gebiet, Kunde, Kampagne, Qualifikation, Abwesenheit und Kalender. | `HR-TIME-FIELD-001` |
| Analytics | SAP/Oracle/Shiftfy bieten Berichte und Alerts. | Cockpit-KPIs vorhanden. | P1 | Management-Dashboards fuer Ueberstunden, Fehlzeiten, Saisonlast, Payroll-Blocker, Fahrer-Compliance. | `HR-TIME-ANALYTICS-001` |
| Sicherheit und Datenschutz | Enterprise-Rollen, Audit, DSGVO, SSO. | Keycloak/OIDC-Strategie vorhanden, Detailrollen offen. | P1 | Rollenmodell fuer Mitarbeitende, Manager, HR, Dispo, Payroll, Admin; Datenminimierung und Audit. | `HR-TIME-SEC-001` |
| Offline/Mobile | Shiftfy PWA, SAP mobile; Fahrer/Lager brauchen robuste App. | Frontend-Web vorhanden, keine Offlinefaehigkeit. | P2 | PWA/Offline-Queue fuer Fahrer, Lager und Aussendienst mit spaeter Synchronisation. | `HR-TIME-MOBILE-001` |

## Lastenheft

### Ziel

VALEO stellt eine produktionsfaehige deutsche Arbeitszeit-, Abwesenheits- und Einsatzplanungsloesung fuer einen Landhandel mit ca. 27 Mitarbeitenden bereit. Die Loesung muss Standard-HRM-Faehigkeiten auf SAP-/Oracle-Niveau fuer Kernprozesse erreichen und gleichzeitig die Landhandel-Speziallogik abbilden.

### Nicht-Ziele

- keine vollstaendige SAP-/Oracle-HCM-Kopie
- keine Uebernahme von AGPL-/GPL-Zeiterfassungs-Code in VALEO
- keine automatische Rechtsberatung oder Bussgeldbewertung
- keine produktive Tacho-/Telematik-Anbindung ohne Anbieterfreigabe, Datenschutzpruefung und Testdaten

### Rollen

- Mitarbeitende: Zeiten buchen, Abwesenheiten sehen, Korrekturen beantragen.
- Schichtleitung/Teamleitung: Zeiten pruefen, Schichten planen, Konflikte loesen.
- Disposition: Fahrer, Fahrzeuge, Touren und Ladefenster planen.
- HR: Stammprofile, Abwesenheiten, Regeln und Freigaben verwalten.
- Payroll/Steuerbuero: freigegebene Lohnwerte exportieren.
- Geschaeftsfuehrung/Controlling: Kapazitaet, Kosten, Fehlzeiten und Saisonlast steuern.
- Agent/Copilot: Workboard-, Check-, Konflikt- und Handoff-Hinweise erzeugen, aber keine ungeprueften Buchungen finalisieren.

### Funktionale Anforderungen

| ID | Muss/Soll | Anforderung |
|----|-----------|-------------|
| F-01 | Muss | Zeiten koennen per Desktop und mobil erfasst, korrigiert, kommentiert und freigegeben werden. |
| F-02 | Muss | Jeder Zeitdatensatz hat Quelle, Mitarbeiter, Zeitraum, Status, Kostenstelle, Arbeitsbereich, Audit und Korrekturgrund. |
| F-03 | Muss | Fahrerzeit unterscheidet Fahren, Be-/Entladen, sonstige Arbeit, Bereitschaft, Pause, Ruhezeit, Tourstart/-ende, Fahrzeugwechsel und Tacho-/Telematik-Import. |
| F-04 | Muss | Abwesenheiten blockieren Schicht, Tour, Waage, Aussendienst und Payroll-Export. |
| F-05 | Muss | ArbZG- und Fahrerzeitbefunde werden als Hinweise, Warnungen oder Blocker ausgewiesen. |
| F-06 | Muss | Freigegebene Zeiten koennen mit Lohnarten, Zuschlaegen, Kostenstellen und Abwesenheiten exportiert werden. |
| F-07 | Muss | Kalenderereignisse fuer Urlaub, Schicht, Tour, Aussendienst, Schulung und Wartung koennen synchronisiert oder als ICS bereitgestellt werden. |
| F-08 | Soll | Saisonplanung zeigt Kapazitaetsengpaesse je Standort, Rolle, Qualifikation, Fahrzeug und Kampagne. |
| F-09 | Soll | Kampagneninterferenzen werden erkannt: Ernteannahme vs. Auslieferung, Siloauslastung, Labor, Waage, Fahrer, Aussendiensttermine. |
| F-10 | Soll | Aussendiensttermine beruecksichtigen Gebiet, Kunde, Kultur, Kampagne, Wetter-/Saisonfenster, Abwesenheit und Reisezeit. |
| F-11 | Soll | Qualifikationen wie Staplerschein, Gefahrgut, Fuehrerscheinklasse, Pflanzenschutz-Sachkunde und Tacho-Karte begrenzen Planungsvorschlaege. |
| F-12 | Kann | KI-Copilot erzeugt Claim-/Handoff-/Check-Vorschlaege fuer HR-Time-Slices und Konfliktklaerungen. |

### Nicht-funktionale Anforderungen

- DSGVO: Datenminimierung, Rollenrechte, Audit, Export/Loeschkonzept, AVV fuer Fremdanbieter.
- Verfuegbarkeit: Tagesbetrieb muss auch bei kurzzeitigem Kalender-/Telematik-Ausfall weiterlaufen.
- Nachvollziehbarkeit: jede Aenderung an Zeit, Abwesenheit, Freigabe und Export ist auditierbar.
- Datenportabilitaet: CSV/JSON-Export fuer Lohn, Audit und Anbieterwechsel.
- Mandantenfaehigkeit: alle Daten fuehren Tenant-/Standortbezug.
- Bedienbarkeit: Fahrer, Lager und Saisonkraefte brauchen sehr kurze Buchungswege.

## Mitarbeitertypen im Landhandel

| Mitarbeitertyp | Typische Anliegen | Zu beruecksichtigen |
|----------------|-------------------|---------------------|
| LKW-Fahrer | Touren, Fahrzeug, Lenk-/Ruhezeit, Be-/Entladen, Wartezeit, Spesen, Tacho-Korrekturen. | Mobile/offline Buchung, Tacho-/Telematik-Import, Dispo-Freigabe, Tour-/Frachtbrief-/Waagebezug, Fahrerkarte. |
| Lager/Stapler/Verladung | Schicht, Wareneingang/-ausgang, Verladung, Staplerschein, Ueberstunden in Spitzen. | Qualifikationen, Standort, Lagerbereich, Schichtstaerke, Verladefenster, Sicherheitsunterweisungen. |
| Waage/Annahme | Ernteannahme, Lieferantenandrang, Proben, Wartezeiten, Tagesabschluss. | Kampagnenkalender, Waage-Slots, Labor-/Qualitaetskapazitaet, Pausenvertretung. |
| Silo/Produktion/Mischfutter | Produktionslauf, Reinigung, Wartung, Schichtuebergabe, Rohwarenverfuegbarkeit. | Maschinen-/Anlagenkalender, Wartungsfenster, Qualifikation, Produktionsauftrag, HACCP/Qualitaet. |
| Werkstatt/Fuhrpark | Fahrzeugwartung, Reparatur, HU/SP, Ersatzfahrzeug, Pannen. | Fahrzeugverfuegbarkeit, Wartungskalender, Tourblocker, Arbeitszeit/Kostenstelle. |
| Verkauf/Innendienst | Kundenauftraege, Telefon, Rechnungsfragen, Saisonaktionen. | Buerokalender, Vertretung bei Urlaub, Kampagnenlast, Kundensla. |
| Aussendienst/Agrarberater | Hofbesuche, Feldtermine, Kultur-/Saisonfenster, Angebote, Reklamationen. | Kalender, Route, Gebiet, CRM, Kampagne, Abwesenheit, Reisezeit, Qualifikation. |
| Einkauf/Disposition | Lieferfenster, Verfuegbarkeit, Frachtraum, Saisonmengen, Engpaesse. | Tourplanung, Fahrer-/Fahrzeugkapazitaet, Lager/Silo, Kampagnenkonflikte. |
| Buchhaltung/HR/Controlling | Lohnabschluss, Abwesenheiten, Kostenstellen, Auswertungen, Compliance. | Payroll-Export, Freigabestatus, Audit, Berechtigungen, Reports. |
| Saisonkraefte/Aushilfen | Schneller Start, einfache Buchung, befristete Vertraege, wechselnde Standorte. | Onboarding-Light, Vertragszeitraum, Qualifikation, mobile Buchung, klare Freigabe. |
| Fuehrung/Schichtleitung | Einsatzplanung, Freigaben, Konfliktloesung, Ueberstundensteuerung. | Manager-Cockpit, Alerts, Stellvertretung, Eskalation, Kapazitaetsheatmap. |

## Integrationsanforderungen

| Integration | Richtung | Mindestvertrag |
|-------------|----------|----------------|
| Keycloak/OIDC | VALEO nutzt Identitaet und Rollen. | `employee_id`, `tenant_id`, Rollen, Gruppen, Managerbezug, MFA-Status. |
| HR-Stamm | bidirektional oder VALEO-fuehrend | Mitarbeiter, Vertrag, Standort, Kostenstelle, Manager, Qualifikation, Arbeitszeitprofil. |
| Urlaubsverwaltung/Absence | Import/Sync | Abwesenheitstyp, Zeitraum, Status, Vertreter, Genehmiger, Aenderungszeitpunkt. |
| Time Booking | VALEO-fuehrend | Zeitereignis, Quelle, Status, Korrektur, Audit, Kostenstelle, Projekt/Tour. |
| Tourenplanung/Fuhrpark | bidirektional | Tour, Fahrer, Fahrzeug, Zeitfenster, Lade-/Entladeort, Frachtbrief, Blocker. |
| Waage/Annahme | Ereignis-/Kontextimport | Lieferant/Kunde, Waagezeit, Produkt, Probe, Wartezeit, Kampagne, Schichtlast. |
| Lager/Silo/Produktion | Planungsinput | Produktions-/Verladefenster, Anlagenverfuegbarkeit, Qualifikationsbedarf. |
| CRM/Aussendienst | bidirektional | Besuch, Kunde, Gebiet, Kultur, Kampagne, Follow-up, Angebot/Auftrag. |
| Payroll/DATEV/Lohn | Export | freigegebene Zeiten, Lohnarten, Zuschlaege, Abwesenheiten, Kostenstellen, Korrekturen. |
| Microsoft 365 Kalender | Sync/Publish | Graph Calendar Events, attendees, busy/free, Kategorien, private Sichtbarkeit. |
| Google Kalender | Sync/Publish | Calendar Events, OAuth Scopes, Kalender-ID, Event-Status, recurrence. |
| ICS/CalDAV | Publish/Fallback | read-only Abonnement fuer Urlaub, Schicht, Tour, Wartung, Kampagne. |
| Tacho/Telematik | Import | Fahrerkarte, Fahrzeug, Aktivitaet, Start/Ende, Position/Geofence, Importzeit, Signatur/Quelle. |
| DMS | Ablage | Korrekturbelege, Exportpakete, Freigaben, Pruefprotokolle. |
| Flow-Spine/NeuroASSIST | Hinweise | Konflikte, Blocker, Handoff, Checkliste, Claim-Vorschlag, keine automatische Freigabe. |

## Kreuzverbindungen im ERP

| HR-Time verbindet mit | Warum |
|----------------------|-------|
| Tourenplanung | Fahrer- und Fahrzeugverfuegbarkeit, Lenk-/Ruhezeit, Ladefenster, Spesen. |
| Waage | Ernteannahme erzeugt Arbeitsspitzen, Wartezeiten und Plausibilitaet fuer Fahrerereignisse. |
| Lager/Silo | Schichtstaerke haengt an Kampagne, Anlagenlauf, Verladung und Reinigung. |
| Einkauf/Disposition | Mengen, Lieferfenster und Frachtraum bestimmen Personalbedarf. |
| CRM/Aussendienst | Kundenbesuche duerfen nicht mit Urlaub, Kampagnen oder Pflichtterminen kollidieren. |
| Finance/Controlling | Zeitwerte muessen Kostenstellen, Projekten, Touren und Lohnarten zuordenbar sein. |
| DMS/Audit | Korrekturen, Exportpakete und Compliance-Befunde brauchen revisionsfaehige Ablage. |
| Agent-Ops | Slices, Checks, Handoffs und offene Risiken sollen standardisiert weiterlaufen. |

## Kalenderintegration

Ziel ist ein `CalendarEventContract`, der nicht an einen Anbieter gebunden ist:

- Ereignistypen: Urlaub, Krankheit, Schicht, Bereitschaft, Tour, Ladefenster, Aussendienstbesuch, Schulung, Wartung, Kampagne, Payroll-Stichtag.
- Felder: `event_id`, `source_system`, `employee_id`, `resource_id`, `start_at`, `end_at`, `timezone`, `visibility`, `status`, `sync_state`, `conflict_level`.
- Richtungen: VALEO publiziert Schicht/Tour/Kampagne; VALEO importiert Frei/Gebucht und externe Termine nur mit minimalem Inhalt.
- Datenschutz: private Termine nur als Busy-Block; keine privaten Betrefftexte in Dispo-/HR-Ansichten.
- Konflikte: Abwesenheit vs. Tour, Schicht vs. Ruhezeit, Aussendienst vs. Kampagne, Wartung vs. Fahrzeugplanung.

## Saison- und Arbeitsspitzenplanung

Landhandel muss Kapazitaet nach Saison statt nur nach Kalenderwoche planen:

- Ernteannahme: Waage, Probe/Labor, Silo, Lager, Fahrer, Verladung.
- Saat/Fruehjahr: Auslieferung Saatgut, Duenger, Pflanzenschutz, Beratungstermine.
- Duenge-/Pflanzenschutzfenster: wetter- und lieferfensterabhaengige Spitzen.
- Winter: Salz/Heizstoffe/Futtermittel, Fahrzeugverfuegbarkeit, Witterung.
- Jahresabschluss/Inventur: Buchhaltung, Lagerzaehlung, reduzierte Touren.

Planungsobjekte:

- Kampagne mit Zeitraum, Produktgruppe, Standort, erwarteter Menge, benoetigten Rollen und Prioritaet.
- Kapazitaetsheatmap je Woche/Tag/Standort/Rolle.
- Engpasswarnung, wenn Abwesenheit, Qualifikation, Fahrerzeit oder Fahrzeugwartung die Mindestbesetzung bricht.

## Kampagneninterferenzen

| Konflikt | Beispiel | Systemreaktion |
|----------|----------|----------------|
| Ernteannahme vs. Auslieferung | Fahrer werden fuer Hofabholung und Kundenlieferung gleichzeitig gebraucht. | Fahrer-/Fahrzeugkonflikt, Alternativfenster, Prioritaet nach Kampagne. |
| Waage vs. Labor | Waage kann mehr Anlieferungen annehmen als Probe/Labor verarbeiten. | Kapazitaetswarnung und Schichtvorschlag fuer Labor/Annahme. |
| Silo vs. Verladung | Silo wird fuer Einlagerung und Auslagerung parallel belegt. | Ressourcenblocker mit Produkt-/Reinigungslogik. |
| Aussendienst vs. Saisonhotline | Agrarberater sind im Feld, aber Innendienst braucht Fachexpertise. | Vertreter-/Bereitschaftsplanung und Besuchsverschiebung. |
| Urlaub vs. Kampagne | Geplante Abwesenheiten fallen in Erntepeak. | Fruehwarnung, nicht automatische Ablehnung; HR- und Teamleiterentscheidung. |
| Wartung vs. Tour | Fahrzeugwartung blockiert geplante Tour. | Fahrzeug-/Tour-Reschedule und Werkstattkalender. |

## Aussendienstplanung

Aussendienst ist kein normales Buero-Kalenderproblem. VALEO muss Kundentermin, Kultur, Saisonfenster und Route verbinden:

- Gebiet/Route: Kundencluster, Fahrzeit, Tagesfenster.
- Kultur/Kampagne: Saat, Duengung, Pflanzenschutz, Ernte, Reklamation.
- CRM-Verbindung: Besuch erzeugt Follow-up, Angebot, Auftrag oder Reklamation.
- HR-Time-Verbindung: Abwesenheit, Arbeitszeit, Ruhezeit nach langen Fahrtagen, Vertreter.
- Kalender: Outlook/Google/ICS fuer Terminblocker und Einladungen.
- Dispo-Interferenz: Aussendienst darf nicht kritische Ernte-/Waage-/Hotline-Besetzung ausduennen.

## Roadmap mit Milestones

| Milestone | Zeitraum | Ergebnis | Abnahme |
|-----------|----------|----------|---------|
| M0 Discovery und Fachfreigabe | 1-2 Wochen | Rollen, Regeln, Tarif/BV, Lohnarten, Saisonkalender, Anbietergrenzen geklaert. | Fachbereich signiert Lastenheft-Scope und offene Rechtsfragen. |
| M1 HR-Time-Datenkern | 2 Wochen | `EmployeeTimeProfile`, persistente Zeitereignisse, Audit, Statusmodell. | API-Vertrag, Migration, Tests, Beispielseed fuer 27 Mitarbeitende. |
| M2 Buchung und Freigabe | 2-3 Wochen | Clock-in/out, Korrektur, Managerfreigabe, Compliance-Befunde. | End-to-end Buchung bis Freigabe und Cockpit. |
| M3 Abwesenheitsintegration | 1-2 Wochen | Urlaubsverwaltung/SaaS-Adapter oder Mockable Contract. | Abwesenheit blockiert Schicht, Tour, Kalender und Payroll. |
| M4 Dienstplanung und Kalender | 3 Wochen | Schichten, Vorlagen, Qualifikationen, Outlook/Google/ICS, Teamkalender. | Konfliktfreie Planung fuer Lager, Waage, Fahrer, Buero. |
| M5 Driver-Time produktionsnah | 3-4 Wochen | Fahrerzeit-Persistenz, Tour/Fahrzeug, Tacho-/Telematik-Adaptervertrag, Spesenbasis. | Fahrerpilot mit Import-/Manuell-Abgleich und Blockerlogik. |
| M6 Saison- und Kampagnenplanung | 3 Wochen | Kampagnenkalender, Kapazitaetsheatmap, Interferenzmatrix. | Ernte-/Saat-Szenario erkennt Personal- und Ressourcenengpaesse. |
| M7 Payroll/DATEV Export | 2 Wochen | Lohnarten, Zuschlaege, Kostenstellen, Exportpaket, DMS-Ablage. | Steuerbuero-/Payroll-Testexport mit Auditprotokoll. |
| M8 Aussendienstplanung | 2-3 Wochen | Gebiet, Route, CRM-Terminkopplung, Kalender, Saisonkonflikte. | Agrarberaterplanung verhindert Abwesenheits-/Kampagnenkonflikte. |
| M9 Mobile/Offline und Rollout | 3 Wochen | PWA/Offline-Queue, Schulung, Pilotgruppe, Betriebsuebergabe. | Pilot mit 27 Mitarbeitenden oder definierter Teilgruppe produktionsnah. |

## Naechste umsetzbare Slices

| Slice | Ziel | Dateibesitz-Vorschlag |
|-------|------|-----------------------|
| `HR-TIME-DATA-001` | Persistente HR-Time-Profile und Zeitereignisse. | API, Migration, Tests, HR-Domain. |
| `HR-TIME-BOOK-001` | Buchungs-/Korrektur-/Freigabeworkflow. | Personal-Endpoint, Frontend-Zeiterfassung, Tests. |
| `HR-TIME-ABS-001` | Abwesenheits-Connector/Contract mit Urlaubsverwaltung. | Adapter, API, Doku, Integrationstests. |
| `HR-TIME-SCHED-001` | Schichtplanung mit Qualifikationen und Standort. | Backend-Modelle, Frontend-Kalender, Tests. |
| `HR-TIME-CAL-001` | Outlook/Google/ICS Calendar Contract. | Integration-Service, OAuth-Konzept, API-Vertrag. |
| `HR-TIME-PAY-001` | Payroll-/DATEV-Exportvertrag. | Export-Service, DMS-Ablage, Audit, Tests. |
| `HR-TIME-CAMPAIGN-001` | Saison-/Kampagnen-Kapazitaetsplaner. | Campaign-Model, Planning-API, Cockpit. |
| `HR-TIME-FIELD-001` | Aussendienstplanung mit CRM-/Kalenderbezug. | CRM/Calendar-Adapter, Field-Service-UI. |

## Offene Entscheidungen

- Welche Lohnsoftware oder welches Steuerbuero-Format ist verbindlich: DATEV CSV, LODAS/Lohn und Gehalt, anderes?
- Gibt es Betriebsvereinbarungen, Tarifregeln oder regionale Zuschlagsmodelle?
- Welche Telematik-/Tacho-Anbieter sind im Fuhrpark real vorhanden?
- Soll Urlaubsverwaltung produktiv betrieben oder nur als Referenz/Adapter genutzt werden?
- Ist Microsoft 365, Google Workspace oder beides fuer Kalender fuehrend?
- Welche Saisonkampagnen sind fuer den ersten Rollout verbindlich: Ernteannahme, Saatgut, Duenger, Pflanzenschutz, Futtermittel, Heizstoffe?

## Quellenstand

Geprueft am 2026-05-08:

- SAP SuccessFactors Time Tracking Features: https://www.sap.com/products/hcm/employee-time-tracking-software/features.html
- SAP Employee Central Time Sheet Funktionen: https://help.sap.com/docs/successfactors-employee-central/using-time-management-in-sap-successfactors/features-and-functions-of-employee-central-time-sheet-for-employees
- Oracle Cloud HCM Time and Labor Readiness: https://docs.oracle.com/en/cloud/saas/readiness/hcm/24b/tila-24b/24B-time-labor-wn-t55862.htm
- Shiftfy Zeiterfassung und Dienstplanung: https://www.shiftfy.de/
- Microsoft Graph Calendar API: https://learn.microsoft.com/en-us/graph/api/resources/calendar-overview
- Google Calendar API Overview: https://developers.google.com/workspace/calendar/api/guides/overview
- BAuA Arbeitszeiterfassung: https://www.baua.de/DE/Themen/Arbeitsgestaltung/Arbeitszeit/Arbeitszeiterfassung
- EUR-Lex Verordnung (EG) Nr. 561/2006: https://eur-lex.europa.eu/eli/reg/2006/561/oj
