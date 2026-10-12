---
title: Vorschlag fuer zentrales Identitaets-, Rechte- und Agentenmanagement
type: explanation
audience: [architect, entwickler, agent]
owner: Codex
status: proposed
last_reviewed: 2026-10-12
description: Konsolidiertes Zielbild aus dem Auftraggebervorschlag mit Integrationsfolge und pruefbaren Abnahmekriterien.
---

# Zentrales Identitaets-, Rechte- und Agentenmanagement

**Status: Vorschlag, keine vollstaendige Lieferfreigabe.** Grundlage ist der am
2026-10-12 vom Auftraggeber eingebrachte Entwurf gleichen Titels. Die laufende
Reparatur der Mandantenbindung bleibt beauftragt. Weitergehende Sitzungs-,
Autonomie- und Tarifregeln werden hier als Zielbild beschrieben.

## Architekturgrundsatz

Jeder geschuetzte Zugriff braucht eine gepruefte Identitaet, einen autorisierten
Mandanten, ein Recht fuer die Handlung und das konkrete Fachobjekt sowie einen
zulaessigen Freigabestatus. Die Pruefung gilt gleichermassen fuer Menschen,
Portalnutzer, Integrationen und Agenten, fuer Lesen, Schreiben, Suche, Export,
MCP und laufende Verbindungen. Eine sichtbare Schaltflaeche oder ein breites
Leserecht ersetzt keine serverseitige Objekt- und Mandantenpruefung.

Der bestehende Identity Provider Keycloak bleibt die Anmeldebasis. Keine zweite
Passwortverwaltung und keine neun neuen Container aus den unten genannten
Verantwortlichkeiten ableiten. Vor jeder Implementierung bestehende Komponenten,
Claims und Verbraucher inventarisieren. Fuer den Lieferstand bleiben
[Process Kernel STATUS](../process-kernel/STATUS.md) und
[Active Workboard](../../agent-ops/active-workboard.md) massgeblich.

## Identitaet und Mandantenmitgliedschaft

Menschen erhalten persoenliche Identitaeten. Maschinen erhalten eigene
Serviceidentitaeten mit Eigentuemer, Zweck und begrenzten Werkzeugrechten.
Kein Teilen menschlicher Zugangsdaten, keine Selbstvergabe von Rechten oder
Selbstfreigabe durch Agenten.

Der aktive ERP-Mandant stammt aus der vom Server geprueften Identitaet und einer
administrativ gepflegten Mitgliedschaft. Benutzer duerfen das mandantenbestimmende
Providerattribut nicht selbst aendern. Bei mehreren Mitgliedschaften wird der
Wechsel autorisiert und ein eindeutig gebundener Kontext ausgegeben; Header und
Rumpf allein berechtigen keinen Wechsel. Fehlende oder widerspruechliche Bindung
darf keinen Standardmandanten waehlen. Ein Verzeichnis-Claim wie `tid` ist nicht
automatisch ein ERP-Mandant.

Gemeinsame Stammdaten und Konzernzugriffe brauchen eine ausdrueckliche Policy.
Die Sichtbarkeit eines gemeinsamen Kontenrahmens erteilt kein Aenderungsrecht.
Eine Fremdmandanten-ID in einem Folgeobjekt bleibt unzulaessig, auch wenn die
Hauptanfrage den richtigen Mandanten traegt. Fachlich erlaubte Intercompany-
Beziehungen werden als eigene autorisierte Operation geprueft.

## Rechte, Delegation und Freigaben

Rollen geben Grundrechte; Attribute und Fachobjektregeln begrenzen sie. Fuer
delegierte Agenten gilt die Schnittmenge aus Agentenrechten, aktuellen Rechten
des Auftraggebers, Mandant und Auftragsmandat. Widerruf und Aufgabenende entziehen
die Ausfuehrungsberechtigung. Ein genehmigter Hintergrundjob kann unabhaengig von
der Browseranmeldung laufen, wenn sein eigenes Servicemandat dies ausdruecklich
erlaubt. Ein Logout erteilt diese Erlaubnis nicht automatisch.

| Stufe | Zulaessige Autonomie | Abnahme |
| --- | --- | --- |
| A0 | Beobachten innerhalb erlaubter Daten | Kein Schreibzugriff, keine fremden Daten |
| A1 | Entwuerfe und Vorschlaege | Fachausfuehrung braucht separate Freigabe |
| A2 | Begrenzte Routineaktionen | Policygrenzen, Idempotenz, Nachweis und Stichproben |
| A3 | Aktionen mit hohem Risiko | Menschliche Freigabe vor Ausfuehrung |

Zahlungen, Abschlussfreigaben und kritische Stammdatenoperationen brauchen
fachlich definierte Risikoregeln. Eine zweite Maschinenidentitaet ersetzt nicht
das menschliche Vier-Augen-Prinzip. Freigaben binden Mandant, Aktion, Objekt und
Inhaltsfassung; nach relevanter Aenderung ist eine neue Freigabe erforderlich.
Wiederholte Ausfuehrung darf keine zweite Buchung oder Bestellung erzeugen.

## Sitzungen, Widerruf und Audit

Inaktivitaetssperre, absolute Laufzeit und erneute starke Authentifizierung fuer
kritische Aktionen werden konfigurierbar. Die genannten 15 Minuten und acht
Stunden sind Vorschlagswerte, keine bereits beschlossenen Einstellungen.
Clientseitiges Sperren allein genuegt nicht; der Server prueft Ablauf und
Widerruf. Eine Widerrufsstrategie mit nachgewiesener maximaler Wirklatenz ist
auch fuer Token-Caches, WebSockets und Agentenjobs festzulegen. Ein gueltiges
signiertes JWT allein belegt keinen sofort wirksamen Rechtewiderruf.

Logout und Sperre werden je Geraet beziehungsweise Sitzung behandelt; bereits
korrekt gebuchte Fachvorgaenge werden dadurch nicht rueckgaengig gemacht.
Audit protokolliert geprueften Urheber, Mandant, Auftrag, Aktion, Zeitpunkt,
Freigabe und Ergebnis. Bei Delegation werden Agent und Auftraggeber getrennt
nachgewiesen. Keine Passwoerter, Roh-Token oder unnoetigen Bewerber-/Kundendaten
in Audit oder Fehlermeldungen. Aufbewahrung, Zugriffsschutz und Manipulationsschutz
sind gesondert abzunehmen; ein vorhandenes Log allein ist kein solcher Nachweis.

## Logische Verantwortlichkeiten

| Verantwortung | Aufgabe und Integration |
| --- | --- |
| Identity Provider | Bestehendes Keycloak fuer Anmeldung, SSO und starke Authentifizierung |
| Tenant Resolver | Gepruefte Mitgliedschaft und eindeutiger aktiver Mandant |
| Authorization | Gemeinsame Rollen-, Attribut-, Objekt- und Shared-Data-Regeln |
| Session Management | Ablauf, Sperre und Widerruf fuer jede Zugriffsart |
| Audit | Geschuetzter Nachweis von Identitaet, Auftrag und Wirkung |
| Agent Registry | Eigentuemer, Zweck, Mandat und Abschaltung jeder Maschinenidentitaet |
| Approval | Fachliche Freigabe der konkreten Inhaltsfassung |
| Subscription und Metering | Menschliche Seats, Maschinenkontingente und Verbrauch getrennt |
| Resource Governor | Limits am Scheduler, Model-Gateway und Werkzeugaufruf |

Diese Verantwortlichkeiten koennen vorhandene Module gemeinsam tragen.
Zusaetzliche Dienste erfordern einen belegten Bedarf und eine Architekturentscheidung.

## Effizienz und Kontingente

Aktive menschliche Nutzer, zugelassene Maschinenidentitaeten, parallele Jobs und
Ressourcenverbrauch werden getrennt gezaehlt. Gesperrte historische Nutzer sind
keine aktiven Seats. Portal-Leserechte sind nicht automatisch volle ERP-Lizenzen.
Mehrmandanten-Nutzer und interne Subagenten brauchen eine vertraglich bestimmte
Zuordnung; zehn Subagenten begruenden nicht automatisch zehn neue Lizenzen.
Beispielkontingente und Geldschwellen aus dem Ausgangsentwurf sind unverbindlich.

Limits greifen vor teuren Aufrufen und bei jedem weiteren Ausfuehrungsschritt.
Pro Mandant und Auftrag gelten Laufzeit-, Parallelitaets-, Wiederholungs- und
Kostenbudgets. Abbruch muss Werkzeuge und reservierte Ressourcen freigeben.
Sicherheitsentscheidungen duerfen zur Beschleunigung gecacht werden, sofern
Mandant, Identitaet, Policyfassung und Widerrufsstrategie Teil des Cachevertrags
sind. Keine unbefristeten Rechte-Caches oder unkontrollierten Agentenschleifen.

## Integrationsfolge und noch erforderliche Nachweise

1. **Identitaet und Mandantenbindung:** Provider-Mitgliedschaften, HTTP, MCP,
   Streams, Hintergrundjobs und alle Folgeobjekte inventarisieren. Echte signierte
   Token mit zwei Mandanten pruefen; fremde Header, Pfade, Filter und Rumpffelder
   vor Fachzugriff abweisen. Rollen und erlaubte Shared Data separat testen.
   Laufender Claim: SYSTEM-TENANT-BOUNDARY-20261012. Noch kein Gesamtabschluss.
2. **Sitzung und Audit:** Widerruf unter laufenden Verbindungen, Rechtewechsel,
   erneute Authentifizierung und sichere Urhebernachweise pruefen. Fachaktionen
   duerfen nach Widerruf nicht durch Cache oder Wiederholung weiterlaufen.
3. **Agenten und Freigaben:** Serviceidentitaeten und begrenzte Mandate an vorhandene
   Job-/Approvalwege anbinden. Selbstfreigabe, Mandatsausweitung, doppelte Wirkung
   und Ausfuehrung einer geaenderten freigegebenen Fassung nachweisbar verhindern.
4. **Autonomie und Verbrauch:** Erst nach diesen Abnahmen Routineautonomie und
   Kontingente aktivieren. Last, Fairness, Abschaltung und Kostenobergrenzen messen.

Jeder Schritt bekommt abgegrenzten Dateibesitz, QA-Nachweis und Doku-Update.
Gemeinsamen Pruefstand verwenden; keine Datenbank oder Container pro Test erzeugen.
Gesetzliche Einstufung und konkrete Lizenzbedingungen sind separate Entscheidungen;
dieser technische Vorschlag behauptet dazu keine abgeschlossene Bewertung.
