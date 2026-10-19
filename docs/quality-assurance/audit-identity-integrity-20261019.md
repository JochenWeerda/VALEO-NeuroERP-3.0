# Audit-Identitaet und gemeinsame Transaktionsgrenzen

Stand: 19.10.2026. Owner: Codex. Slice AUDIT-IDENTITY-INTEGRITY-20261019, erster Integrationsmeilenstein.

## Befund und Umsetzung

Das migrationsbasierte Pruefstandschema besitzt keinen Fremdschluessel von audit_logs.user_id auf users. Die ORM-Metadaten folgen nun diesem Schema. Die Entwicklungsdatenbank wurde weder migriert noch veraendert.

HTTP-Audit uebernimmt die vollstaendige gepruefte Tokenkennung; explizite Urheberparameter koennen sie nicht ersetzen. Fehlende Identitaet wird abgewiesen. Nur interne Aufrufe ohne HTTP-Request behalten die explizite Systemkennung. Erforderliche Persistenzfehler werden generisch weitergegeben und zurueckgerollt; SQL und Eingabewerte werden nicht protokolliert.

Attestierungen behalten ihren Nutzer-Fremdschluessel. Die Aufloesung erfordert genau ein aktives Profil desselben Mandanten anhand lokaler Kennung oder keycloak_id. Fehlende, fremde und mehrdeutige Zuordnungen sind verboten. Der urspruengliche Subject und Issuer bleiben zusaetzlich in changes.actor erhalten. Verzeichnisfehler werden nicht durch einen Systemnutzer verdeckt.

Kontenplan anlegen/aendern/deaktivieren und Periode anlegen/aendern flushen die Fachmutation vor dem erforderlichen Audit; erst dessen erfolgreicher Abschluss committet beide. Der zentrale Helfer bietet commit=False fuer weitere explizite Transaktionsbesitzer.

## Pruefung

Tests verwenden ausschliesslich den bestehenden valeo_probe. Neue SQL-Vertraege isolieren eigene Daten ueber eine aeussere Rollbacktransaktion. Signierte Tokens, kontrollierte JWKS und die produktive Bearer-/Mandantenpruefung pruefen die neue Identitaetsgrenze. Bestehende Mini-App-Vertraege erhalten ihre synthetische Identitaet ausschliesslich in der dokumentierten Testgrenze.

Echte Audit-Persistenzfehler werden durch einen unzulaessigen action-Wert beim Flush ausgeloest. Alle fuenf Fachmutationen muessen dabei unveraendert bleiben; positive Gegenproben muessen genau einen korrekt zugeordneten Audit-Eintrag erzeugen. Attestierungsfaelle pruefen lange Kennungen, Fremdmandanten, Mehrdeutigkeit, fehlende Identitaet und echte SQL-Fehler.

## Verbleibende Grenzen

Dieser Meilenstein belegt keine systemweite gemeinsame Transaktion. Journal-, Beleg-, OP- und Connectorwege mit vorangehenden eigenen Commits benoetigen weitere Integration. Eine nachtraegliche Auditfehlermeldung allein kann eine bereits committete Mutation nicht zurueckrollen. Die physische Entwicklungs-Schemadrift bleibt bis zu einem koordinierten Wartungsfenster bestehen.

Ergebnis des gemeinsamen Regressionslaufs: **87 bestanden**, eine bestehende Starlette-Testclient-Abkuendigungswarnung. Lokal: artifacts/audit-integrity-regression-final.txt.
