# HRM-Betriebsfreigaben und Go-live-Evidenzpaket

| Feld | Eintrag |
|---|---|
| System | VALEO NeuroERP |
| Modul | HRM / Personal / Payroll / Compliance |
| Dokumenttyp | Gesamtwerk mit Mustervorlagen |
| Version | 1.0 |
| Stand | 2026-05-13 |
| Gueltig fuer Release | Sprint 24-Q2-Personal/B7 |
| Dokumentenstatus | Entwurf / In Pruefung / Freigegeben |
| Verantwortlich | [Name / Rolle] |
| Ablageort | `docs/hrm-go-live-templates/` |

---

## Zweck dieses Gesamtwerks

Dieses Dokument buendelt Vordrucke, Nachweise und Freigabeprotokolle fuer die Einfuehrung und den produktiven Betrieb eines HRM-Systems in Deutschland.

Es dient als Evidence-Paket fuer folgende HRM-Gates:

1. eAU-Kommunikationszugang und Krankenkassen-Testverfahren
2. DATEV-/Payroll-Zielformat und Steuerberaterfreigabe
3. Microsoft 365, Google Workspace und SSO
4. LibreOffice-Rendering, DMS und E-Signatur
5. AVV/DPA, Hosting, Subprozessoren und Datenexport
6. Betriebsrat, DSFA und Analytics-/KI-Freigaben
7. Rechtsfreigabe fuer Retention und Dokumentklassen

## Rechtlicher Arbeitshinweis

Dieses Dokument ist eine operative Arbeitsvorlage. Es ersetzt keine Rechtsberatung, keine Datenschutzberatung und keine steuerliche Beratung.

Vor Produktivsetzung sind mindestens zu pruefen:

- Datenschutzrechtliche Pruefung
- Arbeitsrechtliche Pruefung
- Payroll-/Steuerberaterfreigabe
- IT-Sicherheitsfreigabe
- Geschaeftsfuehrungsfreigabe
- Falls vorhanden: Betriebsratsbeteiligung
- Falls kein Betriebsrat vorhanden: Betriebsratsstatus-Erklaerung

Orientierungspunkte sind insbesondere BDSG Paragraf 26 fuer Beschaeftigtendaten, DSGVO Art. 13 fuer Informationspflichten, DSGVO Art. 28 fuer Auftragsverarbeitung, DSGVO Art. 30 fuer das Verzeichnis von Verarbeitungstaetigkeiten, DSGVO Art. 32 fuer TOMs/Sicherheit, DSGVO Art. 35 fuer DSFA und BetrVG Paragraf 87 fuer Mitbestimmung bei technischen Einrichtungen. Offizielle Quellen:

- BDSG Paragraf 26: <https://www.gesetze-im-internet.de/bdsg_2018/__26.html>
- BfDI Hinweise und Muster zum Verzeichnis von Verarbeitungstaetigkeiten: <https://www.bfdi.bund.de/DE/Fachthemen/Inhalte/Allgemein/Verzeichnis-Verarbeitungstaetigkeiten.html>

---

# 0. HRM-Gate-Matrix

| Gate-ID | Gate | Status | Owner | Evidence | Blocker | Abnahmekriterium | Freigabe durch | Freigabe am |
|---|---|---|---|---|---|---|---|---|
| HRM-GATE-001 | eAU-Kommunikationszugang | Offen / Blockiert / Freigegeben | [Name] | [Link] | Ja / Nein | Erfolgreicher Testabruf und dokumentierter Fehlerprozess | [Name] | [Datum] |
| HRM-GATE-002 | DATEV-/Payroll-Zielformat | Offen / Blockiert / Freigegeben | [Name] | [Link] | Ja / Nein | Testexport durch Payroll/Steuerberater abgenommen | [Name] | [Datum] |
| HRM-GATE-003 | Office/SSO | Offen / Blockiert / Freigegeben | [Name] | [Link] | Ja / Nein | SSO, Rollen und Zugriffstest erfolgreich | [Name] | [Datum] |
| HRM-GATE-004 | DMS/E-Signatur/Rendering | Offen / Blockiert / Freigegeben | [Name] | [Link] | Ja / Nein | Dokumentenerzeugung, Ablage und Signaturprozess geprueft | [Name] | [Datum] |
| HRM-GATE-005 | AVV/DPA/Hosting/Subprozessoren | Offen / Blockiert / Freigegeben | [Name] | [Link] | Ja / Nein | AVV, TOMs, Subprozessoren und Datenexport geprueft | [Name] | [Datum] |
| HRM-GATE-006 | Betriebsrat/DSFA/KI | Offen / Blockiert / Freigegeben | [Name] | [Link] | Ja / Nein | Betriebsratsstatus, DSFA-Vorpruefung und KI-Freigabe dokumentiert | [Name] | [Datum] |
| HRM-GATE-007 | Retention/Dokumentklassen | Offen / Blockiert / Freigegeben | [Name] | [Link] | Ja / Nein | Loesch- und Aufbewahrungskonzept rechtlich freigegeben | [Name] | [Datum] |

---

# 1. HRM-Go-live-Freigabeprotokoll

## 1.1 Stammdaten

| Feld | Eintrag |
|---|---|
| System | VALEO NeuroERP |
| Modul | HRM / Personal |
| Release | Sprint 24-Q2-Personal/B7 |
| Umgebung | Test / Staging / Produktion |
| Geplanter Go-live | [Datum] |
| Verantwortlicher Fachbereich | [HR / Payroll / Geschaeftsfuehrung] |
| IT-Verantwortlicher | [Name] |
| Datenschutz-Verantwortlicher | [Name] |
| Payroll-Verantwortlicher | [Name] |

## 1.2 Zusammenfassung der Gates

| Kennzahl | Wert |
|---|---|
| Gesamtanzahl Gates | 7 |
| Freigegeben | [Anzahl] |
| Offen | [Anzahl] |
| Blockiert | [Anzahl] |
| Evidence-Artefakte | [Anzahl] |
| Kritische Go-live-Blocker | [Anzahl] |

## 1.3 Go-live-Entscheidung

- [ ] Go-live freigegeben
- [ ] Go-live mit Auflagen freigegeben
- [ ] Go-live blockiert

**Begruendung:** [Text einfuegen]

**Auflagen oder Blocker:**

| Nr. | Punkt | Owner | Faellig bis |
|---|---|---|---|
| 1 | [Bedingung oder Blocker] | [Name] | [Datum] |
| 2 | [Bedingung oder Blocker] | [Name] | [Datum] |

## 1.4 Restrisiken

| Risiko | Bewertung | Massnahme | Owner | Faellig bis |
|---|---|---|---|---|
| [Risiko] | Niedrig / Mittel / Hoch | [Massnahme] | [Name] | [Datum] |

## 1.5 Unterschriften

| Rolle | Name | Entscheidung | Datum | Unterschrift |
|---|---|---|---|---|
| Geschaeftsfuehrung | [Name] | Freigegeben / Abgelehnt | [Datum] | |
| HR-Leitung | [Name] | Freigegeben / Abgelehnt | [Datum] | |
| Payroll | [Name] | Freigegeben / Abgelehnt | [Datum] | |
| IT | [Name] | Freigegeben / Abgelehnt | [Datum] | |
| Datenschutz | [Name] | Freigegeben / Abgelehnt | [Datum] | |
| Legal | [Name] | Freigegeben / Abgelehnt | [Datum] | |

---

# 2. Betriebsratsstatus-Erklaerung bei nicht vorhandenem Betriebsrat

Im Betrieb / Unternehmen **[Unternehmensname, Adresse, Standort]** besteht zum Zeitpunkt der geplanten Einfuehrung des HRM-Systems kein gewaehlter Betriebsrat.

Eine Betriebsvereinbarung zur Einfuehrung und Nutzung des HRM-Systems kann daher zum aktuellen Zeitpunkt nicht abgeschlossen werden. Die Einfuehrung ersetzt nicht Informationspflichten gegenueber Beschaeftigten, datenschutzrechtliche Pruefung, arbeitsrechtliche Pruefung, technische Sicherheitspruefung oder das Recht der Beschaeftigten, nach gesetzlichen Voraussetzungen einen Betriebsrat zu waehlen.

## 2.1 Ersatzweise interne Freigabedokumente

- [ ] Mitarbeiterinformation HRM-System
- [ ] Datenschutzfreigabe
- [ ] DSFA-Vorpruefung
- [ ] Rollen- und Berechtigungskonzept
- [ ] TOM-/IT-Sicherheitsfreigabe
- [ ] Geschaeftsfuehrungsfreigabe
- [ ] Payroll-/DATEV-Abnahme
- [ ] Retention- und Loeschkonzept
- [ ] KI-/Analytics-Freigabe, falls relevant

## 2.2 Erklaerung zur Ueberwachungsfreiheit

Das HRM-System wird nicht zur verdeckten Leistungs- oder Verhaltenskontrolle von Beschaeftigten eingesetzt. Auswertungen erfolgen nur zweckgebunden, rollenbasiert, protokolliert, nach Need-to-know und im Rahmen dokumentierter HR-, Payroll-, Compliance- und Sicherheitszwecke.

## 2.3 Aenderung bei spaeterer Betriebsratswahl

Wird zu einem spaeteren Zeitpunkt ein Betriebsrat gewaehlt, wird die Nutzung des HRM-Systems im Hinblick auf moegliche Mitbestimmungsrechte erneut geprueft.

| Rolle | Name | Datum | Unterschrift |
|---|---|---|---|
| Geschaeftsfuehrung | [Name] | [Datum] | |
| HR-Leitung | [Name] | [Datum] | |
| Datenschutz | [Name] | [Datum] | |
| IT | [Name] | [Datum] | |

---

# 3. Mitarbeiterinformation zur Einfuehrung des HRM-Systems

## 3.1 Betreff

**Information zur Einfuehrung und Nutzung des HRM-Systems VALEO NeuroERP**

Liebe Mitarbeiterinnen und Mitarbeiter,

wir fuehren das HRM-System VALEO NeuroERP ein, um Personalprozesse, Arbeitszeit, Abwesenheiten, Dokumente, Payroll-Vorbereitung und gesetzliche Nachweispflichten sicherer, transparenter und effizienter zu verwalten.

Diese Information erlaeutert, welche Daten verarbeitet werden, zu welchen Zwecken dies geschieht, wer Zugriff hat und welche Rechte Sie haben.

## 3.2 Verantwortlicher

| Feld | Eintrag |
|---|---|
| Verantwortlicher | [Unternehmensname] |
| Adresse | [Adresse] |
| Ansprechpartner HR | [Name / E-Mail] |
| Datenschutzbeauftragter | [Name / E-Mail] |
| IT-Ansprechpartner | [Name / E-Mail] |

## 3.3 Zwecke und Datenkategorien

| Bereich | Beispiele |
|---|---|
| Zwecke | Personalverwaltung, digitale Personalakte, Arbeitszeit, Abwesenheiten, eAU, Payroll-/DATEV-Vorbereitung, Dokumentenerstellung, Rollenverwaltung, Compliance, Audit, IT-Sicherheit, aggregiertes Reporting |
| Allgemeine Daten | Name, Anschrift, Kontaktdaten, Personalnummer, Beschaeftigungsdaten, Vertragsdaten, Eintritt, Austritt, Abteilung, Rolle, Funktion |
| HR-/Payroll-Daten | Arbeitszeitdaten, Abwesenheiten, Krankmeldungsstatus, Kostenstellen, payroll-relevante Daten, Dokumente und Nachweise |
| Systemdaten | Rollen, Berechtigungen, Protokolle, Auditdaten, Freigabestatus |

## 3.4 Besondere Kategorien personenbezogener Daten

Gesundheitsbezogene Informationen werden nur verarbeitet, soweit dies fuer gesetzliche, arbeitsvertragliche oder abrechnungsbezogene Zwecke erforderlich ist. Diagnosen werden im HRM-System nicht gespeichert, sofern dies nicht ausdruecklich gesetzlich zulaessig und erforderlich ist.

## 3.5 Rechtsgrundlagen, Empfaenger und Zugriffe

| Thema | Beschreibung |
|---|---|
| Rechtsgrundlagen | Beschaeftigungsverhaeltnis, gesetzliche Pflichten, berechtigtes Interesse an sicherer Personalverwaltung, Einwilligung nur wo erforderlich, steuer- und sozialversicherungsrechtliche Pflichten |
| Empfaenger/Schnittstellen | HR, Payroll, Steuerberater, Krankenkassen/eAU, DATEV/Payroll-System, IT, DMS, E-Signatur, Hosting, Datenschutz, Legal, Behoerden soweit gesetzlich erforderlich |
| Rollen | Beschaeftigte sehen grundsaetzlich eigene Daten; Fuehrungskraefte sehen erforderliche Teamdaten; HR, Payroll, IT und Datenschutz erhalten nur erforderliche Rechte |

## 3.6 Keine verdeckte Ueberwachung, KI und Rechte

Das HRM-System wird nicht zur verdeckten Leistungs- oder Verhaltenskontrolle eingesetzt. Systemprotokolle dienen IT-Sicherheit, Nachvollziehbarkeit, Fehleranalyse und gesetzlichen Nachweispflichten.

Automatisierte Entscheidungen mit rechtlicher Wirkung oder vergleichbarer erheblicher Wirkung werden nicht ohne gesonderte Pruefung und Freigabe eingesetzt. KI- oder Analytics-Funktionen duerfen nur genutzt werden, wenn sie geprueft, dokumentiert und freigegeben sind.

Beschaeftigte haben insbesondere Rechte auf Auskunft, Berichtigung, Loeschung, Einschraenkung der Verarbeitung, Widerspruch soweit anwendbar, Datenuebertragbarkeit soweit anwendbar und Beschwerde bei einer Datenschutzaufsichtsbehoerde.

**Kontakt:** HR [Name / E-Mail], Datenschutz [Name / E-Mail], IT [Name / E-Mail]

---

# 4. Verzeichnis der Verarbeitungstaetigkeit: HRM-System

| Feld | Eintrag |
|---|---|
| Bezeichnung | HRM-System / Personalverwaltung |
| System | VALEO NeuroERP |
| Verantwortlicher | [Unternehmensname] |
| Fachverantwortlicher | [Name / HR] |
| Technischer Verantwortlicher | [Name / IT] |
| Datenschutzbeauftragter | [Name] |
| Erstellt am | [Datum] |
| Letzte Pruefung | [Datum] |
| Naechste Pruefung | [Datum] |

## 4.1 Zwecke, Personen und Daten

| Kategorie | Inhalt |
|---|---|
| Zwecke | Personalverwaltung, digitale Personalakte, Arbeitszeit, Abwesenheit, eAU, Payroll, DATEV, Dokumentenmanagement, Rollensteuerung, Audit, ESS/MSS, freigegebenes Reporting |
| Betroffene Personen | Beschaeftigte, Bewerber falls angebunden, ehemalige Beschaeftigte, Fuehrungskraefte, HR-/Payroll-Nutzer, externe Dienstleister mit Nutzerkonto |
| Datenkategorien | Stamm-, Kontakt-, Beschaeftigungs-, Vertrags-, Arbeitszeit-, Abwesenheits-, Krankmeldungs-, Payroll-, Organisations-, Dokument-, Rollen-, Berechtigungs-, Protokoll- und Auditdaten |
| Besondere Datenkategorien | Gesundheitsdaten im Rahmen von Krankmeldung/eAU; weitere besondere Kategorien nur nach gesonderter Pruefung |

## 4.2 Rechtsgrundlagen und Empfaenger

| Zweck | Rechtsgrundlage | Bemerkung |
|---|---|---|
| Personalverwaltung | Beschaeftigungsverhaeltnis / gesetzliche Pflichten | [Details] |
| Payroll | gesetzliche Pflichten / Beschaeftigungsverhaeltnis | [Details] |
| eAU | gesetzliche Pflichten | [Details] |
| Arbeitszeit | gesetzliche Pflichten / Beschaeftigungsverhaeltnis | [Details] |
| Dokumentenmanagement | Beschaeftigungsverhaeltnis / gesetzliche Pflichten | [Details] |
| IT-Sicherheit | berechtigtes Interesse / gesetzliche Pflichten | [Details] |
| Reporting | berechtigtes Interesse / interne Steuerung | nur aggregiert oder rollenbasiert |

Empfaenger koennen HR, Payroll, Geschaeftsfuehrung soweit erforderlich, Fuehrungskraefte soweit erforderlich, IT, Datenschutz, Steuerberater, Krankenkassen, Sozialversicherungstraeger, Behoerden, Auftragsverarbeiter, DMS-, E-Signatur- und Hosting-Anbieter sein.

## 4.3 Drittlanduebermittlung und Fristen

- [ ] Keine Drittlanduebermittlung
- [ ] Drittlanduebermittlung vorhanden

| Empfaenger | Drittland | Grundlage | Garantien | Pruefung am |
|---|---|---|---|---|
| [Name] | [Land] | [SCC / Angemessenheitsbeschluss / Sonstiges] | [Details] | [Datum] |

| Datenklasse | Frist | Loeschregel |
|---|---|---|
| Bewerberdaten | [Frist] | [Regel] |
| Personalakte | [Frist] | [Regel] |
| Payroll-Daten | [Frist] | [Regel] |
| Arbeitszeitdaten | [Frist] | [Regel] |
| Auditlogs | [Frist] | [Regel] |

| Rolle | Name | Datum | Freigabe |
|---|---|---|---|
| HR | [Name] | [Datum] | Ja / Nein |
| IT | [Name] | [Datum] | Ja / Nein |
| Datenschutz | [Name] | [Datum] | Ja / Nein |

---

# 5. AVV-/DPA-Pruefprotokoll

| Feld | Eintrag |
|---|---|
| Anbieter | [Name] |
| Dienstleistung | [Hosting / DMS / E-Signatur / Payroll / eAU / Sonstiges] |
| Ansprechpartner Anbieter | [Name / E-Mail] |
| Interner Owner | [Name] |
| Pruefung am | [Datum] |

## 5.1 Rollen und AVV/DPA-Status

- [ ] Anbieter ist Auftragsverarbeiter
- [ ] Anbieter ist eigener Verantwortlicher
- [ ] gemeinsame Verantwortlichkeit moeglich
- [ ] Rollenklaerung offen

| Pruefpunkt | Status | Bemerkung |
|---|---|---|
| AVV vorhanden | Ja / Nein / n. a. | [Text] |
| Gegenstand und Dauer geregelt | Ja / Nein | [Text] |
| Art und Zweck geregelt | Ja / Nein | [Text] |
| Datenarten geregelt | Ja / Nein | [Text] |
| Betroffenenkategorien geregelt | Ja / Nein | [Text] |
| TOMs beigefuegt | Ja / Nein | [Text] |
| Weisungsregelung vorhanden | Ja / Nein | [Text] |
| Subprozessoren geregelt | Ja / Nein | [Text] |
| Loeschung/Rueckgabe geregelt | Ja / Nein | [Text] |
| Audit-/Nachweisrechte geregelt | Ja / Nein | [Text] |
| Meldepflichten bei Vorfaellen geregelt | Ja / Nein | [Text] |

## 5.2 Subprozessoren und Datenexport

| Subprozessor | Leistung | Land | Kritikalitaet | Geprueft |
|---|---|---|---|---|
| [Name] | [Leistung] | [Land] | Niedrig / Mittel / Hoch | Ja / Nein |

- [ ] Datenexport moeglich
- [ ] Exportformat dokumentiert
- [ ] Loeschung nach Vertragsende geregelt
- [ ] Rueckgabe der Daten geregelt
- [ ] Nachweis der Loeschung moeglich

## 5.3 Entscheidung

- [ ] Freigegeben
- [ ] Mit Auflagen freigegeben
- [ ] Blockiert

| Rolle | Name | Datum | Unterschrift |
|---|---|---|---|
| Datenschutz | [Name] | [Datum] | |
| IT | [Name] | [Datum] | |
| Fachbereich | [Name] | [Datum] | |

---

# 6. DSFA-Vorpruefung

| Feld | Eintrag |
|---|---|
| Verarbeitung | HRM-System / Personalverwaltung |
| System | VALEO NeuroERP |
| Owner | [Name] |
| Pruefung am | [Datum] |
| Pruefer | [Name] |

## 6.1 Prueffragen

| Frage | Ja | Nein | Bemerkung |
|---|---|---|---|
| Werden Gesundheitsdaten verarbeitet? | [ ] | [ ] | [Text] |
| Werden umfangreiche Beschaeftigtendaten verarbeitet? | [ ] | [ ] | [Text] |
| Gibt es systematische Ueberwachung? | [ ] | [ ] | [Text] |
| Gibt es Leistungs- oder Verhaltensauswertungen? | [ ] | [ ] | [Text] |
| Gibt es Profiling oder Scoring? | [ ] | [ ] | [Text] |
| Gibt es automatisierte Entscheidungen mit Wirkung auf Beschaeftigte? | [ ] | [ ] | [Text] |
| Gibt es KI-gestuetzte Empfehlungen? | [ ] | [ ] | [Text] |
| Gibt es neue Technologien mit hohem Risiko? | [ ] | [ ] | [Text] |
| Gibt es Drittlanduebermittlungen? | [ ] | [ ] | [Text] |
| Sind besonders viele Beschaeftigte betroffen? | [ ] | [ ] | [Text] |

## 6.2 Risiken und Ergebnis

| Risiko | Eintritt | Schwere | Bewertung | Massnahme |
|---|---|---|---|---|
| Unbefugter Zugriff auf Personalakte | Niedrig / Mittel / Hoch | Niedrig / Mittel / Hoch | Niedrig / Mittel / Hoch | Rollenrechte, MFA, Auditlog |
| Zweckwidrige Auswertung | Niedrig / Mittel / Hoch | Niedrig / Mittel / Hoch | Niedrig / Mittel / Hoch | Reporting-Freigabe, Berechtigungen |
| Falsche Payroll-Daten | Niedrig / Mittel / Hoch | Niedrig / Mittel / Hoch | Niedrig / Mittel / Hoch | Vier-Augen-Prinzip |
| Gesundheitsdaten-Fehlzugriff | Niedrig / Mittel / Hoch | Niedrig / Mittel / Hoch | Niedrig / Mittel / Hoch | Einschraenkung eAU-Rollen |

- [ ] Keine vollstaendige DSFA erforderlich
- [ ] Vollstaendige DSFA erforderlich
- [ ] Entscheidung offen

| Rolle | Name | Datum | Entscheidung |
|---|---|---|---|
| Datenschutz | [Name] | [Datum] | Freigegeben / DSFA erforderlich |
| HR | [Name] | [Datum] | Freigegeben / Blockiert |
| IT | [Name] | [Datum] | Freigegeben / Blockiert |

---

# 7. Rollen- und Berechtigungskonzept

Ziel ist ein rollenbasierter, zweckgebundener und nachvollziehbarer Zugriff auf Beschaeftigtendaten.

## 7.1 Rollenuebersicht

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

## 7.2 Berechtigungsmatrix

| Datenbereich | Employee | Manager | HR | Payroll | IT | Datenschutz | Legal | GF |
|---|---|---|---|---|---|---|---|---|
| Eigene Stammdaten | R | - | R/W | R | - | R | - | - |
| Team-Stammdaten | - | R | R/W | R | - | R | - | - |
| Personalakte | - | - | R/W | R teilweise | - | R | R teilweise | - |
| Arbeitszeit | R eigene | R Team | R/W | R | - | R | - | Aggregiert |
| Abwesenheiten | R eigene | R Team | R/W | R | - | R | - | Aggregiert |
| eAU-Status | R eigene eingeschraenkt | - | R/W eingeschraenkt | R/W | - | R | - | - |
| Payroll-Daten | - | - | R teilweise | R/W | - | R | - | Aggregiert |
| Systemlogs | - | - | R eingeschraenkt | - | R/W technisch | R | - | - |
| Reports | Eigene | Team | HR | Payroll | - | Pruefung | Pruefung | Aggregiert |

Legende: R = Lesen, W = Schreiben, R/W = Lesen und Schreiben, `-` = kein Zugriff.

## 7.3 Kritische Rechte und Rezertifizierung

Kritisch sind Export von Personaldaten, Loeschung von HR-Daten, Aenderung von Payroll-Daten, Zugriff auf eAU-/Krankmeldungsdaten, Rollenvergabe, Auditlog-Zugriff, KI-/Analytics-Auswertungen und Massenaenderungen.

| Pruefung | Intervall | Verantwortlich |
|---|---|---|
| HR-Rollen | Quartalsweise | HR-Leitung |
| Payroll-Rollen | Quartalsweise | Payroll Lead |
| IT-Adminrechte | Monatlich | IT-Leitung |
| Kritische Rechte | Monatlich | Datenschutz / IT |
| Austritte | Bei Austritt sofort | HR / IT |

---

# 8. TOM-/IT-Sicherheitsfreigabe

| Feld | Eintrag |
|---|---|
| System | VALEO NeuroERP HRM |
| Umgebung | Produktion |
| Hosting | [Anbieter / Standort] |
| Datenbank | [System] |
| Authentifizierung | [SSO / MFA / Local] |
| Verantwortlich IT | [Name] |
| Pruefung am | [Datum] |

| Massnahme | Status | Nachweis |
|---|---|---|
| MFA aktiviert | Ja / Nein | [Link] |
| SSO geprueft | Ja / Nein | [Link] |
| Rollenrechte umgesetzt | Ja / Nein | [Link] |
| Verschluesselung Transport | Ja / Nein | [Link] |
| Verschluesselung Speicherung | Ja / Nein | [Link] |
| Backup eingerichtet | Ja / Nein | [Link] |
| Restore-Test durchgefuehrt | Ja / Nein | [Link] |
| Logging aktiviert | Ja / Nein | [Link] |
| Audit-Trail aktiviert | Ja / Nein | [Link] |
| Mandantentrennung geprueft | Ja / Nein | [Link] |
| Secrets Management eingerichtet | Ja / Nein | [Link] |
| Patchprozess definiert | Ja / Nein | [Link] |
| Incident-Prozess definiert | Ja / Nein | [Link] |
| Loeschprozess technisch moeglich | Ja / Nein | [Link] |
| Datenexport moeglich | Ja / Nein | [Link] |

- [ ] IT-Sicherheitsfreigabe erteilt
- [ ] Mit Auflagen freigegeben
- [ ] Blockiert

| Rolle | Name | Datum | Unterschrift |
|---|---|---|---|
| IT-Leitung | [Name] | [Datum] | |
| Datenschutz | [Name] | [Datum] | |
| HR-Systemowner | [Name] | [Datum] | |

---

# 9. Retention- und Loeschkonzept

Dieses Dokument definiert Aufbewahrungs-, Sperr- und Loeschregeln fuer HRM-Daten und Dokumente.

| Klasse | Beschreibung | Aufbewahrung | Loeschung / Sperrung | Owner |
|---|---|---|---|---|
| Personalstammdaten | Basisdaten Beschaeftigte | [Frist] | [Regel] | HR |
| Arbeitsvertraege | Vertraege und Nachtraege | [Frist] | [Regel] | HR / Legal |
| Payroll-Daten | Lohnabrechnungsdaten | [Frist] | [Regel] | Payroll |
| Arbeitszeitdaten | Zeitbuchungen | [Frist] | [Regel] | HR / Payroll |
| Abwesenheiten | Urlaub, Krankheit, Sonderurlaub | [Frist] | [Regel] | HR |
| eAU-Status | Krankmeldungsprozess | [Frist] | [Regel] | Payroll / HR |
| Bewerberdaten | Bewerbungen | [Frist] | [Regel] | Recruiting |
| Auditlogs | System- und Aenderungsprotokolle | [Frist] | [Regel] | IT / Datenschutz |
| Dokumentenvorlagen | Vertrags- und HR-Vorlagen | [Frist] | [Regel] | HR / Legal |
| KI-/Analytics-Auswertungen | Reports und Scores | [Frist] | [Regel] | HR / Datenschutz |

## 9.1 Loeschprozess

1. Datenklasse identifizieren
2. Aufbewahrungsfrist pruefen
3. Sperrgrund pruefen
4. Loeschlauf vorbereiten
5. Vier-Augen-Freigabe einholen
6. Loeschung durchfuehren
7. Loeschung protokollieren
8. Stichprobe durchfuehren

| Loeschlauf | Datenklasse | Zeitraum | Anzahl Datensaetze | Freigegeben durch | Durchgefuehrt durch | Datum |
|---|---|---|---|---|---|---|
| [ID] | [Klasse] | [Zeitraum] | [Anzahl] | [Name] | [Name] | [Datum] |

| Rolle | Name | Datum | Freigabe |
|---|---|---|---|
| Legal | [Name] | [Datum] | Ja / Nein |
| Datenschutz | [Name] | [Datum] | Ja / Nein |
| HR | [Name] | [Datum] | Ja / Nein |
| IT | [Name] | [Datum] | Ja / Nein |

---

# 10. eAU-Freigabeprotokoll

| Feld | Eintrag |
|---|---|
| Gate-ID | HRM-GATE-001 |
| Gate | eAU-Kommunikationszugang und Krankenkassen-Testverfahren |
| Owner | [Name] |
| Status | Offen / Blockiert / Freigegeben |
| Pruefung am | [Datum] |

| Pruefpunkt | Status | Nachweis |
|---|---|---|
| eAU-Prozess fachlich beschrieben | Ja / Nein | [Link] |
| Berechtigte Rollen definiert | Ja / Nein | [Link] |
| Zertifikat vorhanden | Ja / Nein | [Link] |
| Kommunikationszugang eingerichtet | Ja / Nein | [Link] |
| Testabruf erfolgreich | Ja / Nein | [Link] |
| Fehlerprozess dokumentiert | Ja / Nein | [Link] |
| Datenschutzinformation angepasst | Ja / Nein | [Link] |
| Zugriff auf Gesundheitsdaten eingeschraenkt | Ja / Nein | [Link] |
| Auditlog aktiv | Ja / Nein | [Link] |

| Testfall | Ergebnis | Datum | Bearbeiter | Bemerkung |
|---|---|---|---|---|
| Testabruf eAU | Erfolgreich / Fehlgeschlagen | [Datum] | [Name] | [Text] |
| Fehlerfall Zertifikat | Erfolgreich / Fehlgeschlagen | [Datum] | [Name] | [Text] |
| Rollenpruefung | Erfolgreich / Fehlgeschlagen | [Datum] | [Name] | [Text] |
| Auditlog-Pruefung | Erfolgreich / Fehlgeschlagen | [Datum] | [Name] | [Text] |

- [ ] eAU-Gate freigegeben
- [ ] eAU-Gate mit Auflagen freigegeben
- [ ] eAU-Gate blockiert

| Rolle | Name | Datum | Unterschrift |
|---|---|---|---|
| Payroll | [Name] | [Datum] | |
| HR | [Name] | [Datum] | |
| IT | [Name] | [Datum] | |
| Datenschutz | [Name] | [Datum] | |

---

# 11. DATEV-/Payroll-Abnahmeprotokoll

| Feld | Eintrag |
|---|---|
| Gate-ID | HRM-GATE-002 |
| Gate | DATEV-/Payroll-Zielformat und Steuerberaterfreigabe |
| Owner | [Name] |
| Status | Offen / Blockiert / Freigegeben |
| Pruefung am | [Datum] |
| Zielsystem | DATEV / anderes Payroll-System |
| Exportformat | [Format] |
| Exportintervall | Monatlich / Woechentlich / Ad hoc |

| Pruefpunkt | Status | Nachweis |
|---|---|---|
| Lohnartenmapping erstellt | Ja / Nein | [Link] |
| Kostenstellenmapping erstellt | Ja / Nein | [Link] |
| Mitarbeiterstammdaten geprueft | Ja / Nein | [Link] |
| Arbeitszeitdaten geprueft | Ja / Nein | [Link] |
| Abwesenheiten geprueft | Ja / Nein | [Link] |
| Ueberstundenlogik geprueft | Ja / Nein | [Link] |
| Testexport erstellt | Ja / Nein | [Link] |
| Testimport geprueft | Ja / Nein | [Link] |
| Steuerberaterfreigabe vorhanden | Ja / Nein | [Link] |
| Fehlerprozess dokumentiert | Ja / Nein | [Link] |

| Testlauf | Zeitraum | Ergebnis | Fehler | Freigabe |
|---|---|---|---|---|
| [ID] | [Zeitraum] | Erfolgreich / Fehlgeschlagen | [Text] | Ja / Nein |

| Rolle | Name | Datum | Unterschrift |
|---|---|---|---|
| Payroll Lead | [Name] | [Datum] | |
| Steuerberater | [Name] | [Datum] | |
| HR | [Name] | [Datum] | |
| IT | [Name] | [Datum] | |

---

# 12. Office-/SSO-Abnahmeprotokoll

| Feld | Eintrag |
|---|---|
| Gate-ID | HRM-GATE-003 |
| Gate | Microsoft 365, Google Workspace und SSO |
| Owner | [Name] |
| Status | Offen / Blockiert / Freigegeben |

| Pruefpunkt | Status | Nachweis |
|---|---|---|
| Identity Provider definiert | Ja / Nein | [Link] |
| SSO eingerichtet | Ja / Nein | [Link] |
| MFA erzwungen | Ja / Nein | [Link] |
| Rollen-/Gruppenmapping geprueft | Ja / Nein | [Link] |
| Joiner-Prozess geprueft | Ja / Nein | [Link] |
| Mover-Prozess geprueft | Ja / Nein | [Link] |
| Leaver-Prozess geprueft | Ja / Nein | [Link] |
| Kalenderintegration geprueft | Ja / Nein | [Link] |
| Zugriffsentzug bei Austritt geprueft | Ja / Nein | [Link] |
| Notfallkonto geregelt | Ja / Nein | [Link] |

| Testfall | Ergebnis | Bemerkung |
|---|---|---|
| Login mit SSO | Erfolgreich / Fehlgeschlagen | [Text] |
| MFA Challenge | Erfolgreich / Fehlgeschlagen | [Text] |
| Rollenmapping HR | Erfolgreich / Fehlgeschlagen | [Text] |
| Rollenmapping Payroll | Erfolgreich / Fehlgeschlagen | [Text] |
| Austritt / Deprovisioning | Erfolgreich / Fehlgeschlagen | [Text] |

| Rolle | Name | Datum | Unterschrift |
|---|---|---|---|
| IT | [Name] | [Datum] | |
| HR | [Name] | [Datum] | |
| Datenschutz | [Name] | [Datum] | |

---

# 13. LibreOffice-/DMS-/E-Signatur-Abnahmeprotokoll

| Feld | Eintrag |
|---|---|
| Gate-ID | HRM-GATE-004 |
| Gate | LibreOffice-Rendering, DMS und E-Signatur |
| Owner | [Name] |
| Status | Offen / Blockiert / Freigegeben |

| Pruefpunkt | Status | Nachweis |
|---|---|---|
| Dokumentvorlagen vorhanden | Ja / Nein | [Link] |
| LibreOffice-Rendering funktioniert | Ja / Nein | [Link] |
| PDF-Erzeugung geprueft | Ja / Nein | [Link] |
| DMS-Ablage geprueft | Ja / Nein | [Link] |
| Dokumentklassen zugeordnet | Ja / Nein | [Link] |
| E-Signatur-Prozess geprueft | Ja / Nein | [Link] |
| Signaturstatus rueckgefuehrt | Ja / Nein | [Link] |
| Berechtigungen im DMS geprueft | Ja / Nein | [Link] |
| Versionierung aktiv | Ja / Nein | [Link] |
| Loesch-/Retention-Regeln angebunden | Ja / Nein | [Link] |

| Dokument | Vorlage | Ergebnis | Nachweis |
|---|---|---|---|
| Arbeitsvertrag | [Vorlage] | Erfolgreich / Fehlgeschlagen | [Link] |
| Zusatzvereinbarung | [Vorlage] | Erfolgreich / Fehlgeschlagen | [Link] |
| Bescheinigung | [Vorlage] | Erfolgreich / Fehlgeschlagen | [Link] |
| Hinweis / Abmahnung | [Vorlage] | Erfolgreich / Fehlgeschlagen | [Link] |
| Austrittsdokument | [Vorlage] | Erfolgreich / Fehlgeschlagen | [Link] |

| Rolle | Name | Datum | Unterschrift |
|---|---|---|---|
| Document Management | [Name] | [Datum] | |
| HR | [Name] | [Datum] | |
| Legal | [Name] | [Datum] | |
| IT | [Name] | [Datum] | |

---

# 14. KI-/Analytics-Freigabe

Diese Vorlage prueft, ob HRM-Analytics oder KI-Funktionen eingesetzt werden duerfen.

| Feld | Eintrag |
|---|---|
| Funktion | [Name der KI-/Analytics-Funktion] |
| Zweck | [Beschreibung] |
| Betroffene Nutzer | [Personengruppe] |
| Datenquellen | [Datenquellen] |
| Output | Empfehlung / Report / Score / Textvorschlag |
| Owner | [Name] |

| Frage | Ja | Nein | Bemerkung |
|---|---|---|---|
| Betrifft die Funktion Beschaeftigte? | [ ] | [ ] | [Text] |
| Werden personenbezogene Daten genutzt? | [ ] | [ ] | [Text] |
| Werden besondere Datenkategorien genutzt? | [ ] | [ ] | [Text] |
| Entsteht ein Score oder Ranking? | [ ] | [ ] | [Text] |
| Wird Recruiting beeinflusst? | [ ] | [ ] | [Text] |
| Wird Performance bewertet? | [ ] | [ ] | [Text] |
| Gibt es automatisierte Entscheidungen? | [ ] | [ ] | [Text] |
| Gibt es menschliche Kontrolle? | [ ] | [ ] | [Text] |
| Koennen Betroffene eine Entscheidung nachvollziehen? | [ ] | [ ] | [Text] |
| Ist eine DSFA erforderlich? | [ ] | [ ] | [Text] |

## 14.1 Erlaubte und blockierte Nutzung

Erlaubt nach Freigabe:

- [ ] Nur Textvorschlaege
- [ ] Nur Zusammenfassungen
- [ ] Nur aggregierte Reports
- [ ] Nur Entscheidungsvorbereitung mit menschlicher Pruefung
- [ ] Keine automatisierte Entscheidung
- [ ] Keine verdeckte Leistungs-/Verhaltenskontrolle

Blockiert:

- [ ] Automatische Kuendigungsentscheidung
- [ ] Automatische Befoerderungsentscheidung
- [ ] Automatisches Ranking ohne menschliche Pruefung
- [ ] Emotionserkennung am Arbeitsplatz
- [ ] Verdeckte Leistungsueberwachung
- [ ] Zweckaenderung ohne neue Pruefung

| Rolle | Name | Datum | Entscheidung |
|---|---|---|---|
| HR | [Name] | [Datum] | Freigegeben / Blockiert |
| Datenschutz | [Name] | [Datum] | Freigegeben / Blockiert |
| Legal | [Name] | [Datum] | Freigegeben / Blockiert |
| IT | [Name] | [Datum] | Freigegeben / Blockiert |

---

# 15. Evidence- und Auditprotokoll

## 15.1 Evidence-Artefakt

| Feld | Eintrag |
|---|---|
| Evidence-ID | HRM-EVID-[Nummer] |
| Zugehoeriges Gate | [Gate-ID] |
| Titel | [Titel] |
| Typ | Protokoll / Vertrag / Screenshot / Export / Testbericht / Freigabe |
| Ablageort | [Link / Pfad] |
| Erstellt von | [Name] |
| Erstellt am | [Datum] |
| Gueltig bis | [Datum / n. a.] |
| Vertraulichkeit | Intern / Vertraulich / Streng vertraulich |

**Inhaltliche Zusammenfassung:** [Kurze Beschreibung des Nachweises]

| Prueffrage | Ergebnis | Bemerkung |
|---|---|---|
| Artefakt vollstaendig? | Ja / Nein | [Text] |
| Artefakt aktuell? | Ja / Nein | [Text] |
| Artefakt dem richtigen Gate zugeordnet? | Ja / Nein | [Text] |
| Artefakt durch Owner geprueft? | Ja / Nein | [Text] |
| Artefakt revisionssicher abgelegt? | Ja / Nein | [Text] |

| Datum | Person | Aktion | Ergebnis |
|---|---|---|---|
| [Datum] | [Name] | Erstellt | [Text] |
| [Datum] | [Name] | Geprueft | [Text] |
| [Datum] | [Name] | Freigegeben | [Text] |

---

# 16. HRM-Geschaeftsfuehrungsfreigabe

| Feld | Eintrag |
|---|---|
| System | VALEO NeuroERP HRM |
| Release | Sprint 24-Q2-Personal/B7 |
| Go-live-Datum | [Datum] |
| Vorlage erstellt durch | [Name] |
| Datum | [Datum] |

| Bereich | Status | Bemerkung |
|---|---|---|
| HR-Fachprozesse | Gruen / Gelb / Rot | [Text] |
| Payroll | Gruen / Gelb / Rot | [Text] |
| Datenschutz | Gruen / Gelb / Rot | [Text] |
| IT-Sicherheit | Gruen / Gelb / Rot | [Text] |
| Legal / Retention | Gruen / Gelb / Rot | [Text] |
| Betriebsrat / Kein Betriebsrat | Gruen / Gelb / Rot | [Text] |
| KI / Analytics | Gruen / Gelb / Rot | [Text] |

- [ ] Produktivsetzung freigegeben
- [ ] Produktivsetzung mit Auflagen freigegeben
- [ ] Produktivsetzung abgelehnt

| Rolle | Name | Datum | Unterschrift |
|---|---|---|---|
| Geschaeftsfuehrung | [Name] | [Datum] | |

---

# 17. Optional: Betriebsvereinbarung, falls ein Betriebsrat vorhanden ist

Diese Vorlage ist nur zu verwenden, wenn ein Betriebsrat besteht. Falls kein Betriebsrat besteht, ist stattdessen die Betriebsratsstatus-Erklaerung aus Abschnitt 2 zu verwenden.

## 17.1 Musterstruktur Betriebsvereinbarung HRM-System

**Betriebsvereinbarung zur Einfuehrung und Nutzung des HRM-Systems VALEO NeuroERP**

zwischen **[Unternehmen]** und **dem Betriebsrat der [Betrieb / Standort]**.

Regelungsgegenstand ist Einfuehrung, Betrieb und Nutzung des HRM-Systems. Das System dient Personalverwaltung, Arbeitszeit- und Abwesenheitsverwaltung, Payroll-Vorbereitung, Dokumentenmanagement, Compliance-Nachweisen, Employee Self Service, Manager Self Service und HR-Reporting im freigegebenen Umfang.

Eine verdeckte Leistungs- oder Verhaltenskontrolle findet nicht statt. Personenbezogene Auswertungen sind nur zulaessig, wenn sie fuer den jeweiligen HR-, Payroll- oder Compliance-Zweck erforderlich und freigegeben sind.

Zulaessig sind aggregierte HR-Reports, gesetzlich erforderliche Nachweise, payroll-relevante Auswertungen und freigegebene Management-Reports. Nicht zulaessig sind verdeckte Leistungsueberwachung, heimliche Verhaltensprofile, nicht freigegebene Scoring-Modelle und automatisierte Personalentscheidungen ohne menschliche Pruefung.

Rollen und Zugriffsrechte ergeben sich aus dem Rollen- und Berechtigungskonzept. Systemzugriffe und Aenderungen werden protokolliert, soweit dies fuer IT-Sicherheit, Nachvollziehbarkeit und Compliance erforderlich ist. Loeschung und Aufbewahrung richten sich nach dem Retention- und Loeschkonzept. KI- und Analytics-Funktionen duerfen nur nach gesonderter Pruefung und Freigabe eingesetzt werden.

| Partei | Name | Datum | Unterschrift |
|---|---|---|---|
| Arbeitgeber | [Name] | [Datum] | |
| Betriebsrat | [Name] | [Datum] | |

---

# 18. Ablage- und Dateistruktur im Repo

Empfohlene Ablage:

```text
docs/hrm-go-live-templates/
|-- README.md
|-- 00_hrm_go_live_gesamtwerk.md
|-- 01_hrm_go_live_freigabeprotokoll.md
|-- 02_betriebsratsstatus_kein_betriebsrat.md
|-- 03_mitarbeiterinformation_hrm.md
|-- 04_vvt_hrm_system.md
|-- 05_avv_dpa_pruefprotokoll.md
|-- 06_dsfa_vorpruefung.md
|-- 07_rollen_berechtigungskonzept.md
|-- 08_tom_it_sicherheitsfreigabe.md
|-- 09_retention_loeschkonzept.md
|-- 10_eau_freigabeprotokoll.md
|-- 11_datev_payroll_abnahme.md
|-- 12_office_sso_abnahme.md
|-- 13_dms_esignatur_rendering_abnahme.md
|-- 14_ki_analytics_freigabe.md
|-- 15_evidence_auditprotokoll.md
|-- 16_geschaeftsfuehrungsfreigabe.md
`-- 17_betriebsvereinbarung_optional.md
```

---

# 19. Mindest-Evidence je Gate

| Gate | Mindest-Evidence |
|---|---|
| eAU | eAU-Freigabeprotokoll, Testprotokoll, Rollenpruefung |
| DATEV/Payroll | Lohnartenmapping, Testexport, Steuerberaterfreigabe |
| Office/SSO | SSO-Test, MFA-Nachweis, Rollenmapping |
| DMS/E-Signatur | PDF-Test, DMS-Ablage, Signaturtest, Dokumentklassen |
| AVV/DPA | AVV, TOMs, Subprozessorenliste, Datenexportnachweis |
| Betriebsrat/DSFA/KI | Betriebsratsstatus, Mitarbeiterinformation, DSFA-Vorpruefung, KI-Freigabe |
| Retention Legal | Loeschkonzept, Dokumentklassen, Legal-Freigabe |

---

# 20. Abschlussvermerk

Dieses HRM-Go-live-Evidenzpaket wurde geprueft.

| Rolle | Name | Datum | Ergebnis |
|---|---|---|---|
| HR | [Name] | [Datum] | Freigegeben / Offen / Blockiert |
| Payroll | [Name] | [Datum] | Freigegeben / Offen / Blockiert |
| IT | [Name] | [Datum] | Freigegeben / Offen / Blockiert |
| Datenschutz | [Name] | [Datum] | Freigegeben / Offen / Blockiert |
| Legal | [Name] | [Datum] | Freigegeben / Offen / Blockiert |
| Geschaeftsfuehrung | [Name] | [Datum] | Freigegeben / Offen / Blockiert |

**Gesamtstatus:**

- [ ] Go-live freigegeben
- [ ] Go-live blockiert
- [ ] Go-live mit Auflagen freigegeben

**Kommentar:** [Text]
