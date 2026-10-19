# Chroma: geaendertes Deployment erneut bewertet

Stand19.10.2026, CHROMA-DEPLOY-REVIEW-20261019.

Service-Security39263582553 blockierte drei bekannte Findings, weil sich der Fingerprint von docker-compose.yml nach der Bewertung vom16.10. geaendert hatte. Dies war eine wirksame Drift-Sperre.

Alle98 Nachweisdateien aus aktuellem Git-HEAD in einen privaten, unveraenderten Pruefexport gelesen und verglichen. Genau eine Datei abweichend: Compose bindet TEST_DATABASE_URL fuer Studio-Simulation und das gesamte config-Verzeichnis schreibgeschuetzt statt einer einzelnen MCP-Datei ein. Kein Chroma-Server, Remote-Client, Server-RBAC-Provider oder Remote-Code-Pfad kommt hinzu. Beide Clientimplementierungen bleiben eingebettet und unveraendert. Die vorhandene Reachability-Kontrolle besteht fuer den gesamten Export.

Am19.10. erneut gelesen: [Code Injection](https://github.com/advisories/GHSA-36p7-vc44-83pf), [Mandantengrenzen](https://github.com/advisories/GHSA-2wm9-hf6c-p5cr), [RBAC-Provider](https://github.com/advisories/GHSA-xph7-9rjv-w5fr). Alle drei Eintraege nennen weiterhin keine gepatchte Version. Die Bewertung bezieht sich ausschliesslich auf die unerreichbaren Server-Angriffspfade dieser Advisories; keine pauschale Aussage zur RAG-Datenisolation.

Neun bestehende Gate-Tests, zwoelf Backend-Evidenztests und drei Embedded-Only-Vertraege bestehen. Negativfaelle sperren unbekannte/abgelaufene Findings, veraenderte/entfernte Quellen und auch nach Hash-Erneuerung hinzugefuegte Remote-/Serverpfade. Bewertung des unveraenderten originalen Linux-pip-audit-Berichts: zuvor drei blockiert, nach erneuter Kontrolle drei nicht erreichbar und null unbewertet. Scannerdatei bytegleich, keine Findings geloescht. Keine neue Ausnahme und keine Ablaufverlaengerung:23.10.2026 bleibt die ausschliessliche Frist. Jede fruehere Evidenzaenderung sperrt erneut. Kein Datenbank-/Container-/Paketwechsel. GitHub-Nachlauf erforderlich; verbleibende Dependabot-/Sonar-/Runtimebefunde separat offen.
