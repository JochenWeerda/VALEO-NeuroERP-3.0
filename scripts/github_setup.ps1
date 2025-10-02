# GitHub-Setup.ps1
#
# Dieses Skript enthält Anweisungen zum Einrichten eines GitHub-Repositories 
# und zum Pushen des ERP-Systems zu GitHub.
#
# Verwendung: .\github_setup.ps1

Write-Host "GitHub-Setup für das ERP-System" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan
Write-Host ""

# Überprüfen, ob Git installiert ist
try {
    $gitVersion = git --version
    Write-Host "Git gefunden: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "Git konnte nicht gefunden werden. Bitte installieren Sie Git: https://git-scm.com/downloads" -ForegroundColor Red
    exit
}

Write-Host "`nFolgen Sie diesen Schritten, um Ihr Repository auf GitHub zu pushen:`n" -ForegroundColor Cyan

Write-Host "1. Erstellen Sie ein neues Repository auf GitHub" -ForegroundColor Yellow
Write-Host "   - Gehen Sie zu https://github.com/new"
Write-Host "   - Geben Sie einen Repository-Namen ein (z.B. 'AI_driven_ERP')"
Write-Host "   - Fügen Sie eine Beschreibung hinzu (optional)"
Write-Host "   - Wählen Sie 'Public' oder 'Private'"
Write-Host "   - Klicken Sie auf 'Create repository'"
Write-Host "   - WICHTIG: Aktivieren Sie NICHT die Option 'Initialize this repository with a README'"
Write-Host ""

Write-Host "2. Verknüpfen Sie Ihr lokales Repository mit dem GitHub-Repository" -ForegroundColor Yellow
Write-Host "   Führen Sie im Terminal folgende Befehle aus (ersetzen Sie <username> und <repo> durch Ihre Daten):"
Write-Host "   ```"
Write-Host "   git remote add origin https://github.com/<username>/<repo>.git"
Write-Host "   git branch -M main"
Write-Host "   git push -u origin main"
Write-Host "   ```"
Write-Host ""

Write-Host "3. Oder verwenden Sie diese Befehle mit einem Personal Access Token (für 2FA-aktivierte Konten)" -ForegroundColor Yellow
Write-Host "   ```"
Write-Host "   git remote add origin https://<username>:<token>@github.com/<username>/<repo>.git"
Write-Host "   git branch -M main"
Write-Host "   git push -u origin main"
Write-Host "   ```"
Write-Host ""
Write-Host "   Hinweis: Erstellen Sie einen Personal Access Token unter https://github.com/settings/tokens"
Write-Host "   mit den Berechtigungen 'repo' und 'workflow'"
Write-Host ""

Write-Host "4. Alternativ mit SSH-Authentifizierung (falls eingerichtet)" -ForegroundColor Yellow
Write-Host "   ```"
Write-Host "   git remote add origin git@github.com:<username>/<repo>.git"
Write-Host "   git branch -M main"
Write-Host "   git push -u origin main"
Write-Host "   ```"
Write-Host ""

Write-Host "Nach erfolgreicher Einrichtung können Sie Änderungen wie folgt pushen:" -ForegroundColor Green
Write-Host "   ```"
Write-Host "   git add ."
Write-Host "   git commit -m 'Beschreibung der Änderungen'"
Write-Host "   git push"
Write-Host "   ```"

Write-Host "`nMöchten Sie die Remote-URL jetzt einrichten? (J/N)" -ForegroundColor Cyan
$response = Read-Host

if ($response -eq "J" -or $response -eq "j") {
    $username = Read-Host "GitHub-Benutzername"
    $repo = Read-Host "Repository-Name"
    $authType = Read-Host "Authentifizierungstyp (HTTPS/SSH)"
    
    if ($authType -eq "HTTPS") {
        $useToken = Read-Host "Personal Access Token verwenden? (J/N)"
        
        if ($useToken -eq "J" -or $useToken -eq "j") {
            $token = Read-Host "Personal Access Token"
            $remoteUrl = "https://$username`:$token@github.com/$username/$repo.git"
        } else {
            $remoteUrl = "https://github.com/$username/$repo.git"
        }
    } else {
        $remoteUrl = "git@github.com:$username/$repo.git"
    }
    
    Write-Host "Remote-URL wird eingerichtet: $remoteUrl" -ForegroundColor Yellow
    git remote add origin $remoteUrl
    
    Write-Host "Branch auf 'main' setzen..." -ForegroundColor Yellow
    git branch -M main
    
    $pushNow = Read-Host "Jetzt pushen? (J/N)"
    if ($pushNow -eq "J" -or $pushNow -eq "j") {
        Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
        git push -u origin main
    } else {
        Write-Host "Um später zu pushen, führen Sie aus: git push -u origin main" -ForegroundColor Yellow
    }
} else {
    Write-Host "Sie können die Remote-URL später manuell einrichten." -ForegroundColor Yellow
} 