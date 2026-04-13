# ERP Reference Gap Analysis: AMIC, Community ERP, SAP Fiori

Stand: `2026-04-12`

## Zweck

Diese Referenzdatei haelt den externen Vergleich gegen etablierte ERP-Funktionsbilder fest, damit spaetere Ausbau-Slices in VALEO nicht nur aus dem Ist-Code, sondern auch aus reifen Vergleichssystemen abgeleitet werden.

Die Datei dient als:

- Referenz fuer fachlich noch duenne Bereiche in VALEO
- Priorisierungshilfe fuer kommende Ausbau-Slices
- Quellenliste fuer moegliche Upstream-Muster oder reiferen Referenzcode
- Lizenzhinweis fuer spaetere kommerzielle Nutzung

## Verwendete Referenzen

### AMIC / A.eins Hilfe

- AMIC Hilfe Index: <https://www.amic.de/hilfe/index.html#>
- Kontrakt: <https://www.amic.de/hilfe/index.html#!_kontrakt.htm>
- Finanzbuchhaltung: <https://www.amic.de/hilfe/index.html#!finanzbuchhaltung20.htm>
- Frachtwesen: <https://www.amic.de/hilfe/index.html#!frachtwesen.htm>

Beobachtung:
AMIC bildet ERP-Funktionalitaet sehr fein in fachlichen Untermodulen ab. Besonders auffaellig sind die Tiefe bei Kontrakt, Finanzbuchhaltung, Frachtwesen, Waagen-/Rohwarenlogik und den dazugehoerigen Parametern, Sonderfaellen und Auswertungen.

### Community-ERP-Addons und Community-Funktionsrepositorien

- Community Agreement Repository: <https://github.com/OCA/agreement>
- Community Stock Logistics Workflow: <https://github.com/OCA/stock-logistics-workflow>
- Community Account Financial Tools: <https://github.com/OCA/account-financial-tools>
- Community Purchase Workflow: <https://github.com/OCA/purchase-workflow>
- Community Helpdesk: <https://github.com/OCA/helpdesk>

Beobachtung:
Diese Repositorien liefern reife Referenzmuster fuer Geschaeftsobjekte, States, Parameterisierung, Dokumenten-/Workflowlogik und Integrationsmuster. Sie sind als Funktions- und Datenmodell-Referenz wertvoll, aber lizenzseitig differenziert zu behandeln.

### SAP Fiori / OpenUI5

- SAP Fiori Object Page: <https://experience.sap.com/fiori-design-web/object-page/>
- SAP Fiori Overview Page: <https://experience.sap.com/fiori-design-web/v1-48/overview-page/>
- SAP Learning, Fiori Floorplans: <https://learning.sap.com/courses/ui-development-with-sap-fiori/working-with-sap-fiori-design-guidelines_ab11c169-54de-4f51-87b9-f61c8a5198be>
- SAP UI5 FAQ / OpenUI5 Lizenz: <https://pages.community.sap.com/topics/ui5/faq>

Beobachtung:
SAP Fiori ist fuer VALEO vor allem als UI- und Navigationsreferenz wertvoll: Object Page, Overview Page, Worklist, Wizard, klare Aufgabenorientierung, flexible Header, statusstarke Aktionsfuehrung und dichte, aber lesbare Betriebsbilder.

## Vergleich: AMIC-Funktionsbild vs. VALEO-Iststand

### 1. Kontrakt

AMIC zeigt in diesem Bereich eine deutlich tiefere fachliche Untergliederung:

- Kontraktklassen
- Kontraktgruppen
- Kontraktvarianten
- Kontraktdispositionskennzeichen
- Kontraktparitaetenstamm
- Kontraktausweichliste
- Kontraktabschreibung
- Kontrakt-Hedging
- Kontraktengagement
- Auswertungen / Listen ueber Kontrakte
- Formulareinrichtung fuer Kontraktdruck
- Washout and Circle
- Kontraktbewertung zum Marktpreis
- Kontrakt-Mahnung

VALEO hat bereits belastbare Grundbausteine:

- `packages/frontend-web/src/pages/kontrakte/LstKontraktUebersicht.tsx`
- `packages/frontend-web/src/pages/kontrakte/KontraktPositionsmonitor.tsx`
- `packages/frontend-web/src/pages/kontrakte/KontraktAlarmDashboard.tsx`
- `packages/frontend-web/src/pages/kontrakte/FrmKontraktDetail.tsx`
- `packages/frontend-web/src/pages/contracts-v2.tsx`

Noch fachlich duenn:

- Vertragsklassifizierung und Variantenmodell
- Preis-/Paritaetslogik
- explizite Engagement-Sicht
- Marktpreisbewertung / Bewertung zum Stichtag
- Hedging-/Fixierungslogik als eigener Arbeitsraum
- Mahnung / Abschreibung auf Kontraktebene
- Formular-/Drucksteuerung
- Ausweich- und Sonderfalllogik

Prioritaet:
hoch

### 2. Finanzbuchhaltung

AMIC beschreibt FIBU als voll integrierten Kern mit gemeinsam genutzter Datengrundlage und zusaetzlichen FIBU-exklusiven Stammdaten und Parametern.

AMIC nennt u. a.:

- Stammdaten der Fibu
- Belegerfassung
- Buchungen Finanzbuchhaltung
- Kontoblattdruck
- Umsatzsteuer
- eBilanz-Online
- OP-Verwaltung
- Konteninformationen
- Waehrungsbehandlung
- Mahnwesen
- Zahlungsverkehr
- e-Clearing
- Kostenrechnung
- Zinswesen
- Anlagenbuchhaltung
- Jahreswechsel
- Wechselbuchhaltung
- Chefcockpit / Kennzahlenanalyse
- Fibu Reorganisator
- Fibu Schnittstellen

VALEO ist hier bereits breit aufgestellt:

- `packages/frontend-web/src/pages/finance/*`
- `packages/frontend-web/src/pages/fibu/*`

Noch fachlich duenn:

- FIBU-exklusive Parameter-/Stammdatentiefe
- eBilanz / eClearing / Wechselbuchhaltung
- Zinswesen als eigener Fachraum
- Jahreswechsel / Reorganisator / technische Revisionspfade
- staerkere Zusammenfassung der FIBU-Schnittstellenlandschaft
- durchgehende Management-Fuehrung fuer Abschluss, Reorg und Schnittstellenbetrieb

Prioritaet:
hoch

### 3. Frachtwesen, Rohware, Waage, Partie

AMIC fuehrt Frachtwesen, Rohware-Modul, Waagenanbindung und Partieverwaltung als eigene starke Funktionsraeume.

VALEO hat bereits viele Teilraeume:

- `packages/frontend-web/src/pages/logistik/frachtbriefe.tsx`
- `packages/frontend-web/src/pages/einkauf/frachtauftraege-eingang.tsx`
- `packages/frontend-web/src/pages/annahme/rohware.tsx`
- `packages/frontend-web/src/pages/waage/*`
- `packages/frontend-web/src/pages/charge/*`

Noch fachlich duenn:

- durchgaengige Objektkette `Partie -> Annahme -> Wiegung -> Charge -> Lager -> Fracht -> Abrechnung`
- explizite betriebliche Leitstaende fuer Rohware/Fracht/Waage
- verdichtete Ausnahmebehandlung bei Abweichungen
- starker Zusammenhang zwischen Dokument, Gewicht, Partie, Vertrag und Abrechnung

Prioritaet:
hoch

### 4. Dokumentenverwaltung

AMIC fuehrt die Dokumentenverwaltung als eigenstaendigen Fachraum.

VALEO hat:

- `packages/frontend-web/src/pages/dokumente/ablage.tsx`
- `packages/frontend-web/src/pages/portal/dokumente.tsx`
- verschiedene objektnahe Dokumentpfade

Noch fachlich duenn:

- staerkere Objektverknuepfung ueber alle Kernworkflows
- Dokumentstatus, Freigabe, Wiedervorlage und Verwendungsnachweis
- klarere Trennung zwischen Ablage, Vorgangsbezug und revisionsrelevantem Nachweis

Prioritaet:
mittel

### 5. Preise / Konditionen / Kunden-Lieferanten-/Artikelkern

AMIC fuehrt diese Bereiche als tief ausgepraegte Stammdaten- und Bewegungslogik.

VALEO hat bereits breite Stammdatenraeume, aber noch nicht ueberall dieselbe operative Verdichtung:

- Kunden-/Lieferantenbild
- Artikel-/Bestandssicht
- Preis-/Konditionssteuerung
- kunden- und lieferantenbezogene Sonderfaelle

Noch fachlich duenn:

- konditionsseitige Tiefenmodelle
- durchgaengige Preisstory pro Objekt und Vorgang
- zentralere Sicht auf kundenspezifische und lieferantenspezifische Sonderregeln

Prioritaet:
mittel bis hoch

## Geeignete Upstream-Referenzen fuer spaetere Ausbauslices

### Community-ERP-Addons als fachliche und technische Referenz

Sinnvoll als Referenz fuer:

- Geschaeftsobjekte und Statusmodelle
- Account-/Finance-Werkzeuge
- Stock-/Logistik-Workflows
- Agreement-/Contract-Muster
- Parameterisierung und technische Glue-Module

Empfehlung:

- zuerst Modell, Felder, States, Guards und Arbeitslogik studieren
- nur dann Code uebernehmen, wenn Lizenz und Kopplung zum Ziel passen
- bei AGPL-lizenzierten Community-Modulen nur sehr vorsichtig mit echter Codeuebernahme umgehen

Besonders plausible Referenzfamilien:

- `agreement`
- `stock-logistics-workflow`
- `account-financial-tools`
- `purchase-workflow`
- `helpdesk`

### SAP Fiori / OpenUI5 als UIX-Referenz

Sinnvoll als Referenz fuer:

- Object Page als Objektarbeitsplatz
- Overview Page fuer Leitstaende / Cockpits
- Worklists mit klarer Aufgabenorientierung
- Wizard-Fuehrung fuer Einfuehrung, Onboarding und komplexe Prozesse
- lesbare Header-, Status- und Aktionsmuster

Empfehlung:

- Fiori nicht als Funktion kopieren, sondern als UI-Architekturprinzip nutzen
- OpenUI5 nur dann als Codequelle heranziehen, wenn wirklich Komponenten oder Strukturen daraus noetig sind
- primaer Designmuster und Interaktionslogik uebernehmen

## Lizenzampel fuer spaetere kommerzielle Nutzung

### Gruen

- OpenUI5: Apache 2.0
- SAP Fiori Design Guidelines als Referenz fuer Informationsarchitektur und Interaktionsmuster

### Gelb

- Community-Repositorien unter LGPL oder aehnlichen kompatiblen Open-Source-Lizenzen:
  vor echter Codeuebernahme immer modulweise pruefen

### Rot / Vorsicht

- AGPL-3.0-Repositorien:
  fuer ein proprietaer oder gemischt kommerziell vertriebenes ERP in der Regel keine unkritische Copy-Paste-Quelle
- kommerziell lizenzierte Enterprise-Codebasen:
  nicht als freie Copy-Source behandeln; proprietaere Lizenzbedingungen beachten

Kurzregel:

- Ideen, Fachstruktur und UX-Muster aus allen drei Referenzwelten nutzbar
- direkter Code vor allem aus permissiven oder klar kompatiblen Quellen
- starke Copyleft- oder proprietaere Quellen nur nach expliziter Lizenzentscheidung

## Priorisierte Ausbaukandidaten fuer VALEO

1. Kontrakt-Profi-Block
2. FIBU-Tiefenblock
3. Partie-/Rohware-/Waage-/Fracht-End-to-End-Block
4. Dokumentenverwaltung mit staerkerem Vorgangsbezug
5. Preis-/Konditions- und Stammkunden-/Lieferantenverdichtung

## Folgerung fuer kommende Slices

Wenn fuer einen Ausbau echte Referenzimplementierung noetig ist:

1. zuerst permissive oder kompatible Quelle suchen
2. bevorzugt reife Repositories mit breiter Nutzung
3. Lizenz vor Codeuebernahme dokumentieren
4. nur das uebernehmen, was architektonisch zu VALEO passt

Kein Ziel ist:

- AMIC oder SAP Fiori als Ganzes nachzubauen
- einen zweiten Orchestrator oder ein zweites Produktmodell einzubetten
- Lizenzrisiken durch unkritische Codeuebernahme einzugehen
