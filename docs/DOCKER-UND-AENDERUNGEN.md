# Docker: Nutzung der Änderungen (Backend, Frontend, Middleware)

## Kurzfassung

**Ja – alle von uns geänderten Stellen werden in Docker genutzt**, sofern ihr mit den unten beschriebenen Compose-Dateien und Volumes arbeitet.

---

## 1. Welche Änderungen wurden gemacht?

- **Backend:** `main.py` (globaler Exception-Handler mit DEBUG-Detail), `app/api/v1/endpoints/portal_feldbuch.py` (Fehlerbehandlung, JSON-Serialisierung, OperationalError), `alembic/versions/feldbuch_schlag_massnahme_20260226.py` und `agrar_maschinen_wetter_20260301.py` (CREATE SCHEMA IF NOT EXISTS).
- **Frontend:** Keine Code-Änderungen in dieser Runde; Konfiguration (z. B. Proxy) bleibt in `packages/frontend-web`.
- **Middleware:** Läuft im Backend (`main.py`: Auth, CORS, GZip, Logging, globaler Exception-Handler) und im Frontend (Vite-Proxy für `/api/v1` → Backend).

---

## 2. docker-compose.yml (Vollstack)

| Service       | Nutzt unsere Änderungen? | Wie? |
|---------------|---------------------------|------|
| **backend**   | **Ja**                    | Volumes mounten Host-Code: `./app`, `./main.py`, `./alembic`, `./alembic.ini`, `./modules`. Der Container läuft mit diesem gemounteten Code (und `--reload`). |
| **frontend-web** | **Ja** (Frontend-Code) | Volume `./packages/frontend-web:/app` – der Container nutzt euren aktuellen Frontend-Stand. |
| **bff-web**   | Ja                        | Volume `.:/app` – BFF-Code vom Host. |
| **dev-sse**   | Ja                        | Volume `.:/app` – SSE-Server vom Host. |

- **Proxy:** Im Container setzt das Frontend `VITE_BACKEND_PROXY: http://backend:8000`. Aufrufe von `localhost:3000` zu `/api/v1/...` gehen an Vite und werden an den Service **backend:8000** weitergeleitet – also an das Backend mit den gemounteten Änderungen.
- **Middleware:** Die gesamte Backend-Middleware (Auth, CORS, GZip, Exception-Handler usw.) liegt in `main.py` und `app/` und wird durch die Volumes aktiv genutzt.
- **Migrationen:** Das Backend startet mit `alembic upgrade head` (fehlertolerant), danach `uvicorn ...`. So werden Schemas (z. B. `domain_agrar`) beim Start angelegt. Bei Fehlern von Alembic startet der Server trotzdem; dann ggf. manuell: `docker compose exec backend alembic upgrade head`.

---

## 3. docker-compose.dev.yml (Minimal: DB + Backend)

| Service   | Nutzt unsere Änderungen? | Wie? |
|-----------|---------------------------|------|
| **backend** | **Ja**                  | Volume `.:/app:cached` – kompletter Host-Stand wird gemountet. Zusätzlich nutzt das Backend `Dockerfile.backend.dev` und `entrypoint.sh`, der vor dem Start **alembic upgrade head** ausführt. |

- Hier läuft **kein** Frontend in Docker; das Frontend startet man lokal (`npm run dev`) und spricht per Proxy mit dem Backend-Container. Die Backend-Änderungen (inkl. Middleware) sind im Container aktiv.

---

## 4. Migrationen im Vollstack

Im **Vollstack** führt das Backend beim Start automatisch `alembic upgrade head` aus (fehlertolerant). Wenn trotzdem Schemas fehlen (z. B. nach DB-Reset):

```bash
docker compose exec backend alembic upgrade head
```

---

## 5. Production-Build (Image ohne Volumes)

Wenn Images **ohne** Volumes genutzt werden (z. B. Production), kommen die Änderungen nur ins Image, wenn **nach** den Code-Änderungen neu gebaut wird:

```bash
docker compose build backend
# bzw. docker build -f Dockerfile.backend -t valeo-backend .
```

Dann enthält das Image den Stand von `main.py`, `app/` und `alembic/` zum Build-Zeitpunkt.
