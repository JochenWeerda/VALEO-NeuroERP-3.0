---
title: Art.-33-DSGVO-Meldeentwurf (Vorlage zur DSB-Freigabe)
type: report
audience: [datenschutz, betrieb, lead]
owner: Claude
status: entwurf
last_reviewed: 2026-07-05
version: 1.0.0
description: Fertiger Meldeentwurf nach Art. 33 DSGVO fuer den PII-Vorfall im oeffentlichen Repo — DSB muss nur pruefen, Risiko final bewerten und ggf. absenden.
---

# Meldung einer Verletzung des Schutzes personenbezogener Daten (Art. 33 DSGVO) — ENTWURF

> **Status:** Entwurf zur Freigabe durch den/die Datenschutzbeauftragte(n).
> Dies ist keine Rechtsberatung. Die finale Risikobewertung und die Entscheidung
> ueber die Meldung (Art. 33 Abs. 1 vs. interne Dokumentation nach Abs. 5) trifft der DSB.
> Zustaendige Aufsichtsbehoerde (nach Sitz des Verantwortlichen zu bestaetigen):
> Landesbeauftragte fuer den Datenschutz Niedersachsen (LfD), sofern Sitz Niedersachsen.

## 1. Verantwortlicher

| Feld | Angabe |
|---|---|
| Verantwortlicher | _<Firmenname/Betreiber eintragen>_ |
| Anschrift | _<eintragen>_ |
| DSB (Kontakt) | _<Name, E-Mail, Telefon eintragen>_ |

## 2. Art der Verletzung

Unbeabsichtigte **unbefugte Offenlegung** personenbezogener Daten (Art. 4 Nr. 12 DSGVO)
durch Veroeffentlichung in einem **oeffentlichen GitHub-Repository** des Verantwortlichen.
Keine Fremdeinwirkung/kein Angriff — Ursache war das versehentliche Einchecken von
Lead-Datendateien in ein oeffentlich sichtbares Code-Repository.

## 3. Betroffene Daten und Personen

| Feld | Angabe |
|---|---|
| Datenkategorien | Name, Postleitzahl, Ort, Betrag der GAP-/EU-Agrarfoerderung; in einer historischen Datei zusaetzlich abgeleiteter **Lead-Score** und **Betriebsgroessenschaetzung** (Profilbildung) |
| Betroffenenkategorie | Empfaenger von EU-Agrarfoerderung (Landwirte/Betriebe); mutmasslich ueberwiegend natuerliche Personen (Namen ohne Rechtsformzusatz) |
| Anzahl Betroffene | Im Arbeitsstand zuletzt 30 benannte Personen; in der Git-Historie zusaetzlich bis zu 100 Personen (mit Score/Profil). Rohdatenbasis (nicht im Repo): 15.985 Zeilen — Betroffenenzahl der Rohbasis separat zu klaeren. |
| Datenquelle | Amtliche EU-Agrarfonds-Empfaengerveroeffentlichung (GAP-Zahlungen), gefiltert auf PLZ-Raum 26400–26999 (Ostfriesland) |

## 4. Zeitlicher Ablauf

| Ereignis | Datum |
|---|---|
| Erstmalige Veroeffentlichung im oeffentlichen Repo (Commit) | 2025-11-21 |
| Expositionsdauer | ~7,5 Monate (2025-11-21 bis 2026-07-02/05) |
| Kenntnisnahme durch Verantwortlichen | 2026-07-02 (Verifikations-/Remediation-Lauf) |
| Entfernung aus Arbeitsbaum | 2026-07-02 |
| **Git-History-Purge (Force-Push, alle Branches/Tags)** | **2026-07-05** |

Hinweis zur 72-Stunden-Frist (Art. 33 Abs. 1): Fristbeginn mit Kenntnisnahme (2026-07-02).
Der DSB bewertet, ob eine Meldung erforderlich ist; falls ja, ist die Fristwahrung bzw. eine
Begruendung der Verzoegerung (Art. 33 Abs. 1 S. 2) zu dokumentieren.

## 5. Wahrscheinliche Folgen (Risikoabwaegung — durch DSB zu finalisieren)

- **Risikomindernd:** Die Grunddaten (Name, Ort, Foerderbetrag) waren bereits durch die amtliche
  GAP-Transparenzveroeffentlichung oeffentlich zugaenglich.
- **Risikoerhoehend:** Zusammenfuehrung/Anreicherung zu Vertriebs-Leads inkl. abgeleitetem
  Lead-Score und Betriebsgroessenschaetzung (Profilbildung); zeitlich unbegrenzte Abrufbarkeit
  und maschinelle Weiterverwertbarkeit im Repo; moegliche Forks/Caches Dritter.
- Mögliche Beeintraechtigung: Zweckentfremdung amtlich veroeffentlichter Daten zu
  kommerziellen Vertriebszwecken ohne Rechtsgrundlage/Information der Betroffenen.

## 6. Ergriffene und vorgeschlagene Massnahmen

**Bereits umgesetzt (technisch):**
- Entfernung aller Lead-Daten und Lead-Mining-Skripte aus dem Arbeitsbaum (2026-07-02).
- Vollstaendiger Git-History-Purge via git-filter-repo ueber alle Branches und Tags,
  Force-Push (2026-07-05); Backup-Mirror des Vorzustands gesichert.
- `.gitignore` gehaertet (`*_leads.json`, `ostfriesland_*.json` u. a.); Secret-Scan (gitleaks)
  ohne Baseline als CI-Gate.
- Verifikation: 0 PII-Blobs in Origin-Historie/HEAD nach Purge.

**Noch erforderlich (organisatorisch/extern):**
- **GitHub-Support-Ticket** zur Entfernung gecachter Views/dangling commits (Force-Push
  entfernt nur die Erreichbarkeit; GitHub haelt unreferenzierte Objekte bis zur GC/Ticket vor).
- Pruefung auf **Forks** des Repos und ggf. Kontaktaufnahme.
- Klaerung Verbleib/Loeschung der **Rohdatenbasis** (lokale CSV, nicht im Repo).
- Bewertung Information der Betroffenen nach **Art. 34** (nur bei voraussichtlich hohem Risiko).

## 7. Anlagen / Nachweise

- `artifacts/pii-remediation-report.md` (technischer Befund, Klassifizierung, Scan-Ergebnisse)
- `scripts/purge_pii_history.sh` (Purge-Verfahren) + Ausfuehrungsprotokoll 2026-07-05
- Backup-Mirror des Vorzustands (Aufbewahrung als Nachweis, Zugriff beschraenken)

---
_Erstellt als Entwurf. Freigabe, finale Risikoeinstufung und ggf. Absendung durch den DSB._
