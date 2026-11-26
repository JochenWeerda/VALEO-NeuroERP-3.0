---
title: M7 und M8 - Abhaengigkeiten und Vorarbeiten
type: plan
audience: [entwickler, betrieb, geschaeftsfuehrung]
owner: Claude Code
status: aktiv
last_reviewed: 2026-11-25
version: 1.0.0
description: Welche Lieferungen von M7 (On-Prem-Verkaufsprodukt) und M8 (SaaS) von M6 abhaengen, welche vorher beginnen koennen, Bestand im Repository und naechste Schnitte.
---

# M7 und M8 - Abhaengigkeiten und Vorarbeiten

Grundlage: `docs/roadmap/fahrplan-verkaufsprodukt.md` (M7, M8). Nutzerauftrag 25.11.2026: alle Vorarbeiten beginnen,
die nicht vom Abschluss von M6 abhaengen. Bestand ermittelt aus dem Repository am 25.11.2026.

## 1. M7 Verkaufsprodukt On-Premises

| Lieferung | Haengt an M6? | Bestand | Naechster Schritt |
|---|---|---|---|
| Installationspaket, Update-Verfahren | nein (braucht M5-Betriebsreife) | Produktions-Compose mit Pflichtgeheimnissen (#177), Migrationen per Alembic | Installationsskript aus dem Repo auf leerem Host, als Probe in der CI |
| Installations- und Betriebshandbuch | nein | `docs/admin/backup-restore.md`, Runbooks unter `docs/deployment/` | Handbuch-Gerippe entlang der Neuinstallation |
| Fernwartungskonzept | nein | - | Konzept: Zugang nur auf Anforderung, protokolliert, Agentenmatrix (`docs/security/umgebungen-und-agentenrechte.md`) |
| Modul- und Lizenzsteuerung | nein | `app/core/module_registry.py` (INSTALLED_MODULES, TENANT_MODULE_FLAGS aus der Konfiguration) | Lizenzdatei signiert pruefen statt Konfiguration; keine Lizenzlogik bisher |
| Preismodell | nein, fachlich | - | Geschaeftsfuehrung |
| AVV, TOM, Verarbeitungsverzeichnis, Loeschkonzept | nein | Verarbeitungsverzeichnis als Maske (`pages/compliance/verarbeitungsverzeichnis.tsx`), DSGVO-Loeschung Art. 17 im System, GoBD-Loeschsperren | Loeschkonzept aus den vorhandenen Fristen und Sperren ableiten; AVV/TOM als Entwurf, **rechtliche Pruefung extern** |
| AGB, SLA, Supportprozess | nein, rechtlich | - | Entwurf nur mit rechtlicher Pruefung (extern) |
| Demo-Mandant, Schulungsunterlagen, In-App-Hilfe | nein | Benutzerhandbuch `docs/benutzerhandbuch/`, Mandanten-Anlageweg (M5) | Demo-Mandant mit synthetischen Daten als ein Kommando |
| Lasttest | teilweise - realistische Mengen kommen aus dem Spiegelbetrieb | Artillery entfernt (PR #41) | Lastprofil mit synthetischen Daten; Nachmessung mit Spiegelmengen |
| Barrierefreiheitsbericht | nein | Designregeln WCAG AA (CLAUDE.md), Kontrast-Utilities | Bericht nach BFSG/EN 301 549 aus automatischer Pruefung + Stichproben |
| SBOM | nein | **vorhanden**: CycloneDX in `quality-gate.yml` (Job `sbom`) | dem Installationspaket beilegen |
| Penetrationstest | nein, extern | - | extern beauftragen, sobald STAGING steht |
| **Abnahme** (Installation bei fremdem Betrieb) | **ja** - nach Abloesung von L3 | - | - |

## 2. M8 SaaS

| Lieferung | Haengt an M6? | Bestand | Naechster Schritt |
|---|---|---|---|
| Betrieb auf Helm/ArgoCD | nein | `docs/deployment/gitops/argocd.md`, Helm-Werte unter `docs/deployment/helm/` (Teilbestand) | Chart fuer Backend/Frontend/Worker vervollstaendigen |
| Mandanten-Selbstanlage | nein (baut auf M5-Anlageweg) | Mandanten-Anlageweg M5 | Selbstanlage mit Freigabe durch eine Person |
| Abo-Abrechnung | nein | - | nach Preismodell (M7) |
| Rufbereitschaft | nein, organisatorisch | Ueberwachung/Alarme (M5) | Bereitschaftsplan |
| ISO-27001-Luecken | nein | Geheimnis-Inventar, Agentenmatrix, RLS-Kernel | Lueckenanalyse gegen Annex A |
| **Abnahme** (zweiter Mandant produktiv, Fremdtoken-Probe) | **ja** - braucht produktiven Betrieb | RLS-Fremdmandanten-Proben vorhanden | - |

## 3. Reihenfolge der Vorarbeiten (intern, ohne externe Tore)

1. Loeschkonzept aus vorhandenen Fristen/Sperren (P0-nah: DSGVO).
2. Installationsprobe aus dem Repo (leerer Host, CI) und Handbuch-Gerippe.
3. Demo-Mandant mit synthetischen Daten als ein Kommando.
4. Lizenzpruefung auf dem Modulregister (signierte Lizenzdatei, Default: nur Kernmodule).
5. Helm-Chart vervollstaendigen.

Externe Tore: rechtliche Pruefung (AVV, AGB, SLA), Penetrationstest, Preismodell, STAGING-Host.

## 4. Loeschkonzept - Ausgangslage und Pruefpunkte

Vorhanden: Fristenregeln `app/core/gobd_retention.py` (`build_default_retention_regeln`), DSGVO-Loeschung nach
Art. 17 und Anonymisierung von Klarnamen, GoBD-Loeschsperren, Verarbeitungsverzeichnis mit Loeschfrist je Taetigkeit
(Art. 30), beschlossene Aufbewahrungsfrist fuer Bewerberdaten (kein Standardwert).

**Umgesetzt am 25.11.2026 (Nutzerauftrag "nach geltendem Recht umsetzen"):** Der Katalog
`app/core/gobd_retention.py` ist die einzige Quelle; Finance-Fristberechnung, Standardrichtlinien
(`gobd_aufbewahrungsrichtlinien`, Migration `aufbewahrung_geltendes_recht_20261125`), Mandanten-Governance und
Personalakte folgen ihm. Ratsche: `tests/test_aufbewahrungsfristen_recht.py`.

| Kategorie | Frist | Rechtsgrundlage |
|---|---|---|
| Buecher, Journal, Jahresabschluss, Inventar, Verfahrensdokumentation | 10 Jahre | § 147 Abs. 1 Nr. 1, Abs. 3 AO; § 257 HGB |
| Buchungsbelege, Rechnungen, Gutschriften, Zahlungsbelege, Lohnabrechnungen | 8 Jahre | § 147 Abs. 1 Nr. 4, Abs. 3 AO; § 14b UStG (BEG IV, ab 01.01.2025; Art. 97 § 19a EGAO) |
| Handels- und Geschaeftsbriefe, Vertraege, Reklamationen, Arbeitsvertrag | 6 Jahre | § 147 Abs. 1 Nr. 2, 3, 5 AO; § 257 HGB |
| Lieferscheine ohne Belegfunktion | bis Erhalt/Versand der Rechnung | § 147 Abs. 3 Satz 3, 4 AO |
| Pflanzenschutz-Aufzeichnungen | mind. 3 Jahre | § 11 PflSchG, Art. 67 VO (EG) 1107/2009 |
| Duengungsaufzeichnungen | 7 Jahre | § 10 Abs. 5 DueV |
| Fristbeginn | Schluss des Kalenderjahres | § 147 Abs. 4 AO, § 257 Abs. 5 HGB |
| Ablaufhemmung | solange Festsetzungsfrist offen | § 147 Abs. 3 Satz 5 AO |

Ohne gesetzliche Mindestfrist und deshalb als betriebliche Festlegung gekennzeichnet: Siloreinigung (6 Jahre),
Qualitaetsprotokolle (5 Jahre). Kundenstammdaten haben keine eigene Frist; sie sind zu loeschen, sobald kein Beleg mit
laufender Frist mehr auf sie verweist. Die Archivklassen fuer Workflow-Instanzen (`process_archive_contracts`) sind
keine rechtlichen Dokumentarten und bleiben unveraendert.

**Loeschpruefung (26.11.2026):** `app/services/loeschpruefung.py` bewertet Belege (Docflow) und Journal je Kategorie
nach dem Katalog. Der Bericht zeigt je Kategorie, wie viele Saetze noch aufzubewahren, gesperrt oder loeschbar sind,
mit den IDs der loeschbaren Saetze und ohne Inhalte. Einbezogen sind:

- Lieferscheine ueber die verknuepfte Rechnung, ohne Verknuepfung vorsichtig als Buchungsbeleg,
- aktive Loeschsperren,
- die Ablaufhemmung: ohne Datum der Festsetzungsfrist steht ein Vorbehalt im Bericht, mit Datum ist bis dahin nichts
  loeschbar.

Die Pruefung loescht nichts. Test: `tests/test_loeschpruefung.py`.

Naechster Schritt: ein Loeschlauf mit Freigabe durch eine Person (irreversibel, Agentenmatrix) und Loeschnachweis,
dazu die Datenkategorien ausserhalb von Docflow und Journal (Portal, Personal, Protokolle).
