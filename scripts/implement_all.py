#!/usr/bin/env python3
"""
Implementiert automatisch alle Code-Artefakte aus der MongoDB.
"""

import os
import sys
import asyncio
import logging
import json
from datetime import datetime
from bson import ObjectId

# Pfad zum Projekt-Root hinzufügen
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.apm_framework.mongodb_connector import APMMongoDBConnector

# Logger konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MongoJSONEncoder(json.JSONEncoder):
    """JSON-Encoder für MongoDB-Objekte."""
    
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(MongoJSONEncoder, self).default(obj)


async def implement_all():
    """
    Implementiert automatisch alle Code-Artefakte aus der MongoDB.
    """
    try:
        # MongoDB-Verbindung herstellen
        mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        mongodb_db = os.getenv("MONGODB_DB", "valeo_neuroerp")
        
        logger.info(f"Stelle Verbindung zu MongoDB her: {mongodb_uri}, DB: {mongodb_db}")
        mongodb = APMMongoDBConnector(mongodb_uri, mongodb_db)
        await mongodb.connect()
        
        # Code-Artefakte abrufen
        code_artifacts = await mongodb.find_many("code_artifacts", {})
        
        if code_artifacts:
            print(f"\nImplementiere {len(code_artifacts)} Code-Artefakte...")
            
            # Ordnerstruktur erstellen
            backend_components_dir = "backend/components"
            frontend_components_dir = "frontend/src/components"
            backend_tests_dir = "backend/tests"
            frontend_tests_dir = "frontend/src/tests"
            
            os.makedirs(backend_components_dir, exist_ok=True)
            os.makedirs(frontend_components_dir, exist_ok=True)
            os.makedirs(backend_tests_dir, exist_ok=True)
            os.makedirs(frontend_tests_dir, exist_ok=True)
            
            # Code-Artefakte implementieren
            for i, artifact in enumerate(code_artifacts):
                name = artifact.get("name")
                language = artifact.get("language")
                code = artifact.get("code", "")
                
                # Dateiendung und Ordner bestimmen
                if language == "Python":
                    file_ext = ".py"
                    folder = backend_components_dir
                elif language == "TypeScript":
                    file_ext = ".tsx"
                    folder = frontend_components_dir
                else:
                    file_ext = ".js"
                    folder = frontend_components_dir
                
                # Datei speichern
                file_path = os.path.join(folder, f"{name}{file_ext}")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(code)
                
                logger.info(f"Code-Artefakt {i+1}/{len(code_artifacts)} implementiert: {file_path}")
                print(f"Code-Artefakt {i+1}/{len(code_artifacts)} implementiert: {file_path}")
            
            print(f"\nAlle Code-Artefakte wurden erfolgreich implementiert!")
        else:
            print("\nKeine Code-Artefakte gefunden.")
        
        # Testfälle abrufen
        test_cases = await mongodb.find_many("test_cases", {})
        
        if test_cases:
            print(f"\nImplementiere {len(test_cases)} Testfälle...")
            
            # Testfälle implementieren
            for i, test in enumerate(test_cases):
                name = test.get("name", "").replace("Test für ", "")
                test_code = test.get("test_code", "")
                
                # Dateiendung und Ordner bestimmen
                if "UserInterface" in name:
                    file_ext = ".test.tsx"
                    folder = frontend_tests_dir
                else:
                    file_ext = "_test.py"
                    folder = backend_tests_dir
                
                # Datei speichern
                file_path = os.path.join(folder, f"{name}{file_ext}")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(test_code)
                
                logger.info(f"Testfall {i+1}/{len(test_cases)} implementiert: {file_path}")
                print(f"Testfall {i+1}/{len(test_cases)} implementiert: {file_path}")
            
            print(f"\nAlle Testfälle wurden erfolgreich implementiert!")
        else:
            print("\nKeine Testfälle gefunden.")
        
        # Ressourcenanforderungen in Konfigurationsdateien umwandeln
        resource_requirements = await mongodb.find_many("resource_requirements", {})
        
        if resource_requirements:
            print(f"\nErstelle Konfigurationsdateien für {len(resource_requirements)} Ressourcenanforderungen...")
            
            # Ordner für Konfigurationsdateien erstellen
            config_dir = "config"
            os.makedirs(config_dir, exist_ok=True)
            
            # Alle Ressourcenanforderungen in einer JSON-Datei speichern
            resources_config = {
                "resources": [
                    {
                        "name": resource.get("name"),
                        "type": resource.get("type"),
                        "description": resource.get("description"),
                        "quantity": resource.get("quantity"),
                        "configuration": resource.get("configuration", {})
                    }
                    for resource in resource_requirements
                ]
            }
            
            resources_file_path = os.path.join(config_dir, "resources.json")
            with open(resources_file_path, "w", encoding="utf-8") as f:
                json.dump(resources_config, f, indent=2, cls=MongoJSONEncoder)
            
            logger.info(f"Ressourcenanforderungen gespeichert in: {resources_file_path}")
            print(f"Ressourcenanforderungen gespeichert in: {resources_file_path}")
            
            # Docker Compose-Datei erstellen
            docker_compose = {
                "version": "3.8",
                "services": {}
            }
            
            # Services basierend auf Ressourcenanforderungen hinzufügen
            for resource in resource_requirements:
                name = resource.get("name", "").lower().replace("-", "_")
                resource_type = resource.get("type", "").lower()
                
                if resource_type == "database" and "postgresql" in name.lower():
                    docker_compose["services"]["postgres"] = {
                        "image": f"postgres:{resource.get('configuration', {}).get('version', 'latest')}",
                        "environment": {
                            "POSTGRES_PASSWORD": "postgres",
                            "POSTGRES_USER": "postgres",
                            "POSTGRES_DB": "valeo_neuroerp"
                        },
                        "ports": ["5432:5432"],
                        "volumes": ["postgres_data:/var/lib/postgresql/data"]
                    }
                elif resource_type == "database" and "mongodb" in name.lower():
                    docker_compose["services"]["mongodb"] = {
                        "image": f"mongo:{resource.get('configuration', {}).get('version', 'latest')}",
                        "ports": ["27017:27017"],
                        "volumes": ["mongodb_data:/data/db"]
                    }
                elif resource_type == "cache" and "redis" in name.lower():
                    docker_compose["services"]["redis"] = {
                        "image": f"redis:{resource.get('configuration', {}).get('version', 'latest')}",
                        "ports": ["6379:6379"]
                    }
                elif resource_type == "server" and "api" in name.lower():
                    docker_compose["services"]["api"] = {
                        "build": {
                            "context": ".",
                            "dockerfile": "docker/api-server.Dockerfile"
                        },
                        "ports": ["8000:8000"],
                        "depends_on": ["postgres", "mongodb", "redis"],
                        "environment": {
                            "MONGODB_URI": "mongodb://mongodb:27017/",
                            "POSTGRES_URI": "postgresql://postgres:postgres@postgres:5432/valeo_neuroerp",
                            "REDIS_URI": "redis://redis:6379/0"
                        }
                    }
                elif resource_type == "server" and "frontend" in name.lower():
                    docker_compose["services"]["frontend"] = {
                        "build": {
                            "context": ".",
                            "dockerfile": "docker/frontend-server.Dockerfile"
                        },
                        "ports": ["3000:3000"],
                        "depends_on": ["api"]
                    }
            
            # Volumes hinzufügen
            docker_compose["volumes"] = {
                "postgres_data": {},
                "mongodb_data": {}
            }
            
            # Docker Compose-Datei speichern
            docker_compose_path = "docker-compose.yml"
            with open(docker_compose_path, "w", encoding="utf-8") as f:
                yaml_content = "# Automatisch generierte Docker Compose-Datei\n\n"
                yaml_content += "version: '3.8'\n\n"
                
                yaml_content += "services:\n"
                for service_name, service_config in docker_compose["services"].items():
                    yaml_content += f"  {service_name}:\n"
                    
                    if "image" in service_config:
                        yaml_content += f"    image: {service_config['image']}\n"
                    
                    if "build" in service_config:
                        yaml_content += f"    build:\n"
                        yaml_content += f"      context: {service_config['build']['context']}\n"
                        yaml_content += f"      dockerfile: {service_config['build']['dockerfile']}\n"
                    
                    if "ports" in service_config:
                        yaml_content += f"    ports:\n"
                        for port in service_config["ports"]:
                            yaml_content += f"      - {port}\n"
                    
                    if "volumes" in service_config:
                        yaml_content += f"    volumes:\n"
                        for volume in service_config["volumes"]:
                            yaml_content += f"      - {volume}\n"
                    
                    if "depends_on" in service_config:
                        yaml_content += f"    depends_on:\n"
                        for dependency in service_config["depends_on"]:
                            yaml_content += f"      - {dependency}\n"
                    
                    if "environment" in service_config:
                        yaml_content += f"    environment:\n"
                        for env_key, env_value in service_config["environment"].items():
                            yaml_content += f"      - {env_key}={env_value}\n"
                    
                    yaml_content += "\n"
                
                yaml_content += "volumes:\n"
                for volume_name in docker_compose["volumes"]:
                    yaml_content += f"  {volume_name}:\n"
            
                f.write(yaml_content)
            
            logger.info(f"Docker Compose-Datei gespeichert in: {docker_compose_path}")
            print(f"Docker Compose-Datei gespeichert in: {docker_compose_path}")
            
            # Dockerfile für API-Server erstellen
            os.makedirs("docker", exist_ok=True)
            
            api_dockerfile_path = "docker/api-server.Dockerfile"
            api_dockerfile_content = """# Automatisch generierte Dockerfile für API-Server
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
            with open(api_dockerfile_path, "w", encoding="utf-8") as f:
                f.write(api_dockerfile_content)
            
            logger.info(f"API-Server Dockerfile gespeichert in: {api_dockerfile_path}")
            print(f"API-Server Dockerfile gespeichert in: {api_dockerfile_path}")
            
            # Dockerfile für Frontend-Server erstellen
            frontend_dockerfile_path = "docker/frontend-server.Dockerfile"
            frontend_dockerfile_content = """# Automatisch generierte Dockerfile für Frontend-Server
FROM node:18-alpine as build

WORKDIR /app

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

FROM nginx:alpine

COPY --from=build /app/build /usr/share/nginx/html
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
"""
            with open(frontend_dockerfile_path, "w", encoding="utf-8") as f:
                f.write(frontend_dockerfile_content)
            
            logger.info(f"Frontend-Server Dockerfile gespeichert in: {frontend_dockerfile_path}")
            print(f"Frontend-Server Dockerfile gespeichert in: {frontend_dockerfile_path}")
            
            # NGINX-Konfiguration erstellen
            nginx_conf_path = "docker/nginx.conf"
            nginx_conf_content = """server {
    listen 3000;
    
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://api:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
"""
            with open(nginx_conf_path, "w", encoding="utf-8") as f:
                f.write(nginx_conf_content)
            
            logger.info(f"NGINX-Konfiguration gespeichert in: {nginx_conf_path}")
            print(f"NGINX-Konfiguration gespeichert in: {nginx_conf_path}")
        else:
            print("\nKeine Ressourcenanforderungen gefunden.")
        
        # CI/CD-Konfiguration erstellen
        print(f"\nErstelle CI/CD-Konfiguration...")
        
        # GitHub Actions Workflow erstellen
        github_dir = ".github/workflows"
        os.makedirs(github_dir, exist_ok=True)
        
        github_workflow_path = os.path.join(github_dir, "ci_cd.yml")
        github_workflow_content = """name: CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_USER: postgres
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      mongodb:
        image: mongo:5
        ports:
          - 27017:27017
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        pytest backend/tests/
      env:
        MONGODB_URI: mongodb://localhost:27017/
        POSTGRES_URI: postgresql://postgres:postgres@localhost:5432/test_db
  
  build:
    runs-on: ubuntu-latest
    needs: test
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to Docker Hub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKER_HUB_USERNAME }}
        password: ${{ secrets.DOCKER_HUB_TOKEN }}
    
    - name: Build and push API image
      uses: docker/build-push-action@v4
      with:
        context: .
        file: ./docker/api-server.Dockerfile
        push: true
        tags: valeo/neuroerp-api:latest
    
    - name: Build and push Frontend image
      uses: docker/build-push-action@v4
      with:
        context: .
        file: ./docker/frontend-server.Dockerfile
        push: true
        tags: valeo/neuroerp-frontend:latest
  
  deploy:
    runs-on: ubuntu-latest
    needs: build
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to production
      run: |
        echo "Deployment would happen here"
        # In a real scenario, you would use kubectl, helm, or another deployment tool
"""
        with open(github_workflow_path, "w", encoding="utf-8") as f:
            f.write(github_workflow_content)
        
        logger.info(f"GitHub Actions Workflow gespeichert in: {github_workflow_path}")
        print(f"GitHub Actions Workflow gespeichert in: {github_workflow_path}")
        
        # Anforderungen in requirements.txt speichern
        requirements_path = "requirements.txt"
        requirements_content = """# Automatisch generierte requirements.txt
fastapi>=0.95.0
uvicorn>=0.21.1
sqlalchemy>=2.0.9
psycopg2-binary>=2.9.6
motor>=3.1.2
pymongo>=4.3.3
redis>=4.5.4
pydantic>=1.10.7
python-jose>=3.3.0
passlib>=1.7.4
python-multipart>=0.0.6
pytest>=7.3.1
httpx>=0.24.0
"""
        with open(requirements_path, "w", encoding="utf-8") as f:
            f.write(requirements_content)
        
        logger.info(f"Requirements gespeichert in: {requirements_path}")
        print(f"Requirements gespeichert in: {requirements_path}")
        
        # README.md erstellen
        readme_path = "README.md"
        readme_content = """# VALEO-NeuroERP

Ein modernes ERP-System mit KI-Unterstützung.

## Komponenten

Das System besteht aus folgenden Hauptkomponenten:

"""
        
        # Komponenten zum README hinzufügen
        for artifact in code_artifacts:
            name = artifact.get("name")
            description = artifact.get("description")
            readme_content += f"- **{name}**: {description}\n"
        
        readme_content += """
## Installation

### Voraussetzungen

- Docker und Docker Compose
- Node.js 18 oder höher (für lokale Entwicklung)
- Python 3.11 oder höher (für lokale Entwicklung)

### Mit Docker

```bash
docker-compose up -d
```

### Lokale Entwicklung

```bash
# Backend
pip install -r requirements.txt
uvicorn backend.main:app --reload

# Frontend
cd frontend
npm install
npm start
```

## Tests

```bash
pytest backend/tests/
```

## CI/CD

Das Projekt verwendet GitHub Actions für CI/CD. Bei jedem Push auf den main-Branch werden Tests ausgeführt und bei Erfolg Docker-Images gebaut und in die Registry gepusht.

## Lizenz

MIT
"""
        
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme_content)
        
        logger.info(f"README gespeichert in: {readme_path}")
        print(f"README gespeichert in: {readme_path}")
        
        print("\n" + "=" * 80)
        print("Implementierung abgeschlossen!")
        print("=" * 80)
        print("\nFolgende Dateien und Verzeichnisse wurden erstellt:")
        print(f"- Backend-Komponenten: {backend_components_dir}/")
        print(f"- Frontend-Komponenten: {frontend_components_dir}/")
        print(f"- Backend-Tests: {backend_tests_dir}/")
        print(f"- Frontend-Tests: {frontend_tests_dir}/")
        print(f"- Docker-Konfiguration: docker/")
        print(f"- Docker Compose: docker-compose.yml")
        print(f"- CI/CD-Konfiguration: {github_dir}/ci_cd.yml")
        print(f"- Ressourcenkonfiguration: {config_dir}/resources.json")
        print(f"- Requirements: requirements.txt")
        print(f"- README: README.md")
        print("\nSie können die Anwendung nun mit Docker Compose starten:")
        print("docker-compose up -d")
    
    except Exception as e:
        logger.error(f"Fehler bei der Implementierung: {str(e)}")
        print(f"\nFehler: {str(e)}")
    
    finally:
        # MongoDB-Verbindung trennen
        if 'mongodb' in locals():
            await mongodb.disconnect()


if __name__ == "__main__":
    # Asynchrone Funktion ausführen
    asyncio.run(implement_all()) 