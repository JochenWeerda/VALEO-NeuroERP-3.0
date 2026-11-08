---
title: JWT-Vorpruefung vor externer Schluesselladung
type: qa
audience: [entwickler, qa, sicherheit]
owner: Codex
status: active
last_reviewed: 2026-10-15
version: 1.0.0
---

# Ungueltige Bearer-Tokens ohne Anbieterzugriff abweisen

18 wiederholte Recruiting-Authentifizierungsfaelle der Vollsuite meldeten 503 statt 401, sobald der Identitaetsanbieter nicht erreichbar war. Ursache war kein fehlendes Fachrecht: _validate_jwt lud die JWKS vor der lokalen Headerpruefung. Selbst dev-token, kaputte JWT-Kompaktform und nicht unterstuetzte Algorithmen veranlassten damit externen Zugriff.

Die bestehende lokale PyJWT-Headerpruefung und die Allowlist asymmetrischer Algorithmen laufen jetzt vor _get_jwks. Nicht-stringfoermige alg-/kid-Werte werden ebenfalls als ungueltig abgewiesen. Headerdaten erteilen keine Identitaet oder Berechtigung; Signatur, Anbieter, Zielgruppe, Ablauf, Mandant und Sitzung werden weiterhin auf den bestehenden Wegen geprueft. Regulare Tokenform bei echtem Provider-Ausfall liefert weiterhin 503. Ungepruefte Headerinhalte werden in dieser Ablehnungsstelle nicht protokolliert.

## Nachweis

Vorherige echte HTTP-Gegenprobe: sechs Negativfaelle scheitern reproduzierbar, der regulaere Provider-Ausfall besteht. Nachher: alle sieben neuen HTTP-Vertraege plus die vorhandenen Recruiting-Rollen-/Authentifizierungsvertraege bestehen, insgesamt 188 Tests. Providerzugriff wird fuer ungueltige Token ausdruecklich ausgeschlossen; der geschuetzte Handler darf nie erreicht werden. Keine vorgetaeuschte Identitaet wird als signaturgeprueft ausgegeben; Produktionsauth bleibt unveraendert verbindlich.

Die neue isolierte HTTP-Test-App benoetigt weder die Kompatibilitaets-App noch Datenbank-Seeddaten. Entsprechende geerbte Fixturevorbereitungen werden ausschliesslich in diesem Testmodul durch leere Vorbereitungen ersetzt. Lokale Sandbox-Laufzeitblockaden wurden durch regulaere autorisierte Testausfuehrung geloest, nicht durch eine Aenderung der Authpruefung. Keine Datenbank, kein Container, keine Fachdaten angelegt.

Dateibesitz war auf _validate_jwt begrenzt. Der Funktionsblock stimmte vor dem Claim in HEAD und Arbeitskopie ueberein. Fremde andere security.py-Aenderungen bleiben in der gemeinsamen Arbeitskopie erhalten; committet wird ausschliesslich der kanonische HEAD plus dieser Funktionspatch. Die bestehende echte RSA-/JWKS-/HTTP-/WebSocket-Mandantenregression bestand zusaetzlich mit 63 Tests (gueltige Signaturen, Fremdmandanten, Anbieter-/Zielgruppenbindung und Streaminggrenzen).

Lokale Nachweise: artifacts/auth-preflight-before-authorized.txt, auth-preflight-after.txt und auth-preflight-rsa-regression.txt. Neue GitHub-Gesamtabnahme nach Push steht aus. Service-Security besitzt zusaetzlich drei abgelaufene ChromaDB-Serverpfadbewertungen; diese werden hier nicht als geschlossen behauptet.
