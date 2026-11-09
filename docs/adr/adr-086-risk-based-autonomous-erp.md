# ADR-086: Risk-based Autonomous ERP - Agent Trust & Autonomy Engine

## Status

**Vorgeschlagen - fachliche Freigabe ausstehend.** Version 1.0.0 der Autonomiepolitik
(`config/agent_autonomy_policy.yaml`). Technisch umgesetzt und getestet, aber **nicht wirksam**: Solange die
Fassung fuer einen Mandanten nicht fachlich freigegeben ist, bucht kein Agent autonom; es gilt der bisherige Weg
(Agent schlaegt vor, ein Mensch gibt frei). Die Freigabe erteilt je Mandant eine Person mit Freigaberolle
(`GESCHAEFTSFUEHRUNG` oder `FINANCE_ADMIN`), nicht die Autorin, kein Agent, kein technisches Konto
(`POST /api/v1/agenten/autonomie/politik/actions/freigeben`). Sie gilt genau fuer den Inhaltsabdruck dieser Fassung.

## Verhaeltnis zu FIN-CONTROL-001 und APPROVAL-001

**Beide bleiben unveraendert.** Diese Entscheidung setzt auf der zentralen Risiko-Engine auf und kann keine ihrer
Entscheidungen lockern:

* Die Risiko-Engine (`app/core/freigabe.py`, `app/services/freigabe_engine.py`) bewertet jeden Vorgang nach Risiko,
  nicht nach Identitaet. Was sie fuer einen Menschen als Routine einstuft, ist es auch fuer einen Agenten; was einen
  kritischen Befund hat oder R3/R4 verlangt, braucht fuer beide eine unabhaengige Freigabe.
* Funktionstrennung und "ein technisches Konto entscheidet nie" (`technisches_konto`) gelten weiter. Ein Agent gibt
  nie frei - weder eigene noch fremde Vorschlaege, weder Politik noch Delegation.
* Die Buchung selbst laeuft ueber denselben Weg wie die eines Menschen (`DocflowService.post_document`), der die
  Risiko-Engine noch einmal fragt. Selbst ein Fehler in der Autonomieentscheidung kann eine verlangte Freigabe nicht
  umgehen.

Neu ist allein: Wo FIN-CONTROL-001 einem Menschen erlaubt, Routine ohne zweite Person zu buchen, darf das unter den
Bedingungen dieser Politik auch ein Agent, dem ein Mensch die Faehigkeit ausdruecklich delegiert hat.

## Kontext

Bis jetzt durfte ein Agent eine Gutschrift nur vorschlagen; jede Buchung brauchte die Freigabe eines Menschen - auch
die Routinegutschrift, die ein Sachbearbeiter nach FIN-CONTROL-001 selbst gebucht haette. Das behandelte Agenten
anders als Menschen, nicht wegen des Risikos, sondern wegen der Identitaet. Ziel: maximale sichere Automatisierung,
minimale unnoetige menschliche Eingriffe, nachweisbar bessere Prozessqualitaet.

## Entscheidung

### 1. Autonomie nur, wenn alles zutrifft (`app/services/agent_autonomie.py::entscheide`)

1. **Politik fachlich freigegeben** - genau diese Fassung (Abdruck) fuer diesen Mandanten.
2. **Ausdruecklich delegiert** - ein Mensch delegiert dem Agenten eine Faehigkeit; er muss das Recht selbst haben
   (keine Rechteausweitung), begrenzt durch Betrag, Ablauf und jederzeit widerrufbar. Nie an sich selbst.
3. **Qualitaet im Rahmen** - siehe 2.
4. **Deterministische Fach- und Sicherheitspruefungen bestanden** (z. B. Steuerschluessel, Konten, Betrag).
5. **Die Risiko-Engine verlangt keine unabhaengige Freigabe.**
6. **Kein Einwand eines Pruefagenten** - siehe 3.

Sonst: kein autonomer Vorgang, sondern der bisherige Vorschlagsweg. Jede Entscheidung - auch jede abgelehnte - steht
unveraenderlich in `domain_shared.agent_autonomy_decisions` (Politikversion, Abdruck, Risiko, Gruende).

### 2. Agent Trust: messbares Qualitaetsmodell (`qualitaet`, `vertrauen`)

Messpunkte je Agent und Faehigkeit in `domain_shared.agent_quality_events` (unveraenderlich): ausgefuehrt,
korrigiert (nur eine Person stellt das fest), Befund der Kontroll-Engine, Einwand eines Pruefagenten, abgelehnt,
Testnachweis bestanden/fehlgeschlagen (CI oder Person - nie der Agent selbst). Daraus im Beobachtungsfenster:
Fehlerquote, Befundquote, Einwandquote, Alter und Ergebnis des letzten Testnachweises. Grenzen stehen je Faehigkeit
in der Politik; in der Startphase (wenige Vorgaenge) zaehlen absolute Fehler.

**Automatische Ruecknahme:** Verlaesst ein Agent den Rahmen (Quote ueberschritten, Test fehlgeschlagen oder
veraltet), wird seine Delegation entzogen (`revoked_by = qualitaetsmodell`) und der Controller-Pruefkorb erhaelt einen
Befund. Wieder autonom wird er nur durch eine neue Delegation eines Menschen.

**Vertrauensstufe** (aus dem Zielbild Identitaet/Agenten): A0 beobachten (nichts freigegeben oder delegiert), A1
vorschlagen (delegiert, Qualitaet nicht im Rahmen), A2 begrenzt autonom. A3 "nur mit menschlicher Freigabe" ist keine
Stufe, die ein Agent erreicht - sie beschreibt Vorgaenge, die immer einen Menschen brauchen. Die Stufe wird
abgeleitet, nie gesetzt (`GET /api/v1/agenten/autonomie/vertrauen`).

### 3. Unabhaengige Pruefagenten (optional, `app/services/agent_pruefagenten.py`)

Je Faehigkeit nennt die Politik Pruefagenten. Ein Pruefagent hat eine eigene Kennung, prueft keinen eigenen Vorgang
und kann **nur Einwaende** erheben; ein Einwand fuehrt zum Menschen und zaehlt im Qualitaetsmodell. Faellt ein
Pruefagent aus, ist das ein Einwand (fail-closed), nie Zustimmung. Registriert ist ein deterministischer
Plausibilitaetspruefer (Bezugsrechnung vorhanden, Gutschriften uebersteigen die Rechnung nicht). Ein KI-Pruefagent
(Sprachmodell mit eigener Maschinenidentitaet) schliesst sich ueber `registriere` mit derselben Schnittstelle an.

### 4. Lernende Autonomie-Governance (`lernvorschlaege`)

Die Governance lernt, die Politik nicht. Aus Bilanz und Entscheidungsprotokoll entstehen Vorschlaege mit Belegen:
**erweitern** (lange fehlerfreie Bilanz), **einschraenken** (Fehler, Befunde, Einwaende), **pruefen** (viele Vorgaenge
nur wegen der Politikgrenze an Menschen). Kein Vorschlag wirkt selbst: Er wird als neue Fassung der Politik
geschrieben und braucht eine neue fachliche Freigabe (`GET /api/v1/agenten/autonomie/lernvorschlaege`). So bleibt jede
Ausweitung der Autonomie eine menschliche, dokumentierte Entscheidung - und jede Einschraenkung kann sofort durch
Widerruf der Delegation oder Politik wirken.

### 5. Durchsetzung an genau einer Stelle: das Tor in der Freigabe-Engine

Pruefung vom 09.11.2026 (Auftrag: "konsequente Durchsetzung durch die zentrale Policy Engine"). Befund im ersten
Stand: Entschieden wurde nur im MCP-Werkzeug `sales.gutschrift.buchen`. Ein Agententoken mit Buchungsrolle haette ueber
`POST /api/v1/docflow/{id}/post` (oder jeden anderen Buchungsweg) gebucht, ohne Politik, Delegation, Vertrauensstufe
und Qualitaetsmodell - die Risiko-Engine allein haette die Routine erlaubt. Die Maskenaktionen der Belegmaske waren
fuer Agenten gesperrt (`adapter_nur_mensch`), der REST-Weg nicht.

Behoben: `agent_autonomie.tor` wird von `FreigabeEngine.verlange_fuer` gerufen, die jeder freigaberelevante Vorgang
jedes Bereichs passiert (DocFlow, Eingangsrechnung, Hauptbuch, Zahlungslauf, Einkaufsbelege) - gleich ob REST, Maske,
CLI, MCP oder Kernel.

* **Wer handelt:** Ein Agent wird am MCP-Werkzeugkontext (jeder Werkzeugaufruf, ausser die Identitaet weist einen
  Menschen aus) oder an seinem Token (`identity_type=agent`, `agent_id`, `act`) erkannt. Menschen: unveraendert.
* **Routine (Risiko-Engine ohne Freigabebedarf):** Der Agent braucht Stufe A2 fuer die Faehigkeit der Belegart und
  Aktion, Grenzen und keinen Pruefagenten-Einwand. **Belegart/Aktion ohne Faehigkeit in der Politik: kein Agent
  fuehrt aus (fail-closed).**
* **Kritisch (R3/R4):** wie bisher - die Engine verlangt und verbraucht die Freigabe einer unabhaengigen Person.
* **Einzelfreigabe:** Ein von einem Menschen freigegebener Vorschlag (`menschlich_freigegeben`) ist kein
  Autonomiefall.
* **Eine Quelle:** Vertrauensstufe (`vertrauen`) und Durchsetzung (`entscheide`) lesen dieselben Voraussetzungen
  (`a2_gruende`); angezeigte Stufe und Entscheidung koennen nicht auseinanderlaufen (Test).
* **Protokoll:** Eine Ablehnung wird ueber eine eigene Verbindung protokolliert und bleibt, auch wenn das Kommando
  zurueckrollt; eine autonome Ausfuehrung steht mit Messpunkt in derselben Transaktion wie die Buchung.

### 6. Erste Faehigkeit: `sales.gutschrift.buchen`

`sales.gutschrift.buchen` mit `credit_note_id` bucht autonom, wenn die Entscheidung "autonom" lautet; sonst 409 mit
den Gruenden. Mit `proposal_id` bleibt der Weg aus menschlich freigegebenem Vorschlag unveraendert. Startwerte der
Politik: Hoechstbetrag 1.000 EUR brutto je Gutschrift (wie die Gutschriftgrenze der Risiko-Engine), Fehlerquote 2 %,
Befund- und Einwandquote 10 %, Testnachweis hoechstens 30 Tage alt. **Die Werte sind Startwerte, keine
Risikopolitik** - sie werden mit der fachlichen Freigabe bestaetigt oder angepasst.

## Folgen

* Routinegutschriften bucht ein delegierter Agent ohne Wartezeit; Menschen sehen Ausnahmen statt jeder Buchung.
* Messbar: Fehler-, Befund- und Einwandquote je Agent, Entscheidungsprotokoll je Vorgang, Pruefkorb-Befunde bei
  Entzug. Nachweis besserer Prozessqualitaet: Korrekturquote autonomer Buchungen gegen den Vorschlagsweg (Folgearbeit:
  Korrekturen menschlicher Buchungen mit derselben Kennzahl erfassen).
* Weitere Faehigkeiten (z. B. Eingangsrechnung, Zahlungsabgleich) schliessen sich je mit eigener Politikfassung an.
* Offen: Studio-Masken fuer Politikfreigabe, Delegationen und Qualitaetsbild (bis dahin REST/CLI/MCP-Lesewege).

## Nachweis

`tests/test_agent_autonomie.py` (gegen die echte Datenbank): ohne Freigabe keine Autonomie; Regeln der
Politikfreigabe (Rolle, Person, nicht die Autorin); geaenderte Fassung nicht freigegeben; Delegation nur des eigenen
Rechts unter der Politikgrenze; Routinegutschrift autonom mit Protokoll und genau einer Buchung; Grenze, Risiko-Engine
und Pruefagent fuehren zum Menschen; ausgefallener oder befangener Pruefagent ist ein Einwand; Korrekturen und
fehlgeschlagene Tests entziehen die Delegation; kein Agent bewertet sich selbst; Protokoll unveraenderlich;
Vertrauensstufe; Lernvorschlaege aendern die Politik nicht; der direkte Buchungsweg (ohne MCP) fragt das Tor; ohne
Faehigkeit bucht kein Agent und die Ablehnung bleibt protokolliert; ein Mensch bucht wie bisher; ein freigegebener
Vorschlag ist kein Autonomiefall; angezeigte Stufe und Durchsetzung stimmen ueberein; Agentenerkennung am Token.
