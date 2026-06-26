# Kontrakte-Modul Setup

## Migration
1. `alembic upgrade head`

## Seed (optional)
1. `python scripts/seed_kontrakte.py`

## Rollen
Folgende Rollen für Benutzer vergeben:
- `KONTRAKT_LESEN`
- `KONTRAKT_BEARBEITEN`
- `KONTRAKT_LOESCHEN`
- `KONTRAKT_ADMIN`

## UI-Routen
- `/kontrakte` (LstKontraktUebersicht)
- `/kontrakte/neu` (FrmKontraktDetail)
- `/kontrakte/:id` (FrmKontraktDetail)
- `/vertrag/neu` (Alias auf FrmKontraktDetail)

## Smoke-Checkliste
1. `/kontrakte` öffnen, Filter anwenden.
2. Neuer Kontrakt speichern.
3. Kontrakt öffnen und Positionen ändern.
4. `Umsätze`-Dialog öffnen.
5. `PROTOKOLL`-Tab prüfen.
6. Lookup/Matchcode-Dialog öffnen.
