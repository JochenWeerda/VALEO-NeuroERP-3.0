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

Pruefpunkte - die hinterlegten Fristen weichen vom Rechtsstand ab, den ich kenne. **Vor einer Aenderung durch
Steuerberater bzw. Fachbereich bestaetigen lassen.** Zu lange Aufbewahrung personenbezogener Daten ist ein
DSGVO-Thema, zu kurze ein AO-Thema.

| Regel im Code | Hinterlegt | Abweichung |
|---|---|---|
| `ap_invoice`, `payment_run` (Buchungsbelege) | 10 Jahre | Seit 01.01.2025 (Buerokratieentlastungsgesetz IV) gelten fuer Buchungsbelege nach § 147 Abs. 1 Nr. 4 AO **8 Jahre** (§ 147 Abs. 3 AO); Buecher und Jahresabschluesse bleiben bei 10 |
| alle AO-Fristen | Beginn mit Jahresabschluss, Buchungs- oder Erstellungsdatum | § 147 Abs. 4 AO: Frist beginnt mit dem **Schluss des Kalenderjahres** der Entstehung |
| `psm_protokoll` | 10 Jahre (§ 11 PflSchG) | § 11 PflSchG i. V. m. Art. 67 VO (EG) 1107/2009 verlangt **mindestens 3 Jahre** |
| `duenge_bilanz` | 10 Jahre (§ 10 DueV) | § 10 DueV: Aufzeichnungen **7 Jahre** |
| `reklamation` | 6 Jahre (§ 195 BGB) | § 195 BGB ist die dreijaehrige Verjaehrung; 6 Jahre ergaeben sich aus § 257 HGB (Handelsbriefe) - Rechtsgrundlage klaeren |

Naechster Schritt nach Bestaetigung: Fristen korrigieren (Ratschen-Test gegen die bestaetigte Tabelle), Loeschkonzept
je Datenkategorie (Stammdaten, Belege, Protokolle, Portal, Personal) mit Loeschlauf und Nachweis.
