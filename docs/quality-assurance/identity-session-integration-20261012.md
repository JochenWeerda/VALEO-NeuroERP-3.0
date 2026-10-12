# Sitzungsgrenze und Browseranmeldung

Stand: 2026-10-12. Teilmeilenstein von `IDENTITY-CONTROL-20261012` und
`IDENTITY-INTEGRATION-REST-20261012`.

Alle geschuetzten Anfragen pruefen den gemeinsamen Sitzungszustand: Idle-Limit,
absolute Laufzeit und Widerruf. Bei Speicherausfall wird der Zugriff verweigert.
Keycloaks `session_state` sowie `sid` verbinden erneuerte JWTs mit derselben
Sitzungssperre. Logout und administrativer Subjektwiderruf enthalten den
verifizierten Urheber im atomar geschriebenen Audit, keine Roh-Token.

WebSockets pruefen auch beim Warten auf Eingaben wiederholt und schliessen nach
Widerruf. SSE prueft vor Fachausgabe und bei Warteunterbrechungen. Standardpoll
ist fuenf Sekunden; ausgehende Daten erhalten keine Sitzung kuenstlich am Leben.
Provider-/Redis-I/O blockiert nicht die Ereignisschleife. Redis-Pools werden
wiederverwendet; reine Kontrollpolls verlaengern die gespeicherte Ablaufzeit nicht.

Der verifizierte interne Kontext enthaelt Subjekt, Mandant, Rollen und Scopes
aus der Anmeldung. Er wird am Ende jeder HTTP-/WS-Anfrage entfernt und in
Arbeits-Threads uebernommen. Seine Textdarstellung zeigt weder Token noch Claims.
Die unbenutzte konkurrierende HS-Authentifizierung `app/auth/dependencies.py`
wurde nach Verbraucherpruefung entfernt. Administrierte `erp_scopes` werden an
der bestehenden OIDC-Scope-Grenze ausgewertet.

Browserclients verwenden PKCE S256 und pruefen State, Nonce, Issuer, Audience und
Ablauf der Anmeldeantwort. Rueckfaelle auf Dev-Token, Standardmandant und offene
Masken bei fehlender OIDC-Konfiguration sind entfernt. Die lokale Entwicklungs-
Vorgabe verweist auf den vorhandenen ERP-Realm; andere Hosts brauchen eine
ausdrueckliche Providerkonfiguration. Die serverseitige Signaturpruefung bleibt
massgeblich. Ein lokales JWT-Decoding ist keine Sicherheitsabnahme.

Logout entfernt lokale Token sofort und wartet auf Sitzungs-/Providerwiderruf.
Ein parallel laufender Refresh kann danach keine Token wieder einsetzen.
Gleichzeitige Refresh-Anfragen werden zusammengefuehrt. Fehler werden ohne
Zugangswerte gemeldet. Eine fehlende Fachrolle beendet keine gueltige Sitzung.

## Nachweise

- 77 Sitzungs-/RSA-/Transport-/Streamvertraege bestanden, darunter offener
  WebSocket nach Widerruf, Keycloak-Refresh nach Logout, Kontextbereinigung,
  parallele Geraete und ungueltige Zeitclaims.
- 14 Browser-Vertraege fuer PKCE, Replay, Nonce, Refresh-/Logout-Rennen sowie
  die bestehenden Mandanten- und Rollenhinweise bestanden.
- Finale TypeScript- und ESLint-Pruefung der Authquellen bestanden.
- Inventare werden aus committed HEAD plus eigenen Quellen isoliert erzeugt.
  Fremde Masken- und Metadatenarbeit bleibt erhalten.

Die gemeinsame Kompatibilitaets-App der Fachtests setzt jetzt auch einen
ausdruecklichen Testnutzer. Claudes Finanzkorrekturen bleiben erhalten. Im
Pruefstand liefen 127 von 130 Nachbarfaellen gruen; der verbliebene lokale
Produktionsimport wurde korrigiert. Zwei Snapshot-Faelle haben eine fehlende
Migration und bleiben gesondert offen. Keine Produktionsauth wurde dafuer gelockert.

## Noch erforderliche Abnahmen

Persoenliche ERP-Erstanmeldung/MFA, Browser-SSO-Abmeldung, externe Provider-
Rollenwechsel, Benutzerabschaltung und kritische erneute Authentifizierung sind
damit noch nicht vollstaendig abgenommen. Agentenmandate, Freigaben und Quoten
werden als naechster Teil an diese Grenze gebunden. Der neue Kontrollcode ist
bis zu seiner eigenen Integrationsabnahme keine abgeschlossene Lieferbehauptung.
Audit-Aufbewahrung/-Integritaet und Sicherung des Redis-Volumes bleiben eigene
Betriebsvertraege. Die gesamte GitHub-CI ist erneut zu pruefen.
