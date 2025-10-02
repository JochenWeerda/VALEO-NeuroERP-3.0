# Admin-User erstellen
$body = @{
    username = "admin"
    password = "admin"
    email = "admin@valeo.com"
    full_name = "Administrator"
    role = "admin"
} | ConvertTo-Json

Write-Host "Erstelle Admin-User..."
Write-Host "Body: $body"

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8001/api/v1/auth/register" -Method POST -ContentType "application/json" -Body $body
    Write-Host "Admin-User erfolgreich erstellt:"
    Write-Host ($response | ConvertTo-Json -Depth 3)
} catch {
    Write-Host "Fehler beim Erstellen des Admin-Users:"
    Write-Host $_.Exception.Message
}
