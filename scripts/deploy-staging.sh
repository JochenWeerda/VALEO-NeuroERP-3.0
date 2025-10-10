#!/bin/bash
# VALEO-NeuroERP 3.0 - Staging-Deployment-Script
# Automatisiertes Deployment zu Staging-Environment

set -e

echo "🚀 VALEO-NeuroERP 3.0 - Staging-Deployment"
echo "=========================================="
echo ""

# Configuration
NAMESPACE="${NAMESPACE:-staging}"
VERSION="${VERSION:-3.0.0-staging}"
REGISTRY="${REGISTRY:-ghcr.io/valeo}"
HELM_RELEASE="valeo-erp-staging"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Helper Functions
log_info() {
  echo -e "${GREEN}✅ $1${NC}"
}

log_warn() {
  echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
  echo -e "${RED}❌ $1${NC}"
}

# Step 1: Build Docker-Images
echo -e "${YELLOW}📦 Step 1: Building Docker-Images...${NC}"

# Backend
docker build -t ${REGISTRY}/valeo-erp-backend:${VERSION} -f Dockerfile .
log_info "Backend-Image built"

# Frontend (falls vorhanden)
if [ -f "packages/frontend-web/Dockerfile.frontend" ]; then
  cd packages/frontend-web
  docker build -t ${REGISTRY}/valeo-erp-frontend:${VERSION} -f Dockerfile.frontend .
  cd ../..
  log_info "Frontend-Image built"
fi

# Step 2: Push to Registry
echo ""
echo -e "${YELLOW}📤 Step 2: Pushing Images to Registry...${NC}"

docker push ${REGISTRY}/valeo-erp-backend:${VERSION}
log_info "Backend-Image pushed"

if [ -f "packages/frontend-web/Dockerfile.frontend" ]; then
  docker push ${REGISTRY}/valeo-erp-frontend:${VERSION}
  log_info "Frontend-Image pushed"
fi

# Step 3: Create Namespace
echo ""
echo -e "${YELLOW}🏗️  Step 3: Creating Namespace...${NC}"

kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
kubectl label namespace ${NAMESPACE} environment=staging --overwrite
log_info "Namespace created/updated: ${NAMESPACE}"

# Step 4: PostgreSQL-Setup
echo ""
echo -e "${YELLOW}🗄️  Step 4: PostgreSQL-Setup...${NC}"

if ! kubectl get statefulset -n ${NAMESPACE} postgresql >/dev/null 2>&1; then
  log_warn "PostgreSQL not found, installing..."
  
  helm install postgresql bitnami/postgresql \
    --namespace ${NAMESPACE} \
    --set auth.username=valeo \
    --set auth.password=staging_password_change_me \
    --set auth.database=valeo_erp \
    --set primary.persistence.size=10Gi \
    --wait
  
  log_info "PostgreSQL installed"
else
  log_info "PostgreSQL already exists"
fi

# Wait for PostgreSQL
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=postgresql -n ${NAMESPACE} --timeout=300s
log_info "PostgreSQL ready"

# Step 5: Create Secrets
echo ""
echo -e "${YELLOW}🔐 Step 5: Creating Secrets...${NC}"

kubectl create secret generic valeo-erp-db-secret \
  --from-literal=database-url=postgresql://valeo:staging_password_change_me@postgresql:5432/valeo_erp \
  --namespace=${NAMESPACE} \
  --dry-run=client -o yaml | kubectl apply -f -

log_info "Secrets created"

# Step 6: Database-Migrations
echo ""
echo -e "${YELLOW}🔄 Step 6: Running Database-Migrations...${NC}"

# Via Job
kubectl apply -f - <<EOF
apiVersion: batch/v1
kind: Job
metadata:
  name: valeo-erp-migrations-$(date +%s)
  namespace: ${NAMESPACE}
spec:
  template:
    spec:
      containers:
      - name: migrations
        image: ${REGISTRY}/valeo-erp-backend:${VERSION}
        command: ["alembic", "upgrade", "head"]
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: valeo-erp-db-secret
              key: database-url
      restartPolicy: Never
  backoffLimit: 3
EOF

# Wait for Job
kubectl wait --for=condition=complete job -l job-name=valeo-erp-migrations* -n ${NAMESPACE} --timeout=300s
log_info "Migrations completed"

# Step 7: Helm-Deployment
echo ""
echo -e "${YELLOW}🚀 Step 7: Deploying VALEO-ERP...${NC}"

helm upgrade --install ${HELM_RELEASE} ./k8s/helm/valeo-erp \
  --namespace ${NAMESPACE} \
  --set image.repository=${REGISTRY}/valeo-erp-backend \
  --set image.tag=${VERSION} \
  --set replicaCount=2 \
  --set ingress.hosts[0].host=staging.erp.valeo.example.com \
  --set ingress.tls[0].secretName=valeo-erp-staging-tls \
  --set ingress.tls[0].hosts[0]=staging.erp.valeo.example.com \
  --wait \
  --timeout 10m

log_info "VALEO-ERP deployed"

# Step 8: Verify Deployment
echo ""
echo -e "${YELLOW}🔍 Step 8: Verifying Deployment...${NC}"

# Check Pods
POD_COUNT=$(kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/name=valeo-erp -o json | jq '.items | length')
READY_COUNT=$(kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/name=valeo-erp -o json | jq '[.items[] | select(.status.phase=="Running")] | length')

echo "Pods: ${READY_COUNT}/${POD_COUNT} ready"

if [ "${READY_COUNT}" -lt 1 ]; then
  log_error "No pods ready!"
  exit 1
fi

log_info "Pods ready"

# Health-Check
echo ""
echo -e "${YELLOW}🏥 Health-Checks...${NC}"

sleep 10  # Give pods time to start

if curl -f https://staging.erp.valeo.example.com/healthz >/dev/null 2>&1; then
  log_info "Liveness-Probe OK"
else
  log_warn "Liveness-Probe failed (might need more time)"
fi

if curl -f https://staging.erp.valeo.example.com/readyz >/dev/null 2>&1; then
  log_info "Readiness-Probe OK"
else
  log_warn "Readiness-Probe failed (might need more time)"
fi

# Step 9: Summary
echo ""
echo "=========================================="
echo -e "${GREEN}✅ Staging-Deployment Complete${NC}"
echo "=========================================="
echo ""
echo "Environment: ${NAMESPACE}"
echo "Version: ${VERSION}"
echo "URL: https://staging.erp.valeo.example.com"
echo ""
echo "Next Steps:"
echo "1. Open Grafana: kubectl port-forward -n monitoring svc/prometheus-operator-grafana 3000:80"
echo "2. Run E2E-Tests: cd playwright-tests && npx playwright test"
echo "3. Start UAT with test-users"
echo "4. Monitor: https://staging.erp.valeo.example.com/metrics"
echo ""
echo -e "${GREEN}🎉 Ready for UAT!${NC}"

