# CI: Positionen, Verkaufsauftraege und Reklamationen

Stand 2026-10-13. Slices CI-POSITION-SALES-IDENTITY-20261013,
TEST-NUMBERING-FILE-ISOLATION-20261013 und CI-COMPLAINT-ISOLATION-20261013.
Ausgangsbezug: PostgreSQL-CI 38360982633.

## Positionen

Die drei positiven Positions-HTTP-Vertraege sendeten einen dev-token. Sie
verwenden nun RSA-signierte Testtoken mit einem eigenen Mandanten. Der
Produktionsdienst behaelt Middleware, Signatur- und Tenantverifikation;
JWKS-Transport und Sitzungsstore sind ausdruecklich im vorhandenen Probe-Kontext
isoliert. Die DB-Fixture loescht keinen festen gemeinsamen Tenant mehr.
Eigene Tenantdaten und Endpoint-Commits bleiben in Savepoints einer aeusseren
Transaktion; Rollback entfernt die eigenen Wirkungen. Alte/fehlende Tokens
und fremde Tenantheader werden in drei neuen Faellen abgewiesen.

## Verkaufsauftraege

Jeder HTTP-Fall fordert den freigegebenen vorhandenen Pruefstand an. Damit
koennen auch die frueher unmarkierten schreibenden Smokes nicht still auf einer
Entwicklungsdatenbank arbeiten. Die Testidentitaet ist ausdruecklich signiert;
Kunde, Mandant und Belege sind eigene rollback-isolierte Datensaetze.
Keine manuelle DELETE-Bereinigung und kein Skip nach einem HTTP-Fehler.

Die positive Anlage akzeptierte zuvor auch 422. Sie muss nun 201 liefern und
den realen eigenen Kunden verwenden. Ein anschliessender GET prueft den
persistierten Auftrag. Der Nichtgefunden-Test verlangt 404, nicht alternativ
204. Der Maskenkopf-Vertrag prueft weiterhin CRM-Kundenname und Kundennummer.
Drei neue negative Faelle decken fehlende/alte Identitaet und fremden Tenant ab.

Der Nummerngenerator-Unit-Test rief den gemeinsamen JSON-Nummernkreis auf.
Er verwendet nun den echten NumberingService mit einer eigenen temporaeren
Datei. Die positive HTTP-Anlage traegt eine eigene explizite Testbelegnummer,
so dass sie den gemeinsamen Nummernkreis nicht weiterschaltet. Bereits
bestehende Nummernkreisdateien wurden nicht zurueckgesetzt oder entfernt.

## Reklamationen

Die bereits isolierte Miniapp deklarierte noch keinen Testmandanten. Ihre
autouse-Bereinigung konnte zudem vor require_db feste gemeinsame Tenantdaten
loeschen. Diese Bereinigung und die Referenz auf den Kompatibilitaets-Store
sind entfernt. Die Fixture fordert zuerst require_db an und isoliert einen
eigenen Tenant samt Daten in Savepoints und aeusserem Rollback.
Sie deklariert ihre Tenantattrappe nur in der Miniapp; dies ist eine
Fach-/Persistenzabnahme, kein Anmelde- oder Signaturnachweis. Die drei
CRM-/DMS-/SLA-/Auditassertions bleiben erhalten. Aufruferakteure in den
Produktionswegen sind mit dieser Fixtureaenderung nicht sicherheitsgeprueft.

## Nachweis und offene Arbeit

Sechs Dateien zusammen streng: **98 bestanden**, eine Warnung, 44,33 Sekunden.
Darin die drei Fachdateien, unveraenderte Produktionsauth-/RSA-/Tenantvertraege
und die globale Testdatenbankgrenze. Beide DB-URLs auf valeo_probe; Status
vorher gelesen, Revision einkauf_rechnung_steuerschluessel_20261013.
Keine Migration, Ruecksetzung, neue Datenbank oder Container. Log:
artifacts/ci-position-sales-complaint-proof.log.

Sieben zuvor rote Fachfaelle sind damit repariert. Vom Ausgangslauf bleiben
vier Dateien offen: GoBD, beide Feed-Ketten und Logistik (damals zusammen 35
Fehler). Ein neuer vollstaendig gruener GitHub-Lauf wird nicht behauptet.
Prod-Rollen-/Auditakteure, Workflowmandantenmodell, Budgetintegration und
weitere Sicherheitsbefunde der Identity-Elternclaims bleiben getrennt offen.
