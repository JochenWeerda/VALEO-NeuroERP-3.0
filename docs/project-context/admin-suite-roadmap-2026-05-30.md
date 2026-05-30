# VALEO Admin Suite Roadmap

Stand: `2026-05-30`

## Ziel

Die VALEO Admin Suite wird als gefuehrte Orchestrierungs- und Evidenzschicht unter
`/admin-suite` aufgebaut. Bestehende Admin-, Health-, Migrations-, Integrations-
und Betriebsfunktionen bleiben ihre jeweiligen Sources of Truth.

Die Suite darf keinen produktiven Erfolg behaupten, wenn nur Code, Konfiguration
oder ein simulierter Test vorhanden ist. Externe Abnahmen, Live-Probes und
Restore-Drills werden als eigene Evidenztypen gefuehrt.

## Leitplanken

- Keine parallelen Health-, RBAC-, Connector- oder Device-Welten einfuehren.
- Keine produktiven Secrets im API-Vertrag oder UI anzeigen.
- Jeder Status benoetigt Quelle, Evidenztext und Pruefzeitpunkt.
- `unchecked` ist ein gueltiger und sichtbarer Zustand.
- Schreibende Aktionen werden erst nach lesender Evidenzsicht und Audit-Vertrag
  freigeschaltet.
- Migrationen laufen ueber Staging, Batch-ID, Abnahme und Rollback-Marker.

## Risikobewertung

| Risiko | Auswirkung | Eintritt | Gegenmassnahme | Gate |
|---|---|---|---|---|
| Fake-Gruen durch reine Konfigurationspruefung | Kritisch | Hoch | Konfiguration maximal als `warning`; `ready` erst nach belastbarer Evidenz | Jeder Readiness-Adapter hat Evidenzklasse |
| Doppelte Betriebslogik | Hoch | Mittel | Admin Suite aggregiert bestehende Services; keine zweite Health-Engine | Architekturreview je Adapter |
| Secrets im UI oder Log | Kritisch | Mittel | Nur `gesetzt`, `fehlt`, `ungueltig`; keine Token- oder Credential-Werte | API- und Snapshot-Test |
| Direkter Produktivimport | Kritisch | Mittel | Staging, Dry Run, Batch-ID, Reconciliation und Freigabe erzwingen | Migration-Gate vor Execute |
| Rechteeskalation durch Admin oder Agent | Kritisch | Mittel | Effektive Rechte, SoD, Break-glass Audit und Agentenrollen getrennt modellieren | Security-Gate vor Schreib-UI |
| Hardwarestatus ohne reale Probe | Hoch | Hoch | Registrierung, Heartbeat und UAT-Evidenz getrennt bewerten | Device-Gate je Standort |
| Restore-Simulation als Betriebsnachweis | Kritisch | Mittel | Nur realer Restore-Drill darf `ready` setzen | Restore-Evidence-Gate |
| Konflikte mit Parallelagenten | Hoch | Mittel | Kleine additive Slices, expliziter Dateibesitz, Claim-Commit | Workboard-Validierung |

## Umsetzungsreihenfolge

### Phase 1: Sichtbarkeit und belastbare Statussprache

#### `ADMIN-SUITE-001` - Home und Production Readiness

Ziel:
- `/api/v1/admin-suite/readiness`
- `/admin-suite`
- Kacheln fuer Setup, Migration, Rechte, Connectoren, Hardware, Compliance,
  Backup/Restore und Systemstatus
- Score nur aus bewerteter Evidenz; `unchecked` wird nicht als Erfolg gezaehlt

Risikoanpassung:
- Live-Probes bleiben ausserhalb des initialen GET-Endpunkts, damit ein
  Dashboard-Aufruf keine externen Systeme belastet.
- Bestehende Konfigurationschecks werden als `warning` oder `blocked`
  normalisiert, nicht als produktiver Erfolg.

Gate:
- Backend-Vertragstest
- Frontend-Typecheck
- Routing-Integritaet
- Workboard-Validierung

#### `ADMIN-SUITE-002` - Setup Wizard und persistierte Schritte

Ziel:
- Persistierte Setup-Session pro Tenant
- Schritte: Firma, Standorte, Geschaeftsjahr, Kontenrahmen, Steuern,
  Nummernkreise, Benutzer, Rollen, Geraete, Schnittstellen, Import, Testlauf
- Evidenz und Verantwortlicher pro Schritt

Risikoanpassung:
- Vorhandene Fachmasken werden verlinkt und nicht kopiert.
- Abschlussstatus entsteht nur durch Adapter oder explizite fachliche Abnahme.

Gate:
- Tenant-Isolation
- Resume nach Browser-Neustart
- Keine implizite Freigabe durch Navigation

### Phase 2: Migrationssicherheit

#### `ADMIN-SUITE-003` - Migration Core und L3 Cockpit

Ziel:
- Generisches Quellen-, Batch-, Mapping-, Staging-, Fehler- und
  Reconciliation-Modell
- Bestehenden L3-Importer einbinden
- Dry Run, Mapping-Version, Hash, Batch-ID, Import-Diff und Rollback-Marker

Risikoanpassung:
- Bestehende `l3_staging`- und `app_control.l3_import_runs`-Logik wird
  generalisiert, nicht ersetzt.
- Produktivimport bleibt gesperrt, solange Pflichtabgleiche offen sind.

Gate:
- Idempotente Wiederholung
- Kein Schreiben in Fachtabellen vor Freigabe
- Summenabgleich fuer Anzahl, Salden, OP und Lager

#### `ADMIN-SUITE-004` - CSV und AMIC Source Profiles

Ziel:
- CSV/Excel als zweites produktives Profil
- AMIC/A.eins nach verifiziertem Feldkatalog
- Transformationsbibliothek und Mapping-Vorlagen

Risikoanpassung:
- AMIC folgt erst nach dem generischen Core und einem echten Quellenprofil.
- Unbekannte Felder blockieren den Import statt still verworfen zu werden.

Gate:
- Profilversionierung
- Beispieldaten-UAT
- Fachliche Freigabe der Mapping-Bibliothek

### Phase 3: Governance

#### `ADMIN-SUITE-005` - Security und Agent Governance

Ziel:
- Permission Sets, Rollenmatrix und Benutzerzuordnung
- Mandanten-, Standort- und Lagerfilter
- Effektive-Rechte-Simulation und Rollen-Diff
- SoD-Warnungen, Break-glass Audit, Agentenrollen und Kill Switch

Risikoanpassung:
- Statisches RBAC bleibt bis zur kontrollierten Migration aktiv.
- Agenten erhalten nie mehr Rechte als eine explizite technische Rolle.

Gate:
- Negative Tests fuer Rechteeskalation
- SoD-Regeln fuer Buchen/Freigeben
- Audit-Nachweis fuer Break-glass

### Phase 4: Integrationen und Betrieb

#### `ADMIN-SUITE-006` - Connector Hub

Ziel:
- Katalog fuer Superglue, DMS, FinTS, ELSTER, Fiskaly, DATEV, Webhooks,
  Voice/LLM und weitere Adapter
- Einheitlicher Status-, Test-, Retry- und DLQ-Vertrag
- Credential-Metadaten ohne Secret-Werte

Gate:
- Rate-Limit- und Retry-Verhalten
- Secret-Redaction
- Live-Probe getrennt von Konfigurationsstatus

#### `ADMIN-SUITE-007` - Hardware Center

Ziel:
- Device Registry fuer Waage, Drucker, Scanner, POS/TSE und mobile Geraete
- Standort, Protokoll, Heartbeat, Fehler, Testaktion und Diagnose

Gate:
- Hardware-UAT pro Standort
- Eich-/TSE-Nachweis getrennt vom technischen Heartbeat

#### `ADMIN-SUITE-008` - Backup, Restore, Release und Diagnose

Ziel:
- Sicht auf Backup-Lauf, Restore-Drill, Release-Versionen, Alembic-Stand,
  Jobs und Diagnosepakete

Risikoanpassung:
- Vorhandene Helm-CronJobs sind Grundlage.
- Simulierte Python-Restorepfade sind kein produktiver Nachweis.

Gate:
- Wiederherstellung in isolierter Umgebung
- Nachweis mit Zeitstempel, Artefakt und Ergebnis

#### `ADMIN-SUITE-009` - Compliance Evidence Center

Ziel:
- Read-only Katalog fuer GoBD, DSGVO, POS/TSE, ELSTER, ATLAS, Meldewesen und
  Sanktionspruefung
- Implementierungsstatus, Runtime-Nachweis und externe Freigabe getrennt
  anzeigen
- Bestehende Fachmasken und API-Vertraege als Sources of Truth verlinken

Risikoanpassung:
- Vorhandener Code wird nicht als produktiver Betriebsnachweis gewertet.
- Zertifikate, Behoerdenquittungen, Testate und produktive UATs bleiben
  explizite externe Gates.

Gate:
- Kein implizites `ready` fuer ungepruefte Runtime-Evidenz
- Frontend-Typecheck
- Backend-Vertragstest

## Abhaengigkeiten

| Slice | Abhaengig von |
|---|---|
| `ADMIN-SUITE-001` | keine |
| `ADMIN-SUITE-002` | `ADMIN-SUITE-001` |
| `ADMIN-SUITE-003` | `ADMIN-SUITE-001` |
| `ADMIN-SUITE-004` | `ADMIN-SUITE-003` |
| `ADMIN-SUITE-005` | `ADMIN-SUITE-001` |
| `ADMIN-SUITE-006` | `ADMIN-SUITE-001` |
| `ADMIN-SUITE-007` | `ADMIN-SUITE-001`, optional `ADMIN-SUITE-006` |
| `ADMIN-SUITE-008` | `ADMIN-SUITE-001` |
| `ADMIN-SUITE-009` | `ADMIN-SUITE-001` |

## Naechster konkreter Schritt

Die repo-seitige MVP-Kette `ADMIN-SUITE-001` bis `ADMIN-SUITE-009` ist umgesetzt.
Naechste Ausbauschritte sind bewusst evidenz- oder migrationspflichtig:

- verifizierten AMIC-Feldkatalog und Beispieldaten-UAT bereitstellen
- produktiven L3-Execute-Adapter hinter den Reconciliation-Gates anbinden
- normalisierte Permission Sets, Standort-/Lagerfilter und Break-glass Audit migrieren
- Connector-Retry-/DLQ-Aktionen mit Audit-Vertrag freischalten
- reale Heartbeats, Standort-UAT und Restore-Drill-Evidenz importieren
