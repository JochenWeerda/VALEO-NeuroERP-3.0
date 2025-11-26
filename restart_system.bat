@echo off
echo 🔧 VALEO NeuroERP System-Neustart
echo =====================================

echo 📝 Stoppe alle Docker Services...
docker-compose down

echo ⏳ Warte 5 Sekunden...
timeout /t 5 /nobreak > nul

echo 🚀 Starte System neu...
docker-compose up -d

echo ⏳ Warte auf Service-Start (30 Sek)...
timeout /t 30 /nobreak > nul

echo ✅ System-Neustart abgeschlossen!
echo 🌐 Frontend: http://localhost:3000
echo 🔧 Backend: http://localhost:8000

pause

