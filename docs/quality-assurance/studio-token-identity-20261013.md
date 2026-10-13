---
title: Tokengebundene Studio-Identitaet
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: abgeschlossen
last_reviewed: 2026-10-13
---

# Tokengebundene Studio-Identitaet

## Geschlossene Luecken

Alle Studio-Wege verlangen die bestehende gepruefte Anmeldung. Entwurfsanlage, Aenderung und Review-Einreichung nehmen den Urheber aus get_current_user.sub; X-Actor-ID ist keine API-Abhaengigkeit mehr. Ein fehlender Subject wird abgewiesen statt durch studio-user ersetzt.

Publizieren und Zurueckziehen verlangen die bestehende Rolle admin und den verifizierten Providerclaim identity_type=human, entsprechend der vorhandenen Identitaetsadministration. Dienstkonten, unklassifizierte Identitaeten und Fachadministratoren erhalten dadurch kein Publikationsrecht. Vorschlagen, Validieren und Entwuerfe vorlegen bleiben authentifizierten Mandantenmitgliedern moeglich. Die fachlichen Berechtigungen der referenzierten Commands bleiben unveraendert.

Im Memory- und SQL-Speicher laesst ein Review-Statuswechsel updated_by unveraendert: Es bleibt die Kennung der letzten Inhaltsbearbeitung. Vorher konnte ein anderer Einreicher den Editor ueberschreiben und damit der urspruenglichen Person eine Selbstfreigabe ermoeglichen. Die bestehende Vier-Augen-Pruefung verhindert das jetzt.

## Nachweis

73 Tests bestanden in test_meridian_screen_studio_api.py, test_meridian_screen_studio_persistence.py, test_studio_token_identity.py und test_uix090_studio_validation.py. Ausgefuehrt auf vorhandenem valeo_probe, Revision control_findings_20261013. Geprueft: echte Speicherpersistenz, Mandantentrennung, zwei ausdruecklich verschiedene Testidentitaeten statt Headerwechsel, Header-Spoofing, unbekannter Subject, fehlende Adminrolle, Dienstkonto und Review-Selbstfreigabe.

Die HTTP-Identitaetsdoubles ersetzen ausschliesslich Testanwendungen; dieser Nachweis ersetzt keinen RSA-/Provider-Gesamtnachweis. Produktionsverifikation bleibt get_current_user. Bestehende RSA-/Mandantenvertraege sind separat dokumentiert in finance-test-identity-approval-20261013.md.

Die SQL-Testfixture loescht keine gemeinsamen Studio-Entwuerfe mehr. Sie verwendet eigene Mandantenkennungen und entfernt nur die eigenen Zeilen. Keine neue Datenbank, kein Dockercontainer und kein Reset. Eine redundante, noch laufende Sandbox-Testinstanz wurde nach Pruefung ihres exakten Aufrufs beendet; die vollstaendige 73-Faelle-Abnahme lief erfolgreich.

## Weiter offen

Inhalts-/Versionsbindung zwischen Anzeige, Pruefung und atomarer Veroeffentlichung, dauerhafte Publikationsauditkette, Wiederanlauf/Idempotenz und entsprechender Studio-Frontend-Anmeldewechsel bleiben eigenstaendige Folgeslices. Die urheberfreie Header-Eingabe im bestehenden Frontend erteilt keine Rechte mehr, muss aber aus dem Bedienablauf entfernt werden. Keine Produktivpublikation oder zusaetzliche Rolle fuer eine reale Testkennung durchgefuehrt.

Aktueller Parallelstand: FIN-CONTROL-001 ersetzt die fruehere betragbasierte Freigabepolitik; fremde aeltere generierte Arbeitskopien bleiben geschuetzt. Controller-Rechteprojektion und Konsolidierung mit BELEG-021 werden separat abgenommen.
