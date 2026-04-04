# INT-SG-034 - Superglue Bootstrap

## Ziel

Secret-, Host- und Vault-Mapping fuer die Inbetriebnahme explizit und skriptgestuetzt machen.

## Umsetzung

- `scripts/superglue/bootstrap-secrets.sh`
- `scripts/superglue/bootstrap-secrets.ps1`
- Ausgabe des erwarteten Namespace-, SecretStore-, Host- und Vault-Pfad-Mappings

## Ergebnis

Der produktive Bootstrap-Pfad ist jetzt nachvollziehbar und wiederholbar statt nur als freie Handarbeit dokumentiert.

