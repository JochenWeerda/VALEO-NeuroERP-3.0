Write-Host "=== Customer POST Simple Test ==="

# Token
$tok = Invoke-RestMethod -Method POST -Uri "http://localhost:8000/token" -ContentType "application/x-www-form-urlencoded" -Body "username=admin&password=admin"
$hdr = @{ Authorization = "Bearer $($tok.access_token)" }
Write-Host "Token OK"

# GET Customers
$customers = Invoke-RestMethod -Method GET -Uri "http://localhost:8000/api/customers" -Headers $hdr
Write-Host "Kunden: $($customers.Count)"

# POST Customer (ohne Listen)
$custJson = '{"id":"test123","customerNumber":"T123","debtorAccount":"T123","customerGroup":"Test","salesRep":"Test","dispatcher":"Test","creditLimit":1000,"name":"Test GmbH","address":{"street":"Test 1","zipCode":"12345","city":"Test","country":"DE"},"phone":"123","status":"active","priority":"medium","createdAt":"2024-01-01T00:00:00Z","updatedAt":"2024-01-01T00:00:00Z","totalRevenue":0,"openInvoices":0,"creditUsed":0,"paymentTerms":"30","customerSegment":"regular","riskScore":1}'

try {
    $created = Invoke-RestMethod -Method POST -Uri "http://localhost:8000/api/customers" -ContentType "application/json" -Body $custJson -Headers $hdr
    Write-Host "POST OK: $($created.name)"
} catch {
    Write-Host "POST Error: $($_.Exception.Message)"
}

Write-Host "Done"
