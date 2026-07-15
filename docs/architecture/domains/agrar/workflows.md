---
title: Agrar — Workflows
type: explanation
audience: [entwickler, fachlich]
owner: domain/agrar
status: aktiv
last_reviewed: 2026-06-27
version: 1.0.0
---

# Agrar — Workflows

## Fuetterungsberatung

Tiergruppenpflege: berechtigten Betrieb waehlen -> Profil/Leistungsparameter
erfassen -> Revision 1 -> Aenderung mit erwarteter Revision und Pflichtgrund ->
append-only Snapshot. Stale Revisionen liefern 409; fremde Betriebsscope-IDs 404.
Die native ObjectPage zeigt aktuellen Stand und Historie ueber dieselbe
ScreenDefinition-/RenderPlan-Runtime.

Referenzdaten: Naehrstoff oder Einheit ueber den effektiven Katalog lesen ->
Dimension, Bezugsbasis und Herkunft pruefen -> FM/TM-Wert mit explizitem Typ
`quantity` oder `concentration` konvertieren -> erst anschliessend mit expliziter
Praezision und Modus runden. Unpassende Dimensionen sowie TM <= 0 oder > 100
werden vor einer Berechnung abgewiesen.

Futtermittelkatalog: vorhandenen Feed-Kopf suchen/anlegen -> Klassifikation und
Freigabe pflegen -> Referenzwerte mit Einheit/Basis/Herkunft erfassen ->
Lieferprodukt mit Gebinde, Mindestabnahme, Preis und Fracht zuordnen ->
Solveradapter erzeugt den stabilen Rechenvertrag. Kopfupdates erwarten Revision
und Pflichtgrund; Legacy-CRUD laeuft ueber denselben Rollen-/Auditpfad.

Rationslebenszyklus: Gruppe waehlen -> Entwurf im Solver -> unveraenderlichen
Snapshot anlegen -> fachliche Pruefung -> Freigabe -> sofortige oder geplante
Aktivierung -> Fuetterung -> Abloesung/Archivierung. Jede Transition ist rollen-
und tenantgebunden, erwartet den aktuellen Status und erzeugt ein Audit-Ereignis.
Eine neue aktive Version setzt die vorherige Gruppenration auf `retired`; der
Scheduler aktiviert faellige Planungen alle fuenf Minuten.

Vor Review bewertet der Solver-Snapshot jede Komponente gegen vorhandenen Bestand,
Tagesbedarf, verifizierte Analyse und gültigen Preis. Blocker verhindern Freigabe
und Aktivierung; eine begründete Ausnahme wird mit `OVERRIDE:` kenntlich gemacht
und über die normale Lifecycle-Transition auditiert.

Nach Fuetterungsstart werden manuelle, Mischwagen-, Herd- oder Importwerte über
`Gruppe + Tag + Quelle + Quellenreferenz` idempotent gespeichert. Die aktive
Rationsversion liefert den Sollstand. ECM und N-Effizienz werden nur bei
vollständiger Datengrundlage berechnet; Methanschätzungen bleiben gekennzeichnet.

- Ernteannahme → Partie → Settlement: [seq-agrar-settlement.md](../../views/sequences/seq-agrar-settlement.md)
- [Benutzerhandbuch Annahme](../../../benutzerhandbuch/annahme.md)
- Kontrakte / Trocknung / Selbstabrechnung — Process Kernel Agrar-Wellen
- Waage / L3: externe Integration (System Context)
- Herd-Data-Delta-Sync: Verbindung freigeben → täglicher Worker →
  providerneutral normalisieren → idempotent speichern → Fütterungsberatung.
  Gruppenwechsel und Lösch-/Abgangsereignisse werden explizit erhalten;
  Live-Zugriff bleibt ohne Vertrag und Betriebseinwilligung blockiert.

### Futteranalyse und Provenienz

1. Bericht manuell erfassen oder PDF/CSV nebenwirkungsfrei vorprüfen.
2. Material/Feed und Messwerte mit Originaleinheit, Rechenwert, Basis und
   Wertstatus zuordnen.
3. Importierten Originalbeleg revisionssicher im DMS referenzieren.
4. Plausibilität ausführen; Blocker verhindern die Freigabe.
5. Approver aktiviert die Analyse mit Auditgrund. Eine aktive Analyse desselben
   Feed-/Scopes wird atomar `superseded`; bestehende Rationsversionen bleiben
   unverändert.
