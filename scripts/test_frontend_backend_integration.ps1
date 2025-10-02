Write-Host "=== Frontend-Backend Integration Test ==="

# Backend Health Check
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health"
    Write-Host "✓ Backend Health: $($health.status)"
} catch {
    Write-Host "✗ Backend nicht erreichbar: $($_.Exception.Message)"
    exit 1
}

# Test 1: User Registration
Write-Host "`n1. User Registration Test"
$regData = @{ username='frontend_user'; password='test123'; email='frontend@test.de' } | ConvertTo-Json -Compress
try {
    $regResult = Invoke-RestMethod -Method POST -Uri "http://localhost:8000/api/v1/auth/register" -ContentType "application/json" -Body $regData
    Write-Host "✓ User registriert: $($regResult.user.username)"
} catch {
    Write-Host "! User bereits vorhanden oder Fehler: $($_.Exception.Message)"
}

# Test 2: Authentication
Write-Host "`n2. Authentication Test"
try {
    $token = Invoke-RestMethod -Method POST -Uri "http://localhost:8000/token" -ContentType "application/x-www-form-urlencoded" -Body "username=frontend_user&password=test123"
    $authHeader = @{ Authorization = "Bearer $($token.access_token)" }
    Write-Host "✓ Authentication erfolgreich"
} catch {
    Write-Host "✗ Authentication fehlgeschlagen: $($_.Exception.Message)"
    exit 1
}

# Test 3: Customer API Tests
Write-Host "`n3. Customer API Tests"

# GET Customers
try {
    $customers = Invoke-RestMethod -Method GET -Uri "http://localhost:8000/api/customers" -Headers $authHeader
    Write-Host "✓ GET /api/customers: $($customers.Count) Kunden"
    
    if ($customers.Count -gt 0) {
        Write-Host "  - Beispiel: $($customers[0].name) (ID: $($customers[0].id))"
    }
} catch {
    Write-Host "✗ GET Customers Fehler: $($_.Exception.Message)"
}

# POST Customer
Write-Host "`n4. Customer Creation Test"
$newCustomer = @{
    id = "frontend-test-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    customerNumber = "FE-$(Get-Date -Format 'yyyyMMdd')"
    debtorAccount = "FE001"
    customerGroup = "Frontend-Test"
    salesRep = "Frontend Test Rep"
    dispatcher = "Frontend Dispatcher"
    creditLimit = 5000.0
    name = "Frontend Test GmbH"
    address = @{
        street = "Frontend Str. 1"
        zipCode = "12345"
        city = "Frontend Stadt"
        country = "Deutschland"
    }
    phone = "+49 123 frontend"
    status = "active"
    priority = "medium"
    createdAt = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssZ")
    updatedAt = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssZ")
    totalRevenue = 0.0
    openInvoices = 0.0
    creditUsed = 0.0
    paymentTerms = "30 Tage Frontend"
    customerSegment = "regular"
    riskScore = 2
} | ConvertTo-Json -Depth 5 -Compress

try {
    $createdCustomer = Invoke-RestMethod -Method POST -Uri "http://localhost:8000/api/customers" -ContentType "application/json" -Body $newCustomer -Headers $authHeader
    Write-Host "✓ POST Customer erfolgreich: $($createdCustomer.name)"
    
    # Test GET specific customer
    $fetchedCustomer = Invoke-RestMethod -Method GET -Uri "http://localhost:8000/api/customers/$($createdCustomer.id)" -Headers $authHeader
    Write-Host "✓ GET Customer by ID erfolgreich: $($fetchedCustomer.name)"
    
} catch {
    Write-Host "✗ POST Customer Fehler: $($_.Exception.Message)"
}

# Test 5: CORS Test (simuliert Frontend-Request)
Write-Host "`n5. CORS Test"
try {
    $corsHeaders = @{
        'Origin' = 'http://localhost:3000'
        'Access-Control-Request-Method' = 'GET'
        'Access-Control-Request-Headers' = 'authorization,content-type'
    }
    $corsResponse = Invoke-RestMethod -Method OPTIONS -Uri "http://localhost:8000/api/customers" -Headers $corsHeaders
    Write-Host "✓ CORS Test erfolgreich"
} catch {
    Write-Host "! CORS möglicherweise problematisch: $($_.Exception.Message)"
}

Write-Host "`n=== Integration Test Abgeschlossen ==="
Write-Host "Backend ist bereit für Frontend-Integration!"

# Frontend-Status prüfen
Write-Host "`n6. Frontend Connection Test"
try {
    $frontendTest = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 5
    if ($frontendTest.StatusCode -eq 200) {
        Write-Host "✓ Frontend läuft auf http://localhost:3000"
    }
} catch {
    Write-Host "! Frontend nicht verfügbar auf Port 3000"
    Write-Host "  Starte Frontend manuell mit: npm run dev"
}
