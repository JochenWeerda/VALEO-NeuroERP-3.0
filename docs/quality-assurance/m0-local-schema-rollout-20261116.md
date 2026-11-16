---
title: M0 lokale Bereitstellung und SSO-Portkonflikt
owner: Codex
type: reference
status: in Arbeit
last_reviewed: 2026-11-16
---

# Lokale Bereitstellung

PR145 ist nach 68 erfolgreichen Checks als a5f60738a nach main gemergt;
develop wurde ohne Force nachgezogen. Die externe Review-Ausnahme betraf kein
Testgate. Backend und Frontend wurden aus dem unveraenderlichen Git-Stand gebaut.

Vor der Schemaumstellung wurden vorhandene Rollen, Revision und Fremdnutzung
lesend geprueft. Vollsicherung: 8467511 Bytes, 9493 validierte Archiveintraege;
Datei/Hash bleiben im privaten ignorierten Betriebsverzeichnis. Die notwendige
administrative Rolle diente ausschliesslich dem vollstaendigen lesenden Backup;
DDL erfolgte als valeo_migrator/valeo_owner. Die fuenf ausschliesslich gemergten
Migrationen bestanden eine aeussere Rollback-Transaktion: Datenpruefsummen,
Struktur, Funktionen, Indizes und Revision in 389 Tabellen der betroffenen
Schemata unveraendert; Sequenzzaehler wurden ausdruecklich nicht verglichen.

Kanonisches Alembic erreichte rohware_schema_canonical_20261115. Alle drei neuen
Tabellen haben RLS und vier aktionsgetrennte Policies; valeo_app hat weder
Superuser noch BYPASSRLS. Nur bestehendes Backend und Frontend wurden ersetzt,
keine Datenbank oder fremden Dienste zurueckgesetzt. Gesundheit200, geschuetzte
Budget-/Rohware-APIs unauthentifiziert401; Loginseiten auf3000/3001 erreichbar.
Keine lokalen Fachtest-Schreibdatensaetze. Browsersteuerung brach die erste
Sichtpruefung wegen unsicherer URL-Erkennung ab; kein erfolgreicher visueller
Anmeldenachweis wurde daraus abgeleitet.

## Nachfolgender SSO-Befund

Der Nutzer meldete Failed to fetch. Direkte Pruefung zeigte auf Windows
localhost:8080 eine Tomcat404 ohne CORS, intern im unveraenderten Keycloak jedoch
Discovery200. Auf dem Windows-Loopback lauscht WSL-Relay spezifisch vor dem
Docker-Wildcardlistener. Keine fremden Prozesse oder globalen WSL-Einstellungen
werden veraendert.

Das lokale Previewprofil veroeffentlicht Keycloak deshalb ausschliesslich an
127.0.0.1:8081 (ueber VALEO_LOCAL_IDENTITY_PORT anpassbar). KC_HOSTNAME_URL,
Backend-OIDC_ISSUER_URL und der oeffentliche Frontend-Discovery-Buildparameter
verwenden denselben Ursprung. Der alte KC_HOSTNAME wird entfernt; der interne
Keycloak-Port bleibt8080. Dockerfile.frontend nimmt nur die zwei oeffentlichen
Providerparameter vor dem Build entgegen, nach der Abhaengigkeitsinstallation.
Kein fest eingebauter Callbackport:3000 und3001 bleiben dynamische Origins.

Zehn gezielte Preview-/Produktionskonfigurationsfaelle bestanden. Die tatsaechlich
aufgeloeste Compose-Konfiguration bestaetigt Portersetzung und gleiche Issuer,
ohne geheime Werte auszugeben. Keycloak speichert bereits in PostgreSQL;
Benutzer, Rollen, Realm und Datenvolumes werden nicht veraendert. Authentifizierung,
Issuer-/Nonce-/Audience-Pruefung und PKCE bleiben bestehen. Die reale neue
Discovery-/CORS-/SSO-Gegenprobe folgt vor Abschluss dieses Nachweises.
