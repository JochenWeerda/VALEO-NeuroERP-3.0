# Abhaengigkeitssicherheit – 21.10.2026

Die neuen Befunde im CI-Nachlauf werden durch offizielle Patchversionen behoben:
follow-redirects 1.16.1, Vite 6.4.4. Der Vite-Override gilt ausschliesslich fuer
betroffene 6.x-Versionen; keine Herabstufung anderer Hauptversionen. Der regulaere
pnpm-Generator aktualisierte den Lock; dessen Paketbestand bleibt bis auf diese
beiden Patchidentitaeten gleich (3012). 36 Workspaces frozen geprueft.

Primaerquellen:
- [Arrayheader](https://github.com/advisories/GHSA-q3jh-wrc6-jgq8)
- [Headernamen](https://github.com/advisories/GHSA-8r9p-f939-6h3c)
- [Editorpfade](https://github.com/advisories/GHSA-587h-7wmj-h5pm)
- [Prozentexpansion](https://github.com/advisories/GHSA-698v-4r3x-3vcv)
- [Editorargumente](https://github.com/advisories/GHSA-r825-w8mm-5pxw)

## Nachweise

Offizielle npm-Tararchive der beiden Redirectversionen per SHA512 verifiziert.
Echte lokale HTTP-Redirects: Original1.16.0 zwei normale Vertraege gruen, drei
Angriffstests rot;1.16.1 alle fuenf gruen. Kein externer HTTP-Testempfaenger.
Der neue Vite-Test prueft die tatsaechlichen gebuendelten Editorfunktionen in
isolierter VM, ohne Shell/Editorstart: Prozentexpansion und Zeilentrenner werden
abgelehnt, relative Namen zu absoluten Pfaden, normale Zeilen-/Spaltenparameter
bleiben erhalten. Fuenf Vertraege gruen. Eine lokale alte Vite-Installation
besass andere Quellgrenzen; deren VM-Abbruch ist kein Angriffsnachweis.

Vollstaendiger Frontendbuild mit separat installierter Vite6.4.4 bestand in
45,47s. Der erste Versuch fand im isolierten Pruefumfeld terser nicht; nach
Leseverknuepfung auf den bereits vorhandenen Komprimierer bestand der Build.
Gemeinsame Installation unveraendert, keine neue Datenbank/Container.

Frischer Production-Audit: null Critical/Moderate/Low, genau zwei High,
node-forge und braces. Fuenf neue Befunde sind entfernt. Beide bestehenden
Quellreparaturen wurden erneut anhand offizieller SHA512-Originalarchive,
59 JS-Dateien, exakten Patch-/Installationshashes und echten Laufzeitvertraegen
geprueft. Originale3 normale Faelle gruen/9 Angriffe rot. Zusammen mit den
fail-closed Auditkontrollen und neuen Vertraegen37/37 gruen. Audit-CLI:
2 source_backported,0 blocked. Rohbefunde bleiben sichtbar.

Reviewhashes sind an den neuen Manifest-/Lockstand gebunden; Abnahme21.10.,
Wiedervorlage28.10. Keine blosse Fristverlaengerung. Kein neuer Advisory-
Ausnahmeeintrag, keine Severity-Absenkung. Der bestehende Audit-CLI-Einstieg
ruft beide neuen Vertraege auf und entfernt deren Testpfad-Overrides zuvor.
Unbekannte Befunde, geaenderte Quellen und abgelaufene Reviews bleiben blockierend.

GitHub-Gesamtnachlauf und Live-Installation sind gesonderte Schritte. Dieses
Ergebnis bescheinigt weder alle Abhaengigkeiten ausserhalb dieses Production-
Scans noch den vollstaendigen Abschluss des Studio-Gesamtziels.


## Nachlauf und getrennte Dependabot-Meldungen

Korrekturen a9f454271 nach main gepusht. GitHub-Nachlauf gestartet, noch keine
Gesamtfreigabe. GitHub-Dependabot-API meldet am21.10. zusaetzlich offene Alerts
in pnpm-lock.yaml: markdown-it692/691/690, sprintf-js677, stream-json666/665,
http-cache-semantics653 sowie den bekannten node-forge651. Ausserdem chromadb
in services/ai/requirements.txt502(Critical),501/500(High), ohne dort angegebene
Patchversion. Diese Meldungen werden durch einen reinen pnpm-Production-Audit
nicht vollstaendig abgedeckt; Abhaengigkeits-/Verbraucherpfade und Python-
Altbestand sind separat zu klaeren. Keine Entwarnung aus einem einzelnen Scan,
keine Alert-Schliessung oder unsicheren Major-Overrides vorgenommen.
