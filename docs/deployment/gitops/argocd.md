# ArgoCD / GitOps Integration

## Zielbild
- App-of-Apps mit Root-Application in Namespace `argocd`
- Child-Application deployt Plattform-Ressourcen aus `k8s/base`
- Auto-Sync mit `prune` + `selfHeal`

## Dateien
- `k8s/argocd/project.yaml`
- `k8s/argocd/root-application.yaml`
- `k8s/argocd/apps/valeo-platform.yaml`
- `k8s/argocd/kustomization.yaml`
- `k8s/argocd/apps/kustomization.yaml`

## Bootstrap
```bash
kubectl apply -n argocd -f k8s/argocd/project.yaml
kubectl apply -n argocd -f k8s/argocd/root-application.yaml
```

## GitOps-Ablauf
1. Änderungen an `k8s/base` committen.
2. ArgoCD erkennt Git-Änderung.
3. Automatischer Sync in Ziel-Cluster/Namespace.

## Hinweise
- `repoURL` in Applications auf euer Git-Remote anpassen.
- Branch (`targetRevision`) auf produktive Strategie anpassen (`develop`/`main`/Tag).
