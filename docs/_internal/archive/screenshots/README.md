# Screenshots

This folder holds screenshots for the main README and project visibility.

## Suggested captures

| File | Description |
|------|-------------|
| `dashboard.png` | AppShell / Dashboard after login, sidebar navigation |
| `finance.png` | Finance – e.g. Open Items or Kreditoren (creditors) |
| `agrar.png` | Agrar – e.g. Ernteannahme (harvest acceptance) or Verträge (contracts) |
| `sales.png` | (Optional) Sales – e.g. Lieferschein (delivery note) |
| `api-docs.png` | (Optional) FastAPI `/docs` or Mask Builder (ListReport/ObjectPage) |

## Automated capture (Playwright)

With frontend (and backend) running:

```bash
cd packages/frontend-web
pnpm screenshots:readme
```

This writes `dashboard.png`, `finance.png`, and `agrar.png` into this folder. For a different base URL (e.g. staging): `FRONTEND_BASE_URL=http://localhost:3001 pnpm screenshots:readme`.

## Manual source

Screenshots can also be taken manually from:

- **Staging:** after running `.\scripts\staging-deploy.ps1` and opening the frontend (e.g. http://localhost:3001)
- **Local:** `pnpm dev` in `packages/frontend-web` and backend on port 8000

The main [README.md](../../README.md) Screenshots section already references the three image paths.
