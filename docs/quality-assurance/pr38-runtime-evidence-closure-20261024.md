# PR38 Runtime-Evidence-Slice (24.10.2026)

Claim: `STUDIO-CLOSURE-PARALLEL-20261023`, Teil `RUNTIME-EVIDENCE`. Die kanonischen ScreenDefinitions werden vor dem stabilen ID-Snapshot ueber `ensure_stamm_screen_registry()` geladen. Ein isolierter Gate-Aufruf und ein Prozess mit vorab importiertem Stamm-Modul sehen nun dieselben registrierten IDs. Der aktuelle Reparatur-View enthaelt 857 Definitionen; der Bestand wurde fuer die Gate-Zahl nicht gekuerzt.

Die sichtbare Studio-Historie waehlt zur Laufzeit zwischen `platform/studio-history` und `platform/studio-history-diff`. Der Gate-E-Scanner erfasst beide Zweige nur, wenn derselbe `screenId` in `useScreenDefinition` und `useUniversalMaskRuntime` verwendet wird. Die negative Gegenprobe mit abweichender Definition bleibt rot. Es wurde kein unsichtbarer Runtime-Marker hinzugefuegt.

Die Routen `/fibu/anlage/:id` und `/waage/wiegeschein/:id` verwenden bei vorhandener ID jetzt `UniversalNativeDetailPage` mit den kanonischen Definitionen `fibu/anlage` bzw. `waage/wiegeschein`; die Listen-Einstiege ohne ID bleiben erhalten. Die Definitionen lesen `/api/v1/finance/asset-accounting/assets/{entity_id}` bzw. `/api/v1/weighing-tickets/{entity_id}`; entsprechende GET-Endpunkte sind vorhanden. Die Asset-Projektion sowie API-/ScreenDefinition-Vertraege werden von den benachbarten Claims gepflegt.

Pruefbelege im Reparatur-View:

- `native-object-routes.test.tsx`: 3/3 bestanden; Detail-ID und Listen-Fallback werden gerendert.
- `test_made_by_studio_gates.py`: 13/13 bestanden; der Standardlauf endet trotzdem mit Code 1, weil die isolierte Suite nur 43,23 % globale Projektabdeckung statt der konfigurierten 60 % erreicht. Das Coverage-Gate wurde nicht veraendert.
- Gezielter fachlicher Lauf mit `-o addopts=`: 4/4 bestanden, darunter neuer Kalt-/Vorimport-Prozessvergleich und beide Studio-History-Definitionen. Die Option dient allein zur lokalen Einzel-Suite-Abnahme; CI behaelt sein Coverage-Gate.
- Direkte Registry-/Gate-Probe: 857 Definitionen; `fibu/anlage` und `waage/wiegeschein` bestehen Gate E und referenzieren die obigen GET-Wege.

Diese Evidenz belegt Runtime-Verdrahtung, nicht die volle fachliche Paritaet. Insbesondere `/fibu/anlage/neu` zeigt weiterhin den Listen-Fallback statt einer Anlage-Erfassungsmaske. Weitere in Gate E sichtbare, aber fachlich ausgeduennte native Seiten bleiben eigenstaendige Migrationsluecken; ihre Zahl darf nicht durch Marker oder Wrapper reduziert werden.
