# Deployment-Skript für das APM Multi-Agenten-System
param(
    [string]$Namespace = "valeo-neuroerp",
    [string]$MongoDBUri,
    [switch]$SkipConfirmation
)

# Funktion zum Überprüfen der Voraussetzungen
function Test-Prerequisites {
    Write-Host "Überprüfe Voraussetzungen..." -ForegroundColor Yellow
    
    # Kubectl überprüfen
    if (!(Get-Command kubectl -ErrorAction SilentlyContinue)) {
        throw "kubectl nicht gefunden. Bitte installieren Sie kubectl."
    }
    
    # Kubernetes-Verbindung testen
    try {
        kubectl version --short
    } catch {
        throw "Keine Verbindung zum Kubernetes-Cluster möglich."
    }
    
    Write-Host "✓ Voraussetzungen erfüllt" -ForegroundColor Green
}

# Funktion zum Erstellen des Namespaces
function New-Namespace {
    Write-Host "Erstelle Namespace $Namespace..." -ForegroundColor Yellow
    
    kubectl create namespace $Namespace --dry-run=client -o yaml | kubectl apply -f -
    
    Write-Host "✓ Namespace erstellt/aktualisiert" -ForegroundColor Green
}

# Funktion zum Erstellen der MongoDB-Credentials
function New-MongoDBSecret {
    Write-Host "Erstelle MongoDB-Credentials..." -ForegroundColor Yellow
    
    if (-not $MongoDBUri) {
        $MongoDBUri = Read-Host "Bitte geben Sie die MongoDB-URI ein"
    }
    
    $encodedUri = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($MongoDBUri))
    
    @"
apiVersion: v1
kind: Secret
metadata:
  name: mongodb-credentials
  namespace: $Namespace
type: Opaque
data:
  uri: $encodedUri
"@ | kubectl apply -f -
    
    Write-Host "✓ MongoDB-Credentials erstellt" -ForegroundColor Green
}

# Funktion zum Anwenden der Sicherheitskonfigurationen
function Apply-SecurityConfigs {
    Write-Host "Wende Sicherheitskonfigurationen an..." -ForegroundColor Yellow
    
    # RBAC
    kubectl apply -f kubernetes-manifests/apm-agents/rbac.yaml
    
    # Network Policies
    kubectl apply -f kubernetes-manifests/apm-agents/network-policy.yaml
    
    # Pod Security Policy
    kubectl apply -f kubernetes-manifests/apm-agents/pod-security-policy.yaml
    
    Write-Host "✓ Sicherheitskonfigurationen angewendet" -ForegroundColor Green
}

# Funktion zum Überprüfen der Sicherheitskonfigurationen
function Test-SecurityConfigs {
    Write-Host "Überprüfe Sicherheitskonfigurationen..." -ForegroundColor Yellow
    
    # RBAC überprüfen
    $serviceAccount = kubectl get serviceaccount apm-multi-agent -n $Namespace -o jsonpath='{.metadata.name}' 2>$null
    if ($serviceAccount -ne "apm-multi-agent") {
        throw "ServiceAccount nicht gefunden"
    }
    
    # Network Policy überprüfen
    $networkPolicy = kubectl get networkpolicy apm-multi-agent-network-policy -n $Namespace -o jsonpath='{.metadata.name}' 2>$null
    if ($networkPolicy -ne "apm-multi-agent-network-policy") {
        throw "NetworkPolicy nicht gefunden"
    }
    
    Write-Host "✓ Sicherheitskonfigurationen erfolgreich überprüft" -ForegroundColor Green
}

# Funktion zum Anwenden der Kubernetes-Manifeste
function Apply-Manifests {
    Write-Host "Wende Kubernetes-Manifeste an..." -ForegroundColor Yellow
    
    # Deployment und Service
    kubectl apply -f kubernetes-manifests/apm-agents/deployment.yaml
    kubectl apply -f kubernetes-manifests/apm-agents/service.yaml
    kubectl apply -f kubernetes-manifests/apm-agents/pdb.yaml
    
    # Monitoring
    kubectl apply -f kubernetes-manifests/monitoring/servicemonitor.yaml
    kubectl apply -f kubernetes-manifests/monitoring/prometheus-rules.yaml
    
    Write-Host "✓ Kubernetes-Manifeste angewendet" -ForegroundColor Green
}

# Funktion zum Überprüfen des Deployments
function Test-Deployment {
    Write-Host "Überprüfe Deployment-Status..." -ForegroundColor Yellow
    
    $maxAttempts = 30
    $attempt = 0
    $success = $false
    
    while ($attempt -lt $maxAttempts) {
        $status = kubectl get deployment apm-multi-agent -n $Namespace -o jsonpath='{.status.availableReplicas}'
        
        if ($status -eq "1") {
            $success = $true
            break
        }
        
        $attempt++
        Write-Host "Warte auf Deployment... ($attempt/$maxAttempts)" -ForegroundColor Yellow
        Start-Sleep -Seconds 10
    }
    
    if ($success) {
        Write-Host "✓ Deployment erfolgreich" -ForegroundColor Green
    } else {
        Write-Host "✗ Deployment fehlgeschlagen" -ForegroundColor Red
        Write-Host "Bitte überprüfen Sie die Logs mit: kubectl logs -n $Namespace deployment/apm-multi-agent"
    }
}

# Hauptausführung
try {
    if (-not $SkipConfirmation) {
        $confirm = Read-Host "Möchten Sie das APM Multi-Agenten-System in Namespace '$Namespace' deployen? (j/n)"
        if ($confirm -ne "j") {
            Write-Host "Deployment abgebrochen." -ForegroundColor Yellow
            exit
        }
    }
    
    Test-Prerequisites
    New-Namespace
    New-MongoDBSecret
    Apply-SecurityConfigs
    Apply-Manifests
    Test-Deployment
    Test-SecurityConfigs
    
    Write-Host "Deployment abgeschlossen!" -ForegroundColor Green
} catch {
    Write-Host "Fehler beim Deployment: $_" -ForegroundColor Red
    exit 1
} 