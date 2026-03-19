## NeuroASSIST Compat Deprecation Plan

Ziel:
- `NeuroASSIST` ist der kanonische Begriff im Anwendungskern.
- `GENXAIS` ist im Anwendungskern entfernt; verbliebene Altbegriffe sind nur noch historische Doku- und Testdateinamen.

Scope der verbleibenden Compat-Schicht:
- Keine produktiven Compat-Routen mehr im Agents-API-Layer.

Phase 1: Abgeschlossen
- Kanonische Module und Services auf `NeuroASSIST` umgestellt.
- Frontend-Client spricht generische `neuroassist`-Run-/Gate-Endpunkte.
- Alt-Routen sind explizit als `deprecated` markiert.

Phase 2: Abgeschlossen
- Alle internen Python-Imports in `app/` und `tests/` auf kanonische `neuroassist*`-Namen gezogen.
- API-Dokumentation und Client-Readmes nur noch mit `neuroassist`-Routen ausgewiesen.

Phase 3: Abgeschlossen
- Alias-Exports aus `app/agents/__init__.py` entfernt.
- Wrapper-Dateien `app/agents/genxais.py` und `app/agents/genxais_service.py` entfernt.
- Deprecated Compat-Route `GET /api/v1/agents/genxais/capabilities` entfernt.

Rest-Cleanup
- Keine offene Compat-Schicht mehr im Anwendungskern oder Agents-API-Layer.

Exit-Kriterien fuer den abgeschlossenen Schnitt
- Kein produktiver Frontend-/Client-Pfad nutzt mehr `bestellvorschlag/*`-Compat-Routen.
- Kein interner Python-Import referenziert mehr entfernte `app.agents.genxais*`-Module.
- Regressionssuiten fuer Agents-/Process-Kernel-/Frontend-API bleiben gruen.
