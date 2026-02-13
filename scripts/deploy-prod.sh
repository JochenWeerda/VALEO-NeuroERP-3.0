#!/bin/bash
# VALEO NeuroERP - Produktions-Deployment-Skript
# =============================================

set -e

echo "🚀 VALEO NeuroERP - Produktions-Deployment"
echo "=========================================="

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funktionen
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Prüfe Umgebungsvariablen
check_env() {
    log_info "Prüfe Umgebungsvariablen..."
    
    if [ ! -f .env.prod ]; then
        log_error ".env.prod Datei nicht gefunden!"
        log_info "Kopiere env.prod.example zu .env.prod und konfiguriere die Werte"
        exit 1
    fi
    
    # Lade Umgebungsvariablen
    source .env.prod
    
    # Prüfe kritische Variablen
    if [ -z "$POSTGRES_PASSWORD" ]; then
        log_error "POSTGRES_PASSWORD nicht gesetzt!"
        exit 1
    fi
    
    if [ -z "$GRAFANA_PASSWORD" ]; then
        log_error "GRAFANA_PASSWORD nicht gesetzt!"
        exit 1
    fi
    
    log_info "Umgebungsvariablen OK"
}

# Backup erstellen
create_backup() {
    log_info "Erstelle Backup..."
    
    BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Docker-Volumes sichern
    docker run --rm -v valeo-neuroerp_postgres_data:/data -v "$(pwd)/$BACKUP_DIR":/backup alpine tar czf /backup/postgres_backup.tar.gz -C /data .
    docker run --rm -v valeo-neuroerp_redis_data:/data -v "$(pwd)/$BACKUP_DIR":/backup alpine tar czf /backup/redis_backup.tar.gz -C /data .
    
    log_info "Backup erstellt: $BACKUP_DIR"
}

# Alte Container stoppen
stop_old_containers() {
    log_info "Stoppe alte Container..."
    
    docker-compose -f docker-compose.prod.yml down --remove-orphans || true
    docker system prune -f
}

# Neue Images bauen
build_images() {
    log_info "Baue Produktions-Images..."
    
    docker-compose -f docker-compose.prod.yml build --no-cache
}

# Container starten
start_containers() {
    log_info "Starte Produktions-Container..."
    
    docker-compose -f docker-compose.prod.yml up -d
    
    log_info "Warte auf Container-Start..."
    sleep 30
}

# Health Checks
health_check() {
    log_info "Führe Health Checks durch..."
    
    # Backend Health Check
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_info "✅ Backend ist gesund"
    else
        log_error "❌ Backend Health Check fehlgeschlagen"
        return 1
    fi
    
    # Frontend Health Check
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        log_info "✅ Frontend ist gesund"
    else
        log_error "❌ Frontend Health Check fehlgeschlagen"
        return 1
    fi
    
    # Database Health Check
    if docker exec valeo-neuroerp-postgres-prod pg_isready -U valeo_user > /dev/null 2>&1; then
        log_info "✅ Database ist gesund"
    else
        log_error "❌ Database Health Check fehlgeschlagen"
        return 1
    fi
    
    log_info "Alle Health Checks erfolgreich!"
}

# Monitoring einrichten
setup_monitoring() {
    log_info "Richte Monitoring ein..."
    
    # Warte auf Prometheus
    sleep 10
    
    # Prüfe Prometheus
    if curl -f http://localhost:9090/-/healthy > /dev/null 2>&1; then
        log_info "✅ Prometheus läuft"
    else
        log_warn "⚠️ Prometheus nicht erreichbar"
    fi
    
    # Prüfe Grafana
    if curl -f http://localhost:3001/api/health > /dev/null 2>&1; then
        log_info "✅ Grafana läuft"
    else
        log_warn "⚠️ Grafana nicht erreichbar"
    fi
}

# Cleanup alte Backups
cleanup_old_backups() {
    log_info "Bereinige alte Backups..."
    
    # Lösche Backups älter als 30 Tage
    find ./backups -name "*.tar.gz" -mtime +30 -delete 2>/dev/null || true
}

# Hauptfunktion
main() {
    log_info "Starte Produktions-Deployment..."
    
    check_env
    create_backup
    stop_old_containers
    build_images
    start_containers
    health_check
    setup_monitoring
    cleanup_old_backups
    
    log_info "🎉 Produktions-Deployment erfolgreich abgeschlossen!"
    log_info ""
    log_info "📊 Verfügbare Services:"
    log_info "   - Frontend: http://localhost:3000"
    log_info "   - Backend Modul: http://localhost:8000"
    log_info "   - Grafana: http://localhost:3001"
    log_info "   - Prometheus: http://localhost:9090"
    log_info ""
    log_info "🔧 Nützliche Befehle:"
    log_info "   - Logs anzeigen: docker-compose -f docker-compose.prod.yml logs -f"
    log_info "   - Container-Status: docker-compose -f docker-compose.prod.yml ps"
    log_info "   - Stoppen: docker-compose -f docker-compose.prod.yml down"
}

# Skript ausführen
main "$@" 
