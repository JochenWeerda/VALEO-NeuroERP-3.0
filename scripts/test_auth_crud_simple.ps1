Write-Host "=== VALEO NeuroERP API Test ==="

# User registrieren
$regBody = '{"username":"admin","password":"admin","email":"admin@valeo.local"}'
try {
    $regResult = Invoke-RestMethod -Method POST -Uri "http://localhost:8000/api/v1/auth/register" -ContentType "application/json" -Body $regBody
    Write-Host "User registriert: $($regResult.user.username)"
} catch {
    Write-Host "User-Registrierung (wahrscheinlich bereits vorhanden): $($_.Exception.Message)"
}

# Token abrufen
try {
    $tok = Invoke-RestMethod -Method POST -Uri "http://localhost:8000/token" -ContentType "application/x-www-form-urlencoded" -Body "username=admin&password=admin"
    Write-Host "Token erhalten"
    $hdr = @{ Authorization = "Bearer $($tok.access_token)" }
} catch {
    Write-Host "Token-Fehler: $($_.Exception.Message)"
    exit 1
}

# GET /api/customers
try {
    $customers = Invoke-RestMethod -Method GET -Uri "http://localhost:8000/api/customers?limit=5" -Headers $hdr
    Write-Host "Customers abgerufen: $($customers.Count) Eintraege"
} catch {
    Write-Host "GET Customers Fehler: $($_.Exception.Message)"
}

Write-Host "Test abgeschlossen"
