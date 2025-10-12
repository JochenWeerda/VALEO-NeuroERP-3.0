#!/bin/bash
# Setup Keycloak for VALEO NeuroERP Development
# Automated Keycloak configuration via Admin REST API

set -e

KEYCLOAK_URL="http://localhost:8080"
ADMIN_USER="admin"
ADMIN_PASSWORD="admin"
REALM="valeo-neuro-erp"

echo "🔐 Setting up Keycloak for VALEO NeuroERP..."

# Wait for Keycloak to be ready
echo "⏳ Waiting for Keycloak to start..."
until curl -sf "${KEYCLOAK_URL}/health/ready" > /dev/null; do
    echo "   Keycloak not ready yet, waiting..."
    sleep 5
done
echo "✅ Keycloak is ready!"

# Get admin token
echo "🔑 Obtaining admin access token..."
ADMIN_TOKEN=$(curl -sf -X POST "${KEYCLOAK_URL}/realms/master/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=${ADMIN_USER}" \
  -d "password=${ADMIN_PASSWORD}" \
  -d "grant_type=password" \
  -d "client_id=admin-cli" \
  | jq -r '.access_token')

if [ -z "$ADMIN_TOKEN" ]; then
    echo "❌ Failed to obtain admin token"
    exit 1
fi

echo "✅ Admin token obtained"

# Check if realm already exists
REALM_EXISTS=$(curl -sf -X GET "${KEYCLOAK_URL}/admin/realms/${REALM}" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" \
  -o /dev/null -w "%{http_code}")

if [ "$REALM_EXISTS" = "200" ]; then
    echo "✅ Realm '${REALM}' already exists, skipping import"
else
    echo "📦 Importing realm from realm-export.json..."
    curl -sf -X POST "${KEYCLOAK_URL}/admin/realms" \
      -H "Authorization: Bearer ${ADMIN_TOKEN}" \
      -H "Content-Type: application/json" \
      -d @config/keycloak/realm-export.json
    
    echo "✅ Realm '${REALM}' imported successfully"
fi

# Verify setup
echo "🔍 Verifying Keycloak setup..."

# Get realm info
REALM_INFO=$(curl -sf -X GET "${KEYCLOAK_URL}/realms/${REALM}" \
  -H "Accept: application/json")

echo "✅ Keycloak setup complete!"
echo ""
echo "📋 Configuration Summary:"
echo "   Realm: ${REALM}"
echo "   URL: ${KEYCLOAK_URL}"
echo "   Admin Console: ${KEYCLOAK_URL}/admin"
echo "   Admin User: ${ADMIN_USER}"
echo "   Admin Password: ${ADMIN_PASSWORD}"
echo ""
echo "🧪 Test Users:"
echo "   admin@valeo-erp.local / admin123 (role: admin)"
echo "   user@valeo-erp.local / user123 (role: user)"
echo "   finance@valeo-erp.local / finance123 (role: finance_manager)"
echo ""
echo "🔗 OIDC Discovery URL:"
echo "   ${KEYCLOAK_URL}/realms/${REALM}/.well-known/openid-configuration"
echo ""
echo "🚀 Ready to use! Update your .env files:"
echo "   OIDC_ISSUER_URL=${KEYCLOAK_URL}/realms/${REALM}"
echo "   OIDC_CLIENT_ID=valeo-neuro-erp-backend"
echo "   OIDC_CLIENT_SECRET=valeo-backend-secret-dev-change-in-prod"
echo "   VITE_OIDC_DISCOVERY_URL=${KEYCLOAK_URL}/realms/${REALM}/.well-known/openid-configuration"
echo "   VITE_OIDC_CLIENT_ID=valeo-neuro-erp-frontend"

