# DOM-DOC-003 - Nachweis und Rueckmeldung

## Ziel

Nachweis-, Bescheid-, Artefakt- und Rueckmeldungskette ueber Dokumente, Meldungen und Vorgangskontext vereinheitlichen.

## Scope

- Dokumentenablage und objektnahe Dokumentpfade
- Compliance- und Meldewesen-Rueckmeldungen
- Bescheid-, Artefakt- und Fehlerstatus
- Wiedervorlage und revisionsrelevante Nachweiskette

## Dateibesitz

- `packages/frontend-web/src/pages/dokumente/*`
- `packages/frontend-web/src/pages/compliance/*`
- `packages/frontend-web/src/pages/fibu/atlas.tsx`
- `packages/frontend-web/src/pages/compliance/meldewesen-konsole.tsx`

## Abnahmekriterien

- Dokumente und Meldungen zeigen revisionsrelevanten Nachweisstatus, Rueckmeldungspfad und Wiedervorlage konsistent.
- Externe Rueckmeldungen erscheinen direkt am fachlichen Vorgang.
- Artefakte und Bescheide werden nicht nur abgelegt, sondern fachlich eingeordnet.

## Risiken

- externer Rueckmeldepfad ist teilweise ops- und systemabhaengig
- Dokumentstatus und Vorgangsstatus koennen semantisch auseinanderlaufen
- Gefahr von Informationsueberladung in Dokumentmasken
