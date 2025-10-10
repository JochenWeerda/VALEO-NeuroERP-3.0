# GitHub Secrets Upload Script
# Automatisches Hochladen der Secrets zu GitHub
# Requires: GitHub CLI (gh) installiert

param(
    [switch]$DryRun = $false
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  GitHub Secrets Upload" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Repository
$REPO = "JochenWeerda/VALEO-NeuroERP-3.0"

# Secrets aus der generierten Datei
$SECRETS = @{
    "STAGING_POSTGRES_PASSWORD" = 'LieE0VQnmN9&r5Pd%RcjbvkU'
    "STAGING_KEYCLOAK_PASSWORD" = 'neZfWPk0utE@rAKBYI8QyMXw'
    "STAGING_PGADMIN_PASSWORD"  = 'D@I2&lyz#SUjMHT8RgYL4ct1'
    "STAGING_REDIS_PASSWORD"    = 'DtOAn!VMK1rL$5lBQE60k%y9'
}

# Pruefe ob GitHub CLI installiert ist
Write-Host "Pruefe GitHub CLI Installation..." -ForegroundColor Yellow
try {
    $ghVersion = gh --version 2>&1 | Select-String "gh version"
    Write-Host "GitHub CLI gefunden: $ghVersion" -ForegroundColor Green
}
catch {
    Write-Host "GitHub CLI nicht gefunden!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Bitte installiere GitHub CLI:" -ForegroundColor Yellow
    Write-Host "  1. Download: https://cli.github.com/" -ForegroundColor White
    Write-Host "  2. Oder via winget: winget install GitHub.cli" -ForegroundColor White
    Write-Host ""
    exit 1
}

# Pruefe Authentifizierung
Write-Host ""
Write-Host "Pruefe GitHub Authentifizierung..." -ForegroundColor Yellow
try {
    $authStatus = gh auth status 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Nicht bei GitHub angemeldet!" -ForegroundColor Red
        Write-Host ""
        Write-Host "Bitte anmelden mit:" -ForegroundColor Yellow
        Write-Host "  gh auth login" -ForegroundColor White
        Write-Host ""
        exit 1
    }
    Write-Host "Bei GitHub angemeldet" -ForegroundColor Green
}
catch {
    Write-Host "Authentifizierung fehlgeschlagen!" -ForegroundColor Red
    exit 1
}

# Dry-Run Info
if ($DryRun) {
    Write-Host ""
    Write-Host "DRY-RUN MODE - Keine Aenderungen!" -ForegroundColor Yellow
    Write-Host ""
}

# Secrets hochladen
Write-Host ""
Write-Host "Lade Secrets zu GitHub Repository: $REPO" -ForegroundColor Cyan
Write-Host ""

$uploaded = 0
$failed = 0

foreach ($secretName in $SECRETS.Keys) {
    $secretValue = $SECRETS[$secretName]
    
    Write-Host "  Processing: $secretName..." -NoNewline
    
    if ($DryRun) {
        Write-Host " [DRY-RUN]" -ForegroundColor Yellow
        $uploaded++
    }
    else {
        try {
            # Secret hochladen
            $secretValue | gh secret set $secretName --repo $REPO
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host " OK" -ForegroundColor Green
                $uploaded++
            }
            else {
                Write-Host " FAILED" -ForegroundColor Red
                $failed++
            }
        }
        catch {
            Write-Host " FAILED: $_" -ForegroundColor Red
            $failed++
        }
    }
    
    Start-Sleep -Milliseconds 500
}

# Zusammenfassung
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Upload abgeschlossen" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Erfolgreich hochgeladen: $uploaded" -ForegroundColor Green
if ($failed -gt 0) {
    Write-Host "Fehlgeschlagen: $failed" -ForegroundColor Red
}
Write-Host ""

if (-not $DryRun) {
    # Secrets verifizieren
    Write-Host "Verifiziere Secrets in GitHub..." -ForegroundColor Yellow
    Write-Host ""
    
    try {
        gh secret list --repo $REPO
        Write-Host ""
        Write-Host "Alle Secrets erfolgreich eingetragen!" -ForegroundColor Green
    }
    catch {
        Write-Host "Konnte Secrets nicht verifizieren" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "Naechster Schritt: Code pushen" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  git add ." -ForegroundColor White
    Write-Host "  git commit -m 'feat: staging deployment setup'" -ForegroundColor White
    Write-Host "  git checkout develop 2>` $null || git checkout -b develop" -ForegroundColor White
    Write-Host "  git push origin develop" -ForegroundColor White
    Write-Host ""
}
else {
    Write-Host "Fuehre das Script ohne -DryRun aus:" -ForegroundColor Yellow
    Write-Host "  .\scripts\upload-github-secrets.ps1" -ForegroundColor White
    Write-Host ""
}
