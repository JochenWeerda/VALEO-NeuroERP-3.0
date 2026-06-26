# Professional Tail Gap Plan 2026-04-09

Stand: `2026-04-09` | Letzte Aktualisierung: `2026-06-26`

## Status-Aktualisierung 2026-06-26

### Abgeschlossen seit 2026-04-09

| Tail-Block | Umgesetzt durch |
|---|---|
| Tail-Serie 6–11 (CRM Opp, Kontakt, FIBU, Futtermittel ×3) | Als abgeschlossen deklariert 2026-04-09 + DOM-004-Wellen |
| Tail-Serie B 12–17 (Zertifikate, Schäden, Fahrer, Tankstelle, Bodenproben, Saatgut) | Als abgeschlossen deklariert 2026-04-09 |
| Tail-Serie C 18–23 (Zulassungen, VVVO, Rahmenverträge, Versicherungen, Labor, Projekte) | Als abgeschlossen deklariert 2026-04-09 |
| TAIL-CRM-001: Duplicate Detection | STMD-DUP-001 (Wave 3, 2026-06-18) — UST-ID/IBAN/PLZ+Name-Fuzzy/EAN-Duplikate + Soft-Merge |
| TAIL-CRM-001: 360°-Kundensicht, KIM | KIM-DS-001, KIM-L3-BACKEND-001, KIM-L3-FRONTEND-001 (2026-06-26) |
| TAIL-SERVICE-001 (im Kern) | WF-TRIGGER-001 (Wave 3) + DOM-SUPPLY-004 Folgebelege |

### Noch offen (Stand 2026-06-26)

| Tail-Block | Was fehlt noch |
|---|---|
| TAIL-CRM-001 | RAG-Panel und Intent-Bar in `LegacyKundenStammModern.tsx` noch als TODO markiert |
| TAIL-NAWARO-001 | Druck-/Vorschau-/Serienbrief-Pfade NaWaRo noch nicht vollständig angeschlossen |
| TAIL-AGRI-001 | PSM-Beratung Demo-Fallback; Saatgut-Edit-Flow noch Placeholder |
| TAIL-SALES-001 | `orders-modern.tsx` Export/Import/Archiv-Aktionen noch Toast-only |

Verbindliche offene Punkte → `docs/project-context/open-gaps-and-known-issues.md`.

---

## Zweck

Diese Datei dokumentiert den verbleibenden langen Tail an fachlich noch duennen oder nur teilweise verdrahteten Modulen nach Abschluss der priorisierten Kernbloecke:

- Kontrakt-Profi
- FIBU-Profi
- Supply-/Rohware-/Waage-/Fracht-E2E
- Dokumenten- und Preis-Profi

Der Fokus liegt nicht mehr auf den grossen Querschnittsraeumen, sondern auf einzelnen Fachmodulen, in denen noch Platzhalter-, Toast- oder Fallback-Logik sichtbar ist oder in denen ein professioneller ERP-Arbeitsplatz fachlich noch nicht voll ausgebildet ist.

## Bewertungslogik

Ein Tail-Modul ist dann relevant, wenn mindestens einer der folgenden Punkte zutrifft:

- Nutzeraktion endet nur in einem Toast statt in echtem Zustandswechsel oder Folgearbeitsplatz
- Fachobjekt hat keinen professionellen Arbeitsraum, sondern nur Formular-/Listencharakter
- Seite nutzt weiterhin Demo-/Fallback-Verhalten statt belastbarem Betriebsbild
- Es fehlt eine klare Verbindung zu Dokumenten, Workflow, Vorgang, Druck, Folgeaktion oder Agenten-/Kontrollzentrum

## Verbleibende Tail-Bloecke

### 1. NaWaRo-Kommunikation und Druck

Betroffene Dateien:

- `packages/frontend-web/src/pages/nawaro/anbauflaechen.tsx`
- `packages/frontend-web/src/pages/nawaro/mitteilung-drucken.tsx`
- `packages/frontend-web/src/pages/nawaro/vertraege.tsx`
- `packages/frontend-web/src/pages/nawaro/raps-profil.tsx`

Ist-Zustand:

- Druck, Vorschau und Serienbrief sind teilweise noch reine Toast-Aktionen.
- Die Seiten sind operativ brauchbar, aber die Kommunikations- und Dokumentlogik ist noch nicht professionell an reale Druck-/Dokumenten-/Versandpfade angeschlossen.

Profi-Zielbild:

- belastbare Druck- und Vorschaupfade
- Dokumentbezug zu Vertrag, Anbauflaeche, Profil und Empfaenger
- Wiedervorlage, Versandstatus, Artefakt-/Belegpfad
- klare Folgeaktion statt nur „erstellt“

Referenzmuster:

- Web-ERP-Standard Object Page / Worklist fuer Kommunikationsobjekte
- Community-Agreement- und Dokumentmuster als Daten-/Statusreferenz

### 2. CRM Modernisierung und Assistenz

Betroffene Dateien:

- `packages/frontend-web/src/pages/crm/kunden-stamm-modern/LegacyKundenStammModern.tsx`

Ist-Zustand:

- Duplicate Detection, RAG-Panel und Intent Bar sind noch als TODO markiert.
- Damit fehlt im modernen CRM-Stamm noch ein Teil der professionellen Assistenz- und Datenqualitaetslogik.

Profi-Zielbild:

- Dublettenpruefung mit Trefferbild und Merge-/Klaerungspfad
- RAG-/Wissenspanel fuer kundenbezogenen Kontext
- Intent-/Naechste-Aktion-Leiste fuer Vertrieb, Service und Reklamation
- sichtbare Folgewege in Dokumente, Tasks und Angebots-/Auftragskontext

Referenzmuster:

- Paperclip-inspirierte Ticket-/Naechste-Aktion-Muster
- Web-ERP-Standard flexible Header/Object Page fuer Kundenarbeitsplaetze

### 3. Agrar Beratung und Saatgut-Stammdaten

Betroffene Dateien:

- `packages/frontend-web/src/pages/agrar/psm/beratung.tsx`
- `packages/frontend-web/src/pages/agrar/saatgut/stamm.tsx`

Ist-Zustand:

- PSM-Beratung arbeitet noch mit Demo-Fallback, wenn die API leer ist.
- Im Saatgut-Stamm ist der Edit-Flow noch als Placeholder markiert.

Profi-Zielbild:

- belastbares Beratungsbild ohne stillen Demo-Charakter
- expliziter Zustand bei fehlender Datengrundlage statt implizitem Fallback
- vollstaendiger Edit-/Freigabe-/Versionspfad fuer Saatgutstammdaten
- klare Fachfolgen in Aussaat, Sortenregister und Dokument-/Nachweisraum

Referenzmuster:

- Web-ERP-Standard Wizard/Object Page fuer Pflege und Beratungsentscheidungen
- Community-Stammdaten-/Katalogmuster als Status- und CRUD-Referenz

### 4. Sales Modern Surface Restlogik

Betroffene Dateien:

- `packages/frontend-web/src/pages/sales/orders-modern.tsx`

Ist-Zustand:

- Export, Import, Filter und Archiv-Aktionen laufen noch nur ueber Toast-Hinweise.
- Die Seite ist damit als moderne Einstiegsflaeche da, aber noch nicht als professioneller Arbeitsraum abgeschlossen.

Profi-Zielbild:

- echte Export-/Import-/Archivierungs- und Filterfuehrung
- sichtbare Queue-/Massenaktionslogik
- Rueckkopplung in Workflow, Dokumente und Freigaben

Referenzmuster:

- Web-ERP-Standard Worklist / Massenaktion
- Community-Sales-Operations-Muster als Zustands- und Bulk-Action-Referenz

### 5. Service-/Field-Kommunikation und Folgebelege

Betroffene Dateien:

- `packages/frontend-web/src/pages/service/anfrage-neu.tsx`
- `packages/frontend-web/src/pages/service/anfrage-detail.tsx`
- `packages/frontend-web/src/pages/service/anfragen.tsx`
- `packages/frontend-web/src/pages/service/rueckmeldung.tsx`
- `packages/frontend-web/src/pages/service/abschluss.tsx`
- `packages/frontend-web/src/pages/agribusiness/field-service-task-neu.tsx`

Ist-Zustand:

- Kernpfade existieren, aber Teile der Kommunikations- und Folgebeleglogik bleiben noch auf Erfassung fokussiert.
- `field-service-task-neu.tsx` traegt den Hinweis `CRM-Fall / Demo-Fallback`.

Profi-Zielbild:

- durchgehender Vorgang von Anfrage ueber Rueckmeldung bis Abschluss
- Folgebelege, Dokumente, CRM-/Task-Verknuepfung, Wiedervorlage
- kein Demo-Charakter mehr in der Neuanlage

Referenzmuster:

- Web-ERP-Standard Object Page / Timeline
- Community-Field-Service-/Helpdesk-Muster als Referenz fuer Status-/Folgeobjekte

## Priorisierung

### Prioritaet A

1. CRM-Assistenz und Datenqualitaet
2. NaWaRo-Kommunikation und Druck
3. Agrar Beratung / Saatgut-Stamm

### Prioritaet B

4. Sales Modern Surface Restlogik
5. Service-/Field-Kommunikation und Folgebelege

## Empfohlene Slice-Struktur

### TAIL-CRM-001

- Duplicate Detection, RAG-Panel, Intent Bar im modernen CRM-Stamm

### TAIL-NAWARO-001

- Druck-/Vorschau-/Serienbrief-/Dokumentenpfad fuer NaWaRo

### TAIL-AGRI-001

- PSM-Beratung ohne stillen Demo-Fallback und Saatgut-Edit-Flow

### TAIL-SALES-001

- professionelle Massen- und Folgeaktionen in `orders-modern.tsx`

### TAIL-SERVICE-001

- professioneller Service-/Field-Kommunikationspfad mit Folgeobjekten

## Lizenz- und Referenzregel

Wenn fuer diese Tail-Bloecke externer Referenzcode noetig wird:

1. zuerst UI- und Datenmodellmuster aus modernen ERP-Oberflächen / OpenUI5 nutzen
2. dann permissive oder kompatible Community-Quellen modulweise pruefen
3. AGPL- oder proprietaeren Enterprise-Code nicht unkritisch uebernehmen
4. Codeuebernahme immer separat dokumentieren

## Folgerung

Die grossen priorisierten ERP-Kernluecken aus dem Agrar-Spezialsoftware-Vergleich sind geschlossen. Der verbleibende Ausbau ist jetzt ein geordneter Fachmodul-Tail. Er sollte nicht breit parallelisiert, sondern blockweise nach betrieblichem Nutzen, Anwenderhaeufigkeit und Verdrahtungstiefe abgearbeitet werden.

## Nächste Tail-Serie

Stand `2026-04-09`: abgeschlossen. Die sechs Folge-Slices unten sind umgesetzt und im Workboard auf `abgeschlossen` gezogen.

### 6. CRM Opportunity Operations

Betroffene Dateien:

- `packages/frontend-web/src/pages/crm/opportunities-liste.tsx`
- `packages/frontend-web/src/pages/crm/opportunities-kanban.tsx`

Ist-Zustand:

- Bulk-Aktionen fuer Konvertierung, Gewinn/Verlust und Import laufen in der Listenmaske noch als Toast oder Hinweis.
- Die Opportunity-Pipeline ist sichtbar, aber Listen- und Kanban-Arbeitsplatz bilden den Vertriebsfortschritt noch nicht gleich tief ab.

Profi-Zielbild:

- Opportunity-Bulk-Aktionen fuehren in echte Folgepfade fuer Angebot, Gewinn, Verlust und Pipeline-Wechsel.
- Listen- und Kanban-Sicht teilen dieselbe operative Story: naechste Aktion, Konvertierungspfad und Vertriebsdruck.

### 7. CRM Kontaktmanagement

Betroffene Dateien:

- `packages/frontend-web/src/pages/crm/kontakt-management.tsx`

Ist-Zustand:

- Export, E-Mail, Anruf, Termin und Deaktivierung sind sichtbar, enden aber noch nur in Toast-/Hinweislogik.

Profi-Zielbild:

- Kontakte fuehren in echte Kommunikations-, Termin-, Deaktivierungs- und Folgeobjektpfade.

### 8. FIBU Buchhaltungsuebersicht

Betroffene Dateien:

- `packages/frontend-web/src/pages/fibu/buchhaltungsuebersicht.tsx`

Ist-Zustand:

- Drilldown ist bereits verlinkt, aber Toolbar-/Footer-Aktionen wie Drucken, Journal, Kontenbewegung oder Fensterraum sind noch nicht als echter Folgearbeitsplatz verdichtet.

Profi-Zielbild:

- Die Buchhaltungsuebersicht ist ein belastbarer FIBU-Leitstand mit echten Folgepfaden fuer Journal, Kontenbewegung, Druck, Export und Periodenauswertung.

### 9. Futtermittel Chargenverfolgung

Betroffene Dateien:

- `packages/frontend-web/src/pages/futtermittel/charge-verfolgung.tsx`

Ist-Zustand:

- Export, Rueckruf und Rueckverfolgung sind noch Toast-Aktionen.

Profi-Zielbild:

- Chargenverfolgung fuehrt in reale Rueckruf-, Export- und Traceability-Pfade mit Dokument- und Qualitaetsbezug.

### 10. Futtermittel Einzelfuttermittel-Stamm

Betroffene Dateien:

- `packages/frontend-web/src/pages/futtermittel/einzelfuttermittel-stamm.tsx`

Ist-Zustand:

- Validierung und Speichern sind noch auf Hinweislogik reduziert.

Profi-Zielbild:

- Stammdatenpruefung, Speichern und Folgebezug zu Rezeptur, Einkauf und Qualitaet sind professionell verdrahtet.

### 11. Futtermittel Mischfuttermittel-Stamm

Betroffene Dateien:

- `packages/frontend-web/src/pages/futtermittel/mischfuttermittel-stamm.tsx`

Ist-Zustand:

- Berechnung, Validierung und Speichern laufen noch nur als Toast.

Profi-Zielbild:

- Rezeptur-Arbeitsplatz mit echter Berechnung, Validierung, Speichern und Folgepfaden in Produktion, Qualitaet und Dokumentation.

## Naechste Tail-Serie B

Stand `2026-04-09`: abgeschlossen.

### 12. Zertifikate Leitstand

Betroffene Dateien:

- `packages/frontend-web/src/pages/zertifikate/liste.tsx`

Ist-Zustand:

- Suche und Ablaufwarnung sind da, aber Export und Folgewege fuer Audit, Dokumente und Verlaengerung fehlen als echte Operator-Aktionen.

Profi-Zielbild:

- Export, Ablauf-Fokus und Folgepfade in Dokumente, Detail und Zertifikatsverlaengerung sind direkt verfuegbar.

### 13. Schaeden Operations

Betroffene Dateien:

- `packages/frontend-web/src/pages/schaeden/liste.tsx`

Ist-Zustand:

- Die Liste zeigt KPI und Meldungsstart, aber kein echter Export- und Folgepfad fuer Regulierung, Dokumente und offene Prueffaelle.

Profi-Zielbild:

- Export, offene-Regulierungs-Sicht und Folgewege in Meldung und Vorgang sind direkt aus dem Arbeitsraum verfuegbar.

### 14. Fahrer Einsatzsicht

Betroffene Dateien:

- `packages/frontend-web/src/pages/transporte/fahrer-liste.tsx`

Ist-Zustand:

- Fahrerstatus ist sichtbar, aber Export und Dispositions-Folgepfad fehlen.

Profi-Zielbild:

- Fahrerarbeitsplatz mit Export, Verfuegbarkeitsfokus und Sprung in Tourenplanung/Disposition.

### 15. Tankstellen Zapfungsraum

Betroffene Dateien:

- `packages/frontend-web/src/pages/tankstelle/zapfungen.tsx`

Ist-Zustand:

- Die Zapfungsliste ist nur eine Tabelle mit KPI; Export und Folgewege in Abrechnung/Vehicle/Ops fehlen.

Profi-Zielbild:

- Zapfungsarbeitsplatz mit Export, Verbrauchsfokus und Folgepfaden in Betrieb/Disposition.

### 16. Bodenproben Leitstand

Betroffene Dateien:

- `packages/frontend-web/src/pages/agrar/bodenproben/liste.tsx`

Ist-Zustand:

- Export ist vorhanden, aber der Arbeitsraum endet noch an der Liste statt an klaren Folgewegen fuer Analyse, Beratung und Auftrag.

Profi-Zielbild:

- Professioneller Labor-/Beratungsraum mit Export, Offene-Proben-Fokus und direkten Folgewegen.

### 17. Saatgut Listenfuehrung

Betroffene Dateien:

- `packages/frontend-web/src/pages/agrar/saatgut-liste.tsx`

Ist-Zustand:

- Liste und Export existieren, aber der Arbeitsplatz zeigt noch zu wenig operative Folgeaktionen und Bestands-/Zulassungsfokus.

Profi-Zielbild:

- Saatgut-Leitstand mit Export, operative Fokussegmente und direkte Folgewege in Stamm, Sicht und Bestand.

## Naechste Tail-Serie C

Stand `2026-04-09`: abgeschlossen.

### 18. Zulassungen Register

Betroffene Dateien:

- `packages/frontend-web/src/pages/compliance/zulassungen-register.tsx`

Ist-Zustand:

- Suche, KPI und Ablaufwarnung sind vorhanden, aber Export, Filterwirkung und echte Folgepfade fuer Dokumente, Registerpflege und auslaufende Zulassungen fehlen.

Profi-Zielbild:

- Zulassungsregister als Operator-Arbeitsplatz mit gefilterter Sicht, CSV-Export, Fokus auf auslaufende Faelle und direkten Folgewegen in Detail, Dokumente und Melde-/Registerkontext.

### 19. VVVO Register

Betroffene Dateien:

- `packages/frontend-web/src/pages/compliance/vvvo-register.tsx`

Ist-Zustand:

- Betriebserfassung und Detailsprung existieren, aber Export, fokussierte Arbeitssegmente und Folgepfade fuer Dokumente und Pflege sind noch duenn.

Profi-Zielbild:

- VVVO-Register mit belastbarer Suche, Export, Aktiv-/Inaktiv-Fokus und klaren Folgewegen in Betriebsprofil, Dokumente und Neuanlage.

### 20. Rahmenvertraege Leitstand

Betroffene Dateien:

- `packages/frontend-web/src/pages/vertrag/rahmenvertraege.tsx`

Ist-Zustand:

- KPI und Listenansicht existieren, aber Export, operative Fokussegmente und Folgepfade in Dokumente und Kontraktsteuerung sind noch nicht professionell verdichtet.

Profi-Zielbild:

- Rahmenvertraege als echter Vertragsarbeitsplatz mit gefilterter Sicht, Export, Auslauf-/Niedrigrestmengen-Fokus und direkten Folgewegen in Detail, Dokumente und Kontraktsteuerung.

### 21. Versicherungen Leitstand

Betroffene Dateien:

- `packages/frontend-web/src/pages/versicherungen/liste.tsx`

Ist-Zustand:

- Versicherungsliste zeigt Kennzahlen, aber Export, Ablauffokus und Folgepfade in Dokumente und Verlängerung fehlen.

Profi-Zielbild:

- Versicherungsarbeitsplatz mit Such- und Exportfunktion, Ablaufwarnung, Fokus auf kritische Policen und klaren Folgewegen in Detail, Dokumente und Neuanlage.

### 22. Laborliste

Betroffene Dateien:

- `packages/frontend-web/src/pages/qualitaet/labor-liste.tsx`

Ist-Zustand:

- Laborauftraege sind sichtbar, aber Suche filtert noch nicht operativ, Export fehlt und Folgepfade fuer offene Analysen, Dokumente und Neuanlage sind duenn.

Profi-Zielbild:

- Laborliste als Qualitaets-Arbeitsplatz mit gefilterter Sicht, Export, Fokus auf offene/in Bearbeitung Auftraege und direkten Folgewegen in Detail, Auftrag und Dokumente.

### 23. Projekte Liste

Betroffene Dateien:

- `packages/frontend-web/src/pages/projekte/liste.tsx`

Ist-Zustand:

- Projektliste zeigt Status und Fortschritt, aber Export, operative Fokussegmente und Folgepfade in Dokumente und Neuanlage sind noch nicht professionell ausgebildet.

Profi-Zielbild:

- Projektarbeitsplatz mit gefilterter Sicht, Export, Fokus auf aktive und stockende Projekte und direkten Folgewegen in Detail, Dokumente und Neuanlage.
