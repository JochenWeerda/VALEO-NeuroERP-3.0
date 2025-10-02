# PowerShell-Tipps für Frontend-Entwicklung

## Befehlsausführung

### Befehlsverkettung

PowerShell verwendet `;` statt `&&` zur Verkettung von Befehlen:

```powershell
# Richtig:
cd frontend; npm start

# Falsch:
cd frontend && npm start
```

### Fehlerbehandlung

```powershell
# Prüfen, ob ein Befehl erfolgreich war
cd frontend
if ($?) {
    echo "Verzeichniswechsel erfolgreich"
} else {
    echo "Fehler beim Verzeichniswechsel"
}

# Fehler abfangen
try {
    npm start
} catch {
    echo "Fehler beim Starten: $_"
}
```

## Portbelegung prüfen

```powershell
# Alle belegten Ports anzeigen
Get-NetTCPConnection -State Listen | 
    Sort-Object -Property LocalPort | 
    Format-Table LocalPort, OwningProcess, State

# Prozess identifizieren
Get-Process -Id <PID>

# Prüfen, ob ein bestimmter Port verfügbar ist
$port = 5173
$inUse = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
if ($inUse) {
    echo "Port $port ist belegt"
} else {
    echo "Port $port ist verfügbar"
}
```

## Umgebungsvariablen

```powershell
# Temporär für die aktuelle Sitzung setzen
$env:PORT = 5000
npm start

# Mehrere Variablen setzen
$env:PORT = 5000
$env:NODE_ENV = "development"
```

## Frontend-Entwicklung

### Skripte nutzen

```powershell
# VAN-Modus Validator ausführen
./scripts/van-frontend-validator.ps1

# Frontend starten
./scripts/start_frontend.ps1
```

### Typische Fehler und Lösungen

#### JSX-Syntax-Fehler
- **Problem**: "The JSX syntax extension is not currently enabled"
- **Lösung**: vite.config.js aktualisieren:
  ```javascript
  esbuild: {
    loader: { '.js': 'jsx', '.ts': 'tsx' },
    jsxFactory: 'React.createElement',
    jsxFragment: 'React.Fragment'
  }
  ```

#### Missing Script: "start"
- **Problem**: npm findet das start-Skript nicht
- **Lösung**: Sicherstellen, dass man im richtigen Verzeichnis ist und package.json die Skripte enthält:
  ```powershell
  cd frontend
  # Skripte in package.json anzeigen:
  (Get-Content package.json -Raw | ConvertFrom-Json).scripts
  ```

#### TypeScript-Fehler
- **Problem**: "Cannot find module 'typescript'"
- **Lösung**: TypeScript installieren:
  ```powershell
  npm install typescript --save-dev
  ```

### Notfalloptionen

Bei hartnäckigen Problemen:

```powershell
# Einfachen HTTP-Server starten
cd frontend
npx http-server -p 8080 .

# Vite direkt starten mit JSX-Loader-Konfiguration
cd frontend
npx vite --port 5000
``` 