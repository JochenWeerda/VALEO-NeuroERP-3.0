# ADR-033 — Rollback-Strategie: Zentral in get_db()

**Status:** Angenommen
**Datum:** 2026-05-26
**Kontext:** Wave B1 Data Integrity

---

## Kontext

117 Endpoint-Dateien riefen `db.commit()` auf, hatten aber kein explizites `db.rollback()`
im Fehlerfall. Obwohl PostgreSQL offene Transaktionen beim Verbindungsabbruch automatisch
zurückrollt, gab es keinen Schutz gegen partielle Commits bei mehreren `db.commit()`-Aufrufen
innerhalb eines Request-Handlers.

## Entscheidung

Rollback wird **zentral in `get_db()`** implementiert:

```python
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
```

## Begründung

- **Einmalige Änderung, maximale Abdeckung:** Statt 117 Dateien zu ändern, deckt eine
  Änderung alle aktuellen und zukünftigen Endpoints ab.
- **Korrekte Session-Semantik:** Nach einem unbehandelten Fehler ist die Session in einem
  aborted-Zustand. Explizites Rollback stellt einen bekannten Zustand wieder her.
- **Fail-Secure:** Neue Endpoints, die `get_db()` nutzen, haben automatisch korrektes
  Rollback-Verhalten.

## Grenzen

Mehrere `db.commit()`-Aufrufe innerhalb eines Handlers bleiben ein Risiko: der erste
Commit ist dauerhaft, auch wenn spätere Operationen fehlschlagen. Für kritische
Multi-Commit-Pfade (z.B. Ernte-Annahme mit Outbox-Event) müssen Handler weiterhin
eigene try/except-Rollback-Blöcke implementieren.

## Konsequenzen

- Alle Tests, die `get_db()` nutzen, erhalten automatisch korrektes Rollback-Verhalten.
- Endpoint-Handler, die bereits eigene Rollback-Logik haben, sind nicht betroffen
  (doppeltes Rollback ist idempotent bei PostgreSQL).
- Service-Layer-Extraktion (B3) sollte die Rollback-Verantwortung auf Service-Methoden
  verlagern für Multi-Commit-Szenarien.
