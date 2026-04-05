# INT-SG-036 - Superglue REST v1

## Ziel

Sync-, Health- und Catalog-Pfade auf den aktuellen `/v1`-REST-Vertrag umstellen.

## Umsetzung

- Tool-Sync liest jetzt `GET /v1/tools`
- Health nutzt `GET /v1/health`
- Tool-Metadaten werden auf den VALEO-Contract mit REST-Quelle und Folder-Metadaten gemappt

## Ergebnis

Provider-Sync und Health-Surface sprechen denselben REST-Vertrag wie der aktuelle Upstream-Server.
