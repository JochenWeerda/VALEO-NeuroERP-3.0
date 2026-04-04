# INT-SG-025 - Superglue K8s Edge

## Ziel

Ingress- und Netzwerkgrenzen fuer den Kubernetes-Pfad festziehen.

## Umsetzung

- `k8s/superglue/ingress.yaml`
- `k8s/superglue/networkpolicy.yaml`
- Helm-Templates fuer Ingress und NetworkPolicy

## Ergebnis

Der K8s-Pfad besitzt jetzt ein explizites Edge-Modell fuer API und MinIO-Konsole sowie Default-Deny-Policies mit kontrolliertem East/West-Traffic.

