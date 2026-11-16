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
127.0.0.1:18081 (ueber VALEO_LOCAL_IDENTITY_PORT anpassbar). KC_HOSTNAME_URL,
Backend-OIDC_ISSUER_URL und der oeffentliche Frontend-Discovery-Buildparameter
verwenden denselben Ursprung. Der alte KC_HOSTNAME wird entfernt; der interne
Keycloak-Port bleibt8080. Dockerfile.frontend nimmt nur die zwei oeffentlichen
Providerparameter vor dem Build entgegen, nach der Abhaengigkeitsinstallation.
Kein fest eingebauter Callbackport:3000 und3001 bleiben dynamische Origins.

Elf gezielte Preview-/Produktionskonfigurationsfaelle bestanden. Die tatsaechlich
aufgeloeste Compose-Konfiguration bestaetigt Portersetzung und gleiche Issuer,
ohne geheime Werte auszugeben. Keycloak speichert bereits in PostgreSQL;
Benutzer, Rollen, Realm und Datenvolumes werden nicht veraendert. Authentifizierung,
Issuer-/Nonce-/Audience-Pruefung und PKCE bleiben bestehen. Die reale neue
Discovery-/CORS-/SSO-Gegenprobe folgt vor Abschluss dieses Nachweises.

Die zunaechst nur gegen Windows gepruefte Portwahl8081 war innerhalb Docker fuer Redis-Commander reserviert. Der Start scheiterte an dieser Belegung. Der korrigierte Standard18081 ist gegen Windows-Listener, saemtliche vorhandenen Container-Portreservierungen und die anderen Compose-Dienste geprueft. Ein neuer Negativvertrag verhindert kuenftige Kollisionen mit dem Basis-Stack; kein fremder Dienst wird angehalten.


## Betriebsunterbrechung bei SSO-Aktivierung

Der neue Frontend-Build bestand die Vite-Kompilierung. Keycloak meldete nach
der Portumstellung zunaechst healthy; das Backend erreichte innerhalb von
vier Minuten keine erfolgreiche Gesundheit. Danach antwortete die Docker-API
nicht mehr (Zeitlimit und HTTP500); auch die externe Discovery lief ins
Zeitlimit. Das ist kein bestandener SSO-Nachweis.

Der regulaere Docker-Desktop-Neustart scheiterte nach 120 Sekunden am Stoppen
der eigenen Prozesse. Die gezielte Wiederherstellung der Docker-WSL-VM wurde
anschliessend eingeleitet. Keine Volumes, Container oder Datenbanken geloescht,
keine fremde WSL-Distribution beendet. Der Frontend-Imageexport und die
Browsergegenprobe sind vor einem Abschluss nachzuholen. Die neue Konfiguration
ist auf dem Ops-Zweig gespeichert; main/develop bleiben beim abgenommenen
Anwendungsstand a5f60738a, bis der SSO-Nachlauf abgenommen ist.

Wiederherstellungsgrenze: Auch Docker Desktop start --timeout 60 endete mit context deadline exceeded; WSL-Auflistung und gezieltes Beenden der Docker-VM antworteten nicht. Keine weiteren konkurrierenden Neustarts ausloesen. Windows-Neustart erforderlich, anschliessend bestehenden Stack und ausschliesslich den SSO-Frontend-Build aus ddc58d254 vervollstaendigen, danach Browsergegenprobe auf 3000/3001. Kein erfolgreicher SSO-Abschluss behauptet.


## Wiederaufnahme nach Docker-Neustart: SSO abgenommen

Am 16.11.2026 nach dem vom Nutzer ausgefuehrten Neustart antwortet Docker
29.9.3 wieder. Bestehendes Backend und Keycloak sind healthy. Der einzelne
Frontend-Build aus unveraenderlicher Quelle ddc58d254 wurde abgeschlossen und
ausschliesslich der bestehende Frontend-Container ersetzt. Image:
sha256:714148731111e4ac69e0e7319d6de76b39fbe0b51da064f7befa3f7c8bf8a4ac.
Alle drei Dienste sind healthy; keine weitere Migration, kein neuer Container
oder Testpruefstand und keine Benutzer-/Rollenveraenderung.

Direkte Discovery liefert fuer Origin localhost:3000 und localhost:3001 HTTP200,
den Issuer http://localhost:18081/realms/valeo-neuro-erp sowie jeweils den
passenden Access-Control-Allow-Origin. Vier enge Konfigurationsvertraege erneut
bestanden; die frueheren elf schliessen sieben Produktionskonfigurationsfaelle ein.

Reale Browsergegenprobe in zwei frischen Chrome-Kontexten: Loginseite laden,
Discovery im Browser lesen, den echten Knopf Mit SSO anmelden klicken und auf
die sichtbare Keycloak-Benutzerkennung warten. Beide Frontendports bestanden
mit null fehlgeschlagenen Browseranfragen. Screenshots beider Login- und
Providerseiten sowie sso-browser-proof.json liegen im ignorierten lokalen
Betriebsartefaktverzeichnis. Beide Provider-Screenshots visuell geprueft; keine
Zugangsdaten eingegeben oder gespeichert. Das belegt die reparierte
Weiterleitung, nicht eine persoenliche Kennwort-/MFA-Anmeldung.

Die erste Testhilfe las den Discovery-Response erst nach Navigation; Chrome
verwarf diesen Body. Die Hilfe liest ihn nun vorher im echten Browser, ohne
Request-Interception oder Lockerung von CORS/Issuer-Pruefungen. Beide
anschliessenden vollstaendigen Portfaelle bestanden.

Abschliessend: Backend healthz200, Login3000/3001 jeweils200, geschuetzter
Budget-GET weiterhin401 ohne Token. Der lokale SSO-Betriebsblocker ist
geschlossen. Die Anwendungs-/Schemaabnahme a5f60738a bleibt unveraendert; die
Previewkorrektur liegt zur separaten Integration auf dem Ops-Zweig.
