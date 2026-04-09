# Professional Tail Gap Plan 2026-04-09

Stand: `2026-04-09`

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

- SAP Fiori Object Page / Worklist fuer Kommunikationsobjekte
- Odoo/OCA Agreement- und Document-Patterns als Daten-/Statusreferenz

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
- SAP Fiori flexible Header/Object Page fuer Kundenarbeitsplaetze

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

- Fiori Wizard/Object Page fuer Pflege und Beratungsentscheidungen
- Odoo/OCA Stammdaten-/Catalog-Patterns als Status- und CRUD-Referenz

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

- SAP Fiori Worklist / Massenaktion
- Odoo Sales Operations als Zustands- und Bulk-Action-Referenz

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

- Fiori Object Page / Timeline
- Odoo Field Service / Helpdesk als Referenz fuer Status-/Folgeobjekte

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

1. zuerst UI- und Datenmodellmuster aus SAP Fiori / OpenUI5 nutzen
2. dann permissive oder kompatible Odoo-/OCA-Quellen modulweise pruefen
3. AGPL- oder Odoo-Enterprise-Code nicht unkritisch uebernehmen
4. Codeuebernahme immer separat dokumentieren

## Folgerung

Die grossen priorisierten ERP-Kernluecken aus dem AMIC-Vergleich sind geschlossen. Der verbleibende Ausbau ist jetzt ein geordneter Fachmodul-Tail. Er sollte nicht breit parallelisiert, sondern blockweise nach betrieblichem Nutzen, Anwenderhaeufigkeit und Verdrahtungstiefe abgearbeitet werden.
