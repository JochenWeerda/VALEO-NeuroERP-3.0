# Login-Varianten: reale Browserabnahme und automatische Vertraege

Stand 2026-10-13. Claims LOGIN-VARIANTS, LOGIN-CALLBACK-REENTRANCY,
LOGIN-ROUTE-COLLISION, LOGIN-RUNTIME-ISSUER, LOGIN-TOPBAR-IDENTITY und LOGIN-REFRESH.

## Bestaetigte Fehler und Reparaturen

Der Callback verbrauchte State/PKCE mehrfach durch StrictMode und neue
Hook-Funktionsreferenzen. Die Seite startet den Austausch jetzt einmal je Mount;
Replay-Abweisung im AuthService bleibt unveraendert. Gross-/Kleinschreibungs-
Duplikate der automatisch erzeugten Authrouten trafen den privaten Layoutzweig;
der Generator laesst die kanonischen oeffentlichen Authpfade einmal bestehen.

Das lokale Backend erwartete den internen Docker-Aussteller statt des vom
Browser erreichbaren Ausstellers. Dev-Compose trennt oeffentlichen Issuer und
internen JWKS-Transport. Der bestehende Backenddienst wurde mit einem eigenen
lokalen Uvicorn-Override ohne init_db, Migration oder Schemaaufbau rekonfiguriert.
Healthz antwortete 200; die echte Anmeldung erreichte anschliessend Start.

Die TopBar zeigte einen festen Testadministrator und hatte keinen Logout-Handler.
Sie verwendet jetzt die kanonische Benutzeridentitaet und den zentralen Logout.
Der Browser zeigte die eigene synthetische Kennung; Abmelden kehrte zur Loginseite
zurueck, erneutes SSO verlangte wieder ein Kennwort.

Beide Axios-Clients holen vor dem Transport ein frisches Zugriffstoken. Bei weniger
als 30 Sekunden Restlaufzeit wird die vorhandene Providererneuerung geteilt.
Beim Kaltstart wird ein strukturell gueltiges, aber abgelaufenes Zugriffstoken nicht
freigegeben; der gespeicherte Refresh dient ausschliesslich dem Provideraufruf.
Die Route wartet auf dessen Ergebnis. Ein laufender Refresh kann die erfolgte
Abmeldung wegen der vorhandenen Generationsgrenze nicht rueckgaengig machen.
Das Backend bleibt fuer Signatur, Aussteller, Audience, Rollen und Mandant zustaendig.

## Nachweise

- 30 Frontendfaelle in sechs Dateien bestanden: AuthService, StrictMode-Callback,
  tatsaechliches TanStack-Routing, TopBar, reale Axios-Adapter und Hook-Bootstrap.
  JWTs in UI-Unit-Tests sind synthetisch; dies ist kein Signaturnachweis.
- TypeScript ohne Emit bestanden fuer die Produktquellen einschliesslich Refresh.
- Ein Compose-Konfigurationsvertrag direkt ohne pytest-/DB-Fixtures bestanden.
- Vorheriger Backendnachweis: 124 Faelle bestanden, eine Warnung, 45,45 Sekunden;
  Token-/Mandantenbindung, Sessions, Streams, MCP und Provider-Provisionierung.
  DATABASE_URL und TEST_DATABASE_URL waren auf den vorhandenen valeo_probe gesetzt.
- Reale Browserfaelle: leere/ unbekannte/ falsche Kennwortanmeldung zurueckgewiesen,
  Wiederherstellungsmaske ohne Versand, gueltige Anmeldung bis Start,
  tatsaechliche Identitaet im Menue, Logout und erneute Kennwortanforderung.
- Echte, gesichtete Screenshots im [Handbuch](../benutzerhandbuch/anmeldung-browsernachweis.md).
  Keine persoenliche Administratorkennung, E-Mail, Token oder Kennwoerter versioniert.

## Offen

Realer Ablauf-/Refresh-Recheck bestanden: Providerlaufzeit lesend mit 300
Sekunden bestaetigt; nach mehr als 333 Sekunden erneut geladen, geschuetzter
Arbeitsplatz und dieselbe synthetische Kennung sichtbar, ohne Kennworteingabe.
Die Aufnahme steht im Handbuch. Kennwortwechsel/MFA im Browser, persoenliche Erstanmeldung,
weitere Provider, Dockerfrontend auf Port 3000 und volle GitHub-Abnahme bleiben
offen. Der private ERP-Layoutzweig ist stets durch ProtectedRoute geschuetzt;
VITE_AUTH_REQUIRED erlaubt keinen UI-Bypass mehr. Sechs neue Layoutfaelle fuer
wahr/falsch/fehlendes Flag bestanden zusammen mit sieben Routing- und drei
Bootstrapfaellen (16 bestanden). Die UI-Mockgrenze prueft die Verkabelung; die
Tokenverifikation wird durch Backendvertraege und realen Providerlogin belegt.
Die Produktions-Compose-Ausstellerkonfiguration ist separat zu korrigieren.
Die eigene Providerfixture bleibt fuer die weiteren Browserfaelle lokal erhalten;
keine vorhandenen Benutzer, Rollen oder Realmrichtlinien wurden geaendert.
Keine neuen Datenbanken/Testcontainer, keine Ruecksetzung oder Migration.


## GitHub-Zwischenstand

Meilenstein 2d6a78a63 nach main gepusht und develop nachgezogen. Docs Governance,
Docs Build und Security Agent waren erfolgreich; andere Jobs liefen noch.
PostgreSQL-Lauf 38360982633 ist rot: 90 fehlgeschlagen, 260 bestanden, fuenf
uebersprungen, zwei Fehler. RFQ- und Workflowmeldungen zeigen unter anderem
503 / Identity provider unavailable. Kein Gesamt-CI-Erfolg behauptet; korrekte
Provider-/Testgrenzen innerhalb der bestehenden Identity-Claims bleiben offen.
