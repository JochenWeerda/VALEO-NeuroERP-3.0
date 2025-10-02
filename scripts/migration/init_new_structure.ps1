***REMOVED*** PowerShell-Skript zur Initialisierung der neuen Projektstruktur
$ErrorActionPreference = "Stop"

***REMOVED*** Basis-Verzeichnis definieren
$BASE_DIR = "C:\Users\Jochen\VALEO-NeuroERP-2.0"

***REMOVED*** Funktion zum Erstellen von Verzeichnissen
function Create-ProjectStructure {
    param (
        [string]$basePath,
        [hashtable]$structure
    )
    
    foreach ($key in $structure.Keys) {
        $path = Join-Path $basePath $key
        
        ***REMOVED*** Verzeichnis erstellen
        New-Item -Path $path -ItemType Directory -Force | Out-Null
        Write-Host "Erstellt: $path"
        
        ***REMOVED*** Wenn es Unterverzeichnisse gibt, rekursiv erstellen
        if ($structure[$key] -is [hashtable]) {
            Create-ProjectStructure -basePath $path -structure $structure[$key]
        }
        
        ***REMOVED*** README.md für jedes Hauptverzeichnis erstellen
        if ($key -notmatch "^\.") {  ***REMOVED*** Keine README für versteckte Verzeichnisse
            $readmePath = Join-Path $path "README.md"
            $readmeContent = @"
***REMOVED*** $key

***REMOVED******REMOVED*** Beschreibung
$(if ($structure[$key] -is [string]) { $structure[$key] } else { "Dieses Verzeichnis enthält..." })

***REMOVED******REMOVED*** Struktur
$(if ($structure[$key] -is [hashtable]) {
    $structure[$key].Keys | ForEach-Object { "- $_" } | Out-String
})

***REMOVED******REMOVED*** Verwendung
Beschreiben Sie hier, wie dieses Modul verwendet wird...
"@
            Set-Content -Path $readmePath -Value $readmeContent -Encoding UTF8
            Write-Host "README erstellt: $readmePath"
        }
    }
}

***REMOVED*** Projektstruktur definieren
$PROJECT_STRUCTURE = @{
    '.cursor' = @{
        'rules' = "Cursor-spezifische Regeln"
    }
    '.github' = @{
        'workflows' = "GitHub Actions Workflows"
    }
    'apps' = @{
        'api' = @{
            'routes' = "API Routen"
            'middleware' = "Middleware-Komponenten"
            'handlers' = "Request Handler"
        }
        'web' = @{
            'src' = @{
                'components' = "React Komponenten"
                'pages' = "Seiten-Komponenten"
                'hooks' = "Custom Hooks"
                'utils' = "Frontend Utilities"
            }
            'public' = "Statische Assets"
        }
        'worker' = @{
            'processors' = "Task Processors"
            'queues' = "Queue Definitionen"
            'handlers' = "Task Handler"
        }
    }
    'core' = @{
        'common' = @{
            'base' = "Basis-Klassen"
            'interfaces' = "Schnittstellen-Definitionen"
            'types' = "Typ-Definitionen"
        }
        'config' = "Konfigurationsmanagement"
        'data' = @{
            'models' = "Datenmodelle"
            'schemas' = "Schema-Definitionen"
            'migrations' = "Datenbank-Migrationen"
        }
        'utils' = "Utility-Funktionen"
    }
    'data_integration' = @{
        'langgraph' = @{
            'nodes' = "Graph-Knoten"
            'edges' = "Graph-Kanten"
            'processors' = "Graph-Prozessoren"
        }
        'mongodb' = @{
            'models' = "MongoDB Modelle"
            'repositories' = "MongoDB Repositories"
            'migrations' = "MongoDB Migrationen"
        }
        'rag' = @{
            'engines' = "RAG Engines"
            'indexers' = "Dokument-Indexierer"
            'retrievers' = "Retrieval-Komponenten"
        }
        'repositories' = "Repository Implementierungen"
    }
    'docs' = @{
        'api' = "API Dokumentation"
        'architecture' = "Architektur-Dokumentation"
        'guides' = @{
            'development' = "Entwickler-Guides"
            'deployment' = "Deployment-Guides"
            'maintenance' = "Wartungs-Guides"
        }
    }
    'infrastructure' = @{
        'docker' = @{
            'api' = "API Docker-Konfiguration"
            'worker' = "Worker Docker-Konfiguration"
            'monitoring' = "Monitoring Docker-Konfiguration"
        }
        'kubernetes' = @{
            'base' = "Basis-Manifeste"
            'overlays' = "Kustomize Overlays"
            'charts' = "Helm Charts"
        }
        'terraform' = @{
            'modules' = "Terraform Module"
            'environments' = "Umgebungs-Konfigurationen"
        }
    }
    'mcp' = @{
        'agents' = "Intelligente Agenten"
        'controllers' = "Prozess-Controller"
        'pipelines' = "Verarbeitungs-Pipelines"
    }
    'scripts' = @{
        'deployment' = "Deployment-Skripte"
        'maintenance' = "Wartungs-Skripte"
        'migration' = "Migrations-Skripte"
    }
    'services' = @{
        'auth' = @{
            'handlers' = "Auth Handler"
            'middleware' = "Auth Middleware"
            'providers' = "Auth Provider"
        }
        'notification' = @{
            'handlers' = "Notification Handler"
            'templates' = "Notification Templates"
            'providers' = "Notification Provider"
        }
        'search' = @{
            'engines' = "Such-Engines"
            'indexers' = "Such-Indexierer"
            'analyzers' = "Text-Analysierer"
        }
    }
    'tests' = @{
        'integration' = "Integrationstests"
        'performance' = "Performance-Tests"
        'unit' = @{
            'core' = "Core Unit-Tests"
            'services' = "Service Unit-Tests"
            'utils' = "Utils Unit-Tests"
        }
    }
    'tools' = @{
        'cli' = "Command Line Tools"
        'generators' = "Code-Generatoren"
    }
}

***REMOVED*** Hauptfunktion
function Initialize-Project {
    ***REMOVED*** Prüfen, ob das Basis-Verzeichnis existiert
    if (Test-Path $BASE_DIR) {
        Write-Host "WARNUNG: Verzeichnis existiert bereits: $BASE_DIR"
        $confirmation = Read-Host "Möchten Sie fortfahren? (j/n)"
        if ($confirmation -ne 'j') {
            Write-Host "Abgebrochen."
            return
        }
    }
    
    ***REMOVED*** Basis-Verzeichnis erstellen
    New-Item -Path $BASE_DIR -ItemType Directory -Force | Out-Null
    Write-Host "Projekt-Verzeichnis erstellt: $BASE_DIR"
    
    ***REMOVED*** Projektstruktur erstellen
    Create-ProjectStructure -basePath $BASE_DIR -structure $PROJECT_STRUCTURE
    
    ***REMOVED*** Git initialisieren
    Set-Location $BASE_DIR
    git init
    
    ***REMOVED*** .gitignore erstellen
    $gitignore = @"
***REMOVED*** Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

***REMOVED*** Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

***REMOVED*** IDEs
.idea/
.vscode/
*.swp
*.swo

***REMOVED*** Environments
.env
.venv
env/
venv/
ENV/

***REMOVED*** Logs
logs/
*.log

***REMOVED*** Database
*.sqlite3
*.db

***REMOVED*** Build
build/
dist/

***REMOVED*** Coverage
.coverage
coverage/

***REMOVED*** Cache
.cache/
.pytest_cache/

***REMOVED*** Local development
.env.local
.env.development.local
.env.test.local
.env.production.local

***REMOVED*** Docker
.docker/

***REMOVED*** Kubernetes
.kube/

***REMOVED*** Terraform
.terraform/
*.tfstate
*.tfstate.*
*.tfvars

***REMOVED*** RAG
data/rag_index/
"@
    Set-Content -Path (Join-Path $BASE_DIR ".gitignore") -Value $gitignore -Encoding UTF8
    
    ***REMOVED*** requirements.txt erstellen
    $requirements = @"
***REMOVED*** Core
fastapi==0.68.1
uvicorn==0.15.0
pydantic==1.8.2
python-dotenv==0.19.0

***REMOVED*** Database
motor==2.5.1
odmantic==0.3.5
beanie==1.11.0

***REMOVED*** RAG
langchain==0.0.184
chromadb==0.3.21
sentence-transformers==2.2.2

***REMOVED*** Graph
networkx==2.6.3
graphviz==0.17

***REMOVED*** Monitoring
prometheus-client==0.11.0
opentelemetry-api==1.11.1
opentelemetry-sdk==1.11.1

***REMOVED*** Testing
pytest==6.2.5
pytest-asyncio==0.15.1
pytest-cov==2.12.1

***REMOVED*** Utils
python-jose==3.3.0
passlib==1.7.4
python-multipart==0.0.5
aiofiles==0.7.0
"@
    Set-Content -Path (Join-Path $BASE_DIR "requirements.txt") -Value $requirements -Encoding UTF8
    
    ***REMOVED*** package.json für Web-App erstellen
    $packageJson = @"
{
  "name": "valeo-neuroerp-web",
  "version": "2.0.0",
  "private": true,
  "dependencies": {
    "@emotion/react": "^11.7.0",
    "@emotion/styled": "^11.6.0",
    "@mui/material": "^5.2.3",
    "@mui/icons-material": "^5.2.1",
    "@reduxjs/toolkit": "^1.7.1",
    "axios": "^0.24.0",
    "react": "^17.0.2",
    "react-dom": "^17.0.2",
    "react-router-dom": "^6.2.1",
    "react-query": "^3.34.0"
  },
  "devDependencies": {
    "@testing-library/jest-dom": "^5.16.1",
    "@testing-library/react": "^12.1.2",
    "@types/node": "^16.11.12",
    "@types/react": "^17.0.37",
    "@types/react-dom": "^17.0.11",
    "typescript": "^4.5.4"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  }
}
"@
    Set-Content -Path (Join-Path $BASE_DIR "apps\web\package.json") -Value $packageJson -Encoding UTF8
    
    Write-Host "Projekt-Initialisierung abgeschlossen!"
    Write-Host "Nächste Schritte:"
    Write-Host "1. Python Virtual Environment erstellen"
    Write-Host "2. Dependencies installieren"
    Write-Host "3. Git Repository konfigurieren"
    Write-Host "4. Entwicklungsumgebung einrichten"
}

***REMOVED*** Skript ausführen
Initialize-Project 