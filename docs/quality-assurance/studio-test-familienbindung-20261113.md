# Maskenfamilien: Versionsbindung im Renderer (13.11.2026)

Der Backend-Vertrag liefert für allgemeine Maskenfamilien `maskVariant`; bisher blieb diese Herkunft im Renderplan unberücksichtigt. Eine reine Versionsänderung traf denselben Cacheeintrag. Der gemeinsame Maskenvertrag validiert jetzt diese Bindung nach dem Familiennamensformat des Backends; `beleg` bleibt dem vorhandenen `documentVariant` vorbehalten, doppelte Bindungen sind ungültig. Der Compiler übernimmt die Herkunft als eigene Kopie und berücksichtigt sie beim Cache. Der Renderer gibt sie in beiden Pfaden über `data-mask-*` aus. Die Angaben beschreiben Herkunft und erteilen keine Freigabe; Hashes werden im Frontend nicht neu berechnet.

Gegenprobe vor der Korrektur: `mask-variant-version.test.tsx` **9 fehlgeschlagen** (Cache, beide Rendererpfade und Validierung). Anschließend gezielt `node node_modules/vitest/vitest.mjs run src/__tests__/render-plan/mask-variant-version.test.tsx src/__tests__/render-plan/document-variant-version.test.tsx --maxWorkers=2` im Verzeichnis `packages/frontend-web` ausgeführt: **2 Dateien, 13 Tests bestanden**. Der direkte lokale Testläufer war nötig, weil der `pnpm`-Starter bei seiner Installation in der Umgebung mit `EPERM` scheiterte. Kein Build und keine Datenbank verwendet.

Der Test belegt keine Backend-Publikation und keine interaktive Browserabnahme. Die Belegbindung bleibt durch ihren bestehenden Test mitgeprüft.

Integrationsnachlauf: Compiler, Overlay, nativer Studio-Import und Waagenliste
bestanden gemeinsam mit 38 Faellen. Die vollstaendige Frontend-Typpruefung
`node --max-old-space-size=4096 node_modules/typescript/bin/tsc --noEmit --project tsconfig.json`
endete mit bestaetigtem Exitcode 0. Die Bindungspruefung verwendet einen kleinen
gemeinsamen Validator; sie fuehrt nicht bei jedem Rendern eine vollstaendige
ScreenDefinition-Validierung aus.
