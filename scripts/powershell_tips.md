***REMOVED*** PowerShell-Tipps für Frontend-Entwicklung

***REMOVED******REMOVED*** Befehlsausführung

***REMOVED******REMOVED******REMOVED*** Befehlsverkettung

PowerShell verwendet `;` statt `&&` zur Verkettung von Befehlen:

```powershell
***REMOVED*** Richtig:
cd frontend; npm start

***REMOVED*** Falsch:
cd frontend && npm start
```

***REMOVED******REMOVED******REMOVED*** Fehlerbehandlung

```powershell
***REMOVED*** Prüfen, ob ein Befehl erfolgreich war
cd frontend
if ($?) {
    echo "Verzeichniswechsel erfolgreich"
} else {
    echo "Fehler beim Verzeichniswechsel"
}

***REMOVED*** Fehler abfangen
try {
    npm start
} catch {
    echo "Fehler beim Starten: $_"
}
```

***REMOVED******REMOVED*** Portbelegung prüfen

```powershell
***REMOVED*** Alle belegten Ports anzeigen
Get-NetTCPConnection -State Listen | 
    Sort-Object -Property LocalPort | 
    Format-Table LocalPort, OwningProcess, State

***REMOVED*** Prozess identifizieren
Get-Process -Id <PID>

***REMOVED*** Prüfen, ob ein bestimmter Port verfügbar ist
$port = 5173
$inUse = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
if ($inUse) {
    echo "Port $port ist belegt"
} else {
    echo "Port $port ist verfügbar"
}
```

***REMOVED******REMOVED*** Umgebungsvariablen

```powershell
***REMOVED*** Temporär für die aktuelle Sitzung setzen
$env:PORT = 5000
npm start

***REMOVED*** Mehrere Variablen setzen
$env:PORT = 5000
$env:NODE_ENV = "development"
```

***REMOVED******REMOVED*** Frontend-Entwicklung

***REMOVED******REMOVED******REMOVED*** Skripte nutzen

```powershell
***REMOVED*** VAN-Modus Validator ausführen
./scripts/van-frontend-validator.ps1

***REMOVED*** Frontend starten
./scripts/start_frontend.ps1
```

***REMOVED******REMOVED******REMOVED*** Typische Fehler und Lösungen

***REMOVED******REMOVED******REMOVED******REMOVED*** JSX-Syntax-Fehler
- **Problem**: "The JSX syntax extension is not currently enabled"
- **Lösung**: vite.config.js aktualisieren:
  ```javascript
  esbuild: {
    loader: { '.js': 'jsx', '.ts': 'tsx' },
    jsxFactory: 'React.createElement',
    jsxFragment: 'React.Fragment'
  }
  ```

***REMOVED******REMOVED******REMOVED******REMOVED*** Missing Script: "start"
- **Problem**: npm findet das start-Skript nicht
- **Lösung**: Sicherstellen, dass man im richtigen Verzeichnis ist und package.json die Skripte enthält:
  ```powershell
  cd frontend
  ***REMOVED*** Skripte in package.json anzeigen:
  (Get-Content package.json -Raw | ConvertFrom-Json).scripts
  ```

***REMOVED******REMOVED******REMOVED******REMOVED*** TypeScript-Fehler
- **Problem**: "Cannot find module 'typescript'"
- **Lösung**: TypeScript installieren:
  ```powershell
  npm install typescript --save-dev
  ```

***REMOVED******REMOVED******REMOVED*** Notfalloptionen

Bei hartnäckigen Problemen:

```powershell
***REMOVED*** Einfachen HTTP-Server starten
cd frontend
npx http-server -p 8080 .

***REMOVED*** Vite direkt starten mit JSX-Loader-Konfiguration
cd frontend
npx vite --port 5000
``` 