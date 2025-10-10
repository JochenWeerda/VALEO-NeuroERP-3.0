***REMOVED***!/bin/bash
***REMOVED*** Chaos Engineering: Pod-Kill-Test
***REMOVED*** Simuliert zufällige Pod-Failures und verifiziert Self-Healing

set -e

NAMESPACE="${NAMESPACE:-production}"
APP_LABEL="app.kubernetes.io/name=valeo-erp"
ITERATIONS="${ITERATIONS:-5}"
SLEEP_BETWEEN="${SLEEP_BETWEEN:-30}"

echo "🔥 Starting Chaos Engineering: Pod-Kill-Test"
echo "Namespace: $NAMESPACE"
echo "Iterations: $ITERATIONS"
echo "Sleep between kills: ${SLEEP_BETWEEN}s"
echo ""

***REMOVED*** Function to check service health
check_health() {
    echo "Checking service health..."
    
    ***REMOVED*** Get service URL (assuming port-forward or ingress)
    SERVICE_URL="${SERVICE_URL:-http://localhost:8000}"
    
    ***REMOVED*** Health check
    HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL/healthz")
    
    if [ "$HEALTH_STATUS" = "200" ]; then
        echo "✅ Health check: OK"
        return 0
    else
        echo "❌ Health check: FAILED (Status: $HEALTH_STATUS)"
        return 1
    fi
}

***REMOVED*** Function to check readiness
check_readiness() {
    echo "Checking service readiness..."
    
    SERVICE_URL="${SERVICE_URL:-http://localhost:8000}"
    READY_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL/readyz")
    
    if [ "$READY_STATUS" = "200" ]; then
        echo "✅ Readiness check: OK"
        return 0
    else
        echo "⚠️  Readiness check: NOT READY (Status: $READY_STATUS)"
        return 1
    fi
}

***REMOVED*** Function to check SSE connections
check_sse() {
    echo "Checking SSE connections..."
    
    SERVICE_URL="${SERVICE_URL:-http://localhost:8000}"
    
    ***REMOVED*** Try to connect to SSE endpoint (timeout after 5s)
    timeout 5 curl -s -N "$SERVICE_URL/api/stream/workflow" > /dev/null 2>&1
    
    if [ $? -eq 0 ] || [ $? -eq 124 ]; then
        ***REMOVED*** Exit 0 = success, 124 = timeout (expected for SSE)
        echo "✅ SSE connection: OK"
        return 0
    else
        echo "❌ SSE connection: FAILED"
        return 1
    fi
}

***REMOVED*** Function to kill random pod
kill_random_pod() {
    echo "Finding random pod to kill..."
    
    POD=$(kubectl get pods -n "$NAMESPACE" -l "$APP_LABEL" -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
    
    if [ -z "$POD" ]; then
        echo "❌ No pods found with label: $APP_LABEL"
        return 1
    fi
    
    echo "🔪 Killing pod: $POD"
    kubectl delete pod "$POD" -n "$NAMESPACE" --wait=false
    
    echo "⏳ Waiting for pod to terminate..."
    kubectl wait --for=delete pod/"$POD" -n "$NAMESPACE" --timeout=60s || true
    
    return 0
}

***REMOVED*** Function to wait for recovery
wait_for_recovery() {
    echo "⏳ Waiting for service to recover..."
    
    MAX_WAIT=120  ***REMOVED*** 2 minutes
    ELAPSED=0
    INTERVAL=5
    
    while [ $ELAPSED -lt $MAX_WAIT ]; do
        sleep $INTERVAL
        ELAPSED=$((ELAPSED + INTERVAL))
        
        echo "Checking recovery... (${ELAPSED}s / ${MAX_WAIT}s)"
        
        ***REMOVED*** Check if new pod is running
        READY_PODS=$(kubectl get pods -n "$NAMESPACE" -l "$APP_LABEL" -o jsonpath='{.items[?(@.status.phase=="Running")].metadata.name}' | wc -w)
        
        echo "Ready pods: $READY_PODS"
        
        if [ "$READY_PODS" -ge 1 ]; then
            echo "✅ Pod recovered!"
            
            ***REMOVED*** Give it a few more seconds to fully start
            sleep 10
            
            ***REMOVED*** Verify health
            if check_health && check_readiness; then
                echo "✅ Service fully recovered"
                return 0
            fi
        fi
    done
    
    echo "❌ Service did not recover within ${MAX_WAIT}s"
    return 1
}

***REMOVED*** Main test loop
FAILED_TESTS=0
SUCCESSFUL_TESTS=0

for i in $(seq 1 "$ITERATIONS"); do
    echo ""
    echo "=========================================="
    echo "Iteration $i / $ITERATIONS"
    echo "=========================================="
    
    ***REMOVED*** Check initial state
    if ! check_health; then
        echo "⚠️  Service not healthy before test, skipping..."
        FAILED_TESTS=$((FAILED_TESTS + 1))
        continue
    fi
    
    ***REMOVED*** Kill pod
    if ! kill_random_pod; then
        echo "❌ Failed to kill pod"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        continue
    fi
    
    ***REMOVED*** Wait for recovery
    if wait_for_recovery; then
        echo "✅ Test iteration $i: PASSED"
        SUCCESSFUL_TESTS=$((SUCCESSFUL_TESTS + 1))
        
        ***REMOVED*** Check SSE reconnection
        if check_sse; then
            echo "✅ SSE reconnection: PASSED"
        else
            echo "⚠️  SSE reconnection: FAILED (non-critical)"
        fi
    else
        echo "❌ Test iteration $i: FAILED"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    
    ***REMOVED*** Sleep between iterations
    if [ $i -lt "$ITERATIONS" ]; then
        echo "⏳ Sleeping ${SLEEP_BETWEEN}s before next iteration..."
        sleep "$SLEEP_BETWEEN"
    fi
done

***REMOVED*** Summary
echo ""
echo "=========================================="
echo "Chaos Test Summary"
echo "=========================================="
echo "Total iterations: $ITERATIONS"
echo "Successful: $SUCCESSFUL_TESTS"
echo "Failed: $FAILED_TESTS"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo "✅ All chaos tests PASSED!"
    echo "Service demonstrates excellent resilience and self-healing capabilities."
    exit 0
else
    echo "❌ Some chaos tests FAILED"
    echo "Service may have issues with self-healing or recovery time."
    exit 1
fi

