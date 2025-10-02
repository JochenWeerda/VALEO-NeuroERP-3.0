# Add-Remaining-Files.ps1
#
# Dieses Skript fügt die verbleibenden Dateien zum Git-Repository hinzu.
#
# Verwendung: .\add_remaining_files.ps1

Write-Host "Hinzufügen der verbleibenden Dateien zum Git-Repository" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

# Backend-Dateien hinzufügen
Write-Host "Backend-Dateien werden hinzugefügt..." -ForegroundColor Yellow
git add backend/tasks/__init__.py
git add backend/tasks/celery_app.py
git add backend/tasks/reports.py
git add backend/api/task_endpoints.py
git add backend/demo_server.py

# Dokumente hinzufügen
Write-Host "Dokumentation wird hinzugefügt..." -ForegroundColor Yellow
git add memory-bank/VAN-Modus.md
git add memory-bank/api_cache_migration_guide.md
git add memory-bank/archive/archive-db-optimization.md
git add memory-bank/database_performance_updates.md
git add memory-bank/db_optimization_implementation.md
git add memory-bank/implementation_plan.md
git add memory-bank/minimal_server_anpassungen.md
git add memory-bank/modularisierung_*.md
git add memory-bank/phase3_*.md
git add memory-bank/redis_cluster_setup.md
git add memory-bank/server_integration_plan.md

# Optimierungen hinzufügen
Write-Host "Optimierungen werden hinzugefügt..." -ForegroundColor Yellow
git add backend/enhanced_cache_manager.py
git add backend/core/health.py
git add backend/core/profiling.py
git add backend/core/routing.py
git add backend/core/server.py
git add backend/db/performance_monitor.py
git add backend/db/db_optimization.py
git add backend/db/materialized_views.py
git add backend/monitoring/

# API-Komponenten hinzufügen
Write-Host "API-Komponenten werden hinzugefügt..." -ForegroundColor Yellow
git add backend/api/articles_api.py
git add backend/api/batch_api.py
git add backend/api/chargen_api.py
git add backend/api/charges_api.py
git add backend/api/inventory_api.py
git add backend/api/notifications_api.py
git add backend/api/performance_api.py
git add backend/api/production_api.py
git add backend/api/qs_api.py
git add backend/api/quality_api.py
git add backend/api/stock_charges_api.py
git add backend/api/system_api.py

# Frontend-Komponenten hinzufügen
Write-Host "Frontend-Komponenten werden hinzugefügt..." -ForegroundColor Yellow
git add frontend/src/components/inventory/ChargenBericht/

# Status anzeigen
Write-Host "`nStatus des Repositories:" -ForegroundColor Cyan
git status

Write-Host "`nErfolgreich abgeschlossen. Sie können jetzt einen Commit erstellen mit:" -ForegroundColor Green
Write-Host "git commit -m 'Hinzufügen der verbleibenden System-Komponenten'" -ForegroundColor Green
Write-Host "und dann das Repository zu GitHub pushen mit:" -ForegroundColor Green
Write-Host "git push origin main" -ForegroundColor Green 