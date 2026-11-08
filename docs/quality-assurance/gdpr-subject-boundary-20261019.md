# Datenschutz: Identitaets- und Mandantengrenze

Stand: 19.10.2026. Slice GDPR-SUBJECT-BOUNDARY-20261019.

Export und Portabilitaet erlaubten zuvor andere Nutzer desselben Mandanten; die Auditfolgeabfrage enthielt keinen Mandantenfilter. Der Anonymisierungsweg konnte fremde Profile veraendern und schrieb aufbewahrte Auditnachweise um. Interne Ausnahmeinhalte gelangten in Antworten.

Alle drei Wege verwenden jetzt die gepruefte Identitaet. Die lokale Nutzerkennung wird mit der Providerkennung verknuepft. Selbstzugriff oder die bestehende Adminrolle erlauben Lesen, ausschliesslich im autorisierten Mandanten. Profilanonymisierung verlangt die bestehende Adminrolle. Sie veraendert keine Auditnachweise. Fehlerantworten und Fehlerlogs enthalten keine Eingabewerte oder SQL-Ausnahmeinhalte. Keine neue Rolle, Freischaltung oder Providerkonfiguration.

## Gepruefte Wirkung

- Sechs SQL-/Providerfaelle gegen den unveraenderten alten Router: sechs Fehler.
- Final tests/test_gdpr_api.py, tests/test_gdpr_subject_boundary.py und tests/compliance/test_gdpr.py: 28 bestanden; GDPR-Modul63 Anweisungen, keine ungetestet,100 Prozent bei geforderten80 Prozent. Globale App-Schwelle unveraendert.
- Echter RSA/JWKS-Providerpfad und produktive Bearer-/Mandantenmiddleware. JWKS-Antwort und Redis-Leasepruefung sind im Test kontrolliert; Benutzeridentitaet wird nicht durch Dependency-Override ersetzt.
- Zwei Mandanten, Selbstzugriff ueber abweichende Provider-/Profilkennungen, Fremdzugriff403, fremder Mandant404, falsche Identitaetsheader, fehlende Authentifizierung401. Administrative Profilanonymisierung erhaelt andere Profile und beide Auditnachweise.
- Vorhandener valeo_probe; eigene Daten in aeusserer Transaktion mit Savepoints, abschliessend Rollback. Keine neue Datenbank, Container, Migration oder dauerhafte Testdaten.
- Nur die drei GDPR-OpenAPI-Pfade aus dem Generator auf aktuellen HEAD uebernommen; andere Pfade und Komponenten bleiben erhalten.

## Grenzen und Folgearbeit

Dies ist kein vollstaendiger Datenschutz- oder GoBD-Konformitaetsnachweis. Der Export umfasst lokale Profildaten und hoechstens1000 Auditzeilen; created_entities ist weiterhin keine vollstaendige fachliche Dateninventur. Profilanonymisierung ist keine Loeschung des Providerkontos und kein vollstaendiger Aufbewahrungs-/Betroffenenprozess. CI-COMPLIANCE-REAL bleibt bis zur echten Workflow-, GoBD- und Ergebnisartefaktabnahme offen. Alte Platzhalter und als Erfolg akzeptierte500-Antworten sind aus dem GDPR-Compliance-Test entfernt.
