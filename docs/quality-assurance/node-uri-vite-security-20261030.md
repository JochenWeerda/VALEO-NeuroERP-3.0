# Node-Sicherheitskorrekturen: URI-Decoding und Vite (2026-10-30)

Der Produktionsgraph enthielt `decode-uri-component` 0.5.0 und Vite 6.4.4. Die Hersteller nennen [0.5.1](https://github.com/advisories/GHSA-qr28-fpjm-wq7f) beziehungsweise [6.4.5](https://github.com/advisories/GHSA-8g5g-mxqh-grgj) als behobene Releases. Das Root-Override und Lockfile setzen diese gezielt um. Die Paket-Integritaeten stammen aus der isolierten Registry-Aufloesung aller 36 Workspace-Manifeste; deren pnpm-10-Lock enthielt zusaetzlichen Drift und wurde deshalb nicht als Ganzes uebernommen.

Die beiden neuen Verhaltenspruefungen im bestehenden Security-Einstieg wurden mit isolierten Original- und Herstellerpaketen ausgefuehrt: 0.5.0 ueberschreitet bei den 32000 unterschiedlichen kodierten Folgen des Advisories die Grenze von fuenf Sekunden, 0.5.1 besteht; Vite 6.4.4 liefert `.env?raw` mit Status 200, 6.4.5 verweigert alle drei Advisory-Queryvarianten und liefert eine oeffentliche Datei. Der Testserver bindet ausschliesslich an 127.0.0.1 und wird geschlossen. Keine Scanner-Ausnahme.

Die existierenden Patchdateien fuer braces und deepmerge stimmen mit ihren hinterlegten SHA-256-Werten ueberein; nur Manifest- und Lock-Bindungen wurden aktualisiert. Die bisherige Reviewfrist 2026-10-30 war am 30.10. UTC abgelaufen; die nachfolgend dokumentierte technische Neubewertung ersetzt sie. Frozen-Installation und Produktionsaudit wurden anschliessend im isolierten Vollgraphen wie unten dokumentiert geprueft.

## Erneute technische Review am 30.10.2026

[GitHub hat das braces-Advisory am 23.10. zurueckgezogen](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm), weil es nicht als praktisch ausnutzbar eingestuft wurde. Fuer die defensiv beibehaltene Tiefenbegrenzung ist dort kein Herstellerfix aufgefuehrt. Das [deepmerge-Advisory](https://github.com/advisories/GHSA-gcqx-w48m-w2h4) bleibt aktiv und nennt keinen behobenen Release. Beide bestehenden Reparaturen bleiben vorerst bestehen; die Entscheidung behauptet keine menschliche Pruefung.

Am 30.10. erneute automatische Gegenprobe: braces Original 1/8 bestanden, sieben Tiefenfaelle rot; reparierter Stand 8/8. Deepmerge Original 9/21 bestanden, zwoelf Angriffsfaelle rot; reparierter Stand 21/21. Alle vier braces- und drei deepmerge-Quelldateihashes sowie beide Patchhashes stimmen mit den vorhandenen Review-Eintraegen ueberein. Owner Codex-runtime-security; reviewed_on 2026-10-30, review_by exklusiv 2026-11-06. Diese auf sieben Tage begrenzte Bewertung ersetzt keine erneute Audit-Evidenz.

## Integrationstest

Isolierte pnpm-9.12-Frozen-Installation aller 36 Workspaces erfolgreich; Aufloesung uebersprungen, Lockfile unveraendert. Security-Haupteinstieg 56/56 bestanden. Frischer unveraenderter Produktionsaudit: 0 Advisories und 0 Findings. Strikter Gate: 0 blockiert, release_allowed true; alle Gate-Laufzeitvertraege bestanden, darunter deepmerge 21/21. Diese Pruefung betrifft den isolierten Pruefstand, nicht eine Deployment-Freigabe. Rohbericht und Entscheidung liegen unter artifacts/security-fix-runtime-20261029/audit-uri-vite-20261030.json und decision-uri-vite-20261030.json.
