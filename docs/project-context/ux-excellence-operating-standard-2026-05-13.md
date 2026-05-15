# UX Excellence Operating Standard

Stand: 2026-05-13

## Zweck

Dieser Standard uebertraegt die Erfahrungen aus `HRM-Betriebsfreigaben` auf das gesamte VALEO NeuroERP. Jede operative Arbeitsflaeche soll nicht nur Daten anzeigen, sondern die naechste fachlich richtige Handlung erkennbar machen.

## Leitbild

Eine exzellente ERP-Oberflaeche beantwortet fuer die Nutzerin ohne Vorwissen:

1. Worum geht es?
2. Bin ich hier richtig?
3. Was ist gerade kritisch?
4. Was muss ich als Naechstes tun?
5. Welche Vorlage, welcher Nachweis oder welche Freigabe gehoert dazu?
6. Wer ist zustaendig?
7. Was wurde bereits gemacht?
8. Was verhindert den Abschluss?

## Pflichtmuster fuer Arbeitsflaechen

| Muster | Pflicht ab jetzt | Umsetzungshinweis |
|---|---|---|
| Rollenfokus | Ja | HR, Payroll, IT, Datenschutz, Management oder domaenenspezifische Rollen duerfen unterschiedliche Einstiege bekommen. |
| Aufgabenplan | Ja | Komplexe Statusseiten brauchen konkrete Arbeitsschritte mit erledigt/offen. |
| Naechste Aktion | Ja | Jede kritische Zeile muss eine klare naechste Handlung zeigen. |
| Vorlage-/Nachweislink | Ja | Wenn ein Prozess Evidence braucht, muss die passende Vorlage direkt erreichbar sein. |
| Gefuehrte Eingabe | Ja | Auswahllisten vor Freitext; Freitext nur fuer Kommentar, Link oder Begruendung. |
| Audit-Zeitleiste | Ja | Nachweis, Test, Entscheidung und Rueckfrage sollen chronologisch sichtbar sein. |
| Management-Bild | Ja | Go-live, Abschluss, Zahlung, Versand oder Freigabe brauchen eine verdichtete Entscheidungsansicht. |
| Leere-/Fehlerzustaende | Ja | Keine leeren Tabellen ohne Erklaerung; Fehler muessen Handlung anbieten. |
| Normalsprache | Ja | Keine internen Begriffe, wenn ein normaler Bueroanwender eine einfache Formulierung braucht. |

## Wiederverwendbarer Frontend-Baukasten

Die Komponenten liegen unter `packages/frontend-web/src/components/workflow/ux-standard.tsx` und werden ueber `@/components/workflow` exportiert.

| Komponente | Zweck | Typischer Einsatz |
|---|---|---|
| `RoleFocusBar` | Rollen- oder Sichtfilter mit erklaerendem Kontext. | HR/Payroll/IT/Leitung, Buchhaltung/Controlling/Steuerberater, Einkauf/QS/Finance. |
| `OperationalTaskPlan` | Arbeitsschritte mit erledigt/offen und Hinweistext. | Abschlusslisten, Gate-Bearbeitung, Wareneingang, Zahlungslauf, Reklamation. |
| `NextActionPanel` | Eine konkrete naechste Handlung sichtbar machen. | Detailseiten, Pruefungen, Fehler- und Blockerlagen. |
| `EvidenceTemplateLink` | Vorlage oder Nachweisformular direkt aus der UI oeffnen. | eAU-Protokoll, DATEV-Testexport, AVV/DPA, Frachtbrief, Pruefbericht. |
| `AuditTimeline` | Nachweis-, Test-, Entscheidungs- und Rueckfrageverlauf anzeigen. | Freigaben, Storno, Abschluss, QS, Zahlung, Dokumentversionen. |
| `ManagementDecisionPanel` | Verdichtete Abschluss-/Freigabeentscheidung zeigen. | Go-live, Monatsabschluss, Zahlungslauf, Versand, Sperre/Freigabe. |
| `CrudCapabilityChecklist` | CRUD- und Workflow-Abdeckung transparent pruefen. | UX-Reviews und komplexe Stammdaten-/Belegseiten. |
| `EmptyStateWithAction` | Leere Zustaende mit sinnvoller Handlung statt leerer Tabelle. | Neue Mandanten, leere Suchergebnisse, fehlende Nachweise. |

## CRUD-Abdeckung

CRUD wird nicht nur technisch verstanden. Eine exzellente ERP-Seite muss auch die fachlichen Nebenpfade sichtbar machen.

| Faehigkeit | UX-Frage | Mindestanforderung |
|---|---|---|
| Create | Kann ein neuer Vorgang sicher angelegt werden? | Pflichtfelder, Vorbelegung, Plausibilitaet und klare Erfolgsmeldung. |
| Read | Ist der Vorgang schnell verstehbar? | Status, Owner, Risiko, Faelligkeit und naechste Aktion sichtbar. |
| Update | Sind Aenderungen gefuehrt? | Validierung, Aenderungsgrund wo noetig, kein unerklaerter Freitextzwang. |
| Delete | Ist Loeschen fachlich sicher? | Storno, Sperre oder Loeschfreigabe statt riskanter Direktloeschung bei Belegen. |
| Approve | Kann freigegeben werden? | Rolle, Datum, Kommentar und Entscheidung sichtbar. |
| Reject | Kann sauber zurueckgewiesen werden? | Begruendung, Rueckfrage und naechste Aktion erforderlich. |
| Export | Ist der Export nachvollziehbar? | Zweck, Format, Empfaenger und Auditbezug sichtbar. |
| Audit | Ist die Historie sichtbar? | Chronologische Timeline mit Person, Zeitpunkt, Aktion und Ergebnis. |
| Evidence | Sind Nachweise auffindbar? | Vorlage, DMS-Link, Aktenzeichen oder Datei-Referenz direkt verknuepft. |

## Domaenenuebertragung

| Domaene | Rollenfokus | Aufgabenplan | Evidence/Vorlage | Audit/Entscheidung |
|---|---|---|---|---|
| HRM | HR, Payroll, IT, Datenschutz, Legal, Leitung | Betriebsfreigabe-Gates | HRM-Go-live-Templates | Gate-Audit und Go-live-Policy |
| Finance/FIBU | Buchhaltung, Controlling, Steuerberater, Leitung | Periodenabschluss, Zahlungen, Mahnwesen | Export-, Freigabe- und Abstimmvorlagen | Abschluss-/Zahlungsentscheidung |
| Einkauf | Einkauf, Wareneingang, QS, Finance | Anfrage, Bestellung, Wareneingang, Rechnung | Lieferanten-, Avis- und Pruefbelege | Bestell- und Rechnungsfreigabe |
| CRM/Vertrieb | Vertrieb, Innendienst, Leitung | Lead, Angebot, Auftrag, Follow-up | Angebots- und Kontaktvorlagen | Opportunity-/Auftragsverlauf |
| Logistik/Waage | Disposition, Fahrer, Waage, QS | Tour, Verwiegung, Frachtbrief, Abweichung | Wiegeschein, Frachtbrief, Abweichungsprotokoll | Tour- und Warenausgangsstatus |
| Dokumente/DMS | Fachbereich, Legal, Datenschutz, Audit | Eingang, Klassifikation, Freigabe, Ablage | Dokumentklasse und Retention | Versions- und Freigabeverlauf |
| Produktion/Qualitaet | Schicht, QS, Leitung | Auftrag, Rueckmeldung, Pruefung, Sperre | Pruefprotokoll und Abweichung | Chargen- und Freigabeverlauf |

## Abnahmekriterien fuer neue oder ueberarbeitete Seiten

Eine Seite gilt erst als UX-ready, wenn sie mindestens diese Punkte erfuellt:

- Zielgruppe und Rolle sind auf der Seite erkennbar.
- Der kritische Gesamtstatus steht oberhalb der Detaildaten.
- Es gibt eine konkrete naechste Aktion.
- Komplexe Prozesse sind als Schritte oder Aufgabenplan sichtbar.
- Erforderliche Nachweise oder Vorlagen sind direkt verlinkt.
- Kritische Entscheidungen zeigen Owner, Datum, Status und Begruendung.
- Fehler- und Leerzustaende enthalten einen sinnvollen naechsten Schritt.
- Keine hypothetischen Funktionen oder Risiken werden angezeigt, wenn sie technisch nicht vorgesehen sind.

## Rollout-Reihenfolge

1. HRM-Betriebsfreigaben als Referenz abschliessen.
2. Finance/FIBU auf Abschluss-, Zahlungs- und Mahnwesen-UX uebertragen.
3. Einkauf auf Lieferanten-, Avis-, Rechnungseingang- und Freigabe-UX uebertragen.
4. CRM/Vertrieb auf Opportunity-, Angebot- und Auftrag-Follow-up uebertragen.
5. Logistik/Waage auf Tour-, Frachtbrief-, Verwiegungs- und Abweichungs-UX uebertragen.
6. Dokumente/DMS auf Klassifikation, Retention, Version und Freigabe uebertragen.
7. Produktion/QS auf Chargen-, Pruef- und Sperrprozesse uebertragen.

## Rollout-Status

| Slice | Domaene | Status | Ergebnis |
|---|---|---|---|
| `HRM-GO-LIVE-UX-001` | HRM | abgeschlossen | Betriebsfreigaben als Referenz mit Rollenfokus, Aufgabenplan, Vorlage-Link, Audit-Zeitleiste und Managemententscheidung. |
| `UX-STANDARD-COMPONENTS-001` | Plattform | abgeschlossen | Wiederverwendbarer Baukasten unter `@/components/workflow`. |
| `UX-FINANCE-001` | Finance/FIBU | abgeschlossen | Kreditoren-Zahlungslauf nutzt Rollenfokus, Aufgabenplan, Managemententscheidung, Next Action und CRUD-Abdeckung. |
| `UX-FINANCE-002` | Finance/FIBU | abgeschlossen | UStVA nutzt Rollenfokus, Melde-Aufgabenplan, Managemententscheidung, Next Action und CRUD-/Meldeabdeckung. |
| `UX-FINANCE-003` | Finance/FIBU | abgeschlossen | Mahnwesen nutzt Rollenfokus, Mahn-Aufgabenplan, Eskalationsentscheidung, Next Action und CRUD-/Kommunikationsabdeckung. |
| `UX-FINANCE-004` | Finance/FIBU | abgeschlossen | Periodenabschluss nutzt Rollenfokus, Close-Aufgabenplan, Managemententscheidung, Next Action und CRUD-/Close-Abdeckung. |
| `UX-EINKAUF-001` | Einkauf | abgeschlossen | Rechnungseingaenge nutzen Rollenfokus, Freigabeplan, Managemententscheidung, Next Action und CRUD-/Workflow-Abdeckung. |
| `UX-EINKAUF-002` | Einkauf | abgeschlossen | Bestellungen nutzen Rollenfokus, Bestell-Follow-up-Plan, Managemententscheidung, Next Action und CRUD-/Liefer-Abdeckung. |
| `UX-EINKAUF-003` | Einkauf | abgeschlossen | Wareneingang nutzt Rollenfokus, Eingangspruefplan, Managemententscheidung, Next Action und CRUD-/Nachweis-Abdeckung. |
| `UX-EINKAUF-004` | Einkauf | abgeschlossen | Lieferantenstamm nutzt Rollenfokus, Lieferanten-Onboardingplan, Managemententscheidung, Next Action, Nachweislink und CRUD-/Compliance-Abdeckung. |
| `UX-EINKAUF-005` | Einkauf | abgeschlossen | Lieferantenbewertung nutzt Rollenfokus, Bewertungsplan, Eskalationsentscheidung, Next Action und CRUD-/Nachweis-Abdeckung. |
| `UX-EINKAUF-006` | Einkauf | abgeschlossen | Retouren und Gutschriften/Belastungen nutzen Rollenfokus, Freigabeplan, Stopperentscheidung, Next Action und CRUD-/Nachweis-Abdeckung. |
| `UX-EINKAUF-007` | Einkauf | abgeschlossen | Einkaufs-Dashboard nutzt Rollenfokus, Einkaufs-Prioritaetsplan, Managemententscheidung, Next Action und CRUD-/Nachweis-Abdeckung. |
| `UX-CRM-001` | CRM/Vertrieb | abgeschlossen | Opportunities nutzen Rollenfokus, Follow-up-Plan, Managemententscheidung, Next Action und CRUD-/Pipeline-Abdeckung. |
| `UX-SALES-001` | Sales/Verkauf | abgeschlossen | Verkaufsauftraege nutzen Rollenfokus, Auftrag-Follow-up-Plan, Managemententscheidung, Next Action und CRUD-/Fulfillment-Abdeckung. |
| `UX-SALES-002` | Sales/Verkauf | abgeschlossen | Angebote nutzen Rollenfokus, Angebots-Follow-up-Plan, Managemententscheidung, Next Action und CRUD-/Conversion-Abdeckung. |
| `UX-SALES-003` | Sales/Verkauf | abgeschlossen | Auftragseditor nutzt Rollenfokus, Auftrags-Erfassungsplan, Managemententscheidung, Next Action und CRUD-/Folgebeleg-Abdeckung. |
| `UX-SALES-004` | Sales/Verkauf | abgeschlossen | Rechnungs- und Lieferschein-Editor nutzen Rollenfokus, Folgebelegplan, Managemententscheidung, Next Action und CRUD-/Nachweis-Abdeckung. |
| `UX-SALES-005` | Sales/Verkauf | abgeschlossen | Gutschriften-Editor nutzt Rollenfokus, Freigabeplan, Managemententscheidung, Next Action und CRUD-/Nachweis-Abdeckung. |
| `UX-SALES-006` | Sales/Verkauf | abgeschlossen | Verkaufsdashboard, Rechnungs- und Lieferlisten nutzen Rollenfokus, Prioritaetsplan, Managemententscheidung, Next Action und CRUD-/Nachweis-Abdeckung. |
| `UX-SALES-007` | Sales/Verkauf | abgeschlossen | Moderne Sales-Auftragssicht nutzt Rollenfokus, Eskalationsplan, Managemententscheidung, Next Action und CRUD-/Nachweis-Abdeckung. |
| `UX-LOGISTIK-001` | Logistik | abgeschlossen | Tourenplanung nutzt Rollenfokus, Dispo-Aufgabenplan, Managemententscheidung, Next Action und CRUD-/Transport-Abdeckung. |
| `UX-LOGISTIK-002` | Logistik | abgeschlossen | Frachtbriefe nutzen Rollenfokus, Dokument-Follow-up-Plan, Managemententscheidung, Next Action und CRUD-/Nachweis-Abdeckung. |
| `UX-LOGISTIK-003` | Logistik/Waage | abgeschlossen | Waagearbeitsflaechen nutzen Rollenfokus, Waage-Aufgabenplan, Stopperentscheidung, Next Action und CRUD-/Nachweis-Abdeckung. |
| `UX-LOGISTIK-004` | Logistik/Waage | abgeschlossen | Hofliste und Waagenliste nutzen Rollenfokus, Prioritaetsplan, Stopperentscheidung, Next Action und CRUD-/Nachweis-Abdeckung. |
| `UX-LOGISTIK-005` | Logistik/Bestand | abgeschlossen | Bestands-/Logistik-Dashboard nutzt Rollenfokus, Bestands-Kettenplan, Managemententscheidung, Next Action und CRUD-/Nachweis-Abdeckung. |

Naechste Rollout-Slices:

- `UX-EINKAUF-008`: Einkaufs-Ausnahmen wie OCR/EDI/Service Entry mit Stopper-, Prioritaets- und Nachweissicht.
- `UX-SALES-008`: Sales-Assistenz fuer Angebots-/Auftragsuebergaben mit naechster Aktion und Nachweisstatus.
- `UX-LOGISTIK-006`: Fracht-/Speditions-Ausnahmen mit Eskalationssicht, naechster Aktion und Kettennachweis.

## Nicht-Ziel

Dieser Standard verlangt keine Marketingseiten und keine dekorativen UIs. Ziel ist ein ruhiges, dichtes und handlungsorientiertes ERP fuer wiederkehrende Bueroarbeit.
