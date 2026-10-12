# Bestehenden ERP-Anmeldedienst verbindlich konfigurieren

Stand: 2026-10-12. Teilmeilenstein `IDENTITY-CONTROL-20261012` und
`IDENTITY-PROVIDER-RUNTIME-20261012`.

Der vorhandene Keycloak betreibt den ERP-Realm. Die deklarierte Konfiguration
enthaelt keine Musterbenutzer oder Clientgeheimnisse. Browserclients verlangen
PKCE S256; Passwort- und Implicit-Grants sind deaktiviert. Zugriffstoken laufen
nach 300 Sekunden ab, Provider-Sitzungen nach 900 Sekunden Inaktivitaet oder
28800 Sekunden absolut. Refresh-Token-Wiederverwendung ist deaktiviert.

Die 34 Fachrollen aus `fachrollen.json` stehen im Entwicklungs- und Staging-Export
sowie im laufenden ERP-Realm. `manager` bleibt als ausdrueckliche Rolle erhalten,
weil bestehende Wege sie pruefen; sie wird keinem Benutzer automatisch vergeben.
Fachrollen werden ebenfalls nicht automatisch zugewiesen. Vorhandene Rollen,
Komposite, Benutzer und Zuordnungen bleiben beim erneuten Einrichten erhalten.

`scripts/provision_identity_provider.py` legt fehlende deklarierte Rollen an,
prueft ihr Bestehen und aktualisiert ausschliesslich die eigenen Einstellungen
und Mapper. Clientgeheimnisse und fremde Mapper bleiben im vorhandenen Dienst
erhalten. Die konfigurierte Profilfunktion schuetzt `tenant_id`, `identity_type`
und `erp_scopes` vor Benutzerbearbeitung. Keycloak 22 unterstuetzt die neuere
Option `unmanagedAttributePolicy` noch nicht; ihre Durchsetzung wird fuer diesen
Dienst deshalb nicht behauptet.

Nachweis: neun Konfigurations-/Rollenvertraege bestanden, darunter Erhalt
bestehender Komposite, wiederholte Einrichtung und abgebrochene Einrichtung
bei fehlender Providerbestaetigung. Beide Katalogpruefungen sind gruen. Die
Live-Abfrage bestaetigt 34 Fachrollen, PKCE, deaktivierte Passwort-Grants,
Laufzeiten und administrativen Schutz des Mandantenattributs.

Die ausdruecklich beauftragte erste persoenliche Administratorzuordnung liegt
nur im Provider und der privaten lokalen Ablage. Erstkennwortwechsel und
persoenliche TOTP-Einrichtung sind fuer die erste Anmeldung erforderlich.
Eine vom Benutzer abgeschlossene Anmeldung in der ERP-Maske ist noch nicht
abgenommen. Persoenliche Werte erscheinen weder hier noch in den Exporten.

## Wiederholbare Einrichtung

Das Skript liest technische Providerzugangswerte aus
`VALEO_IDP_ADMIN_USERNAME` und `VALEO_IDP_ADMIN_PASSWORD`; keine Passwoerter
als Kommandozeilenparameter verwenden. Persoenliche Eingaben ueber
`--personal-file` sind nur ausserhalb des Repositorys erlaubt. Ein vorhandenes
Konto wird nur bei uebereinstimmender persoenlicher Definition bearbeitet;
sein Kennwort wird dabei nicht ersetzt. Neue Konten erhalten ein zufaelliges
temporaeres Kennwort und verpflichtende Erstaktionen.

## Weiterhin offen

Die bisherigen technischen Bootstrap-/Datenbankzugangswerte im Entwicklungs-
Compose sind noch abzulösen und privat zu rotieren. Browseranmeldung und
Providerabmeldung, serverseitige Sessions, ausserhalb des ERP geaenderte Rollen,
Agentenmandate, Freigaben und Ressourcenbegrenzung sind eigene Abnahmen.
Administrierte `erp_scopes` sind deklariert; ihre Integration in alle Verbraucher
bleibt im uebergeordneten Claim. Dieser Meilenstein schliesst die Gesamtarchitektur
nicht ab und lockert keine Produktionsauthentifizierung.
