---
title: M0 Budget-Schema und Freigabegrenzen
owner: Codex
type: reference
status: in Arbeit
last_reviewed: 2026-11-15
---

# Budget-Schema und Freigabegrenzen

## Umsetzung

`domain_finance.budget_plans` und `budget_lines` erhalten Mandantenbindung,
vier aktionsgetrennte RLS-Policies, Indizes und zusammengesetzte Fremdschluessel.
Eine Position referenziert ausschliesslich den eigenen Plan, das eigene aktive,
nicht geloeschte, bebuchbare Konto aus `domain_erp.chart_of_accounts` und optional
die eigene Kostenstelle aus `domain_finance.kostenstellen`. Kein zweiter Konten-
oder Kostenstellenstamm. Betraege muessen endlich sein und in NUMERIC(16,2)
passen; mehr als zwei Nachkommastellen werden nicht still gerundet.

Neue Plaene beginnen ausschliesslich als ENTWURF, auch bei direktem Handleraufruf.
Die bestehende Finanzschreibrolle darf Positionen nur im ENTWURF anlegen oder
aendern. Genehmigung benoetigt weiter finance_admin. Genehmigung und
Positionsmutationen sperren denselben Plan: Nach Genehmigung darf der Inhalt
nicht unter unveraenderter Freigabe weitergeschrieben werden. GENEHMIGT und
GESPERRT ergeben fuer beide Positions-Writes 409. Kein ungepruefter
Wiedereroeffnungsweg. Der Detailweg liefert Positionen bereits; ein zusaetzlicher
Positions-Leseweg ohne Verbraucher wurde nicht eingefuehrt.

Die Budgetliste paginiert mit tenantbezogener Gesamtzahl und stabiler Sortierung.
Nicht verfuegbare Istwerte liefern Rollback und neutralen 503, keinen erfundenen
Nullverbrauch. Eine fehlende Plan-ID ergibt 404.

## Nachweise

- Aktuelle datenbankfreie Budget-/Istwertvertraege: 25 bestanden, ein echter
  PostgreSQL-Vertrag ausdruecklich ausgeschlossen. Enthalten sind vier neue
  Negativfaelle fuer Aenderungen genehmigter/gesperrter Positionen.
- Vor dieser letzten Freigabeverschaerfung bestanden beide neuen DB-Vertraege
  im kombinierten StrictDB-Job 43748281469 auf 4866020db (692 passed / 3 skipped
  insgesamt). Echte eingeschraenkte Rolle valeo_app, RLS, drei getrennte
  Fremdschluessel und eigener Lebenszyklus wurden geprueft.
- Der erweiterte PostgreSQL-Vertrag prueft jetzt zusaetzlich: positive Aenderung
  vor Genehmigung, danach abgewiesenes Ergaenzen und Aendern, unveraenderter Betrag
  und unveraenderte Positionszahl. Dieser erweiterte Nachweis ist noch ausstehend.
- Keine neue Datenbank oder Dockerinstanz pro Test. Die kanonische Pruefhilfe
  rollt alle eigenen Daten und Transaktionen zurueck.

## Grenzen

Die Summary summiert Journalzeilen des Jahres; der Vergleich beruecksichtigt
Konto und Monat, aber noch keine Kostenstelle. Buchungsstatus, Vorzeichen und
Kostenstellenzuordnung benoetigen eine fachliche Harmonisierung. Bestehende
Kostenstellen-Periodenbudgets unter domain_controlling sind keine nachgewiesene
Projektion dieser kontenscharfen Jahresplaene; eine gemeinsame fuehrende
Planungs-/Freigabewahrheit ist damit nicht belegt. Keine fachliche Gesamtfreigabe
oder neue MCP-Schreibfreischaltung daraus ableiten. Browserabnahme und lokale
Bereitstellung dieser Migrationen stehen aus.
