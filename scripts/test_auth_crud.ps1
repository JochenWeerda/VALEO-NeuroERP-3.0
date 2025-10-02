# Test Auth und CRUD

Write-Host "=== VALEO NeuroERP API Test ==="

# User registrieren
$regData = @{ username='admin'; password='admin'; email='admin@valeo.local' } | ConvertTo-Json -Compress
try {
    $regResult = Invoke-RestMethod -Method POST -Uri "http://localhost:8000/api/v1/auth/register" -ContentType "application/json" -Body $regData
    Write-Host "✓ User registriert: $($regResult.user.username)"
} catch {
    Write-Host "! User-Registrierung: $($_.Exception.Message) (möglicherweise bereits vorhanden)"
}

# Token abrufen
try {
    $tok = Invoke-RestMethod -Method POST -Uri "http://localhost:8000/token" -ContentType "application/x-www-form-urlencoded" -Body "username=admin`&password=admin"
    Write-Host "✓ Token erhalten: $($tok.access_token)"
} catch {
    Write-Host "✗ Token-Fehler: $($_.Exception.Message)"
    return
}

$hdr = @{ Authorization = "Bearer $($tok.access_token)" }

# Test: GET /api/customers
try {
    $customers = Invoke-RestMethod -Method GET -Uri "http://localhost:8000/api/customers?limit=5" -Headers $hdr
    Write-Host "✓ Customers abgerufen: $($customers.Count) Einträge"
    if ($customers.Count -gt 0) {
        Write-Host "Erster Kunde: $($customers[0].name)"
    }
} catch {
    Write-Host "✗ GET Customers Fehler: $($_.Exception.Message)"
}

# Test: POST /api/customers (neuen Kunden erstellen)
$newCustomer = @{
    customerNumber = "TEST-001"
    name = "Test Firma GmbH"
    address = @{
        street = "Teststraße 1"
        zipCode = "12345"
        city = "Teststadt"
        country = "Deutschland"
    }
    phone = "+49 123 456789"
    email = "test@testfirma.de"
    status = "active"
    priority = "medium"
    totalRevenue = 10000.0
    openInvoices = 0.0
    creditUsed = 0.0
    paymentTerms = "30 Tage netto"
    customerSegment = "regular"
    riskScore = 3
    debtorAccount = "TEST001"
    customerGroup = "Standard"
    salesRep = "Test Rep"
    dispatcher = "Test Dispatcher"
    creditLimit = 20000.0
    whatsapp = "+49 123 456789"
    contactPersons = @()
    offers = @()
    orders = @()
    invoices = @()
    documents = @()
    communications = @()
    directBusinesses = @()
    externalStocks = @()
    deals = @()
    reminders = @()
    purchaseOffers = @()
    externalInventory = @()
} | ConvertTo-Json -Depth 5 -Compress

try {
    $createdCustomer = Invoke-RestMethod -Method POST -Uri "http://localhost:8000/api/customers" -ContentType "application/json" -Body $newCustomer -Headers $hdr
    Write-Host "✓ Kunde erstellt: $($createdCustomer.name) (ID: $($createdCustomer.id))"
    
    # Test: GET /api/customers/{id}
    $fetchedCustomer = Invoke-RestMethod -Method GET -Uri "http://localhost:8000/api/customers/$($createdCustomer.id)" -Headers $hdr
    Write-Host "✓ Kunde abgerufen: $($fetchedCustomer.name)"
    
} catch {
    Write-Host "✗ POST Customer Fehler: $($_.Exception.Message)"
}

Write-Host "=== Test abgeschlossen ==="
