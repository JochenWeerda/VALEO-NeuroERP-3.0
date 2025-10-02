Write-Host "=== Minimal Customer POST Test ==="

# Token abrufen
$tok = Invoke-RestMethod -Method POST -Uri "http://localhost:8000/token" -ContentType "application/x-www-form-urlencoded" -Body "username=admin&password=admin"
$hdr = @{ Authorization = "Bearer $($tok.access_token)" }
Write-Host "Token erhalten"

# Zunächst alle Kunden auflisten
$customers = Invoke-RestMethod -Method GET -Uri "http://localhost:8000/api/customers" -Headers $hdr
Write-Host "Aktuelle Kunden: $($customers.Count)"

# Minimal Customer JSON (nur Required-Felder)
$minimalCustomer = @'
{
  "id": "minimal-001",
  "customerNumber": "MIN-001",
  "debtorAccount": "MIN001",
  "customerGroup": "Test",
  "salesRep": "Test Rep",
  "dispatcher": "Test Dispatcher",
  "creditLimit": 1000.0,
  "name": "Minimal Test GmbH",
  "address": {
    "street": "Teststr. 1",
    "zipCode": "12345",
    "city": "Teststadt",
    "country": "Deutschland"
  },
  "phone": "+49 123 456789",
  "status": "active",
  "priority": "medium",
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedAt": "2024-01-01T00:00:00Z",
  "totalRevenue": 0.0,
  "openInvoices": 0.0,
  "creditUsed": 0.0,
  "paymentTerms": "30 Tage netto",
  "customerSegment": "regular",
  "riskScore": 3
}
'@

Write-Host "Versuche minimalen Customer zu erstellen..."
try {
    $createdCustomer = Invoke-RestMethod -Method POST -Uri "http://localhost:8000/api/customers" -ContentType "application/json" -Body $minimalCustomer -Headers $hdr
    Write-Host "✓ Kunde erfolgreich erstellt: $($createdCustomer.name)"
} catch {
    Write-Host "✗ POST Fehler: $($_.Exception.Message)"
    if ($_.Exception.Response) {
        $stream = $_.Exception.Response.GetResponseStream()
        $reader = New-Object System.IO.StreamReader($stream)
        $responseText = $reader.ReadToEnd()
        Write-Host "Antwort: $responseText"
    }
}

Write-Host "Test abgeschlossen"
