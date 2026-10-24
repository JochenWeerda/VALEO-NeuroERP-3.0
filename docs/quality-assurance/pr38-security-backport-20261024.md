# PR38-Sicherheitsnachlauf: gezielte PR39-Übernahme

Stand: 2026-10-24. Dieser Nachlauf übernimmt ausschließlich die bereits geprüften Sicherheitskorrekturen aus `artifacts/security-hotfix-source` in die kanonische PR38-Reparaturansicht. Er ist keine Gesamtfreigabe für PR38 oder den CI-Lauf.

## Übernommener Vertrag

- Root-Override für Fastify und zehn Storybook-Entwicklungsabhängigkeiten im Frontend-Manifest; das Lockfile löst Fastify 5.12.7 und Storybook 8.6.19 auf. Es gab keine pauschale Abhängigkeitsaktualisierung.
- Die zwei zeitlich befristeten Quellcode-Backport-Reviews für `node-forge` und `braces` sind an den exakten Patch, das Root-Manifest und das Lockfile gebunden. Die LF-normalisierten SHA-256-Werte sind `31f326fef44943e7d5277072aef0468ea3a2536cd363f3f7cceaa777f877e128` für `package.json` und `8ada1dec8218efacd72f159428dbb83cb58ed1c0b5dc5c13beda7a07819bca3b` für `pnpm-lock.yaml`; beide stimmen mit `config/security/npm-backport-reviews.json` überein.
- Der AI-Dienst lädt Chroma nicht mehr. Seine bisher simulierten RAG-Antworten werden mit HTTP 503 und `rag_backend_unavailable` abgelehnt. `services/ai/app/services/vector_store.py` wurde entfernt. Die drei abgelaufenen Chroma-Ausnahmen in `config/security/dependency-decisions.json` wurden mit dem PR39-Stand durch eine leere Entscheidungsliste ersetzt. Das betrifft den AI-Dienst; der Chroma-Verbraucher im Hauptbackend ist ein eigener Vertrag.
- Alle 15 übernommenen Dateien stimmen bytegleich mit `artifacts/security-hotfix-source` überein. Alte Chroma-QS-Berichte vom 16. und 19. Oktober dokumentieren frühere Bewertungen und sind keine aktuelle Freigabe des entfernten AI-Verbrauchers.

## Gezielte Prüfung

- AI-/Chroma-Pytest: 7 bestanden, darunter die beibehaltene Backend-Review-Brücke.
- Sicherheits-Triage-Pytest: 23 bestanden.
- Security-Dependency-Gate: 9 Unit-Tests bestanden.
- NPM-Backport-Audit: 15 Node-Tests bestanden, einschließlich negativer Fälle für veränderte Quelle, Lockfile und Manifest.
- Fastify-Header-Vertrag: 2 Node-Tests bestanden. Diese Prüfung nutzte den installierten Paketbestand der separaten PR39-Quelle über `SECURITY_FASTIFY_RUNTIME`; in der PR38-Reparaturansicht ist kein eigener `node_modules`-Baum installiert. Die Aussage ist deshalb auf den übernommenen Quell-/Lockvertrag und diesen geprüften Runtime-Bestand begrenzt.
- AI-Import-Pin-Prüfung: erfolgreich; eine vorhandene optionale `auth_shared`-Warnung bleibt sichtbar.

Keine Testdatenbank oder Container wurden angelegt oder zurückgesetzt. Der abschließende PR38-CI-Lauf muss die übernommene Version im eigenen Installationskontext prüfen.
