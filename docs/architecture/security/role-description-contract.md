# Rollenbeschreibungen als Berechtigungsvertrag

Verbindlicher Nutzerentscheid vom 19.10.2026. Ergaenzt WRITE-AUTH-001 bis 008; kein zweites Rechtesystem.

## Kanonischer Katalog

config/keycloak/fachrollen.json beschreibt vorhandene Fachrollen und unter grundrollen die vorhandenen allgemeinen und historischen Realm-Rollen. Kein Eintrag erteilt eine neue Berechtigung. Jede Rolle hat sieben Pflichtangaben: Zweck, Personenkreis, Geltungsbereich, erlaubte Aktionen, Ausschluesse, zusaetzliche Freigaben und Vergabe-/Entzugsregel.

Die technische Rollenpruefung bleibt in den vorhandenen serverseitigen Domain-Commands und Dependencies. Eine Beschreibung ersetzt weder deren Implementierung noch einen positiven und negativen Berechtigungstest. Technische Administration ersetzt keine fachliche Genehmigung. Leserechte auf personenbezogene, finanzielle und mandantenfremde Daten entstehen nicht durch die Fuehrungsposition.

## Fachliche Leitung im Agrarhandel

Eine Niederlassungsleitung erhaelt eine begruendete Kombination bestehender Fachrollen fuer ihre Aufgaben und ihren autorisierten Umfang. Einkauf, Verkauf, Lager, Agrar, Futtermittel und Finanzbuchhaltung bleiben getrennte Verantwortungen. Eine fachliche ADMIN-Rolle bedeutet keine technische Systemadministration. Loeschrechte beziehen sich ausschliesslich auf fachlich loeschbare Daten; festgeschriebene Belege erfordern Korrektur oder Storno.

Die allgemeine Rolle manager besitzt keine ausreichende Agrarhandelsdefinition. Sie ist eine historische Rolle in Abloesung, darf nicht neu vergeben und nicht pauschal auf weitere Bereiche ausgedehnt werden. finance_manager, inventory_manager und crm_manager sind ebenfalls historische Bezeichnungen; eine automatische Gleichsetzung mit heutigen Fachrollen findet nicht statt. Bestehende Zuweisungen und Verbraucher vor Entzug einzeln pruefen, auf minimal erforderliche Fachrollen umstellen und danach Altrechte entfernen. Es wird kein Live-Konto in diesem Dokumentationsslice veraendert.

## Ausgangsbefund und Durchsetzungsstand

Am Ausgangsstand 3a63b9661 fuehrt app/auth/bereich_roles.py manager ueber _LEITUNG pauschal in Bereichsschreibrechte ein. app/auth/finance_roles.py erlaubt damit unter anderem finance_write und beleg_write. Diese Verwendungen sind Ist-Befunde, keine Genehmigung durch den neuen Vertrag. Der aktive WRITE-ROLES-AREAS-Slice liegt bei Claude; dessen Dateien werden nicht konkurrierend editiert. Die Ueberfuehrung mit Berechtigungs-/Negativtests bleibt zwingende Integrationsarbeit. Auch vorhandene admin-Sonderbehandlungen muessen an den Aktionsvertraegen gemessen werden.

Die gezielte Bestandsaufnahme unter app/auth findet manager in neun Modulen: beleg_roles.py, bereich_roles.py, betrieb_roles.py, deps.py, deps_oidc.py, finance_roles.py, jwt.py, router.py und scopes.py. Darunter sind auch Identitaets-/Scopeprojektionen und Dokumentationsbeispiele; ein Texttreffer allein beweist kein Schreibrecht. Bei der Abloesung sind Tokenprojektion, direkte REST-Dependencies und delegierte Commands gemeinsam zu pruefen.

## Automatischer Nachweis und Grenzen

python scripts/check_fachrollen.py --check prueft Katalogdrift und Pflichtvertraege; --realm prueft zusaetzlich fehlende Realm-Rollen. Beide verweigern fehlende Beschreibungsvertraege. Der Generator erhaelt handgepflegte Vertragsanpassungen; neue Rollen bekommen keinen automatisch genehmigten Vertrag. Der CI-Workflow Role description contracts fuehrt beide Pruefungen und die Negativvertraege aus, ohne Datenbank oder zusaetzliche Pakete.

Das Gate prueft Vollstaendigkeit und Erhalt der Beschreibungen. Es beweist noch keine semantische Gleichheit zwischen allen Endpunkten und den beschriebenen Rechten. Neue oder geaenderte Rollen brauchen weiterhin fachliches Review, konkrete Mandanten-/Objekt-/Aktionspruefungen und serverseitige Negativtests. Die statische Realm-Importdatei erhaelt nur die bereits bestehende, bisher dort fehlende Definition LAGER_BEARBEITEN. Bestehende Realm-Beschreibungen und der laufende Keycloak wurden hier nicht umgeschrieben; deren Beschreibungssynchronisierung ist ein gesonderter Identitaetsintegrationsschritt.

Lokale Abnahme: 12 Tests und 30 Unterfaelle bestanden; Katalogdrift gruen, Realm kennt alle 35 Fachrollen. Keine Datenbank-/Dockerressourcen benoetigt. GitHub-Nachlauf des neuen Workflows ist gesondert zu pruefen.


## Durchsetzung nach dem Ausgangsbefund

MANAGER-ROLE-ENFORCEMENT-20261019 setzt den Ausschluss der historischen allgemeinen Rolle in beiden zentralen Rollen-Guards, Rollen-plus-Scopes und dem internen Aktionsguard durch. Beleg-/Finanzrechte, Scopeprojektionen und generierte Belegmaskenrechte enthalten manager nicht mehr. Sieben direkt pruefende Fachwege wurden zusaetzlich korrigiert. Bestehende Fachrollen und die unveraenderten geprueften Auditclaims bleiben erhalten. Nachweis und Grenzen: docs/quality-assurance/manager-role-retirement-20261019.md.

Die noch vorhandene Nennung in Claudes Bereichslisten gewaehrt ueber die zentrale require_roles-Auswertung keine Berechtigung; die redundante Quelle soll im laufenden Bereichsslice bereinigt werden. Eine Role-Description allein ersetzt weiterhin keinen Domain- oder Objektvertrag. Providerrollout, Sitzungsneuausstellung und unabhaengige fachliche Sichtbarkeitsmodelle werden durch diesen Code-Nachweis nicht als abgenommen dargestellt.
