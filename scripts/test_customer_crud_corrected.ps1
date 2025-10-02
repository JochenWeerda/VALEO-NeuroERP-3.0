Write-Host "=== Customer CRUD Test (Corrected) ==="

# Token abrufen
$tok = Invoke-RestMethod -Method POST -Uri "http://localhost:8000/token" -ContentType "application/x-www-form-urlencoded" -Body "username=admin&password=admin"
$hdr = @{ Authorization = "Bearer $($tok.access_token)" }
Write-Host "Token erhalten"

# Korrigierter Customer JSON (alle Required-Felder + korrektes Address-Objekt)
$custBody = @'
{
  "id": "test-001",
  "customerNumber": "TEST-001",
  "debtorAccount": "TEST001",
  "customerGroup": "Standard",
  "salesRep": "Test Rep",
  "dispatcher": "Test Dispatcher",
  "creditLimit": 20000.0,
  "name": "Test Firma GmbH",
  "address": {
    "street": "Teststraße 1",
    "zipCode": "12345",
    "city": "Teststadt",
    "country": "Deutschland"
  },
  "phone": "+49 123 456789",
  "email": "test@testfirma.de",
  "whatsapp": "+49 123 456789",
  "status": "active",
  "priority": "medium",
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z",
  "totalRevenue": 10000.0,
  "openInvoices": 0.0,
  "creditUsed": 0.0,
  "paymentTerms": "30 Tage netto",
  "customerSegment": "regular",
  "riskScore": 3,
  "contactPersons": [],
  "offers": [],
  "orders": [],
  "invoices": [],
  "documents": [],
  "communications": [],
  "directBusinesses": [],
  "externalStocks": [],
  "deals": [],
  "reminders": [],
  "purchaseOffers": [],
  "externalInventory": []
}
'@

try {
    $createdCustomer = Invoke-RestMethod -Method POST -Uri "http://localhost:8000/api/customers" -ContentType "application/json" -Body $custBody -Headers $hdr
    Write-Host "Kunde erstellt: $($createdCustomer.name) (ID: $($createdCustomer.id))"
    
    # Kunde abrufen
    $fetchedCustomer = Invoke-RestMethod -Method GET -Uri "http://localhost:8000/api/customers/$($createdCustomer.id)" -Headers $hdr
    Write-Host "Kunde abgerufen: $($fetchedCustomer.name)"
    
    # Alle Kunden auflisten
    $allCustomers = Invoke-RestMethod -Method GET -Uri "http://localhost:8000/api/customers" -Headers $hdr
    Write-Host "Gesamt Kunden: $($allCustomers.Count)"
    
} catch {
    Write-Host "POST Customer Fehler: $($_.Exception.Message)"
    if ($_.Exception.Response) {
        $stream = $_.Exception.Response.GetResponseStream()
        $reader = New-Object System.IO.StreamReader($stream)
        $responseText = $reader.ReadToEnd()
        Write-Host "Response Body: $responseText"
    }
}

Write-Host "Customer CRUD Test abgeschlossen"
