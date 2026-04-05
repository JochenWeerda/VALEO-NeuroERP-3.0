# INT-SG-038 - Superglue Bootstrap und Provisioning

## Ziel

Pilotadapter und Bootstrap auf echte Tool-/Secret-Pfade des aktuellen Superglue-Servers ziehen.

## Umsetzung

- Document-, Partner- und Customer-Preview-Adapter nutzen jetzt `/v1/tools/.../run`
- Bootstrap-Mapping dokumentiert `authToken`, `openaiApiKey` und `masterEncryptionKey`
- Zielstruktur in `app/integrations/**` um fehlende Paket- und Port-Dateien ergaenzt

## Ergebnis

Die read-only Pilotpfade laufen ueber denselben Upstream-Tool-Mechanismus wie der restliche Superglue-Provider-Pfad.
