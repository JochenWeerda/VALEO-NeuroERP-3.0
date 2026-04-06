# INT-SG-042 - Superglue Dev-Egress

## Ziel

Den lokalen Dev-Smoke ueber den echten `SuperglueClient` ermoeglichen, ohne die produktive SSRF-/Egress-Policy zu lockern.

## Umsetzung

- neues Flag `SUPERGLUE_ALLOW_LOOPBACK_DEV_EGRESS` in `app/core/config.py`
- `outbound_security.py` erlaubt bei explizitem Opt-in nur Loopback (`localhost`, `127.0.0.1`, `::1`)
- `.internal`-, `.local`-Hosts und private IPs bleiben auch mit Override verboten
- `SuperglueClient` nutzt den Override nur bei `DEBUG=true`

## Ergebnis

Lokale In-App-Smokes gegen `http://localhost:3011` laufen jetzt reproduzierbar ueber den echten Client-Pfad, ohne den generellen SSRF-Schutz fuer produktive Umgebungen aufzuweichen.
