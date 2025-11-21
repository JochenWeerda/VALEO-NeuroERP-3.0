# VALEO NeuroERP 3.0 – Ist-Prozesse

## Einleitung

Dieser Überblick fasst den aktuellen Ablaufstand der Kernprozesse zusammen, bevor Erweiterungen in Richtung Funktionsumfang von a.eins geplant werden. Fokus liegt auf den Bereichen Lead-to-Cash, Procure-to-Pay sowie Service-to-Customer unter Berücksichtigung der bestehenden KI-first Designprinzipien.

## Lead-to-Cash (Ist)

- **Lead-Erfassung & Qualifizierung**: Vertriebsagenten nutzen das integrierte CRM zur Lead-Erfassung; KI-Scoring bewertet Abschlusswahrscheinlichkeit, jedoch ohne automatische Segmentierungslogik nach Branchen.
- **Angebotsmanagement**: Angebotsvorlagen existieren, interaktive Preisleitlinien sind nur teilweise KI-gestützt; Genehmigungsworkflows laufen über statische Regeln.
- **Auftragsabwicklung**: Bestellung wird nach Angebotsannahme manuell in den Auftragsbestand überführt; Fulfillment-Status wird über Eventing aktualisiert, jedoch ohne zentrale SLA-Überwachung.
- **Fakturierung & Erlösbuchung**: Rechnungen entstehen automatisiert auf Basis des Auftrags; Übergabe an Finanzbuchhaltung erfolgt per Batch, Echtzeit-Debitorenbewertung fehlt.
- **Revenue Analytics**: Dashboards liefern Umsatzzahlen in Near-Real-Time, Forecasts basieren auf einfachen Trendmodellen ohne Abgleich mit Supply-Daten.

## Procure-to-Pay (Ist)

- **Bedarfsermittlung**: Einkaufsbedarf wird über Dispositionsregeln aus Lagerbeständen generiert; KI unterstützt Nachschubprognosen, aber ohne dynamische Lieferantenbewertung.
- **Lieferantenauswahl**: Lieferantenstammdaten sind vorhanden, strategische Sourcing-Funktionen (z. B. Auktionen, Scorecards) fehlen.
- **Bestellabwicklung**: Bestellungen werden automatisch erzeugt und an Lieferanten übermittelt; Rahmenverträge werden in separaten Modulen gepflegt, Integration ist rudimentär.
- **Wareneingang & Qualität**: Wareneingänge verbuchen Bestände und lösen Qualitäts-Checklisten aus; Abweichungsmanagement ist größtenteils manuell über Tickets.
- **Rechnungsprüfung & Zahlung**: Dreifachabgleich (Bestellung, Wareneingang, Rechnung) erfolgt teilweise automatisiert; Zahlungsfreigaben folgen starren Limits ohne KI-gestützte Risikoanalyse.

## Service-to-Customer (Ist)

- **Ticket-Erfassung**: Omni-Channel Intake (Portal, E-Mail, API) vorhanden; KI-Klassifizierung für Priorität läuft, jedoch ohne automatische Eskalationsmatrix.
- **Einsatzplanung**: Field-Service-Management nutzt Terminplaner; Disposition basiert auf Verfügbarkeit, nicht auf Kompetenzprofilen oder Routenoptimierung.
- **Serviceausführung**: Mobile App erfasst Checklisten, Materialverbrauch und Kundenunterschrift; Offline-Fähigkeit gegeben, aber keine Echtzeit-Synchronisation mit Ersatzteilbestand.
- **Nachbearbeitung & Billing**: Serviceberichte erzeugen automatisch Folgeaufträge und Rechnungen; Upsell-Empfehlungen sind rudimentär und nicht kontextsensitiv.
- **Feedback & Knowledge Loop**: Kundenfeedback wird gesammelt, doch der Transfer in Self-Service-Wissensartikel oder KI-Modelle erfolgt händisch.

## Querschnittsbeobachtungen

- **Prozessdurchgängigkeit**: Event-getriebene Integrationen existieren, jedoch fehlen Ende-zu-Ende-KPIs mit drill-downfähiger Ursachenanalyse.
- **Datenqualität**: Stammdatenpflege erfolgt teils dezentral; Data Governance ist dokumentiert, aber operative Kontrollen (z. B. Dublettenprüfung) sind punktuell.
- **Mandantenfähigkeit**: Technische Mandantentrennung ist vorbereitet, geschäftliche Parameter (Preislisten, Workflows) werden noch global verwaltet.
- **KI-Nutzung**: KI unterstützt Bewertung und Prognosen, doch Entscheidungslogiken sind selten vollständig eingebettet in autorisierende Workflows.
- **Compliance & Audit**: Audit Trails und Berechtigungstrennung sind vorhanden; Meldepflichten wie InfraStat werden aktuell nicht automatisiert bedient.


