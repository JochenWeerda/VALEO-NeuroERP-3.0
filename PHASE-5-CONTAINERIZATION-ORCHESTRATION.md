# 🐳 PHASE 5: CONTAINERIZATION & ORCHESTRATION
## WEEK 5/16: Infrastructure Setup (Original Week 12)

### OBJECTIVE
Implement Docker containerization and Kubernetes orchestration for VALEO-NeuroERP-3.0

**Week 5 Tasks:**
- ✅ Docker containerization setup
- ✅ Kubernetes deployment manifests
- ✅ Service mesh implementation 
- ✅ Production scaling configuration
- ✅ Resource management optimization

---

## 🐳 **CONTAINERIZATION IMPLEMENTATION**

### **1. Docker Configuration:**
```dockerfile
# Dockerfile.valeo-neuroerp-3.0
FROM node:18-alpine AS base

WORKDIR /app

# Clean Architecture Domain Services Dependencies
COPY domains/shared/src /app/domains/shared/src
COPY domains/crm/src /app/domains/crm/src  
COPY domains/finance/src /app/domains/finance/src
COPY domains/inventory/src /app/domains/inventory/src
COPY domains/analytics/src /app/domains/analytics/src

# Production Dependencies
COPY package*.json ./
RUN npm ci --only=production

# Clean Architecture Build
FROM base AS build
RUN npm run build:domains

# Production Image
FROM node:18-alpine AS production
WORKDIR /app

COPY --from=build /app/.next ./.next
COPY --from=build /app/public ./public
COPY --from=build /app/package*.json ./

EXPOSE 3000
CMD ["npm", "start"]
```

### **2. Kubernetes Manifests:**
```yaml
# k8s/valeo-neuroerp-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: valeo-neuroerp-3.0
spec:
  replicas: 3
  selector:
    matchLabels:
      app: valeo-neuroerp
  template:
    metadata:
      labels:
        app: valeo-neuroerp
        version: "3.0"
        architecture: "clean-architecture"
    spec:
      containers:
      - name: neuroerp-app
        image: valeo/neuroerp-3.0:latest
        ports:
        - containerPort: 3000
          name: http
        env:
        - name: NODE_ENV
          value: "production"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: neuroerp-secrets
              key: database-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: http
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/ready
            port: http
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: valeo-neuroerp-service
spec:
  selector:
    app: valeo-neuroerp
  ports:
  - port: 3000
    targetPort: 3000
    name: http
  type: ClusterIP
```

### **3. Service Mesh Implementation:**
```yaml
# istio/valeo-service-mesh.yaml
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: valeo-neuroerp-gateway
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - "valeo-neuroerp.local"
  - port:
      number: 443
      name: https
      protocol: HTTPS
    tls:
      mode: SIMPLE
      credentialName: neuroerp-tls-cert
    hosts:
    - "valeo-neuroerp.local"
---
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: valeo-neuroerp-routes
spec:
  hosts:
  - "valeo-neuroerp.local"
  gateways:
  - valeo-neuroerp-gateway
  http:
  - match:
    - uri:
        prefix: /api/v1/crm
    route:
    - destination:
        host: valeo-crm-service
    - match:
    - uri:
        prefix: /api/v1
    route:
    - destination:
        host: valeo-finance-service
    - match:
    - uri:
        prefix: /api/v1/inventory
    route:
    - destination:
        host: valeo-inventory-service
```

---

