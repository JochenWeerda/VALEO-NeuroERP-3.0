# Historische Managerrolle: zentrale Durchsetzung

Stand: 19.10.2026. Owner Codex. Slice MANAGER-ROLE-ENFORCEMENT-20261019.

## Verbindlicher Vertrag

Die allgemeine Rolle manager ist laut role-description-contract.md keine definierte Agrarhandelsleitung und darf keine eigenstaendigen Fachrechte verleihen. Bestehende Fachrollen bleiben fuehrend; es wird kein zweites Rechtesystem eingefuehrt. Technische Administration und aktive Fachrollen bleiben unveraendert. Keine Live-Rollenzuweisung oder Nutzerloeschung.

## Umsetzung

Die zentrale effektive Rollenmenge schliesst manager aus. Sowohl der regulaere require_roles-Guard als auch die OIDC-Guards fuer Rollen und Rollen-plus-Scopes verwenden diese Auswertung. Verifizierte Originalclaims und Rollenlisten werden nicht veraendert; die Kennung und Herkunft bleiben fuer Audit und Diagnose erhalten.

Belegrechte fuer alle Standardvarianten sowie die Finanzrollenlisten enthalten manager nicht mehr. Auch die alte allgemeine Rollen-zu-Scopes-Projektion gewaehrt damit nichts. Die kanonische Beleg-Scopeprojektion wird automatisch aus den bestehenden Belegrechten abgeleitet und enthaelt manager ebenfalls nicht mehr.

Claudes aktive Bereichsdatei wurde nicht editiert. Deren normale require_roles-Dependencies unterliegen sofort der zentralen Auswertung nach Deployment; manager allein reicht damit auch dort nicht. Der widerspruechliche Eintrag in den Bereichslisten ist anschliessend im zugehoerigen Slice zu entfernen. Ausnahmen EIGENE_DATEN und GERAET werden nicht als normale Fachrollenpruefung ausgegeben und bleiben gesondert zu pruefen.

Der vorhandene Keycloak-Scope-Reconciler entfernt ausschliesslich das verifizierte historische manager-Mapping aus belege:read und belege:write. Andere unbekannte Mappings verweigern den Vorgang vor jeder Entfernung. DELETE-Fehler, fehlende Rollen-ID und nicht persistierte Entfernung sperren. Wiederholung aendert keine aktiven Zuordnungen. Dies wurde ausschliesslich mit einem kontrollierten HTTP-Transport geprueft, ohne Aufruf des laufenden Providers.

## Nachweise

Vor Reparatur schlugen 44 neue Sicherheitsfaelle fehl; elf bestanden bereits. Die Negativfaelle pruefen die synchronen und asynchronen Guards, aktuelle Bereichsdependencies, alle Belegrechte/Varianten, Finanzrechte und Scopeprojektionen. Positive Gegenproben zeigen, dass manager plus eine Fachrolle exakt dieselben Belegrechte wie die Fachrolle allein behaelt. Signierte RSA-Token mit produktiver Bearer- und Mandantenmiddleware pruefen das Verweigern vor Fachzugriff; JWKS und Sitzungslease sind kontrollierte Testgrenzen.

Der erste Regressionslauf nach Kernreparatur bestand mit121 Tests und30 Unterfaellen. Weitere Integration prueft bestehende Belegoperationen gegen den vorhandenen gemeinsamen valeo_probe und Scope-Entfernungsfehler. Keine neue Datenbank, Container, Migration oder pauschale Bereinigung. Eigene Belegtestdaten werden im eigenen Testmandanten entfernt.

## Verbleibende Grenzen

Keine systemweite Vollstaendigkeit fuer direkte Rollenauswertungen ausserhalb dieser Guards behauptet. Insbesondere eigene UI-Listen und Altadapter sind weiterhin gegen den Rollenvertrag zu inventarisieren. Die Rolle selbst bleibt fuer eine nachvollziehbare Umstellung vorhanden; sie wird keinem Konto hier entzogen oder zugewiesen. Bereits ausgestellte Scopeclaims werden durch einen Quellcodecommit nicht neu ausgestellt. Der Reconciler muss im regulaeren Identitaetsrollout angewendet und Sitzungen gemaess Betriebsregel erneuert werden; Domain-Guards muessen auch vorhandene Tokens mit nicht ausreichenden Fachrollen verweigern. Laufende Dienste und GitHub-Nachlauf sind nicht durch lokale Tests abgenommen.

Finaler Integrationslauf: **721 bestanden**, eine bestehende Testclient-Abkuendigungswarnung. Generator der Maskenrechte mit --check gruen. Konkrete verbleibende unabhaengige Auswerter: app/agrar/rations/authz.py, app/domains/inventory/api/inventory_auth.py, app/services/finance_freigabe.py, app/services/recent_documents_service.py, app/policy/router.py, app/api/v1/endpoints/billing_batch.py und kontrolle.py; nicht allein durch die reparierten zentralen Dependencies abgedeckt.
