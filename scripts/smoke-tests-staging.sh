#!/bin/bash
# ===================================
# VALEO NeuroERP - Staging Smoke Tests
# ===================================
# Version: 3.0.0
# Purpose: Automated health checks and functional tests for staging environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
FRONTEND_URL="http://localhost:3001"
BACKEND_URL="http://localhost:8001"
BFF_URL="http://localhost:4001"
KEYCLOAK_URL="http://localhost:8180"
POSTGRES_CONTAINER="valeo-staging-postgres"
REDIS_CONTAINER="valeo-staging-redis"
KEYCLOAK_CONTAINER="valeo-staging-keycloak"

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0

# ===================================
# Helper Functions
# ===================================

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

test_passed() {
    echo -e "${GREEN}✅ $1${NC}"
    ((TESTS_PASSED++))
}

test_failed() {
    echo -e "${RED}❌ $1${NC}"
    ((TESTS_FAILED++))
}

# ===================================
# Test Functions
# ===================================

test_postgresql_health() {
    log_info "Testing PostgreSQL Health..."
    if docker exec $POSTGRES_CONTAINER pg_isready -U valeo_staging -d valeo_neuro_erp_staging > /dev/null 2>&1; then
        test_passed "PostgreSQL Health Check"
    else
        test_failed "PostgreSQL Health Check"
    fi
}

test_redis_health() {
    log_info "Testing Redis Health..."
    if docker exec $REDIS_CONTAINER redis-cli ping | grep -q "PONG"; then
        test_passed "Redis Health Check"
    else
        test_failed "Redis Health Check"
    fi
}

test_keycloak_health() {
    log_info "Testing Keycloak Health..."
    if curl -sf "$KEYCLOAK_URL/health/ready" > /dev/null 2>&1; then
        test_passed "Keycloak Health Check"
    else
        test_failed "Keycloak Health Check"
    fi
}

test_keycloak_realm() {
    log_info "Testing Keycloak Realm Configuration..."
    response=$(curl -s "$KEYCLOAK_URL/realms/valeo-staging/.well-known/openid-configuration")
    if echo "$response" | grep -q "valeo-staging"; then
        test_passed "Keycloak Realm 'valeo-staging'"
    else
        test_failed "Keycloak Realm 'valeo-staging'"
    fi
}

test_backend_health() {
    log_info "Testing Backend API Health..."
    if curl -sf "$BACKEND_URL/healthz" > /dev/null 2>&1; then
        test_passed "Backend API Health Check"
    else
        test_failed "Backend API Health Check"
    fi
}

test_backend_docs() {
    log_info "Testing Backend API Documentation..."
    if curl -sf "$BACKEND_URL/docs" > /dev/null 2>&1; then
        test_passed "Backend API Docs (Swagger)"
    else
        test_failed "Backend API Docs (Swagger)"
    fi
}

test_bff_health() {
    log_info "Testing BFF Health..."
    if curl -sf "$BFF_URL/health" > /dev/null 2>&1; then
        test_passed "BFF Health Check"
    else
        test_failed "BFF Health Check" 
    fi
}

test_frontend_health() {
    log_info "Testing Frontend Health..."
    if curl -sf "$FRONTEND_URL/" > /dev/null 2>&1; then
        test_passed "Frontend Health Check"
    else
        test_failed "Frontend Health Check"
    fi
}

test_database_tables() {
    log_info "Testing Database Tables..."
    tables=$(docker exec $POSTGRES_CONTAINER psql -U valeo_staging -d valeo_neuro_erp_staging -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';" | tr -d ' ')
    if [ "$tables" -gt 0 ]; then
        test_passed "Database Tables ($tables tables found)"
    else
        test_failed "Database Tables (no tables found)"
    fi
}

test_redis_connection() {
    log_info "Testing Redis Connection..."
    if docker exec $REDIS_CONTAINER redis-cli SET smoke_test_key "test_value" > /dev/null 2>&1; then
        value=$(docker exec $REDIS_CONTAINER redis-cli GET smoke_test_key)
        if [ "$value" == "test_value" ]; then
            docker exec $REDIS_CONTAINER redis-cli DEL smoke_test_key > /dev/null 2>&1
            test_passed "Redis Connection (Read/Write)"
        else
            test_failed "Redis Connection (Read/Write)"
        fi
    else
        test_failed "Redis Connection (Read/Write)"
    fi
}

test_oidc_discovery() {
    log_info "Testing OIDC Discovery Document..."
    response=$(curl -s "$KEYCLOAK_URL/realms/valeo-staging/.well-known/openid-configuration")
    
    if echo "$response" | jq -e '.issuer' > /dev/null 2>&1; then
        issuer=$(echo "$response" | jq -r '.issuer')
        test_passed "OIDC Discovery (Issuer: $issuer)"
    else
        test_failed "OIDC Discovery"
    fi
}

test_oidc_jwks() {
    log_info "Testing OIDC JWKS Endpoint..."
    response=$(curl -s "$KEYCLOAK_URL/realms/valeo-staging/protocol/openid-connect/certs")
    
    if echo "$response" | jq -e '.keys' > /dev/null 2>&1; then
        keys_count=$(echo "$response" | jq '.keys | length')
        test_passed "OIDC JWKS ($keys_count keys available)"
    else
        test_failed "OIDC JWKS"
    fi
}

test_cors_headers() {
    log_info "Testing CORS Headers..."
    response=$(curl -s -I -H "Origin: http://localhost:3001" "$BACKEND_URL/healthz")
    
    if echo "$response" | grep -q "Access-Control-Allow-Origin"; then
        test_passed "CORS Headers"
    else
        test_failed "CORS Headers"
    fi
}

test_container_status() {
    log_info "Testing Container Status..."
    
    containers=("$POSTGRES_CONTAINER" "$REDIS_CONTAINER" "$KEYCLOAK_CONTAINER" "valeo-staging-backend" "valeo-staging-bff" "valeo-staging-frontend")
    
    all_running=true
    for container in "${containers[@]}"; do
        if docker ps | grep -q "$container"; then
            log_info "  ✓ $container is running"
        else
            log_error "  ✗ $container is NOT running"
            all_running=false
        fi
    done
    
    if $all_running; then
        test_passed "All Containers Running"
    else
        test_failed "Some Containers Not Running"
    fi
}

test_disk_space() {
    log_info "Testing Disk Space..."
    
    available=$(df -h / | tail -1 | awk '{print $5}' | sed 's/%//')
    
    if [ "$available" -lt 90 ]; then
        test_passed "Disk Space (${available}% used)"
    else
        test_failed "Disk Space (${available}% used - LOW!)"
    fi
}

test_memory_usage() {
    log_info "Testing Memory Usage..."
    
    # This is a basic check; might need adjustment for Windows
    if command -v free > /dev/null 2>&1; then
        mem_used=$(free | grep Mem | awk '{print int($3/$2 * 100)}')
        
        if [ "$mem_used" -lt 90 ]; then
            test_passed "Memory Usage (${mem_used}% used)"
        else
            test_failed "Memory Usage (${mem_used}% used - HIGH!)"
        fi
    else
        log_warning "Memory check not available on this system"
    fi
}

# ===================================
# API Integration Tests
# ===================================

test_api_customers_list() {
    log_info "Testing API - List Customers..."
    
    # Note: This requires authentication in production, but staging might have test endpoints
    response=$(curl -s "$BACKEND_URL/api/customers")
    
    if [ $? -eq 0 ]; then
        test_passed "API - List Customers"
    else
        test_warning "API - List Customers (might require auth)"
    fi
}

test_api_health_details() {
    log_info "Testing API - Detailed Health..."
    
    response=$(curl -s "$BACKEND_URL/healthz")
    
    if echo "$response" | jq -e '.status' > /dev/null 2>&1; then
        status=$(echo "$response" | jq -r '.status')
        if [ "$status" == "healthy" ] || [ "$status" == "ok" ]; then
            test_passed "API - Detailed Health (Status: $status)"
        else
            test_failed "API - Detailed Health (Status: $status)"
        fi
    else
        # Fallback if response is just "OK" string
        if [ "$response" == "OK" ] || [ "$response" == "ok" ]; then
            test_passed "API - Detailed Health"
        else
            test_failed "API - Detailed Health"
        fi
    fi
}

# ===================================
# Main Test Runner
# ===================================

main() {
    echo "========================================="
    echo "  VALEO NeuroERP - Staging Smoke Tests"
    echo "========================================="
    echo ""
    
    # Infrastructure Tests
    echo "--- Infrastructure Health Checks ---"
    test_postgresql_health
    test_redis_health
    test_keycloak_health
    echo ""
    
    # Application Tests
    echo "--- Application Health Checks ---"
    test_backend_health
    test_bff_health
    test_frontend_health
    echo ""
    
    # OIDC Tests
    echo "--- OIDC Configuration Tests ---"
    test_keycloak_realm
    test_oidc_discovery
    test_oidc_jwks
    echo ""
    
    # Database & Cache Tests
    echo "--- Data Layer Tests ---"
    test_database_tables
    test_redis_connection
    echo ""
    
    # API Tests
    echo "--- API Tests ---"
    test_backend_docs
    test_api_health_details
    test_cors_headers
    echo ""
    
    # System Tests
    echo "--- System Resource Tests ---"
    test_container_status
    test_disk_space
    test_memory_usage
    echo ""
    
    # Summary
    echo "========================================="
    echo "  Test Summary"
    echo "========================================="
    echo -e "${GREEN}✅ Tests Passed: $TESTS_PASSED${NC}"
    echo -e "${RED}❌ Tests Failed: $TESTS_FAILED${NC}"
    echo ""
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}🎉 All Smoke Tests Passed!${NC}"
        exit 0
    else
        echo -e "${RED}⚠️  Some Smoke Tests Failed!${NC}"
        echo "Please check the logs and fix issues before proceeding."
        exit 1
    fi
}

# ===================================
# Run Tests
# ===================================

# Check if specific test requested
if [ ! -z "$1" ]; then
    case $1 in
        health)
            test_postgresql_health
            test_redis_health
            test_keycloak_health
            test_backend_health
            test_bff_health
            test_frontend_health
            ;;
        auth)
            test_keycloak_health
            test_keycloak_realm
            test_oidc_discovery
            test_oidc_jwks
            ;;
        api)
            test_backend_health
            test_backend_docs
            test_api_health_details
            test_cors_headers
            ;;
        *)
            echo "Unknown test suite: $1"
            echo "Available: health, auth, api"
            exit 1
            ;;
    esac
else
    main
fi

