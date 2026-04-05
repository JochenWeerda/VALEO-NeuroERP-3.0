# INT-SG-039 - Superglue Runtime Smoke

## Ziel

Den aktuellen Self-Host-Pfad gegen einen echten lokalen Upstream-Container pruefbar machen.

## Umsetzung

- Compose-Smoke gegen `superglueai/superglue:latest` lokal gefahren
- zwei echte Runtime-Blocker im selben Slice behoben:
  - fehlendes `OPENAI_API_KEY`
  - fehlendes `POSTGRES_SSL=false` fuer lokalen Postgres ohne TLS
- Smoke-Skripte pruefen jetzt Health und optional Tool-Listing

## Ergebnis

Der lokale Runtime-Smoke liefert jetzt reproduzierbar `GET /v1/health` und `GET /v1/tools`.
